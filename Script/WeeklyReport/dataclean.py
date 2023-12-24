import pandas as pd
from plotnine import *

def calculate_change_data(df, analysis_date):
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
    change_data = pd.merge(latest_data_1, latest_data_2, on=['Diseases', 'DiseasesCN'], how='left')
    change_data = pd.merge(change_data, latest_data_3, on=['Diseases', 'DiseasesCN'], how='left')

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
    
    return change_data

def format_table_data(table_data, analysis_date):
    # 复制数据
    table_data = table_data.copy()
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
    table_data = table_data.replace('nan', '/')
    table_data = table_data.replace('inf%', '/')
    
    # select columns
    table_data = table_data[['Diseases',
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
    
    # setting column names
    table_data.columns = ['Diseases',
                          'Cases', 
                          'Comparison with ' + compare_PM, 
                          'Comparison with ' + compare_PY, 
                          'Deaths', 
                          'Comparison with ' + compare_PM, 
                          'Comparison with ' + compare_PY]
    
    # add total row
    table_data = table_data.loc[table_data.index[1:].tolist() + [table_data.index[0]]]
    
    return table_data

def generate_merge_chart(change_data, original_file):
    table_data_original = pd.read_csv(original_file, encoding='utf-8')
    diseases_order = table_data_original['Diseases'].tolist()
    change_data_total = change_data[(change_data['Diseases'] != "Total") & (change_data['Diseases'].isin(diseases_order))]
    change_data_total = change_data_total.sort_values(by='Diseases', key=lambda x: x.map(diseases_order.index))
    diseases = change_data_total['Diseases'].tolist()
    diseases_cn = change_data_total['DiseasesCN'].tolist()
    change_data_total = change_data_total.melt(id_vars=['Diseases', 'DiseasesCN'],
                                              value_vars=['Cases', 'Deaths'], 
                                              var_name='Type',
                                              value_name='Value')
    change_data_total = change_data_total.sort_values(by='Diseases', key=lambda x: x.map(diseases_order.index))

    # Generate plot for Cases
    plot_total = (
        ggplot(change_data_total, 
              aes(y='Value', x='reorder(Diseases, Value)', fill = 'Type')) +
        geom_bar(stat="identity", position="identity") +
        scale_y_continuous(limits = [0, None], expand = [0, 0, 0.2, 0]) +
        coord_flip() +
        theme_bw()+
        theme(legend_position='none')+
        facet_wrap('~Type', nrow=1, scales='free_x')+
        labs(x ='', y = '')
    )
    merged_chart_path = "temp/merged_chart.png"
    plot_total.save(merged_chart_path, dpi=300, width=10, height=10)

    return diseases, diseases_cn