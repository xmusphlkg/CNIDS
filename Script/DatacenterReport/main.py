
## Importing libraries
import pandas as pd
import requests
import os
import glob
import datetime
import xml.etree.ElementTree as ET
import json
import sys

# import functions from function.py
from function import process_files
from function import calculate_HD
import variables

# set working directory
os.chdir("./Data/GetData")

# test get new data
test = os.environ['test_dc']

## get avaliable years
response = requests.get("https://www.phsciencedata.cn/Share/getQuerystart/")

if response.status_code == 200:
    data = json.loads(response.content)
    code_list = [item['code'] for item in data]
    years = code_list
    print("CPHSDC 访问成功")
else:
    print("CPHSDC 访问失败")
    sys.exit()

# detect existing dates
folder_path = "DatacenterReport/"  # file path
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
# find existing years
existing_dates = [date[:4] for date in existing_dates]
existing_dates = list(set(existing_dates))
existing_dates.sort()
# compare with avaliable years
new_dates = list(set(years) - set(existing_dates))

if len(new_dates) == 0 and test == 'False':
    print("Newest data, no need to update")
    need_update = False # no need to update
else:
    if test == 'True':
      new_dates = [max(years)]
      variables.diseaseIds = [variables.diseaseIds[10]]
      print(f"Test mode, only get the latest data: {new_dates}")
    else:
      print("Find new data, need to update:")
      print(new_dates)
    for diseaseId in variables.diseaseIds:
      for year in new_dates:
          for month in variables.months:
              Month = variables.Months[month - 1]        
              file_name = f"{year} {Month} {diseaseId}.xls"
              file_path = os.path.join("DatacenterReport", file_name)
              if os.path.exists(file_path) & (test == False):
                  continue

              url = f"https://www.phsciencedata.cn/Share/frameset?__report=ReportZoneMonth.rptdesign&__title=&__showtitle=false&__toolbar=true&__navigationbar=true&&__format=xls&__locale=zh_CN&__clean=true&__filename=%E5%8D%A0%E4%BD%8D%E7%AC%A6&years={year}&diseaseId={diseaseId}&months={month}&&__dpi=96&__asattachment=true&__overwrite=false"
              r = requests.get(url)
                
              if r.status_code == 200:
                  with open(file_path, "wb") as code:
                      code.write(r.content)
                  print(f"File success download：{file_path}")
                  need_update = True # update the data
                  # time.sleep(random.uniform(3, 5))
              else:
                  print(f"Access fail：{url}")

# check if need to update
if need_update: 
    # setting the folder path
    folder_path = 'DatacenterReport'
    # access the folder
    xls_files = glob.glob(os.path.join(folder_path, '*.xls'))
    xls_files.sort()
    # find need to process files
    xls_files = [file for file in xls_files if os.path.splitext(os.path.basename(file))[0][:4] in new_dates]
    # process files
    process_files(xls_files, variables.provinceName2Code, variables.provinceName2ADCode, variables.diseaseName2Code)

    # calculate the Hepatitis D data
    # setting the folder path
    folder_path = '../CleanData/DatacenterReport/Hepatitis'
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
    # find need to process files
    csv_files = [file for file in csv_files if os.path.splitext(os.path.basename(file))[0][:4] in new_dates]
    # process files
    calculate_HD(csv_files, folder_path)

    # setting the folder path
    folder_path = '../CleanData/DatacenterReport'

    # access the folder and combine all csv files
    csv_files = glob.glob(os.path.join(folder_path, '*/*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)

    # remove duplicates
    data = data.drop_duplicates()

    # get label of the latest data
    max_date = data['YearMonthDay'].max()
    max_date = datetime.datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")

    # save the data
    data.to_csv('../AllData/DatacenterReport/latest.csv', index=False, encoding='utf-8', header=True)
    data.to_csv('../AllData/DatacenterReport/' + max_date + '.csv', index=False, encoding='utf-8', header=True)

    # modify the disease name
    readme_path = "../../Readme.md"
    with open(readme_path, "r") as readme_file:
        readme_content = readme_file.read()

    # get current date
    current_date = datetime.datetime.now().strftime("%Y%m%d")

    # update log
    update_log = f"#### {new_dates[0]}\n\nDate: {current_date}\n\nUpdated: {new_dates}"

    # insert the update log to the "Update Log" section of Readme.md file
    updated_readme_content = readme_content.replace("### Public Health Scientific Data Center", "### Public Health Scientific Data Center\n\n" + update_log)

    # write the updated content to Readme.md file
    with open(readme_path, "w") as readme_file:
        readme_file.write(updated_readme_content)

    # print success message
    print("DatacenterReport data update success!")