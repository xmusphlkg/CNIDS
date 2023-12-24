
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from report_page import create_report_page, create_report_summary, create_report
from report_fig import prepare_disease_data, plot_disease_data, plot_disease_heatmap
from mail_main import create_cover_mail
from web_info import create_web_info

def process_page(i, df, analysis_YearMonth, analysis_MonthYear, diseases_order, custom_total_num):
    create_report_page(df,
                       diseases_order[i],
                       analysis_YearMonth,
                       analysis_MonthYear,
                       i+custom_total_num-len(diseases_order)+1,
                       custom_total_num)

def process_plot(diseases_order, df):
    for disease_name in diseases_order:
        disease_data = prepare_disease_data(df, disease_name)
        plot_disease_data(disease_data, disease_name)
        plot_disease_heatmap(disease_data, disease_name)    

def generate_report(df, table_data, diseases_order, analysis_date, analysis_YearMonth, analysis_MonthYear):
    # create temp folder
    data_path = '../Data/GetData/WeeklyReport'
   
    # create summary page
    df_10 = df[df['Date'] >= analysis_date - pd.DateOffset(years=5)]
    df_10 = df_10[['Date', 'YearMonth', 'Diseases', 'Cases', 'Deaths']]
    df_10 = df_10[df_10['Diseases'].isin(diseases_order)].sort_values(by=['Diseases', 'Date']).reset_index(drop=True)
    df_10['Values'] = df_10['Cases'].astype(str) + " (" + df_10['Deaths'].astype(str) + ")"
    df_10 = df_10.pivot(index='YearMonth', columns='Diseases', values='Values')
    table_data_str = df_10.to_markdown(index=False)
    
    # read legend
    with open(f'{data_path}/{analysis_YearMonth}.txt', 'r') as f:
        table_legend = f.read()

    # create report page
    # process_page(4, df, analysis_MonthYear, diseases_order, 5)
    with ThreadPoolExecutor() as executor:
        # create figures
        future_plot = executor.submit(process_plot, diseases_order, df)
        # create cover and mail
        future_cover_mail = executor.submit(create_cover_mail, table_data_str, table_legend, analysis_YearMonth, analysis_MonthYear)
        # create summary
        future_report_summary = executor.submit(create_report_summary, table_data, table_data_str, analysis_MonthYear, table_legend)
        # create web info
        update_info = os.environ['update_info']
        if update_info == 'True':
            future_web_info = [executor.submit(create_web_info, disease_name) for disease_name in diseases_order]
        
        # wait for cover and mail
        future_plot.result()
        print("Report figures created.")

        future_cover_mail.result()
        print("Report cover and mail created.")

        custom_total_num = future_report_summary.result()
        print("Report summary created with total num:", custom_total_num)

    with ThreadPoolExecutor(max_workers=len(diseases_order)) as executor:
        futures = [executor.submit(process_page, i, df, analysis_YearMonth, analysis_MonthYear, diseases_order, custom_total_num) for i in range(len(diseases_order))]

        # wait for all pages
        for future in as_completed(futures):
            page_result = future.result()
            print(f"Processed report page {futures.index(future)} with result:", page_result)

    # merge created pages
    create_report(diseases_order)

    # remove all png in temp folder
    for file in os.listdir('temp'):
        if file.endswith('.png'):
            os.remove(os.path.join('temp', file))