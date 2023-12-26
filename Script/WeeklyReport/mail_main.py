
import os
import datetime
import requests
from report_text import openai_mail, openai_key, openai_image
from report_page import create_report_cover

def add_mail_main(mail_main, analysis_YearMonth):
    mail_head = "Dear [Recipient],"
    mail_info = f"I hope this email finds you well. China CDC Weekly has published the new data on the cases and deaths of notifiable infectious diseases in mainland China in {analysis_YearMonth}."
    mail_end = "The notion generated automatically, and assistant by ChatGPT. Please check the data and description carefully."
    mail_signature = "Best regards,\n CNIDS"
    mail_time = datetime.datetime.now().strftime("%Y-%m-%d")
    out_content = mail_head + "\n\n" + mail_info + "\n\n" + mail_main + "\n\n" + mail_end + "\n\n" + mail_signature + "\n\n" + mail_time + "\n\n"
    return out_content

def openai_mail_cover(table_data_str, table_legend, analysis_YearMonth):
    mail_content = openai_mail(os.environ['MAIL_MAIN_CREATE'],
                               os.environ['MAIL_MAIN_CHECK'],
                               f"""Examine the monthly cases and deaths related to various diseases in mainland China for the month of {analysis_YearMonth}.
                                Create a list of key points for each disease, and the list should be structured as follows:
                               **1. disease_name:** description.
                               **2. disease_name:** description.
                               **3. disease_name:** description.
                               ......
                               
                               Use the provided data (Cases/Deaths) to support the analysis.
                               {table_data_str}.
                               {table_legend}""")
    key_words = openai_key(os.environ['MAIL_KEYWORDS_CREATE'],
                           os.environ['MAIL_KEYWORDS_CHECK'],
                           f"""Analyze below content, and give a prompt to create a abstract cover image of this report.
                           Keep the cover as simple as possible. Don't touch on any text or statistical charts.
                           The background color should be darkblue. The image theme is technology.

                           {mail_content}""")
    print(key_words)

    image_url = openai_image(os.environ['REPORT_COVER_CREATE'], key_words)
    response = requests.get(image_url)

    if response.status_code == 200:
        with open("./temp/cover.jpg", "wb") as file:
            file.write(response.content)
    else:
        print("Error: Failed to download the image.")
    mail_content = add_mail_main(mail_content, analysis_YearMonth)
    return mail_content

def create_cover_mail(table_data_str, table_legend, analysis_YearMonth, analysis_MonthYear):
    mail_content = openai_mail_cover(table_data_str, table_legend, analysis_YearMonth)
    with open(f'../Report/mail/{analysis_YearMonth}.md', 'w') as f:
        f.write(mail_content)
    try:
        create_report_cover(analysis_MonthYear)
        print("Created the cover image successfully.")
    except:
        print("Error: Failed to create the cover image.")

def create_mail_table(table_data, analysis_YearMonth):
    table_data_str = table_data.to_markdown(index=False)    
    with open(f'../Report/table/{analysis_YearMonth}.md', 'w') as f:
        f.write(table_data_str)