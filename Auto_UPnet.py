from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from warnings import filterwarnings
from time import sleep
from os.path import getsize
from os import getcwd
from pushbullet import PushBullet
from datetime import datetime
from subprocess import CREATE_NO_WINDOW
    
def main():

    new = 0
    
    f = open("login_info.txt", "r")
    info = f.read()
    f.close()
    info = info.split("\n")
    
    username = info[0][10:]
    password = info[1][10:]
    api_key = info[2][9:]

    filterwarnings("ignore")

    submit_button = "[type=button]:not(:disabled), [type=reset]:not(:disabled), [type=submit]:not(:disabled), button:not(:disabled)"
    url = "https://mail1.upnet.gr/?_task=login"

    
    CHROMEDRIVER_PATH = str(getcwd()) + "\chromedriver.exe"
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    WINDOW_SIZE = "400,800"

    service = Service(CHROMEDRIVER_PATH)
    service.creationflags = CREATE_NO_WINDOW #Don't show cmd

    chrome_options = Options()
    chrome_options.add_argument("--headless") #Don't show Chrome
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH
    
    while True:

        try:

            driver = webdriver.Chrome(executable_path = CHROMEDRIVER_PATH, chrome_options = chrome_options, service = service)

            try: driver.get(url)
            except:
                f = open("login_errors.txt", "a", encoding = 'utf-8')
                f.write("The URL didn't load. | {}\n".format(str(datetime.now())[:19]))
                f.close()

            driver.find_element_by_name("_user").send_keys(username)
            driver.find_element_by_name("_pass").send_keys(password)
            driver.find_element_by_css_selector(submit_button).click()

            sleep(2) #Wait for page to load!

            driver.get_screenshot_as_file("New_mail.png")
            driver.close()

            answer = getsize("New_mail.png")

            if answer != 19388 and answer != new: #Check if New_mail.png size matches with no message size

                new = answer #If you received a new mail, next time you will not be notified for the same mail!

                try:
                    pb = PushBullet(api_key)
                    push = pb.push_note("UPnet Webmail", "You have 1 new message!\n{}".format(str(datetime.now())[:19]))

                    with open("New_mail.png", "rb") as pic:
                        file_data = pb.upload_file(pic, "New_mail.png") #Send message to mobile device 
                    push = pb.push_file(**file_data)
                except:
                    f = open("login_errors.txt", "a", encoding = 'utf-8')
                    f.write("Con err. Wrong API_key. | {}\n\n".format(str(datetime.now())[:19]))
                    f.close()
                
        except:
            
            f = open("login_errors.txt", "a", encoding = 'utf-8')
            f.write("Couldn't execute program. | {}\n\n".format(str(datetime.now())[:19]))
            f.close()

        sleep(300) #Δt waiting for new mail check!

main()
