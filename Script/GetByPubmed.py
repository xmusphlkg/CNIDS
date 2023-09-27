import requests
import xmltodict
import re
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
import pandas as pd
import subprocess

def extract_date(text):
    match = re.search(r"\b([A-Za-z]+)\s+(\d{4})\b", text)
    if match:
          return(match.group(2) + " " + match.group(1))
    else:
          return(None)

def git_push(commit_message):
    try:
        subprocess.check_output(['git', 'add', '.'])  # 添加所有更改
        subprocess.check_output(['git', 'commit', '-m', commit_message])  # 提交更改
        subprocess.check_output(['git', 'push'])  # 推送更改
        print("Git push successful.")
    except subprocess.CalledProcessError as e:
        print("Git push failed. Error:", e.output)

# 设置工作路径
os.chdir("../GetData")

# 获取 RSS 网址
url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1tQjT4yH2iuqFpDL7Y1nShJmC4kDC5_BJYgw4R1O0BCs-_Nemt/?limit=100&utm_campaign=pubmed-2&fc=20230905093742"

# 发送请求并获取响应
response = requests.get(url)

# 检查响应状态码
if response.status_code != 200:
    raise Exception("获取 RSS 结果失败，状态码：{}".format(response.status_code))

# 解析 XML 结果
rss_results = xmltodict.parse(response.content)

# 提取结果
results = []
for item in rss_results["rss"]["channel"]["item"]:
    date = extract_date(re.sub(r"[^\w\s-]", "", item["title"]))
    # print(date)
    # print(item["title"])
    date_obj = datetime.strptime(date, "%Y %B")
    formatted_date = date_obj.strftime("%Y/%m/%d")
    results.append({
        "title": item["title"],
        "pubDate": item["pubDate"],
        "dc:date": item["dc:date"],
        "date": date_obj,
        "YearMonthDay": formatted_date,
        "YearMonth": date,
        "doi": item["dc:identifier"]
    })

# 按日期排序
results.sort(key=lambda result: result["date"], reverse=False)

# print(results)
# 获取最近 14 条结果
results = results[-14:]

folder_path = "WeeklyReport/"  # 文件夹路径

existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

new_dates = [result['YearMonth'] for result in results if result['YearMonth'] not in existing_dates]

if len(new_dates) == 0:
    print("已经是最新数据，无需更新")
else:
    print("需要提取以下日期的数据:")
    print(new_dates)
    # 筛选 results
    filtered_results = [result for result in results if result['YearMonth'] in new_dates]
    
    # 提取 DOI
    dois = [re.sub(r"doi:", r"doi/", item["doi"][2]) if len(item["doi"]) > 2 else "" for item in filtered_results]

    # 生成网址
    urls = ["https://weekly.chinacdc.cn/en/article/{}".format(doi) for doi in dois]

    for i, url in enumerate(urls):
        # 发送请求并获取响应
        response = requests.get(url)

        # 检查响应状态码
        if response.status_code != 200:
            raise Exception("获取网页内容失败，状态码：{}".format(response.status_code))

        # 解析 HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找表格
        table = soup.find("table")  # 假设表格是 <table> 标签

        # 提取表格数据
        table_data = []
        for row in table.find_all("tr"):
            row_data = []
            for cell in row.find_all("td"):
                # 剔除除了空格和连字符之外的所有特殊字符
                text = re.sub(r"[^\w\s-]", "", cell.text.strip())
                row_data.append(text)
            table_data.append(row_data)

        # 移除最后一段内容
        table_data = table_data[:-1]
        # 在每个月结果的第一列插入 "YearMonth"
        table_data[0].insert(0, "YearMonth")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["YearMonth"])


        # 在每个月结果的第一列插入 "YearMonthDay"
        table_data[0].insert(0, "YearMonthDay")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["YearMonthDay"])

        # 在每个月结果的第一列插入 "Date"
        table_data[0].insert(0, "Date")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["date"])

        # 在最后一列增加网址
        table_data[0].insert(0, "URL")
        for row in table_data[1:]:
            row.insert(0, urls[i])

        # 在最后一列增加网址
        table_data[0].insert(0, "DOI")
        for row in table_data[1:]:
            row.insert(0, dois[i])

        # 保存每个月的结果到CSV文件
        file_name = os.path.join("WeeklyReport/", filtered_results[i]["YearMonth"] + ".csv")
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            for row in table_data:
                writer.writerow(row)

    # 获取文件夹中所有CSV文件的路径
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # 创建一个空的DataFrame来保存合并的数据
    merged_data = pd.DataFrame()

    # 逐个读取CSV文件并合并到DataFrame中
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        merged_data = merged_data.append(data, ignore_index=True)

    # 对"Date"和"Disease"列进行降序排列
    merged_data = merged_data.sort_values(by=["Date", "Diseases"], ascending=False)
    first_row = merged_data.iloc[0]
    year_month = first_row["YearMonth"]

    # 使用当前的年月作为文件名
    current_date = datetime.now().strftime("%Y%m")
    output_file = f"reportdata/All_data_{current_date}.csv"

    # 将合并后的数据保存为CSV文件
    merged_data.to_csv(output_file, index=False)
    merged_data.to_csv("reportdata/All_data_last.csv", index=False)

    # 读取Readme.md文件内容
    readme_path = "../Readme.md"
    with open(readme_path, "r") as readme_file:
        readme_content = readme_file.read()

    # 获取当前日期
    current_date = datetime.now().strftime("%Y%m%d")

    # 更新日志
    update_log = f"#### {year_month}\n\nDate: {current_date}\n\nUpdated: {new_dates}"

    # 将更新日志插入到Readme.md文件中的"Update Log"部分
    updated_readme_content = readme_content.replace("### China CDC Monthly Report", "### China CDC Monthly Report\n\n" + update_log)

    # 将更新后的内容写入Readme.md文件
    with open(readme_path, "w") as readme_file:
        readme_file.write(updated_readme_content)
        
    # 推送至Github
    commit_message = f"Auto push data {year_month}"
    git_push(commit_message)
    print("Commit success")