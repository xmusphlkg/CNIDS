
import requests
import xmltodict
import re
from bs4 import BeautifulSoup
import os
import pandas as pd
from requests.exceptions import ConnectionError
from datetime import datetime

# define a function to extract date from text
def extract_date(text):
    match = re.search(r"\b([A-Za-z]+)\s+(\d{4})\b", text)
    if match:
          return(match.group(2) + " " + match.group(1))
    else:
          return(None)
    
def find_max_date(YearMonths):
    date_objects = [datetime.strptime(date, "%Y %B") for date in YearMonths]
    max_date = max(date_objects, key=lambda x: x)
    max_date_str = max_date.strftime("%Y %B")
    return max_date_str

# define a function to get Pubmed RSS results
def get_rss_results(url):
    """
    get RSS results from the URL

    Args:
        url (str): RSS URL
    Raises:
        Exception: Failed to fetch RSS results. Status code: {response.status_code}
    Returns:
        list: RSS results
    """
    # Send request and get response
    response = requests.get(url)

    # Check response status code
    if response.status_code != 200:
        raise Exception("Failed to fetch RSS results. Status code: {}".format(response.status_code))

    # Parse XML results
    rss_results = xmltodict.parse(response.content)

    # Extract results
    results = []
    for item in rss_results["rss"]["channel"]["item"]:
        date = extract_date(re.sub(r"[^\w\s-]", "", item["title"]))
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

    # Sort by date
    results.sort(key=lambda result: result["date"], reverse=False)
    # Exclude the first 4 results
    results = results[4:]

    return results


# define a function to get china cdc weekly results

def get_cdc_results(url):
    """
    Extracts links containing "doi" from a given URL.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        list: A list of dictionaries containing the extracted information.
    """
    # Send an HTTP request to get the webpage content
    response = requests.get(url)
    html_content = response.text

    # Use BeautifulSoup to parse the webpage content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <a> tags
    a_tags = soup.find_all("a")

    # Create a list to store the results
    result_list = []

    # Traverse each <a> tag, extract text and link
    for a_tag in a_tags:
        text = a_tag.text.strip()
        link = a_tag.get("href")
        if link and "doi" in link and "National Notifiable Infectious Diseases" in text:
            # Extract the date from the text
            date = extract_date(re.sub(r"[^\w\s-]", "", text))
            date_obj = datetime.strptime(date, "%Y %B")
            formatted_date = date_obj.strftime("%Y/%m/%d")
            # Split the link by "doi/" to get the doi
            doi = link.split("doi/")[1]
            result_list.append({
                "title": text,
                "date": date_obj,
                "YearMonthDay": formatted_date,
                "YearMonth": date,
                "link": url + link,
                "doi": ['missing', 'missing', 'doi:' + doi]
            })

    # Remove duplicate results
    result_list = list({v['link']: v for v in result_list}.values())

    return result_list


# define a function to get table data from URLs

def process_table_data(urls, filtered_results, diseaseCode2Name, dois):
    """
    Process table data from URLs and save the results to CSV files.

    Args:
        urls (list): List of URLs to fetch data from.
        filtered_results (list): List of filtered results.
        diseaseCode2Name (dict): Dictionary mapping disease codes to names.
        dois (list): List of DOIs.

    Raises:
        Exception: If the HTTP response status code is not 200.

    Returns:
        None
    """
    for i, url in enumerate(urls):
        # Send a request and get the response
        response = requests.get(url)

        # Check the response status code
        if response.status_code != 200:
            print(url)
            raise Exception("Failed to fetch web content, status code: {}".format(response.status_code))
        else:
            print("Successfully fetched web content, urls: {}".format(url))

        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table
        table = soup.find("table")  # The table is enclosed in <table> tags

        # Extract table data
        table_data = []
        for row in table.find_all("tr"):
            row_data = []
            for cell in row.find_all("td"):
                # Remove all special characters except spaces and hyphens
                text = re.sub(r"[^\w\s-]", "", cell.text.strip())
                row_data.append(text)
            table_data.append(row_data)

        # Remove the last segment of content
        table_data = table_data[:-1]
        # Insert "YearMonth" in the first column of each month's result
        table_data[0].insert(0, "YearMonth")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["YearMonth"])

        # Insert "YearMonthDay" in the first column of each month's result
        table_data[0].insert(0, "YearMonthDay")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["YearMonthDay"])

        # Insert "Date" in the first column of each month's result
        table_data[0].insert(0, "Date")
        for row in table_data[1:]:
            row.insert(0, filtered_results[i]["date"])

        # Add the URL in the last column
        table_data[0].insert(0, "URL")
        for row in table_data[1:]:
            row.insert(0, urls[i])

        # Add the DOI in the last column
        table_data[0].insert(0, "DOI")
        for row in table_data[1:]:
            row.insert(0, dois[i])

        # Add the Chinese name of the disease
        table_data[0].insert(1, "DiseasesCN")
        for row in table_data[1:]:
            row.insert(1, diseaseCode2Name[row[5]])

        # Add the data source as "China CDC Weekly: Notifiable Infectious Diseases Reports"
        table_data[0].insert(1, "Source")
        for row in table_data[1:]:
            row.insert(1, 'China CDC Weekly: Notifiable Infectious Diseases Reports')

        # Add province information
        table_data[0].insert(1, "Province")
        for row in table_data[1:]:
            row.insert(1, 'China')
        table_data[0].insert(1, "ProvinceCN")
        for row in table_data[1:]:
            row.insert(1, '全国')
        table_data[0].insert(1, "ADCode")
        for row in table_data[1:]:
            row.insert(1, '100000')

        # Add 'Incidence' and 'Mortality' columns
        table_data[0].insert(7, "Incidence")
        for row in table_data[1:]:
            row.insert(7, -10)
        table_data[0].insert(8, "Mortality")
        for row in table_data[1:]:
            row.insert(8, -10)

        # Convert to a DataFrame
        table_data = pd.DataFrame(table_data[1:], columns=table_data[0])

        # Reorder the column names: Date, YearMonthDay, YearMonth, Diseases, DiseasesCN, Cases, Deaths, Incidence, Mortality, ProvinceCN, Province, ADCode, DOI, URL, Source
        table_data = table_data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

        # Save the results for each month to a CSV file
        file_name = os.path.join("WeeklyReport/", filtered_results[i]["YearMonth"] + ".csv")
        table_data.to_csv(file_name, index=False, encoding="UTF-8-sig")

# define a function to get table data from URLs
def chatgpt_description(api_base, api_key, analysis_YearMonth, table_data_str, model, disease_name = ''):
    url = f"{api_base}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': model,
        'temperature': 0.7,
        'max_tokens': 10000,
        'messages': [
            {"role": "user", "content": "I'm working on the results of my paper, playing a professional epidemiologist assisted me to describe the data. Next, I will send you the monthly incidence and death of different diseases. Please describe these data based on this data."},
            {"role": "system", "content": "OK, you can send me the data directly to me."},
            {"role": "user", "content": f"This is the monthly cases and deaths in {analysis_YearMonth} {disease_name}, Please directly write the discussion of the data for paper."},
            {"role": "system", "content": "I will play a professional writer, create the discussion of the paper."},
            {"role": "user", "content": f"In the case of time series data, you can analyze seasonal and cyclical issues. Here is the data:\n{table_data_str}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print('Generate Description Success ' + disease_name)
            out_content = response.json()['choices'][0]['message']['content']
            out_content = out_content.replace('Discussion:\n\n', '')
        else:
            print('Generate Description Fail ' + disease_name)
            print(response)
            out_content = None
    except ConnectionError as e:
        print('Connection Error:', e)
        out_content = None

    return out_content

def chatgpt_mail_raw(api_base, api_key, analysis_YearMonth, table_data_str, model, disease_name = ''):
    url = f"{api_base}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': model,
        'temperature': 0.5,
        'max_tokens': 10000,
        'messages': [
            {"role": "user", "content": f"""Analyze the monthly cases and deaths of different diseases in mainland China for {analysis_YearMonth}.
             Provide a list of key observations and points to note in the data. After I will send data to your, you can start."""},
            {"role": "system", "content": f"""Sure, I can help you analyze the monthly cases and deaths of different diseases in mainland China for {analysis_YearMonth}. 
             Please provide me with the data, and I'll assist you in analyzing it and providing key observations and points to note."""},
             {"role": "user", "content": f"""You need to pay attention: select noteworthy diseases, and give short description."""},
            {"role": "system", "content": f"""Understood. Please provide me with the data for the monthly cases and deaths of different diseases in mainland China for {analysis_YearMonth}, 
             and I will generate the attention points directly."""},
            {"role": "user", "content": f"Here is the data:\n{table_data_str}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print('Generate Mail Success ' + disease_name)
            out_content = response.json()['choices'][0]['message']['content']
            out_content = out_content.replace('Discussion:\n\n', '')
        else:
            print('Generate Mail Fail ' + disease_name)
            print(response)
            out_content = None
    except ConnectionError as e:
        print('Connection Error:', e)
        out_content = None

    return out_content

def chatgpt_mail_rebuild(mail_main, analysis_YearMonth):
    mail_head = "Dear [Recipient],"
    mail_info = f"I hope this email finds you well. China CDC Weekly has published the new data on the cases and deaths of notifiable infectious diseases in mainland China in {analysis_YearMonth}."
    mail_end = "The notion generated automatically, and assistant by ChatGPT. Please check the data and description carefully."
    mail_signature = "Best regards,\n CNIDs"
    mail_time = datetime.now().strftime("%Y-%m-%d")
    out_content = mail_head + "\n\n" + mail_info + "\n\n" + mail_main + "\n\n" + mail_end + "\n\n" + mail_signature + "\n\n" + mail_time + "\n\n"
    return out_content