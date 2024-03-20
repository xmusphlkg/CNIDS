
import re
import os
from datetime import datetime
import pandas as pd
import glob
import yaml
import ast

from function import get_rss_results, get_gov_results, get_cdc_results, process_table_data
from analysis import generate_weekly_report
from sendmail import send_email_to_subscriber

# fetch data from setting
def fetch_data(existing_dates):
    sources = [
        {
            'active': os.environ['SOURCE_PUBMED_ACTIVE'],
            'label': os.environ['SOURCE_PUBMED_LABEL'],
            'url': os.environ['SOURCE_PUBMED_URL'],
            'origin': os.environ['SOURCE_PUBMED_ORIGIN'],
            'function': os.environ['SOURCE_PUBMED_FUNCTION'],
            'results': [],
            'new_dates': []
        },
        {
            'active': os.environ['SOURCE_CDC_ACTIVE'],
            'label': os.environ['SOURCE_CDC_LABEL'],
            'url': os.environ['SOURCE_CDC_URL'],
            'origin': os.environ['SOURCE_CDC_ORIGIN'],
            'function': os.environ['SOURCE_CDC_FUNCTION'],
            'results': [],
            'new_dates': []
        },
        {
            'active': os.environ['SOURCE_GOV_ACTIVE'],
            'label': os.environ['SOURCE_GOV_LABEL'],
            'url': os.environ['SOURCE_GOV_URL'],
            'origin': os.environ['SOURCE_GOV_ORIGIN'],
            'form_data': os.environ['SOURCE_GOV_DATA'],
            'function': os.environ['SOURCE_GOV_FUNCTION'],
            'results': [],
            'new_dates': []
        }
    ]

    for source in sources:
        active = source['active']
        label = source['label']
        if active == 'False':
            print(f"{label} is not active, try next one.")
            continue

        url = source['url']
        origin = source['origin']
        get_results = globals()[source['function']]

        if 'form_data' in source:
            form_data = ast.literal_eval(source['form_data'])
            results = get_results(url, form_data, label, origin)
        else:
            results = get_results(url, label, origin)

        new_dates = [result['YearMonth'] for result in results if result['YearMonth'] not in existing_dates and result['YearMonth'] not in source['new_dates']]
        if not new_dates:
            print(f"No new data in {label}, try next one.")
        else:
            source['results'] = [result for result in results if result['YearMonth'] in new_dates]
            source['new_dates'] = new_dates
            print(f"Find new data in {label}: {new_dates}")

    results = [result for source in sources for result in source['results']]
    new_dates = list(set([date for source in sources for date in source['new_dates']]))
    current_date = datetime.now().strftime("%Y%m%d")

    return results, new_dates, current_date

# set working directory
os.chdir("./Data/GetData")

# detect existing dates
folder_path = "WeeklyReport/"  # file path
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

# get environment from config.yml
with open('../../config.yml', 'r') as file:
    config_dict = yaml.safe_load(file)
for section, subsections in config_dict.items():
    for key, subvalues in subsections.items():
        for subkey, value in subvalues.items():
            if isinstance(value, str):
                env_var_name = f"{section.upper()}_{key.upper()}_{subkey.upper()}"
                os.environ[env_var_name] = value

# Call the function to fetch data
results, new_dates, current_date = fetch_data(existing_dates)

if new_dates:
    print("Find new data, update.")
    print(results)

    # get data from url and save to WeeklyReport
    process_table_data(results)

    # access the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # read and merge CSV files
    merged_data = pd.DataFrame()
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        merged_data = pd.concat([merged_data, data], ignore_index=True)

    merged_data = merged_data.sort_values(by=["Date", "Diseases"], ascending=False)
    first_row = merged_data.iloc[0]
    year_month = first_row["YearMonth"]
    merged_data = merged_data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

    # get the unique values of diseases
    disease_unique = merged_data['Diseases'].unique()
    YearMonth_unique = merged_data['YearMonth'].unique()

    # save the merged data to a CSV file
    for YearMonth in YearMonth_unique:
        date_data = merged_data[merged_data['YearMonth'] == YearMonth]
        if date_data.empty:
            continue
        file_name = '..' + '/CleanData/WeeklyReport/ALL/' + YearMonth + '.csv'
        date_data.to_csv(file_name, index=False, encoding="UTF-8-sig")
        # save the data to a CSV file for each disease
        for disease in disease_unique:
            disease_date_data = date_data[date_data['Diseases'] == disease]
            if disease_date_data.empty:
                continue
            disease = disease.title()
            file_name = '..' + '/CleanData/WeeklyReport/' + disease + '/' + YearMonth + '.csv'
            if not os.path.exists('..' + '/CleanData/WeeklyReport/' + disease):
                os.makedirs('..' + '/CleanData/WeeklyReport/' + disease)
            disease_date_data.to_csv(file_name, index=False, encoding="UTF-8-sig")

    # read all CSV files
    folder_path = '../CleanData/WeeklyReport/'
    csv_files = glob.glob(os.path.join(folder_path, '*/*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)
    data = data.drop_duplicates()
    max_date = data['YearMonthDay'].max()
    max_date = datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")
    data.to_csv('..' + '/AllData/WeeklyReport/latest.csv', index=False, encoding='utf-8', header=True)
    data.to_csv('..' + '/AllData/WeeklyReport/' + max_date + '.csv', index=False, encoding='utf-8', header=True)

    # modify the markdown file
    readme_path = "../../Readme.md"
    with open(readme_path, "r", encoding='utf-8') as readme_file:
        readme_content = readme_file.read()
    update_log = f"#### {year_month}\n\nDate: {current_date}\n\nUpdated: {new_dates}\n\n"
    pattern = re.compile(rf"#### {re.escape(year_month)}.*?(?=####|$)", re.DOTALL)
    if re.search(pattern, readme_content):
        updated_readme_content = re.sub(pattern, update_log, readme_content)
    else:
        updated_readme_content = readme_content.replace("### China CDC Monthly Report", "### China CDC Monthly Report\n\n" + update_log)
    with open(readme_path, "w") as readme_file:
        readme_file.write(updated_readme_content)
    
    test_mail = os.environ['test_mail']
    send_mail = os.environ['send_mail']
    # change working directory
    os.chdir("../../Script")
    for YearMonth in new_dates:
        print("Generate report for " + YearMonth)
        generate_weekly_report(YearMonth)
    if send_mail == 'True':
        send_email_to_subscriber(test_mail)

    # print success message
    print("Data updated successfully!")
else:
    print("No new data, stop.")