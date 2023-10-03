import requests
import json
import os
from onedrivedownloader import download
import pandas as pd
import datetime
import variables
import markdown
import re

def get_access_token():
    tenant_id = os.environ['MS_tenant_id']
    client_id = os.environ['MS_client_id']
    client_secret = os.environ['MS_client_secret']
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=payload)
    access_token = response.json().get("access_token")
    return access_token

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

def send_email(access_token, sender_email, recipient_email, subject, body):
    url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print("Email sent failed!")
        print(response.text)

def get_subscriber_list(url:str, file_name = "subscriber.xlsx"):
    if os.path.exists(file_name):
        os.remove(file_name)
    result = download_onedrive_file(url, file_name)

    if result:
        df = pd.read_excel("subscriber.xlsx")
        df['time'] = datetime.datetime.now()
        df = pd.read_excel("subscriber.xlsx")
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.sort_values('time', ascending=False).drop_duplicates('email').sort_index()
        df = df[df['subscribe'] == 'Subscribe']
        # remove the file
        os.remove(file_name)
        return df

def send_email_to_subscriber():
    access_token = get_access_token()
    sender_email = os.environ['MS_sender_email']
    url = os.environ['MS_subscribe']
    df = get_subscriber_list(url)
    subject = "CNIDs Automatic Report Update!"
    body_main = open("../Report/mail/latest.md", "r").read()
    body_table = open("../Report/table/latest.md", "r").read()
    body_table = markdown.markdown(body_table, extensions=['markdown.extensions.tables'])
    emailInfo = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', variables.emailInfo)
    # send email to all subscribers
    for index, row in df.iterrows():
        recipient_email = row['email']
        subject = subject
        if os.environ['test_analysis'] == "True":
            body_main = "<h1>Project still in test mode, please ignore this email.</h1>\n\n" + body_main
        body = body_main.replace("[Recipient]", row['name']) + emailInfo + "\n\n"
        # trans markdown content to html
        body = body.replace("\n", "<br>")
        body = body.replace("  ", "&nbsp;&nbsp;")

        body = body + f"<h3>Appendix: Notifiable Infectious Diseases Reports: Reported Cases and Deaths of National Notifiable Infectious Diseases</h3>" + "\n\n" + body_table


        send_email(access_token, sender_email, recipient_email, subject, body)

os.chdir("./Data/")
send_email_to_subscriber()