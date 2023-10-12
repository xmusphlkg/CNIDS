
# Importing libraries
import re
import os
from datetime import datetime
import pandas as pd
import glob

# import functions from function.py
from function import get_rss_results
from function import process_table_data
from function import get_cdc_results
from analysis import generate_weekly_report
from function import find_max_date
from sendmail import send_email_to_subscriber
import variables
import shutil

# test get new data
test = os.environ['test']
test_analysis = os.environ['test_analysis']

# set working directory
os.chdir("./Data/GetData")

# detect existing dates
folder_path = "WeeklyReport/"  # file path
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

# Call the function and pass the URL parameter
url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1tQjT4yH2iuqFpDL7Y1nShJmC4kDC5_BJYgw4R1O0BCs-_Nemt/?limit=100&utm_campaign=pubmed-2&fc=20230905093742"
results = get_rss_results(url)

new_dates = [result['YearMonth'] for result in results if result['YearMonth'] not in existing_dates]

if len(new_dates) == 0:
    print("No new data in the Pubmed RSS feed, try China CDC Weekly website.")
    
url = "https://weekly.chinacdc.cn"
results = get_cdc_results(url)
new_dates = [result['YearMonth'] for result in results if result['YearMonth'] not in existing_dates]

# get current date
current_date = datetime.now().strftime("%Y%m%d")

if len(new_dates) == 0:
    print("No new data in the China CDC Weekly website also.")

if len(new_dates) == 0 and test == 'False':
    print("Newest data, no need to update")
else:
    if test == 'True':
      print("Test mode, only get the latest data")
      new_dates = [find_max_date([result['YearMonth'] for result in results])]
      print(new_dates)
    else:
      test_analysis = 'True'
      print("Find new data, need to update:")
      print(new_dates)
          
    # filter results
    filtered_results = [result for result in results if result['YearMonth'] in new_dates]
    # extract DOI
    dois = [re.sub(r"doi:", r"doi/", item["doi"][2]) if len(item["doi"]) > 2 else "" for item in filtered_results]
    # extract URL
    urls = ["https://weekly.chinacdc.cn/en/article/{}".format(doi) for doi in dois]

    # process table data
    process_table_data(urls, filtered_results, variables.diseaseCode2Name, dois)

    # access the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # create an empty DataFrame
    merged_data = pd.DataFrame()

    # read and merge CSV files
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        merged_data = pd.concat([merged_data, data], ignore_index=True)

    # sort by date and disease
    merged_data = merged_data.sort_values(by=["Date", "Diseases"], ascending=False)
    first_row = merged_data.iloc[0]
    year_month = first_row["YearMonth"]

    # convert to a DataFrame
    merged_data = merged_data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

    # get the unique values of diseases
    disease_unique = merged_data['Diseases'].unique()
    # remove 'Total'
    # disease_unique = [d for d in disease_unique if "Total" not in d]

    # get the unique values of date
    YearMonth_unique = merged_data['YearMonth'].unique()

    # save the merged data to a CSV file
    for YearMonth in YearMonth_unique:
        # filter the data by date
        date_data = merged_data[merged_data['YearMonth'] == YearMonth]
        # if no data, skip
        if date_data.empty:
            continue
        # save the data to a CSV file
        file_name = '..' + '/CleanData/WeeklyReport/ALL/' + YearMonth + '.csv'
        date_data.to_csv(file_name, index=False, encoding="UTF-8-sig")
        # save the data to a CSV file for each disease
        for disease in disease_unique:
            # filter the data by disease
            disease_date_data = date_data[date_data['Diseases'] == disease]
            # print(disease_date_data)
            # if no data, skip
            if disease_date_data.empty:
                continue
            # convert the disease name to title case
            disease = disease.title()
            # save the data to a CSV file
            file_name = '..' + '/CleanData/WeeklyReport/' + disease + '/' + YearMonth + '.csv'
            # create the folder if not exist
            if not os.path.exists('..' + '/CleanData/WeeklyReport/' + disease):
                os.makedirs('..' + '/CleanData/WeeklyReport/' + disease)
            disease_date_data.to_csv(file_name, index=False, encoding="UTF-8-sig")

    # set working directory
    folder_path = '../CleanData/WeeklyReport/'

    # read all CSV files
    csv_files = glob.glob(os.path.join(folder_path, '*/*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)

    # remove duplicates
    data = data.drop_duplicates()

    # get max date
    max_date = data['YearMonthDay'].max()
    max_date = datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")

    # save the data to a CSV file
    data.to_csv('..' + '/AllData/WeeklyReport/latest.csv', index=False, encoding='utf-8', header=True)
    data.to_csv('..' + '/AllData/WeeklyReport/' + max_date + '.csv', index=False, encoding='utf-8', header=True)

    # modify the markdown file
    if test == 'False':
        readme_path = "../Readme.md"
        with open(readme_path, "r") as readme_file:
            readme_content = readme_file.read()
        update_log = f"#### {year_month}\n\nDate: {current_date}\n\nUpdated: {new_dates}"
        updated_readme_content = readme_content.replace("### China CDC Monthly Report", "### China CDC Monthly Report\n\n" + update_log)
        with open(readme_path, "w") as readme_file:
            readme_file.write(updated_readme_content)
    
    
    api_key = os.environ['OPENAI_api']
    api_base = os.environ['OPENAI_url']
    test_info = os.environ['test_mail']
    send_mail = os.environ['send_mail']
    for YearMonth in new_dates:
        print("Generate report for " + YearMonth)
        generate_weekly_report(YearMonth, api_base, api_key)
    shutil.copy("../Report/report " + find_max_date(new_dates) + ".pdf", "../Report/report latest.pdf")
    shutil.copy("../Report/mail/" + find_max_date(new_dates) + ".md", "../Report/mail/latest.md")
    if send_mail == 'True':
        send_email_to_subscriber(test_info)

    # print success message
    print("CDCWeekly Data updated successfully!")


