import os
import datetime
import pandas as pd
import xml.etree.ElementTree as ET

def process_files(xls_files, provinceName2Code, provinceName2ADCode, diseaseName2Code):
    '''
    Process xls files

    Args:
        xls_files (list): list of xls files
        provinceName2Code (dict): dictionary of province name to province code
        provinceName2ADCode (dict): dictionary of province name to AD code
        diseaseName2Code (dict): dictionary of disease name to disease code
    Raises:
        None
    Returns:
        None
    '''
    for xls_file in xls_files:
        if os.path.getsize(xls_file) < 6 * 1024:
            continue
        else:
            file_name = os.path.basename(xls_file)
            YearMonth = file_name.split(' ')[0] + " " + file_name.split(' ')[1]
            date_obj = datetime.datetime.strptime(YearMonth, '%Y %B')
            formatted_date = date_obj.strftime("%Y/%m/%d")
            tree = ET.parse(xls_file)
            root = tree.getroot()

            data = pd.DataFrame()

            for worksheet in root.iter('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):
                worksheet_data = []
                table = worksheet.find('{urn:schemas-microsoft-com:office:spreadsheet}Table')

                row_counter = 0
                for row in table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
                    if row_counter < 1:
                        row_counter += 1
                        continue

                    row_data = {}

                    for cell in row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell'):
                        data_elem = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
                        cell_data = data_elem.text if data_elem is not None else ''
                        cell_data = cell_data.replace(' ', '').replace('省', '').replace('市', '').replace('\t', '')
                        row_data[cell.attrib.get('{urn:schemas-microsoft-com:office:spreadsheet}Index', '')] = cell_data

                    worksheet_data.append(row_data)

                if worksheet_data:
                    worksheet_data.pop()

                df = pd.DataFrame(worksheet_data)
                df = df.iloc[:, 1:]
                df.columns = pd.to_numeric(df.columns, errors='coerce')
                df = df.sort_index(axis=1)
                df.iloc[0, :] = df.iloc[0, :].fillna(method='ffill')

                diseases = df.iloc[0, :].unique()
                diseases = diseases[diseases != '']

                for disease in diseases:
                    df_disease = df.loc[:, (df.iloc[0, :] == disease) | (df.iloc[0, :] == '')]
                    df_disease = df_disease.iloc[1:, :]
                    df_disease = df_disease.dropna(axis=1, how='all')
                    df_disease = df_disease.dropna(axis=0, how='all')
                    df_disease.columns = df_disease.iloc[0, :]
                    df_disease = df_disease.iloc[1:, :]
                    df_disease['Date'] = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    df_disease['YearMonthDay'] = formatted_date
                    df_disease['YearMonth'] = YearMonth
                    df_disease['Diseases'] = disease
                    df_disease = df_disease.reset_index(drop=True)
                    data = data.append(df_disease)

            data = data.rename(columns={'地区': 'ProvinceCN', '发病数': 'Cases', '死亡数': 'Deaths', '发病率(1/10万)': 'Incidence', '死亡率(1/10万)': 'Mortality'})
            data['Province'] = data['ProvinceCN'].replace(provinceName2Code)
            data['ADCode'] = data['ProvinceCN'].replace(provinceName2ADCode)
            data['DiseasesCN'] = data['Diseases']
            data['Diseases'] = data['Diseases'].replace(diseaseName2Code)
            data['DOI'] = 'missing'
            data['URL'] = 'https://www.phsciencedata.cn/Share/ky_sjml.jsp'
            data['Source'] = 'The Data-center of China Public Health Science'
            data = data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

            diseases = data['Diseases'].unique()
            diseases = [disease.title() for disease in diseases]

            if len(diseases) != 1:
                combined_string = ' '.join(disease.title() for disease in diseases)
                words = set(combined_string.split())
                common_words = [word for word in words if all(word in disease for disease in diseases)]
                diseases_name = ' '.join(common_words)
            else:
                diseases_name = str(diseases[0])

            if 'Typhoid' in diseases and len(diseases) != 1:
                diseases_name = 'Typhoid Fever And Paratyphoid Fever'

            if 'Hiv' in diseases and len(diseases) != 1:
                diseases_name = 'AIDS And HIV'

            if not os.path.exists('..' + '/CleanData/DatacenterReport/' + diseases_name):
                print(diseases_name)
                os.makedirs('..' + '/CleanData/DatacenterReport/' + diseases_name)

            output_file = '..' + '/CleanData/DatacenterReport/' + diseases_name + '/' + YearMonth + '.csv'
            data.to_csv(output_file, index=False, encoding='utf-8', header=True)

# calculate the case and death of Hepatitis D
def calculate_HD(csv_files, folder_path):
    '''
    Calculate the case and death of Hepatitis D

    Args:
        xls_files (list): list of xls files
        folder_path (str): folder path
    Raises:
        None
    Returns:
        None
    '''
    for file in csv_files:
        # read csv file
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)

        # create a new dataframe
        merged_data = pd.DataFrame()

        # get unique Province
        Province_unique = data['Province'].unique()

        # calculate the case and death of Hepatitis D
        for Province in Province_unique:
            # filter data by Province
            Province_data = data[data['Province'] == Province]

            # calculate the case and death of Hepatitis D
            Hepatitis_data = Province_data[Province_data['Diseases'] == 'Hepatitis']
            Not_Hepatitis_data = Province_data[Province_data['Diseases'] != 'Hepatitis']
            Hepatitis_D_Cases = Hepatitis_data['Cases'] - Not_Hepatitis_data['Cases'].sum()
            Hepatitis_D_Deaths = Hepatitis_data['Deaths'] - Not_Hepatitis_data['Deaths'].sum()

            # add Hepatitis D data to Province_data
            new_row = {
                'Date': Hepatitis_data['Date'].iloc[0],
                'YearMonthDay': Hepatitis_data['YearMonthDay'].iloc[0],
                'YearMonth': Hepatitis_data['YearMonth'].iloc[0],
                'Diseases': 'Hepatitis D',
                'DiseasesCN': '丁肝',
                'Cases': Hepatitis_D_Cases.iloc[0],
                'Deaths': Hepatitis_D_Deaths.iloc[0],
                'Incidence': -10,
                'Mortality': -10,
                'ProvinceCN': Province_data['ProvinceCN'].iloc[0],
                'Province': Province_data['Province'].iloc[0],
                'ADCode': Province_data['ADCode'].iloc[0],
                'DOI': Province_data['DOI'].iloc[0],
                'URL': Province_data['URL'].iloc[0],
                'Source': Province_data['Source'].iloc[0]
            }
            Province_data = Province_data.append(new_row, ignore_index=True)

            # combine data
            merged_data = merged_data.append(Province_data, ignore_index=True)

        # save data
        merged_file_name = os.path.join(folder_path, file)
        merged_data.to_csv(merged_file_name, index=False, encoding="UTF-8-sig")

        # save Hepatitis D data
        Hepatitis_D_data = merged_data[(merged_data['Diseases'] == 'Hepatitis D')]
        file_name = os.path.join('../CleanData/DatacenterReport/Hepatitis D', file)
        Hepatitis_D_data.to_csv(file_name, index=False, encoding="UTF-8-sig")