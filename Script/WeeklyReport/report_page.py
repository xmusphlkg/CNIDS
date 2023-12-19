
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
import matplotlib.colors as mcolors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime
import os
import re
import markdown

from report_fig import prepare_disease_data, plot_disease_data, plot_disease_heatmap
from report_text import openai_single, openai_analysis

def create_report_page(df,
                       disease_name,
                       report_date,
                       page_number,
                       page_total,
                       links_app = "https://lkg1116.shinyapps.io/CNIDS/",
                       links_web = "https://github.com/xmusphlkg/CNID"):
    """
    This function is used to process disease data.

    Parameters:
    - df: the dataframe of disease data
    - disease_name: the name of disease
    - report_date: the date of report, format: "June 2023"
    - page_number: the number of page
    - page_total: the total number of page
    - links_app: the link of app
    - links_web: the link of web
    - foot_left_content: the content of left footer, format: "Page 1 of 1"
    """

    # create figure1 and figure2 of report
    disease_data = prepare_disease_data(df, disease_name)
    plot_disease_data(disease_data, disease_name)
    plot_disease_heatmap(disease_data, disease_name)
    table_data_str = disease_data[['YearMonth', 'Cases', 'Deaths']].to_markdown(index=False)

    # generate introduction content
    introduction_box_content = openai_single('gpt-4',
                                              'gpt-3.5-turbo',
                                              f"Give a brief introduction to {disease_name}, not give any comment (words limit 90 - 100 words).", 
                                              "Introduction",
                                              disease_name)
    # introduction_box_content = "testinfo"
    highlights_box_content = openai_single('gpt-4',
                                            'gpt-3.5-turbo',
                                            f"""Analyze below reported data for {disease_name} in mainland, China,
                                            Please briefly list several epidemiologist furthers people should notice,
                                            no only trends, but also the situation of the disease in {report_date},
                                            only list highlight like below format:

                                            1. Highlight content.<br/>2. Highlight content.</br>......
                                            (words limit 110 - 120 words).
                                            
                                            This the data for {disease_name} in mainland, China:
                                            {table_data_str}""",
                                            "Highlights",
                                            disease_name)
    # highlights_box_content = "testinfo"

    analy_box_content = openai_single('gpt-4',
                                      'gpt-3.5-turbo',
                                      f"""Analyze below reported data for {disease_name} in mainland, China,
                                      Please provide a brief analysis for {disease_name} of the data, like below format:
                                      ### Cases Analysis
                                      ......
                                      ### Deaths Analysis
                                      ......
                                      (The word count for each parts limit 110-120 words.)
                                      This the data for {disease_name} in mainland, China:
                                      {table_data_str}""",
                                      "Analysis",
                                      disease_name)
    # analy_box_content = "### Cases Analysis\n\n testinfo ### Deaths Analysis\n\n testinfo"

    cases_box_content = analy_box_content.split("### Cases Analysis")[1].split("### Deaths Analysis")[0]
    death_box_content = analy_box_content.split("### Deaths Analysis")[1]

    foot_left_content = f"Page {page_number} of {page_total}"

    create_report_disease(disease_name,
                          report_date, 
                          introduction_box_content,
                          highlights_box_content,
                          cases_box_content,
                          death_box_content,
                          foot_left_content,
                          links_app,
                          links_web)

def create_report_disease(set_disease_name,
                          set_report_date, 
                          introduction_box_content,
                          highlights_box_content,
                          incidence_box_content,
                          death_box_content,
                          foot_left_content,
                          links_app,
                          links_web,
                          info_box_content = '<font color="red"><b>' + "IMPORTANT: The text in boxs is generated automatically by ChatGPT. " + '</b></font>', 
                          foot_right_content = "All rights reserved.",
                          set_report_title = "Chinese Notifiable Infectious Diseases Surveillance Report"):
    # setting function description
    """
    This function is used to generate pdf report page for single disease.

    Parameters:
    - set_disease_name (str): the name of disease
    - set_report_date (str): the date of report, format: "June 2023"
    - introduction_box_content (str): the content of introduction box, generated by ChatGPT
    - highlights_box_content (str): the content of highlights box, generated by ChatGPT
    - incidence_box_content (str): the content of incidence box, generated by ChatGPT
    - death_box_content (str): the content of death box, generated by ChatGPT
    - foot_left_content (str): the content of left footer, format: "Page 1 of 1"
    - links_app (str): the link of app
    - links_web (str): the link of web
    - info_box_content (str): the content of informaton box, wanring users that the content of boxs is generated automatically by ChatGPT
    """

    # create pdf
    pdf_filename =  f"./temp/{set_disease_name}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)

    # define page size
    page_width, page_height = A4

    # define title box
    title_box_x = 20
    title_box_y = 730
    title_box_space = 5
    title_box_width = page_width - title_box_x * 2
    title_box_height = 80
    title_box_color = colors.HexColor("#1E5E84")
    title_font_sizes = [18, 16, 12]
    title_line_spacing = [1.5, 1, 1]
    title_font_family = ['Helvetica-Bold', 'Helvetica', 'Helvetica']
    title_text_color = colors.white

    # draw title box
    c.setFillColor(title_box_color)
    c.rect(title_box_x, title_box_y, title_box_width, title_box_height, fill=True, stroke=False)
    title_text_x = title_box_x + title_box_space * 2
    title_text_y = title_box_y + title_box_height - 25
    title_lines = [
        set_report_title,
        set_disease_name,
        set_report_date
    ]
    for i, line in enumerate(title_lines):
        c.setFont(title_font_family[i], title_font_sizes[i])
        c.setFillColor(title_text_color)
        c.drawString(title_text_x, title_text_y, line)
        if i < len(title_lines) - 1:
            title_text_y -= title_font_sizes[i] * title_line_spacing[i] + 2
        else:
            break

    # define content box
    content_box_title_color = colors.HexColor("#2E2F5C")

    introduction_box_height = 120
    introduction_box_y = title_box_y - introduction_box_height - title_box_space * 3
    introduction_box_width = (title_box_width - title_box_space * 2) * 2 / 3

    temporal_trend_box_height = 195
    temporal_trend_box_y = introduction_box_y - temporal_trend_box_height - title_box_space * 2
    temporal_trend_box_width = introduction_box_width

    highlights_box_height = introduction_box_height + temporal_trend_box_height + title_box_space*2
    highlights_box_y = temporal_trend_box_y
    highlights_box_width = (title_box_width - title_box_space*2) * 1 / 3

    incidence_box_width = (title_box_width - title_box_space*2) * 1 / 2
    incidence_box_height = 165
    incidence_box_y = temporal_trend_box_y - incidence_box_height - title_box_space * 2

    month_box_width = (title_box_width - title_box_space*2) * 3 / 4
    month_box_height = 150
    month_box_y = incidence_box_y - month_box_height - title_box_space * 2

    info_box_height = 30

    # draw content box
    box_positions = [
        (title_box_x, introduction_box_y, introduction_box_width, introduction_box_height, "#E6E6E6", introduction_box_content),
        (title_box_x, temporal_trend_box_y, temporal_trend_box_width, temporal_trend_box_height, "#E6E6E6", "figure1"),
        (title_box_x + introduction_box_width + title_box_space*2, highlights_box_y, highlights_box_width, highlights_box_height, "#E6E6E6", highlights_box_content),
        (title_box_x, incidence_box_y, incidence_box_width, incidence_box_height, "#E6E6E6", incidence_box_content),
        (title_box_x + incidence_box_width + title_box_space*2, incidence_box_y, incidence_box_width, incidence_box_height, "#E6E6E6", death_box_content),
        (title_box_x , month_box_y, month_box_width, month_box_height, "#E6E6E6", "figure2"),
        (title_box_x+ month_box_width + title_box_space*2, month_box_y, month_box_width/3, month_box_height, "#D8E6E8", 'figure3'),
        (title_box_x, month_box_y - info_box_height - title_box_space*2, title_box_width, info_box_height, "#E6E6E6", info_box_content)
    ]
    box_titles = [
        "Introduction", 
        "Temporal Trend",
        "Highlights",
        "Cases Analysis",
        "Deaths Analysis",
        "Distribution",
        "",
        None
    ]
    box_links =[
        links_app,
        links_app,
        links_app,
        links_app,
        links_app,
        links_app,
        links_web,
        links_web
    ]
    styles = getSampleStyleSheet()

    for i, (x, y, width, height, color, content) in enumerate(box_positions):
        c.setFillColor(colors.HexColor(color))
        c.rect(x, y, width, height, fill=True, stroke=False)

        if box_titles[i] is None:
            para = Paragraph(content, styles['Normal'])
            para.wrapOn(c, width - 10, height - 10)
            para.drawOn(c, x + 10, y + height - para.height - 8)
        else:
            c.setFont(title_font_family[0], 14)
            c.setFillColor(content_box_title_color)
            c.drawString(x + title_box_space*2, y + height - 15, box_titles[i])

        if content.startswith('figure'):
            if content == 'figure3':
                image_path = f'./{content}.png'
            else:
                image_path = f'temp/{set_disease_name} {content}.png'
            image = ImageReader(image_path)
            iw, ih = image.getSize()
            scale_w = (width - 20) / iw
            scale_h = (height - 30) / ih
            scale = min(scale_w, scale_h)
            new_width = iw * scale
            new_height = ih * scale
            new_x = x + 10 + (width - 20 - new_width) / 2
            new_y = y + 10 + (height - 30 - new_height) / 2
            c.drawImage(image_path, new_x, new_y, new_width, new_height, mask='auto')
            c.linkURL(url=box_links[i], rect=(x + 10, y + 10, x + 10 + width - 20, y + 10 + height - 30))
        elif box_titles[i] is not None:
            content = content.replace('<br/>', 'BR_TAG_PLACEHOLDER')
            content = re.sub('<.*?>', '', content)
            content = content.replace('BR_TAG_PLACEHOLDER', '<br/>')
            para = Paragraph(content, styles['Normal'])
            para.wrapOn(c, width - 15, height - 30)
            para.drawOn(c, x + 10, y + height - para.height - 20)

    # define copy right
    copy_right_font_size = 8
    copy_right_font_family = 'Helvetica'
    copy_right_text_color = colors.black

    ## draw copy right
    c.setFont(copy_right_font_family, copy_right_font_size)
    c.setFillColor(copy_right_text_color)
    foot_right_content_width = c.stringWidth(foot_right_content, copy_right_font_family, copy_right_font_size)
    c.drawString(title_box_x + month_box_width + title_box_space*2 + month_box_width/6 - foot_right_content_width/2,
                month_box_y + month_box_height/4,
                foot_right_content)

    current_time = datetime.datetime.now()
    version_content = f"Version: {current_time.strftime('%Y-%m-%d')} ({current_time.astimezone().strftime('%Z%z').replace('00','')})"
    version_content_width = c.stringWidth(version_content, copy_right_font_family, copy_right_font_size)
    c.drawString(title_box_x + month_box_width + title_box_space*2 + month_box_width/6 - version_content_width/2,
                month_box_y + month_box_height/4 - 15,
                version_content)

    # define page number
    foot_left_y = 8
    foot_font_size = 8
    foot_font_family = 'Helvetica'
    foot_text_color = colors.HexColor("#606060")

    # draw page number
    c.setFont(foot_font_family, foot_font_size)
    c.setFillColor(foot_text_color)
    c.drawString(title_box_x, foot_left_y, foot_left_content, )

    # save pdf
    c.showPage()
    c.save()

    # remove figure1 and figure2
    os.remove(f"./temp/{set_disease_name} figure1.png")
    os.remove(f"./temp/{set_disease_name} figure2.png")
    os.remove(f"./temp/{set_disease_name} figure2_1.png")
    os.remove(f"./temp/{set_disease_name} figure2_2.png")

    print(f"{set_disease_name} report is generated successfully!")


def create_report_summary(table_data, change_data, df_10, analysis_MonthYear):

    elements = []
    analysis_MonthYear = analysis_MonthYear
    doc = SimpleDocTemplate("./temp/cover_summary.pdf",
                            pagesize=A4,
                            topMargin=20,
                            leftMargin=20,
                            rightMargin=20,
                            bottomMargin=0)

    # setting style
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=12, textColor=colors.gray))
    styles.add(ParagraphStyle(name='Notice', parent=styles['Normal'], fontSize=14, textColor=colors.red, alignment=TA_CENTER, borderWidth=3))
    styles.add(ParagraphStyle(name="Cite", alignment=TA_LEFT, fontSize=10, textColor=colors.gray))
    styles.add(ParagraphStyle(name="Author", alignment=TA_LEFT, fontSize=10, textColor=colors.black))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=18, textColor=colors.white))
    styles.add(ParagraphStyle(name='foot', fontName='Helvetica', fontSize=10, textColor=colors.black))
    styles.add(ParagraphStyle(name='pg', fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#606060")))

    # add cover
    elements = add_cover(elements, styles, analysis_MonthYear)
    # add table
    elements = add_table(elements, table_data, change_data, analysis_MonthYear, styles)
    # add monthly analysis
    table_data_str = df_10.to_markdown(index=False)
    analysis_cases = openai_analysis('gpt-4-32k', 'gpt-3.5-turbo',
                                      f"""Analyze the monthly cases of different diseases in mainland China. Provide a deeply and comprehensive analysis of the current situation.
                                      You need to pay attention: select noteworthy diseases, not all diseases. Using below format:
                                      <b>disease name:</b> analysis content<br/><br/> <b>disease name:</b> analysis content<br/><br/>.....
                                      
                                      This the data:
                                      {table_data_str}""",
                                      4096)
    # table_data_str = table_data.to_markdown(index=False)
    # analysis_content = openai_analysis('gpt-4-32k', 'gpt-3.5-turbo',
    #                                   f"""Analyze the monthly cases and deaths of different diseases in mainland China for {analysis_MonthYear}. Provide a deeply and comprehensive analysis of the data.
    #                                   You need to pay attention: select noteworthy diseases, not all diseases and using below format:
    #                                   <b>disease name:</b> analysis content<br/><br/> <b>disease name:</b> analysis content<br/><br/>.....
                                      
    #                                   This the data for {analysis_MonthYear} in mainland, China:
    #                                   {table_data_str}""",
    #                                   4096)
    # analysis_content = """**Prevalence**: this is test information"""
    # analysis_content = markdown.markdown(analysis_content)
    elements = add_analysis(elements, analysis_content, styles)

    # build
    doc.multiBuild(elements)

def add_cover(elements, styles, analysis_MonthYear):
    cover_title = Paragraph("CNIDS: Chinese Notifiable Infectious Diseases Surveillance Project", styles['Subtitle'])
    elements.append(cover_title)
    elements.append(Spacer(30, 100))

    cover_title = Paragraph("A Dynamic Surveillance Report of Notifiable Infectious Diseases Data in Mainland, China", styles['Title'])
    elements.append(cover_title)
    elements.append(Spacer(1, 12))

    cover_title = Paragraph(analysis_MonthYear, styles['Title'])
    elements.append(cover_title)
    elements.append(Spacer(1, 12))

    cover_title = Paragraph("NOTICE: The text in this report was generate by ChatGPT-3.5-turbo-16k for reference only.", styles['Notice'])
    elements.append(cover_title)
    elements.append(Spacer(1, 12))

    elements.append(Spacer(10, 270))

    datenow = datetime.datetime.now()
    datenow = datenow.strftime("%Y-%m-%d")
    text = f"""Automaticly Generate by Python and ChatGPT<br/>
    Power by: Github Action<br/>
    Design by: Kangguo Li<br/>
    Connect with me: <u><a href='mailto:lkg1116@outlook.com'>lkg1116@outlook.com</a></u><br/>
    Generated Date: {datenow}<br/>
    """
    paragraphReportSummary = Paragraph(text, styles["Author"])
    elements.append(paragraphReportSummary)
    elements.append(Spacer(1, 30))

    text = os.environ['cite']
    cover_citation = Paragraph(text, styles['Cite'])
    elements.append(cover_citation)
    elements.append(PageBreak())

    return elements

def add_table(elements, table_data, change_data, analysis_MonthYear, styles):
    doc = SimpleDocTemplate(f"./temp/temp.pdf",
                            pagesize=A4,
                            topMargin=20,
                            leftMargin=20,
                            rightMargin=20,
                            bottomMargin=0)
    # add title
    title = f'Chinese Notifiable Infectious Diseases Surveillance Report<br/><br/>{analysis_MonthYear}'
    title = Paragraph(title, styles['Center'])
    title_table = Table([[title]], colWidths=[doc.width], rowHeights=[80])
    title_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1E5E84")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ])
    elements.append(title_table)
    elements.append(Spacer(1, 12))

    # add table
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#2DA699')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 2), (-1, -1), 7),
        ('LEADING', (0, 2), (-1, -1), 7),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2DA699')),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
        ('LINEABOVE', (1, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, -2), (-1, -1), 1, colors.black),
        ('SPAN', (0, 0), (0, 1)),
        ('SPAN', (1, 0), (3, 0)),
        ('SPAN', (4, 0), (6, 0))
    ]

    data = [
        ('Disease', 'Cases', '', '', 'Deaths', '', ''),
        ('', 'Reported', 'MoM*', 'YoY**', 'Reported', 'MoM*', 'YoY**')
    ] + table_data.values.tolist()

    # setting width of table
    table = Table(data)
    table.setStyle(table_style)
    # prebuild
    elements_temp = [table]
    doc.build(elements_temp)
    # remove temp file
    os.remove(f"./temp/temp.pdf")

    colWidths = sum(table._colWidths)
    col_widths = [width * doc.width/colWidths for width in table._colWidths]
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)

    ## setting color fill
    min_case = min(change_data['Cases'][:-1])
    max_case = max(change_data['Cases'][:-1])
    norm_case = mcolors.Normalize(vmin=min_case, vmax=max_case)
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["#FFFFFFFF", "#088096FF"])
    for i in range(2, len(data)-1):
        value = change_data['Cases'][i-2]
        cell_color = mcolors.to_hex(cmap(norm_case(value)))
        table.setStyle([('BACKGROUND', (1, i), (1, i), colors.HexColor(cell_color))])

    min_death = min(change_data['Deaths'][:-1])
    max_death = max(change_data['Deaths'][:-1])
    norm_death = mcolors.Normalize(vmin=min_death, vmax=max_death)
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["#FFFFFFFF", "#019875FF"])
    for i in range(2, len(data)-1):
        value = change_data['Deaths'][i-2]
        cell_color = mcolors.to_hex(cmap(norm_death(value)))
        table.setStyle([('BACKGROUND', (4, i), (4, i), colors.HexColor(cell_color))])
    elements.append(table)

    # add footnote of table
    footnote = f'*MoM: Month on Month change, **YoY: Year on Year change.'
    footnote = Paragraph(footnote, styles['foot'])
    elements.append(footnote)
    elements.append(PageBreak())

    return elements

def add_analysis(elements, text, styles):
    # md to html

    paragraphReportSummary = Paragraph(text, styles["Author"])
    elements.append(paragraphReportSummary)
    elements.append(Spacer(1, 12))

    return elements

# Example usage:
# disease_name = "Hand foot and mouth disease"
# report_date = "June 2023"
# introduction_box_content = "box information"
# highlights_box_content = "**Prevalence**: this is test information"
# incidence_box_content = "this is test information"
# death_box_content = "this is test information"
# links_app = "https://lkg1116.shinyapps.io/CNIDS/"
# links_web = "https://github.com/xmusphlkg/CNID"
# foot_left_content = "Page 1 of 1"

# create_report_disease(disease_name, report_date, 
#                       introduction_box_content, highlights_box_content,
#                       incidence_box_content, death_box_content,
#                       foot_left_content, links_app, links_web)
