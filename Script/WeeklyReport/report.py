import datetime
from plotnine import *
import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4, inch
from reportlab.graphics.shapes import Line, LineShape, Drawing
from reportlab.lib.colors import Color
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
import time

from function import chatgpt_description
from function import chatgpt_description_time
from function import chatgpt_mail_raw
from function import chatgpt_mail_rebuild

def generate_report(analysis_YearMonth, table_data, df, diseases_order, api_base, api_key):
    table_data_cases = table_data.iloc[:, [0, 2, 3, 4]].sort_values(by='Diseases', key=lambda x: x.map(diseases_order.index))
    table_data_deaths = table_data.iloc[:, [0, 5, 6, 7]].sort_values(by='Diseases', key=lambda x: x.map(diseases_order.index))
    diseases = table_data_cases['Diseases'].tolist()
    table_data_str = table_data.iloc[:, [0, 2, 3, 4, 5, 6, 7]]
    table_data_str = table_data_str.to_markdown(index=False)

    class FooterCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pages = []
            self.width, self.height = letter

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            page_count = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                if self._pageNumber > 1:
                    self.draw_canvas(page_count)
                super().showPage()
            super().save()

        def draw_canvas(self, page_count):
            page = "Page %s of %s" % (self._pageNumber - 1, page_count - 1)
            x = 128
            self.saveState()
            self.setStrokeColorRGB(0, 0, 0)
            self.setLineWidth(0.5)

            self.line(30, self.height - 10, self.width - 30, self.height - 10)
            self.line(30, 50, self.width - 30, 50)
            self.drawString(self.width - x, 25, page)
            self.drawString(self.width - inch * 8 - 5, self.height, "CNIDs: Chinese Notifiable Infectious Diseases Perception Project")
            self.restoreState()

    class PDFPSReporte:
        def __init__(self, path):
            self.path = path
            self.styleSheet = getSampleStyleSheet()
            self.elements = []

            # colors - Azul turkeza 367AB3
            self.colorOhkaGreen0 = Color((45.0/255), (166.0/255), (153.0/255), 1)
            self.colorOhkaGreen1 = Color((182.0/255), (227.0/255), (166.0/255), 1)
            self.colorOhkaGreen2 = Color((140.0/255), (222.0/255), (192.0/255), 1)
            #self.colorOhkaGreen2 = Color((140.0/255), (222.0/255), (192.0/255), 1)
            self.colorOhkaBlue0 = Color((54.0/255), (122.0/255), (179.0/255), 1)
            self.colorOhkaBlue1 = Color((122.0/255), (180.0/255), (225.0/255), 1)
            self.colorOhkaGreenLineas = Color((50.0/255), (140.0/255), (140.0/255), 1)
            # set style
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=12, textColor=colors.gray))
            styles.add(ParagraphStyle(name='Notice', parent=styles['Normal'], fontSize=14, textColor=colors.red, alignment=TA_CENTER, borderWidth=3))
            styles.add(ParagraphStyle(name="Cite", alignment=TA_LEFT, fontSize=10, textColor=colors.gray))
            styles.add(ParagraphStyle(name="Author", alignment=TA_LEFT, fontSize=10, textColor=colors.black))
            styles.add(ParagraphStyle(name='Hed0', fontSize=16, alignment=TA_LEFT, borderWidth=3, textColor=self.colorOhkaGreen0, leftIndent=-16))
            styles.add(ParagraphStyle(name='Hed1', fontSize=14, alignment=TA_LEFT, borderWidth=3, textColor=self.colorOhkaBlue1, leftIndent=-16, rightIndent=-16))
            styles.add(ParagraphStyle(name='Content', fontSize=10, alignment=TA_LEFT, borderWidth=3, textColor=colors.black, leftIndent=-16, rightIndent=-16))
            styles.add(ParagraphStyle(name='Legend', fontSize=12, bold=True, alignment=TA_CENTER, borderWidth=3, textColor=self.colorOhkaBlue0, leftIndent=-16, rightIndent=-16))
            # change style margin
            styles['Normal'].leftMargin = 0
            styles['Normal'].rightMargin = 0
            # set table style
            table_style = TableStyle([
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), self.colorOhkaGreen0),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('LINEBELOW', (0, 0), (-1, -1), 1, self.colorOhkaBlue1),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue)
            ])

            self.firstPage(styles)
            self.nextPagesHeader('Monthly Report -- ' + analysis_YearMonth, styles)
            self.MonthlyPages(styles, table_style, table_data_str)
            self.nextPagesHeader('History Data Analysis' + analysis_YearMonth, styles)
            self.HistoryTotalPages(styles, disease='Total')

            if 'Total' in diseases:
                diseases.remove('Total')
            
            if os.environ['test_analysis'] == "True":
                for i, disease in enumerate(diseases[1:2]):
                    self.HistoryTotalPages(styles, disease, i + 1)
            else:
                for i, disease in enumerate(diseases):
                    self.HistoryTotalPages(styles, disease, i + 1)
            # Build
            self.doc = SimpleDocTemplate(path, pagesize=A4)
            self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

        def firstPage(self, styles):
            cover_title = Paragraph("CNIDs: Chinese Notifiable Infectious Diseases Perception Project", styles['Subtitle'])
            self.elements.append(cover_title)
            self.elements.append(Spacer(30, 100))

            cover_title = Paragraph("A Dynamic Perception Report of Notifiable Infectious Diseases Data in Mainland, China", styles['Title'])
            self.elements.append(cover_title)
            self.elements.append(Spacer(1, 12))

            cover_title = Paragraph(analysis_YearMonth, styles['Title'])
            self.elements.append(cover_title)
            self.elements.append(Spacer(1, 12))

            cover_title = Paragraph("NOTICE: The text in this report was generate by ChatGPT-3.5-turbo-16k-0613, for reference only.", styles['Notice'])
            self.elements.append(cover_title)
            self.elements.append(Spacer(1, 12))

            self.elements.append(Spacer(10, 270))

            datenow = datetime.datetime.now()
            datenow = datenow.strftime("%Y-%m-%d")
            text = f"""Automaticly Generate by Python and ChatGPT<br/>
            Power by: Github Action<br/>
            Design by: Kangguo Li<br/>
            Connect with me: <u><a href='mailto:lkg1116@outlook.com'>lkg1116@outlook.com</a></u><br/>
            Generated Date: {datenow}<br/>
            """
            paragraphReportSummary = Paragraph(text, styles["Author"])
            self.elements.append(paragraphReportSummary)
            self.elements.append(Spacer(1, 30))

            text = os.environ['cite']
            cover_citation = Paragraph(text, styles['Cite'])
            self.elements.append(cover_citation)
            self.elements.append(PageBreak())

        def nextPagesHeader(self, text=None, styles=None):
            paragraphReportHeader = Paragraph(text, styles['Hed0'])
            self.elements.append(paragraphReportHeader)

            spacer = Spacer(10, 10)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-20, 0, 460, 0)
            line.strokeColor = self.colorOhkaGreenLineas
            line.strokeWidth = 2
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 1)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-20, 0, 460, 0)
            line.strokeColor = self.colorOhkaGreenLineas
            line.strokeWidth = 0.5
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 22)
            self.elements.append(spacer)

        def MonthlyPages(self, styles=None, table_style=None, table_data_str=None, api_base=api_base, api_key=api_key):
            image1 = Image('./temp/merged_chart.png', width=500, height=500)
            self.elements.append(image1)
            self.elements.append(Spacer(1, 12))
            legend = Paragraph("Figure 1: Monthly Notifiable Infectious Diseases Reports in " + analysis_YearMonth, styles['Legend'])
            self.elements.append(legend)
            self.elements.append(Spacer(1, 12))

            # generate mail content
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                content = chatgpt_mail_raw(api_base, api_key, analysis_YearMonth, table_data_str, 'gpt-3.5-turbo-16k')
                if content is not None:
                    break
                else:
                    time.sleep(21)
                attempts += 1
            # rebuild mail content
            content = chatgpt_mail_rebuild(content, analysis_YearMonth)
            with open(f'../Report/mail/{analysis_YearMonth}.md', 'w') as f:
                f.write(content)
            with open(f'../Report/table/{analysis_YearMonth}.md', 'w') as f:
                f.write(table_data_str)

            # add out_content
            attempts = 0
            content = None
            while attempts < max_attempts:
                content = chatgpt_description_time(api_base, api_key, analysis_YearMonth, table_data_str, 'gpt-3.5-turbo')
                if content is not None:
                    paragraphChatgpt = Paragraph(content.replace('\n\n', '<br />\n'), styles['Content'])
                    self.elements.append(paragraphChatgpt)
                    self.elements.append(Spacer(1, 12))
                    break
                else:
                    time.sleep(21)
                attempts += 1

            legend = Paragraph("Table 1: Monthly Notifiable Infectious Diseases Cases in " + analysis_YearMonth, styles['Legend'])
            self.elements.append(legend)
            self.elements.append(Spacer(1, 12))
            data = [table_data_cases.columns.tolist()] + table_data_cases.values.tolist()
            table = Table(data)
            table.setStyle(table_style)
            self.elements.append(table)
            self.elements.append(Spacer(1, 12))

            legend = Paragraph("Table 2: Monthly Notifiable Infectious Diseases Deaths in " + analysis_YearMonth, styles['Legend'])
            self.elements.append(legend)
            self.elements.append(Spacer(1, 12))
            data = [table_data_deaths.columns.tolist()] + table_data_deaths.values.tolist()
            table = Table(data)
            table.setStyle(table_style)
            self.elements.append(table)

            self.elements.append(PageBreak())

        def HistoryTotalPages(self, styles=None, disease='Total', i=0, api_base=api_base, api_key=api_key, df = df):
            # add head
            paragraphReportHeader = Paragraph(disease, styles['Hed1'])
            self.elements.append(paragraphReportHeader)
            self.elements.append(Spacer(1, 12))

            # filter data
            disease_data = df[df['Diseases'] == disease].copy()
            disease_data['Date'] = pd.to_datetime(disease_data['Date']).dt.date
            disease_data = disease_data.sort_values(by='Date', ascending=True)
            # 选择列
            disease_data = disease_data[['YearMonthDay', 'Cases', 'Deaths']]
            dates_unrecognized = pd.date_range(disease_data['YearMonthDay'].min(), disease_data['YearMonthDay'].max(), freq='MS').strftime('%Y/%m/%d')
            dates_unrecognized = list(set(dates_unrecognized) - set(disease_data['YearMonthDay']))
            missing_data = pd.DataFrame({'YearMonthDay': dates_unrecognized, 'Cases': None, 'Deaths': None})
            disease_data = pd.concat([disease_data, missing_data])

            disease_data = disease_data.sort_values(by='YearMonthDay', ascending=True)
            disease_data = disease_data.reset_index()
            disease_data = disease_data.drop(['index'], axis=1)
            disease_data['Date'] = pd.to_datetime(disease_data['YearMonthDay'])
            # add YearMonth
            disease_data['YearMonth'] = disease_data['Date'].dt.strftime('%Y %B')

            # 生成折线图1 - Cases
            fig, ax1 = plt.subplots(figsize=(12, 4))
            ax1.plot(disease_data['Date'], disease_data['Cases'], color='blue')
            ax1.set_ylabel("Cases", color='blue')
            ax2 = ax1.twinx()
            ax2.plot(disease_data['Date'], disease_data['Deaths'], color='red')
            ax2.set_ylabel("Deaths", color='red')
            disease_chart1_path = os.path.join("temp", "disease_{}_chart1.png".format(disease))
            plt.savefig(disease_chart1_path)
            plt.close()
            plt.show()

            # table
            disease_data['Year'] = disease_data['Date'].dt.year
            disease_data['Month'] = disease_data['Date'].dt.month
            disease_data = disease_data.drop_duplicates(subset=['Year', 'Month'])
            disease_data = disease_data.melt(id_vars=['Year', 'Month', 'YearMonth'],
                                             value_vars=['Cases', 'Deaths'],
                                             var_name='Type',
                                             value_name='Value')
            disease_data['Value'] = disease_data['Value'].fillna(-10)

            ## heatmap
            plot_total = (
                    ggplot(disease_data[(disease_data['Value'] != -10) & (disease_data['Type'] == 'Cases')],
                           aes(y='factor(Month)', x='factor(Year)', fill='Value')) +
                    geom_tile(aes(width=.95, height=.95)) +
                    scale_fill_continuous(limits=[0, None]) +
                    coord_equal() +
                    theme_bw() +
                    labs(x='Year', y='Month', fill='Cases')
            )

            disease_chart2_path = os.path.join("temp", "disease_{}_chart2.png".format(disease))
            plot_total.save(disease_chart2_path, dpi=300, width=7, height=5)

            plot_total = (
                    ggplot(disease_data[(disease_data['Value'] != -10) & (disease_data['Type'] == 'Deaths')],
                           aes(y='factor(Month)', x='factor(Year)', fill='Value')) +
                    geom_tile(aes(width=.95, height=.95)) +
                    scale_fill_continuous(limits=[0, None]) +
                    coord_equal() +
                    theme_bw() +
                    labs(x='Year', y='Month', fill='Cases')
            )

            disease_chart3_path = os.path.join("temp", "disease_{}_chart3.png".format(disease))
            plot_total.save(disease_chart3_path, dpi=300, width=7, height=5)

            disease_image1 = Image(disease_chart1_path, width=600, height=200)
            self.elements.append(disease_image1)
            self.elements.append(Spacer(1, 12))
            legend = Paragraph(f"Figure {i * 3 + 2}: The Change of {disease} Reports before " + analysis_YearMonth,
                               styles['Legend'])
            self.elements.append(legend)
            self.elements.append(Spacer(1, 12))

            # add out_content
            disease_data_str = disease_data[['YearMonth', 'Type', 'Value']].to_markdown(index=False)

            max_attempts = 10
            attempts = 0
            content = None
            while attempts < max_attempts:
                content = chatgpt_description(api_base, api_key, analysis_YearMonth, disease_data_str,
                                              'gpt-3.5-turbo', disease_name=f'for {disease}')
                if content is not None:
                    paragraphChatgpt = Paragraph(content.replace('\n\n', '<br />\n'), styles['Content'])
                    self.elements.append(paragraphChatgpt)
                    self.elements.append(Spacer(1, 12))
                    break
                else:
                    time.sleep(21)
                attempts += 1

            disease_image1 = Image(disease_chart2_path, width=350, height=250)
            self.elements.append(disease_image1)
            self.elements.append(Spacer(1, 12))
            legend = Paragraph(f"Figure {i * 3 + 3}: The Change of {disease} Cases before " + analysis_YearMonth,
                               styles['Legend'])
            self.elements.append(legend)
            self.elements.append(Spacer(1, 12))

            disease_image1 = Image(disease_chart3_path, width=350, height=250)
            self.elements.append(disease_image1)
            self.elements.append(Spacer(1, 12))
            legend = Paragraph(f"Figure {i * 3 + 4}: The Change of {disease} Deaths before " + analysis_YearMonth,
                               styles['Legend'])
            self.elements.append(legend)
            self.elements.append(PageBreak())

    # 创建报告对象并生成报告
    report = PDFPSReporte(path = "../Report/report " + analysis_YearMonth + ".pdf")
