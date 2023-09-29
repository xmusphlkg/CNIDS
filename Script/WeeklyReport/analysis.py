import pandas as pd
import json
import datetime
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate, Frame, BaseDocTemplate, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch, cm
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas

# set working directory
os.chdir("./GetData")

# 设置字体
pdfmetrics.registerFont(TTFont('SimSun', '../Script/WeeklyReport/SIMSUN.ttf')) 

## 读取log文件
with open('../LOG/WeeklyReport/log.json', 'r') as f:
  log_list = json.load(f)
update_report = log_list[0]["info"]["MRupdate"]

# 判断是否需要更新
if update_report:
  print('Need to update report')
  update_YearMonthDay = log_list[0]["info"]["MRYearMonthDay"]
  analysis_YearMonthDay = max(update_YearMonthDay)
  analysis_date = datetime.datetime.strptime(analysis_YearMonthDay, '%Y/%m/%d')
  analysis_YearMonth = analysis_date.strftime('%Y %B')

  # read all data
  df = pd.read_csv('../AllData/WeeklyReport/latest.csv', encoding='utf-8')
  df['Date'] = pd.to_datetime(df['Date'])

  # get Diseases unique list
  diseases = df['Diseases'].unique()
  # get Date unique list
  dates = df['YearMonthDay'].unique()
  dates.sort()

  # get latest data
  latest_data_1 = df[df['Date'] == analysis_date]
  latest_data_1 = latest_data_1.sort_values(by='Diseases', ascending=True).reset_index()
  latest_data_1 = latest_data_1[['Diseases', 'DiseasesCN', 'Cases', 'Deaths']]
  # get previous data
  latest_data_2 = df[df['Date'] == analysis_date - pd.DateOffset(months=1)]
  latest_data_2 = latest_data_2.sort_values(by='Diseases', ascending=True).reset_index()
  latest_data_2 = latest_data_2[['Diseases', 'DiseasesCN', 'Cases', 'Deaths']]
  latest_data_2.columns = ['Diseases', 'DiseasesCN', 'CasesPM', 'DeathsPM']
  # get previous year data
  latest_data_3 = df[df['Date'] == analysis_date - pd.DateOffset(years=1)]
  latest_data_3 = latest_data_3.sort_values(by='Diseases', ascending=True).reset_index()
  latest_data_3 = latest_data_3[['Diseases', 'DiseasesCN', 'Cases', 'Deaths']]
  latest_data_3.columns = ['Diseases', 'DiseasesCN', 'CasesPY', 'DeathsPY']
  # change_data is join latest_data_1 and latest_data_2
  change_data = pd.merge(latest_data_1, latest_data_2, on=['Diseases', 'DiseasesCN'])
  change_data = pd.merge(change_data, latest_data_3, on=['Diseases', 'DiseasesCN'])

  # ChangeCasesMonth, ChangeCasesYear, ChangeDeathsMonth, ChangeDeathsYear
  change_data['ChangeCasesMonth'] = change_data['Cases'] - change_data['CasesPM']
  change_data['ChangeCasesYear'] = change_data['Cases'] - change_data['CasesPY']
  change_data['ChangeDeathsMonth'] = change_data['Deaths'] - change_data['DeathsPM']
  change_data['ChangeDeathsYear'] = change_data['Deaths'] - change_data['DeathsPY']
  # ChangeCasesMonthPer, ChangeCasesYearPer, ChangeDeathsMonthPer, ChangeDeathsYearPer
  change_data['ChangeCasesMonthPer'] = change_data['ChangeCasesMonth'] / change_data['CasesPM']
  change_data['ChangeCasesYearPer'] = change_data['ChangeCasesYear'] / change_data['CasesPY']
  change_data['ChangeDeathsMonthPer'] = change_data['ChangeDeathsMonth'] / change_data['DeathsPM']
  change_data['ChangeDeathsYearPer'] = change_data['ChangeDeathsYear'] / change_data['DeathsPY']

  # sort by Cases
  change_data = change_data.sort_values(by='Cases', ascending=False).reset_index()

  # 设置工作路径
  os.chdir("../Script")
  # 创建temp文件夹
  if not os.path.exists("temp"):
      os.makedirs("temp")


  # 创建一个包含两个子图的图形
  fig, axes = plt.subplots(1, 2, figsize=(10, 10))

  # 生成图像1 - 柱状图 (Cases)
  sns.barplot(y="Diseases", 
              x="Cases", 
              data=change_data[change_data['Diseases'] != "Total"], 
              palette="Blues_d",
              ax=axes[0])
  for index, row in change_data[change_data['Diseases'] != "Total"].iterrows():
      axes[0].text(row.Cases, index-1, int(row.Cases), color='black', ha="left", va="center")
  axes[0].set_xlim(0, change_data[change_data['Diseases'] != "Total"]['Cases'].max() * 1.3)
  axes[0].set_ylim(-1, len(change_data[change_data['Diseases'] != "Total"]['Diseases']))
  axes[0].set_xlabel("Cases (thousand)")
  axes[0].set_ylabel("")
  axes[0].set_title("A: Monthly Cases Notifiable Infectious Diseases Reports", loc='right')
  formatter = mticker.FuncFormatter(lambda x, pos: '{:.0f}'.format(x/1000))
  axes[0].xaxis.set_major_formatter(formatter)

  # 生成图像2 - 柱状图 (Deaths)
  sns.barplot(y="Diseases", 
              x="Deaths", 
              data=change_data[change_data['Diseases'] != "Total"], 
              palette="Reds_d",
              ax=axes[1])
  for index, row in change_data[change_data['Diseases'] != "Total"].iterrows():
      axes[1].text(row.Deaths, index-1, int(row.Deaths), color='black', ha="left", va="center")
  axes[1].set_xlim(0, change_data[change_data['Diseases'] != "Total"]['Deaths'].max() * 1.3)
  axes[1].set_ylim(-1, len(change_data[change_data['Diseases'] != "Total"]['Diseases']))
  axes[1].set_xlabel("Deaths")
  axes[1].set_ylabel("")
  axes[1].set_title("B: Monthly Deaths Notifiable Infectious Diseases Reports", loc='right')

  # 调整子图之间的间距
  plt.tight_layout()

  # 保存合并的图像
  merged_chart_path = os.path.join("temp", "merged_chart.png")
  plt.savefig(merged_chart_path, dpi=300)

  table_data = change_data
  # 去除index
  table_data = table_data.drop(['index'], axis=1)
  # Cases, Deaths显示千分符号
  table_data['Cases'] = table_data['Cases'].apply(lambda x: format(x, ','))
  table_data['Deaths'] = table_data['Deaths'].apply(lambda x: format(x, ','))

  # ChangeCasesMonth, ChangeCasesYear, ChangeDeathsMonth, ChangeDeathsYear显示千分符号
  table_data['ChangeCasesMonth'] = table_data['ChangeCasesMonth'].apply(lambda x: format(x, ','))
  table_data['ChangeCasesYear'] = table_data['ChangeCasesYear'].apply(lambda x: format(x, ','))
  table_data['ChangeDeathsMonth'] = table_data['ChangeDeathsMonth'].apply(lambda x: format(x, ','))
  table_data['ChangeDeathsYear'] = table_data['ChangeDeathsYear'].apply(lambda x: format(x, ','))

  # ChangeCasesMonthPer, ChangeCasesYearPer, ChangeDeathsMonthPer, ChangeDeathsYearPer显示百分比
  table_data['ChangeCasesMonthPer'] = table_data['ChangeCasesMonthPer'].apply(lambda x: format(x, '.2%'))
  table_data['ChangeCasesYearPer'] = table_data['ChangeCasesYearPer'].apply(lambda x: format(x, '.2%'))
  table_data['ChangeDeathsMonthPer'] = table_data['ChangeDeathsMonthPer'].apply(lambda x: format(x, '.2%'))
  table_data['ChangeDeathsYearPer'] = table_data['ChangeDeathsYearPer'].apply(lambda x: format(x, '.2%'))
  # replace nan% and inf% to '-'
  table_data = table_data.replace('nan%', '/')
  table_data = table_data.replace('inf%', '/')

  # select columns
  table_data = table_data[['Diseases', 'DiseasesCN',
                          'Cases', 
                          'ChangeCasesMonth', 'ChangeCasesMonthPer', 
                          'ChangeCasesYear', 'ChangeCasesYearPer', 
                          'Deaths',
                          'ChangeDeathsMonth', 'ChangeDeathsMonthPer',
                          'ChangeDeathsYear',  'ChangeDeathsYearPer']]
  # paste value and percentage
  table_data['ChangeCasesMonth'] = table_data['ChangeCasesMonth'] + ' (' + table_data['ChangeCasesMonthPer'] + ')'
  table_data['ChangeCasesYear'] = table_data['ChangeCasesYear'] + ' (' + table_data['ChangeCasesYearPer'] + ')'
  table_data['ChangeDeathsMonth'] = table_data['ChangeDeathsMonth'] + ' (' + table_data['ChangeDeathsMonthPer'] + ')'
  table_data['ChangeDeathsYear'] = table_data['ChangeDeathsYear'] + ' (' + table_data['ChangeDeathsYearPer'] + ')'
  # drop percentage columns
  table_data = table_data.drop(['ChangeCasesMonthPer', 'ChangeCasesYearPer', 'ChangeDeathsMonthPer', 'ChangeDeathsYearPer'], axis=1)

  # get compare date
  compare_PM = analysis_date - pd.DateOffset(months=1)
  compare_PM = compare_PM.strftime('%Y %B')
  compare_PY = analysis_date - pd.DateOffset(years=1)
  compare_PY = compare_PY.strftime('%Y %B')

  # set columns name
  table_data.columns = ['Diseases', 'Diseases(Chinese)',
                        'Cases', 
                        'Compare with ' + compare_PM, 
                        'Compare with ' + compare_PY, 
                        'Deaths', 
                        'Compare with ' + compare_PM, 
                        'Compare with ' + compare_PY]
  # 把第一行放到最后一行
  table_data = table_data.append(table_data.iloc[0], ignore_index=True)
  table_data = table_data.drop([0], axis=0)
  # 选择第1-5列
  table_data_cases = table_data.iloc[:, 0:5]
  # 选择第1-2和6-8列
  table_data_deaths = table_data.iloc[:, [0, 1, 5, 6, 7]]

  # 创建报告
  doc = SimpleDocTemplate("../Report/report " + analysis_YearMonth + ".pdf", pagesize=letter)

  # 定义样式
  styles = getSampleStyleSheet()
  styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=12, textColor=colors.gray))

  # 添加封面
  cover_elements = []

  # 添加封面标题
  cover_title = Paragraph("CNID: A Dynamic Sensing Project of Notifiable Infectious Diseases Data in Mainland, China", styles['Title'])
  cover_elements.append(cover_title)
  cover_elements.append(Spacer(1, 12))

  # 添加封面副标题
  cover_subtitle = Paragraph("This report create by reportlab and python, automatically.", styles['Subtitle'])
  cover_elements.append(cover_subtitle)
  cover_elements.append(Spacer(1, 36))

  # 添加封面底部引用
  cover_citation = Paragraph("Cite Us: Reported Cases and Deaths of National Notifiable Infectious Diseases — China, June 2023*[J]. China CDC Weekly. <u><a href='http://dx.doi.org/10.46234/ccdcw2023.130'>doi: 10.46234/ccdcw2023.130</a></u>", styles['Normal'])
  cover_elements.append(cover_citation)
  cover_elements.append(PageBreak())

  # 创建元素列表
  elements = []

  # 添加封面内容到元素列表
  elements.extend(cover_elements)

  # 添加页眉和页码
  def add_page_number(canvas, doc):
      canvas.saveState()
      canvas.setFont("Helvetica", 9)
      canvas.drawString(inch, 0.75 * inch, "CNID dynamic sensing")
      canvas.drawString(7.5 * inch, 0.75 * inch, str(doc.page))
      canvas.restoreState()
      
  # 创建一个自定义的页脚样式
  footer_style = ParagraphStyle(
      name='FooterStyle',
      fontSize=10,
      textColor='gray',
      alignment=1,
      spaceAfter=0.1 * inch
  )

  # 添加页眉和页码模板
  doc = SimpleDocTemplate("../Report/report " + analysis_YearMonth + ".pdf", pagesize=letter)

  # 创建自定义的页面模板，指定页脚回调函数
  page_template = PageTemplate(id='mypagetemplate', onPage=add_page_number)

  # 添加标题
  title = Paragraph("Notifiable Infectious Diseases Reports: Reported Cases and Deaths of National Notifiable Infectious Diseases — China, " + analysis_YearMonth, styles['Title'])
  elements.append(title)
  elements.append(Spacer(1, 12))

  # 添加图像1
  image1 = Image('./temp/merged_chart.png', width=500, height=500)
  elements.append(image1)
  elements.append(Spacer(1, 12))

  # 分割页
  elements.append(PageBreak())

  # 添加二级标题
  subtitle1 = Paragraph("Monthly Cases ———— " + analysis_YearMonth, styles['Heading2'])
  elements.append(subtitle1)
  # 添加表格
  data = [table_data_cases.columns.tolist()] + table_data_cases.values.tolist()
  table = Table(data)
  table_style = TableStyle([
      ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
      ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),
      ('FONTSIZE', (0, 1), (-1, -1), 8),
      ('LEADING', (0, 0), (-1, -1), 6)
  ])
  table.setStyle(table_style)
  elements.append(table)
  elements.append(Spacer(1, 12))
  elements.append(PageBreak())

  # 添加表格标题
  subtitle2 = Paragraph("Monthly Deaths ———— " + analysis_YearMonth, styles['Heading2'])
  elements.append(subtitle2)
  # 添加表格
  data = [table_data_deaths.columns.tolist()] + table_data_deaths.values.tolist()
  table = Table(data)
  table_style = TableStyle([
      ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
      ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),
      ('FONTSIZE', (0, 1), (-1, -1), 8),
      ('LEADING', (0, 0), (-1, -1), 6)
  ])
  table.setStyle(table_style)
  elements.append(table)
  elements.append(Spacer(1, 12))
  elements.append(PageBreak())

  title = Paragraph("Historic Notifiable Infectious Diseases Reports Analysis — China, " + analysis_YearMonth, styles['Title'])
  elements.append(title)
  elements.append(Spacer(1, 12))

  elements.append(PageBreak())

  # 添加每种Disease的页面
  for disease in table_data_cases['Diseases']:
      # 添加标题
      disease_title = Paragraph("Disease: {}".format(disease), styles['Heading2'])
      elements.append(disease_title)
      elements.append(Spacer(1, 12))

      # 获取疾病数据
      disease_data = df[df['Diseases'] == disease].copy()
      disease_data['Date'] = pd.to_datetime(disease_data['Date']).dt.date
      disease_data = disease_data.sort_values(by='Date', ascending=True)
      # 选择列
      disease_data = disease_data[['YearMonthDay', 'Cases', 'Deaths']]
      # 补全缺失的日期，检查dates中是否有缺失的日期
      missing_dates = list(set(dates) - set(disease_data['YearMonthDay']))
      missing_data = pd.DataFrame({'YearMonthDay': missing_dates, 'Cases': None, 'Deaths': None})
      disease_data = pd.concat([disease_data, missing_data])
      # 生成从最小值到最大值的一串日期，间隔为月
      dates_unrecognized = pd.date_range(disease_data['YearMonthDay'].min(), disease_data['YearMonthDay'].max(), freq='MS').strftime('%Y/%m/%d')
      dates_unrecognized = list(set(dates_unrecognized) - set(disease_data['YearMonthDay']))
      missing_data = pd.DataFrame({'YearMonthDay': dates_unrecognized, 'Cases': None, 'Deaths': None})
      disease_data = pd.concat([disease_data, missing_data])
      # 排序
      disease_data = disease_data.sort_values(by='YearMonthDay', ascending=True)
      # 重置索引
      disease_data = disease_data.reset_index()
      # 删除索引列
      disease_data = disease_data.drop(['index'], axis=1)
      # 生成日期列
      disease_data['Date'] = pd.to_datetime(disease_data['YearMonthDay'])

      # 生成折线图1 - Cases
      fig, ax1 = plt.subplots(figsize=(12, 4))
      ax1.plot(disease_data['Date'], disease_data['Cases'], color='blue')
      ax1.set_ylabel("Cases", color = 'blue')
      
      ax2 = ax1.twinx()
      ax2.plot(disease_data['Date'], disease_data['Deaths'], color='red')
      ax2.set_ylabel("Deaths", color = 'red')
      disease_chart1_path = os.path.join("temp", "disease_{}_chart1.png".format(disease))
      plt.savefig(disease_chart1_path)

      # 表格整理
      ## 提取年份和月份
      disease_data['Year'] = disease_data['Date'].dt.year
      disease_data['Month'] = disease_data['Date'].dt.month
      # 去除重复行
      disease_data = disease_data.drop_duplicates(subset=['Year', 'Month'])
      ## 表格转置
      table_data_case = disease_data.pivot(index='Month', columns='Year', values='Cases')
      table_data_death = disease_data.pivot(index='Month', columns='Year', values='Deaths')

      ## 绘制热图1
      # fig, ax = plt.subplots(figsize=(12, 4))
      # sns.heatmap(table_data_case, annot=True, fmt="d", linewidths=.5, ax=ax)
      # plt.title("Heatmap of Cases by Month and Year")
      # plt.xlabel("Year")
      # plt.ylabel("Month")
      # disease_chart2_path = os.path.join("temp", "disease_{}_chart2.png".format(disease))
      # plt.savefig(disease_chart2_path)

      # 添加折线图1
      disease_image1 = Image(disease_chart1_path, width=600, height=200)
      elements.append(disease_image1)
      elements.append(Spacer(1, 12))

      # 添加表格1
      data = [table_data_case.columns.tolist()] + table_data_case.values.tolist()
      table = Table(data)
      table.setStyle(table_style)
      elements.append(table)
      elements.append(Spacer(1, 12))


      # 添加表格2
      data = [table_data_death.columns.tolist()] + table_data_death.values.tolist()
      table = Table(data)
      table.setStyle(table_style)
      elements.append(table)
      elements.append(Spacer(1, 12))

      elements.append(PageBreak())

  # 将元素列表添加到报告中
  doc.build(elements)

  # 删除temp文件夹
  import shutil
  shutil.rmtree("temp")

  # 复制一份文件为 Report latest.pdf
  shutil.copy("../Report/report " + analysis_YearMonth + ".pdf", "../Report/report latest.pdf")