from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from pushbullet import PushBullet
from datetime import datetime

def main():

    output_memory = ""

    f = open("login_info.txt", "r")
    info = f.read()
    f.close()
    
    info = info.split("\n")
    username = info[0][10:]
    password = info[1][10:]
    api_key = info[2][9:]

    submit_button = "[type=button]:not(:disabled), [type=reset]:not(:disabled), [type=submit]:not(:disabled), button:not(:disabled)"
    url = "https://mail1.upnet.gr/?_task=login"

    service = Service(ChromeDriverManager().install())

    options = Options()
    options.add_argument("--headless") #Don't show browser

    while True:

        try:
            driver = webdriver.Chrome(options = options, service = service)

            try: driver.get(url)
            except:
                f = open("login_errors.txt", "a", encoding = 'utf-8')
                f.write("The URL didn't load. | {}\n".format(str(datetime.now())[:19]))
                f.close()

            driver.find_element(By.NAME, "_user").send_keys(username)
            driver.find_element(By.NAME, "_pass").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, submit_button).click()

            html = driver.page_source
                    
            driver.close()

            all_messages_indexStart = html.index('<tbody><tr')
            all_messages_indexEnd = html.index('</div>', all_messages_indexStart)
            all_messages = html[all_messages_indexStart : all_messages_indexEnd]

            messages = all_messages.split('class="message unread')
            messages.pop(0)

            new_messages_number = all_messages.count('class="msgicon status unread" title="Μη αναγνωσμένο "')

            output = ""
            
            for information in range(len(messages)):
                
                if messages[information].count('Μη αναγνωσμένο') == 0: break
                
                mail_address_indexStart = messages[information].index('class="adr"><span title="') + 25
                mail_address_indexEnd = messages[information].index('" class', mail_address_indexStart)
                mail_address = messages[information][mail_address_indexStart : mail_address_indexEnd]

                contact_address_indexStart = messages[information].index('Address') + 9
                contact_address_indexEnd = messages[information].index('</span>', contact_address_indexStart)
                contact_address = messages[information][contact_address_indexStart : contact_address_indexEnd]

                date_indexStart = messages[information].index('class="date skip-on-drag">') + 26
                date_indexEnd = messages[information].index('</span>', date_indexStart)
                date = messages[information][date_indexStart : date_indexEnd]

                title_indexStart = messages[information].index('long_subject_title') + 48
                title_indexEnd = messages[information].index('</span>', title_indexStart)
                title = messages[information][title_indexStart : title_indexEnd]
                
                output += "Τίτλος μυνήματος: "+title+"\nΑποστολέας: "+contact_address+" ["+mail_address+"]\nΗμερομηνία: "+date+"\n\n"

            if output != output_memory:

                output_memory = output
                
                try:
                    pb = PushBullet(api_key)
                    if new_messages_number > 1: push = pb.push_note("UPnet Webmail", "Έχετε {} νέα μυνήματα!\n\n{}Ημερομηνία συγχρονισμού: {}".format(new_messages_number, output, str(datetime.now())[:19]))
                    elif new_messages_number == 1: push = pb.push_note("UPnet Webmail", "Έχετε 1 νέο μύνημα!\n\n{}Ημερομηνία συγχρονισμού: {}".format(output, str(datetime.now())[:19]))

                except:
                    f = open("login_errors.txt", "a", encoding = 'utf-8')
                    f.write("Con err. Wrong API_key. | {}\n\n".format(str(datetime.now())[:19]))
                    f.close()

        except:
            f = open("login_errors.txt", "a", encoding = 'utf-8')
            f.write("Couldn't execute program. | {}\n\n".format(str(datetime.now())[:19]))
            f.close()

        sleep(180) #Δt waiting for new mail check!

main()
