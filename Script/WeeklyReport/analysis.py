import pandas as pd
import datetime
import os
import shutil
from plotnine import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from dataclean import calculate_change_data
from dataclean import format_table_data
from dataclean import generate_merge_chart
from report import generate_report

def generate_weekly_report(analysis_YearMonth, api_base, api_key):
    # set working directory
    os.chdir("../../Script")
    # os.chdir("./GetData")

    # 设置字体
    pdfmetrics.registerFont(TTFont('SimSun', './WeeklyReport/font/SIMSUN.ttf')) 
    pdfmetrics.registerFont(TTFont('Helvetica', './WeeklyReport/font/Helvetica.ttf'))
    pdfmetrics.registerFont(TTFont('Helvetica-Bold', './WeeklyReport/font/Helvetica-Bold.ttf'))
    analysis_date = datetime.datetime.strptime(analysis_YearMonth+' 01', '%Y %B %d')

    # read all data
    df = pd.read_csv('../Data/AllData/WeeklyReport/latest.csv', encoding='utf-8')
    df['Date'] = pd.to_datetime(df['Date'])

    if not os.path.exists("temp"):
        os.makedirs("temp")
    change_data = calculate_change_data(df, analysis_date)
    diseases_order = generate_merge_chart(change_data, original_file='../Data/GetData/WeeklyReport/2020 April.csv')
    table_data = format_table_data(change_data, analysis_date)

    generate_report(analysis_YearMonth, table_data, df, diseases_order, api_base, api_key)     
    shutil.rmtree("temp")