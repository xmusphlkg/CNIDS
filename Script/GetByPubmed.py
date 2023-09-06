import requests
import xmltodict
import re
from bs4 import BeautifulSoup

def extract_date(text):
    match = re.search(r"\b([A-Za-z]+)\s+(\d{4})\b", text)
    if match:
          return(match.group(2) + " " + match.group(1))
    else:
          return(None)
        
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
    results.append({
        "title": item["title"],
        "pubDate": item["pubDate"],
        "dc:date": item["dc:date"],
        "doi": item["dc:identifier"]
    })

# 按日期排序
results.sort(key=lambda result: result["dc:date"], reverse=False)

# 获取最近 12 条结果
results = results[-12:]

# 提取 DOI
dois = [re.sub(r"doi:", r"doi/", item["doi"][2]) for item in results]

# 生成网址
urls = ["https://weekly.chinacdc.cn/en/article/{}".format(doi) for doi in dois]

# 生成日期
dates = [extract_date(item["title"]) for item in results]

# 爬取网页内容
results = {}
for i, url in enumerate(urls):
    # 发送请求并获取响应
    response = requests.get(url)
    print(dates[i])
    print(url)

    # 检查响应状态码
    if response.status_code != 200:
        raise Exception("获取网页内容失败，状态码：{}".format(response.status_code))

    # 解析 HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # 获取 CSV 下载链接
    link = soup.find("a", text = "CSV")

    # 添加结果
    if link is not None:
        results[dates[i]] = link['onclick'].split("'")[1]
    else:
        results[dates[i]] = None
        
## 下载数据
for result,date in zip(results, dates):
    # 发送请求并获取响应
    link = "https://weekly.chinacdc.cn/article/exportCsv?id={}&type=table".format(results[result])
    response = requests.get(link)

    # 检查响应状态码
    if response.status_code != 200:
        raise Exception("获取 CSV 失败，状态码：{}".format(response.status_code))

    # 下载 CSV
    with open("outcome/" + date + ".csv", "wb") as f:
        f.write(requests.get(link, stream=True, timeout=10).content)