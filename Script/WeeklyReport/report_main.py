
import pandas as pd
import os
import datetime
from concurrent.futures import ThreadPoolExecutor
from report_page import create_report_page, create_report_summary
from dataclean import calculate_change_data, format_table_data, generate_merge_chart

def process_page(i, df, analysis_YearMonth, diseases_order):
    print('***'*10)
    print(diseases_order[i])
    create_report_page(df,
                       diseases_order[i],
                       analysis_YearMonth,
                       i+5,
                       len(diseases_order)+6)
    print('***'*10)

if __name__ == "__main__":
    if not os.path.exists("temp"):
        os.makedirs("temp")
    # read data
    df = pd.read_csv('../../Data/AllData/WeeklyReport/latest.csv', encoding='utf-8')
    df['Date'] = pd.to_datetime(df['Date'])
    # using newest data
    analysis_YearMonth = df['Date'].max().strftime("%Y %B")
    analysis_MonthYear = df['Date'].max().strftime("%B %Y")

    analysis_date = datetime.datetime.strptime(analysis_YearMonth+' 01', '%Y %B %d')
    change_data = calculate_change_data(df, analysis_date)
    diseases_order, diseases_order_cn = generate_merge_chart(change_data,
                                                             original_file=f'../../Data/GetData/WeeklyReport/{analysis_YearMonth}.csv')
    table_data = format_table_data(change_data, analysis_date)
    diseases = table_data['Diseases'].tolist()
    print(diseases_order)

    # create summary page
    df_10 = df[df['Date']>=analysis_date-datetime.timedelta(days=365*10)]
    create_report_summary(table_data, change_data, df_10, analysis_MonthYear)

    # create report page
    # process_page(4, df, analysis_MonthYear, diseases_order)
    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     for i in range(len(diseases_order)):
    #         executor.submit(process_page, i, df, analysis_MonthYear, diseases_order)