import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from jinja2 import Template
import os

def update_pages(diseases_order, diseases_order_cn, disease_index, df):
  links = []
  for disease, disease_cn, index in zip(diseases_order, diseases_order_cn, disease_index):
      link = f'<a href="{index}.html">{disease}({disease_cn})</a>'
      links.append(link)

  # Split the links into two columns
  half_length = len(links) // 2
  column1 = links[:half_length]
  column2 = links[half_length:]

  # Create HTML for the two columns
  column1_content = '<br>'.join(column1)
  column2_content = '<br>'.join(column2)
  div_content = f'<div style="display: inline-block; width: 50%;">{column1_content}</div>'
  div_content += f'<div style="display: inline-block; width: 50%;">{column2_content}</div>'

  div_element = f'<div>{div_content}</div>'

  with open('./templates/index.html', 'r') as f:
      template_content = f.read()

  for i, disease in enumerate(diseases_order):
      df_disease = df[df['Diseases'] == disease]
      df_disease = df_disease.sort_values('Date')
      
      fig = go.Figure(layout=go.Layout(
          title=go.layout.Title(text=f'{disease}({diseases_order_cn[i]})'),
          xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
          yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Cases')),
          template='plotly_white'
      ))
      fig.add_trace(go.Scatter(x=df_disease['Date'],
                              y=df_disease['Cases'],
                              mode='lines',
                              name='Cases',
                              hovertemplate='Date: %{x}<br>Cases: %{y}'))
      plot_html_1 = fig.to_html(full_html=False, include_plotlyjs='cdn')

      fig = go.Figure(layout=go.Layout(
          title=go.layout.Title(text=f'{disease}({diseases_order_cn[i]})'),
          xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
          yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Cases')),
          template='plotly_white'
      ))
      fig.add_trace(go.Scatter(x=df_disease['Date'],
                              y=df_disease['Deaths'],
                              mode='lines',
                              name='Deaths',
                              hovertemplate='Date: %{x}<br>Deaths: %{y}'))
      plot_html_2 = fig.to_html(full_html=False, include_plotlyjs='cdn')

      fig = go.Figure(layout=go.Layout(
          title=go.layout.Title(text=f'{disease}({diseases_order_cn[i]})'),
          xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
          yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Cases')),
          template='plotly_white'
      ))
      fig.add_trace(go.Scatter(x=df_disease['Date'],
                              y=df_disease['Deaths'] / df_disease['Cases'],
                              mode='lines',
                              name='Ratio',
                              hovertemplate='Date: %{x}<br>Ratio: %{y}'))
      plot_html_3 = fig.to_html(full_html=False, include_plotlyjs='cdn')

      ## read the analysis of the disease
      body_main = ""
      body_info = ""
      
      main_file_path = f'../Report/history/latest/{disease}.md'
      info_file_path = f'../Report/information/{disease}.md'
      
      if os.path.isfile(main_file_path):
          with open(main_file_path, "r") as main_file:
              body_main = main_file.read().replace('\n\n', '<br>')
      
      if os.path.isfile(info_file_path):
          with open(info_file_path, "r") as info_file:
              body_info = info_file.read().replace('\n\n', '<br>')


      template = Template(template_content)
      rendered_html = template.render(plot_html_1=plot_html_1,
                                      plot_html_2=plot_html_2,
                                      plot_html_3=plot_html_3,
                                      select_div=div_element,
                                      disease=disease,
                                      body_main=body_main,
                                      body_info=body_info,
                                      disease_cn=diseases_order_cn[i])

      # 将渲染后的HTML内容保存到文件
      with open(f'../Pages/{disease_index[i]}.html', 'w') as f:
          f.write(rendered_html)
