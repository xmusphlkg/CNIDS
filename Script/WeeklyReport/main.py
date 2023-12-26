
# Importing libraries
import re
import os
from datetime import datetime
import pandas as pd
import glob

# import functions from function.py
from function import get_rss_results, get_gov_results, get_cdc_results
from function import process_table_data
from analysis import generate_weekly_report
from function import find_max_date
from sendmail import send_email_to_subscriber

# set working directory
os.chdir("./Data/GetData")

# detect existing dates
folder_path = "WeeklyReport/"  # file path
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

results = []
# Get data from pubmed
# url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1tQjT4yH2iuqFpDL7Y1nShJmC4kDC5_BJYgw4R1O0BCs-_Nemt/?limit=100&utm_campaign=pubmed-2&fc=20230905093742"
# results_pubmed = get_rss_results(url)
# new_dates_pubmed = [result['YearMonth'] for result in results_pubmed if result['YearMonth'] not in existing_dates]
# if len(new_dates_pubmed) == 0:
#     print("No new data in the Pubmed RSS feed, try China CDC Weekly website.")
# else:
#     results_pubmed = [result for result in results_pubmed if result['YearMonth'] in new_dates_pubmed]
#     results = results_pubmed

# Get data from cdc weekly
results_cdc = get_cdc_results()
new_dates_cdc = [result['YearMonth'] for result in results_cdc if result['YearMonth'] not in existing_dates]
if not new_dates_cdc:
    print("No new data in the China CDC weekly website, try National Disease Control and Prevention Administration.")
else:
    results.extend([result for result in results_cdc if result['YearMonth'] in new_dates_cdc])

# Get data from gov
results_gov = get_gov_results()
new_dates_gov = [result['YearMonth'] for result in results_gov if result['YearMonth'] not in existing_dates and result['YearMonth'] not in new_dates_cdc]
if not new_dates_gov:
    print("No new data in the National Disease Control and Prevention Administration, stop.")
else:
    results.extend([result for result in results_gov if result['YearMonth'] in new_dates_gov])

new_dates = list(set(new_dates_cdc + new_dates_gov))
print(results)

# get current date
current_date = datetime.now().strftime("%Y%m%d")

if new_dates:
    print("Find new data, update.")
    print(results)

    # process table data
    process_table_data(results)

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

    # read all CSV files
    folder_path = '../CleanData/WeeklyReport/'
    csv_files = glob.glob(os.path.join(folder_path, '*/*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)

    # remove duplicates
    data = data.drop_duplicates()
    max_date = data['YearMonthDay'].max()
    max_date = datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")

    # save the data to a CSV file
    data.to_csv('..' + '/AllData/WeeklyReport/latest.csv', index=False, encoding='utf-8', header=True)
    data.to_csv('..' + '/AllData/WeeklyReport/' + max_date + '.csv', index=False, encoding='utf-8', header=True)

    # modify the markdown file
    if test == 'False':
        readme_path = "../../Readme.md"
        with open(readme_path, "r") as readme_file:
            readme_content = readme_file.read()
        update_log = f"#### {year_month}\n\nDate: {current_date}\n\nUpdated: {new_dates}"
        updated_readme_content = readme_content.replace("### China CDC Monthly Report", "### China CDC Monthly Report\n\n" + update_log)
        with open(readme_path, "w") as readme_file:
            readme_file.write(updated_readme_content)
    
    test_info = os.environ['test_mail']
    send_mail = os.environ['send_mail']
    # change working directory
    os.chdir("../../Script")
    for YearMonth in new_dates:
        print("Generate report for " + YearMonth)
        generate_weekly_report(YearMonth)
    if send_mail == 'True':
        send_email_to_subscriber(test_info)

    # print success message
    print("CDCWeekly Data updated successfully!")


