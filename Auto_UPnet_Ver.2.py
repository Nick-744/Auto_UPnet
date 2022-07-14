from requests import Session
from time import sleep
from plyer import notification
from cryptography.fernet import Fernet
from datetime import datetime
from os.path import exists

def error_handle(errors_number):

    dateTimeNow = str(datetime.now())[:19]
    login_errors_file = "login_errors.txt"

    if exists(login_errors_file) == False:
        with open(login_errors_file, "w") as f:
            f.write('Auto_UPnet Errors that have occurred:\n\n')

    with open(login_errors_file, "a") as f:
        if   errors_number == 1: f.write("The URL didn't load.    | {}\n".format(dateTimeNow)) #getHTML() Err
        elif errors_number == 3: f.write("Couldn't execute check. | {}\n".format(dateTimeNow)) #main() [Loop] Err

    return;

def loginInfo():

    login_info = "login_info.txt"
    
    if exists(login_info) == False:
        success = False
        
        for tries in range(3):
            username = str(input("Πληκτρολόγησε το username σου: "))
            password = str(input("Πληκτρολόγησε το password σου: "))
            
            test_login = getHTML(username, password)
            if test_login.count('Η συνεδρία σας είναι άκυρη ή έχει λήξει.') == 0:
                print("\nΕπιτυχής σύνδεση!\n")
                success = True

                key = Fernet.generate_key()
                with open("the.key", "wb") as f:
                    f.write(key)

                info = "{}\n{}".format(username, password)
                info = bytes(info, encoding = 'utf8')
                info_encrypted = Fernet(key).encrypt(info)
                with open(login_info, "wb") as f:
                    f.write(info_encrypted)
                
                break
            
            print("\nΑποτυχία σύνδεσης!\nΣας απομένουν {} προσπάθειες.\n".format(str(2 - tries)))
            
        if success == False:
            print("- Τερματισμός Προγράμματος -")
            sleep(3)

            exit(1)

    with open("the.key", "rb") as f:
        key = f.read()

    with open(login_info, "rb") as f:
        info_encrypted = f.read()
    info_decrypted = Fernet(key).decrypt(info_encrypted)
    info_decrypted = info_decrypted.decode()
                           
    info = info_decrypted.split("\n")
    username = info[0]
    password = info[1]

    return (username, password);

def getHTML(username, password):

    url = "https://mail1.upnet.gr/?_task=login"

    with Session() as session:
        try:
            response = session.get(url) #Request(find) token

            data = {
                '_token': response.text[2319 : 2351],
                '_task': 'login',
                '_action': 'login',
                '_timezone': 'Europe/Athens',
                '_url': '_task=mail&_mbox=INBOX',
                '_user': username,
                '_pass': password
            }

            session.post(url, data = data)
            response = session.get("https://mail1.upnet.gr/?_task=mail&_action=list&_refresh=1&_layout=widescreen&_mbox=INBOX&_remote=1&_unlock=loading")
            
        except:
            error_handle(1)

            return "";

    return response.text;

def findAndReportNewMessages(html):

    report = ""
    all_messages = html.split('add_message_row')
    all_messages.pop(0)
    new_messages_number = 0
            
    for message in all_messages:
        if message.count('"seen\\":1') == 1: continue; #Έχει αναγνωστεί ήδη αυτό το e-mail από τον χρήστη.

        new_messages_number += 1
                
        mail_address_indexStart = message.index('"adr') + 25
        mail_address_indexEnd = message.index('\\\\\\', mail_address_indexStart)
        mail_address = message[mail_address_indexStart : mail_address_indexEnd]

        contact_address_indexStart = message.index('"rcmContactAddress') + 23
        contact_address_indexEnd = message.index('</span>', contact_address_indexStart)
        contact_address = message[contact_address_indexStart : contact_address_indexEnd]

        date_indexStart = message.index('"date') + 10
        date_indexEnd = message.index('\\"}', date_indexStart)
        date = message[date_indexStart : date_indexEnd]

        title_indexStart = message.index('"subject') + 13
        title_indexEnd = message.index('\\"', title_indexStart)
        title = message[title_indexStart : title_indexEnd]
                
        report += "Τίτλος μυνήματος: "+title+"\nΑποστολέας: "+contact_address+" ["+mail_address+"]\nΗμερομηνία: "+date+"\n"

    return (report, new_messages_number);

def sendNotification(new_messages_number, report):

    notification.notify(title = "UPnet Webmail", message = "{}Ημερομηνία συγχρονισμού: {}".format(report, str(datetime.now())[:19]))

    return report;

def main():

    username, password = loginInfo()
    report_memory = ""

    while True:
        try:
            html = getHTML(username, password)

            report, new_messages_number = findAndReportNewMessages(html)

            if report != report_memory and report != "": report_memory = sendNotification(new_messages_number, report)

        except: error_handle(3)

        sleep(180) #Δt waiting for new mail check!

    return;

if __name__ == "__main__":
    main()
