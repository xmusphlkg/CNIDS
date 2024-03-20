import os
from onedrivedownloader import download
import pandas as pd
import datetime
import variables
import markdown
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def download_onedrive_file(url:str, filename: str):
    max_attempts = 10
    attempts = 0
    content = None

    while attempts < max_attempts:
        try:
            content = download(url, filename, unzip=False)
            if content == "subscriber.xlsx":
                print("Subscribe File downloaded successfully")
                return True
            else:
                print(f'Failed to download file.')
        except Exception as e:
            print(f'Error occurred while downloading the file: {str(e)}')
        attempts += 1

    print(f'Reached maximum attempts, failed to download the file.')
    return None

def send_email(email_address, email_password, email_recipient, smtp_server_url, smtp_server_port, subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    with smtplib.SMTP_SSL(smtp_server_url, smtp_server_port) as smtp_server:
        smtp_server.login(email_address, email_password)
        smtp_server.sendmail(email_address, email_recipient, msg.as_string())

def get_subscriber_list(url:str, file_name = "subscriber.xlsx"):
    if os.path.exists(file_name):
        os.remove(file_name)
    result = download_onedrive_file(url, file_name)

    if result:
        df = pd.read_excel("subscriber.xlsx")
        df['time'] = df['Completion time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.sort_values('time', ascending=False).drop_duplicates('email_address').sort_index()
        df = df[df['subscribe'] == 'Subscribe']
        # remove the file
        os.remove(file_name)
        return df

def send_email_to_subscriber(test_info):
    
    sender_email = os.environ['smtp_sender']
    url = os.environ['smtp_server_url']
    port = os.environ['smtp_server_port']
    passwd = os.environ['smtp_password']
    fileurl = os.environ['onedrive_url']

    df = get_subscriber_list(fileurl)
    recipient_email = df['email_address']
    subject = "CNIDS Automatic Report Update!"

    body_main = open("../Report/mail/latest.md", "r").read()
    body_table = open("../Report/table/latest.md", "r").read()
    body_table = markdown.markdown(body_table, extensions=['markdown.extensions.tables'])
    email_info = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', variables.email_info)

    # send email to all subscribers
    if test_info == "True":
        body_main = "<h1>Project still in test mode, please ignore this email.</h1>\n\n" + body_main
    body = body_main + email_info + "\n\n"
    body = body.replace("\n", "<br>")
    body = body.replace("  ", "&nbsp;&nbsp;")
    body = body + f"<h3>Appendix: Notifiable Infectious Diseases Reports: Reported Cases and Deaths of National Notifiable Infectious Diseases</h3>" + "\n\n" + body_table
    send_email(sender_email, passwd, recipient_email, url, port, subject, body)
