# Importing libraries 
import imaplib, email
from ..models import Setting
from email.header import decode_header
import json
user = Setting.objects.all().values_list('emailID')#"ayan1741995@gmail.com"
password = Setting.objects.all().values_list('password')#"mrntgtvfxzajxsyy"
imap_url = 'imap.gmail.com'


# Function to get email content part i.e its body part 
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


    # Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    #print(data)
    return data


# Function to get the list of emails under this label 
def get_email_num(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        #typ, data = con.fetch(num, '(RFC822)')
        msgs.append(int(num))

    return msgs


def get_email(ID):
    # this is done to make SSL connnection with GMAIL
    con = imaplib.IMAP4_SSL(imap_url)

    # logging the user in
    con.login(user, password)
    #
    # calling function to check for email under this label
    con.select('"[Gmail]/All Mail"')

    # fetching emails from this user "tu**h*****1@gmail.com"
    mailID = ID
    query = '(OR (TO "'+mailID+'") (FROM "'+mailID+'"))'
    result, msgs = con.search(None, query)

    # Uncomment this to see what actually comes as data
    msgs = [int(i) for i in msgs[0].split()]
    print(msgs)
    msgs.sort(reverse=True)
    print(msgs[:3])
    msg_json = []
    # Finding the required content from our msgs
    # User can make custom changes in this part to
    # fetch the required content he / she needs

    # printing them by the order they are displayed in your gmail
    for msg in msgs[:3]:
        typ, data = con.fetch(str(msg), '(RFC822)')
        message = {}
        #print(data)
        for sent in data:

            if isinstance(sent, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(sent[1])
                # decode the email subject
                if msg["Subject"] is not None:
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode('cp1252')
                else:
                    subject = "< No Subject >"
                # email sender
                from_ = msg.get("From")
                to_ = msg.get("To")
                date = msg.get("Date")

                message["Subject"] = subject
                message["From"] = from_
                message["To"] = to_
                message["Date"] = date
                body = ""
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode('cp1252')
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            message["Body"]=body
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode('cp1252')
                    if content_type == "text/plain":
                        # print only text email parts
                        message["Body"] = body
                        pass

                #print("="*100)
        msg_json.append(message)
    con.close()
    con.logout()
    return json.dumps(msg_json)
