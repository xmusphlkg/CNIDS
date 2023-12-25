import plotly.graph_objects as go

def update_pages(diseases_order, diseases_order_cn, disease_index, df, analysis_MonthYear):
  disease = diseases_order[disease_index]
  # read page history
  with open(f'../Report/history/latest/{disease}.md', 'r', encoding='utf-8') as f:
      page_history = f.read()

  # create plotly figure
  df_disease = df[df['Diseases'] == disease]
  df_disease = df_disease.sort_values('Date')

  fig = go.Figure(layout=go.Layout(
      title=go.layout.Title(text=f'{disease}({diseases_order_cn[disease_index]})'),
      xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
      yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Cases')),
      template='plotly_white'
  ))
  fig.add_trace(go.Scatter(x=df_disease['Date'],
                          y=df_disease['Cases'],
                          mode='lines',
                          name=disease,
                          hovertemplate='Date: %{x}<br>Cases: %{y}'))
  plot_html_1 = fig.to_html(full_html=False, include_plotlyjs='cdn')

  fig = go.Figure(layout=go.Layout(
      title=go.layout.Title(text=f'{disease}({diseases_order_cn[disease_index]})'),
      xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
      yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Deaths')),
      template='plotly_white'
  ))
  fig.add_trace(go.Scatter(x=df_disease['Date'],
                          y=df_disease['Deaths'],
                          mode='lines',
                          name=disease,
                          hovertemplate='Date: %{x}<br>Deaths: %{y}'))
  plot_html_2 = fig.to_html(full_html=False, include_plotlyjs='cdn')

  # insert plotly figure into docs
  page_history = page_history.replace('### Cases Analysis', f'### Cases Analysis\n\n{plot_html_1}')
  page_history = page_history.replace('### Deaths Analysis', f'### Deaths Analysis\n\n{plot_html_2}')
  page_history = f"# {disease} \n\nVersion: {analysis_MonthYear} \n\n" + page_history
  with open(f'../docs/{disease}.md', 'w', encoding='utf-8') as f:
      f.write(page_history)
