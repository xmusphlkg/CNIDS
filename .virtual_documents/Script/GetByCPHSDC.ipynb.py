## read data from CPHSDC
import pandas as pd
import requests
import os
import glob
import datetime
import xml.etree.ElementTree as ET
import json
import sys
import multiprocessing

os.chdir("../GetData")


## get avaliable years
response = requests.get("https://www.phsciencedata.cn/Share/getQuerystart/")

if response.status_code == 200:
    data = json.loads(response.content)
    code_list = [item['code'] for item in data]
    years = code_list
    print("CPHSDC 访问成功")
else:
    print("CPHSDC 访问失败")
    sys.exit()

## download data from CPHSDC
months = range(1, 13)
Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
diseaseRawIds = range(1, 1000)

## find avaliable diseaseIds
# diseaseIds = []
# for diseaseId in diseaseRawIds:
#     response = requests.get(f"https://www.phsciencedata.cn/Share/frameset?__report=ReportZoneYear.rptdesign&__title=&__showtitle=false&__toolbar=true&__navigationbar=true&&__format=xls&__locale=zh_CN&__clean=true&__filename=占位符&years=2019&diseaseId={diseaseId}&&__dpi=96&__asattachment=true&__overwrite=false")
#     ## check request size 大于6kb的才是有效的
#     if response.status_code == 200:
#         data = response.content
#         if len(data) > 6000:
#             diseaseIds.append(diseaseId)
# with open('../Script/CPHSDC.txt', 'w') as f:
#         f.write(str(diseaseIds))
# 转换省份名称到英文
provinceName2Code = {
    '全国': 'Total',
    '北京': 'Beijing',
    '天津': 'Tianjin',
    '河北': 'Hebei',
    '山西': 'Shanxi',
    '山东': 'Shandong',
    '内蒙古': 'Inner Mongolia',
    '辽宁': 'Liaoning',
    '吉林': 'Jilin',
    '黑龙江': 'Heilongjiang',
    '上海': 'Shanghai',
    '江苏': 'Jiangsu',
    '浙江': 'Zhejiang',
    '安徽': 'Anhui',
    '福建': 'Fujian',
    '江西': 'Jiangxi',
    '山东': 'Shandong',
    '河南': 'Henan',
    '湖北': 'Hubei',
    '湖南': 'Hunan',
    '广东': 'Guangdong',
    '广西': 'Guangxi',
    '海南': 'Hainan',
    '重庆': 'Chongqing',
    '四川': 'Sichuan',
    '贵州': 'Guizhou',
    '云南': 'Yunnan',
    '西藏': 'Tibet',
    '陕西': 'Shaanxi',
    '甘肃': 'Gansu',
    '青海': 'Qinghai',
    '宁夏': 'Ningxia',
    '新疆': 'Xinjiang',
    '台湾': 'Taiwan',
    '香港': 'Hong Kong',
    '澳门': 'Macao'
    }

# 转换省份到邮政编码
provinceName2ADCode = {
    '全国': '100000',
    '北京': '110000',
    '天津': '120000',
    '河北': '130000',
    '山西': '140000',
    '内蒙古': '150000',
    '辽宁': '210000',
    '吉林': '220000',
    '黑龙江': '230000',
    '上海': '310000',
    '江苏': '320000',
    '浙江': '330000',
    '安徽': '340000',
    '福建': '350000',
    '江西': '360000',
    '山东': '370000',
    '河南': '410000',
    '湖北': '420000',
    '湖南': '430000',
    '广东': '440000',
    '广西': '450000',
    '海南': '460000',
    '重庆': '500000',
    '四川': '510000',
    '贵州': '520000',
    '云南': '530000',
    '西藏': '540000',
    '陕西': '610000',
    '甘肃': '620000',
    '青海': '630000',
    '宁夏': '640000',
    '新疆': '650000',
    '台湾': '710000',
    '香港': '810000',
    '澳门': '820000'
}

## 转换疾病名称到英文
diseaseName2Code = {
    '鼠疫': 'Plague',
    '霍乱': 'Cholera',
    '痢疾': 'Dysentery',
    '细菌性痢疾': 'Bacterial dysentery',
    '阿米巴痢疾': 'Amoebic dysentery',
    '伤寒': 'Typhoid',
    '副伤寒': 'Paratyphoid',
    '伤寒和副伤寒': 'Typhoid fever and paratyphoid fever',
    '艾滋病': 'Acquired immune deficiency syndrome',
    'ＨＩＶ': 'HIV',
    '淋病': 'Gonorrhea',
    '梅毒': 'Syphilis',
    'Ⅲ期梅毒': 'Tertiary syphilis',
    'Ⅱ期梅毒': 'Secondary syphilis',
    'Ⅰ期梅毒': 'Primary syphilis',
    '胎传梅毒': 'Congenital syphilis',
    '隐性梅毒': 'Latent syphilis',
    '疟疾': 'Malaria',
    '麻疹': 'Measles',
    '百日咳': 'Pertussis',
    '流脑': 'Meningococcal meningitis',
    '猩红热': 'Scarlet fever',
    '出血热': 'Epidemic hemorrhagic fever',
    '狂犬病': 'Rabies',
    '钩体病': 'Leptospirosis',
    '布病': 'Brucellosis',
    '炭疽': 'Anthrax',
    '新生儿破伤风': 'Neonatal tetanus',
    '斑疹伤寒': 'Typhus',
    '黑热病': 'Kala azar',
    '恶性疟': 'Malignant malaria',
    '间日疟': 'Tertian malaria',
    '疟疾（未分型）': 'Malaria (unclassified)',
    '乙脑': 'Japanese encephalitis',
    '登革热': 'Dengue',
    '肺结核': 'Tuberculosis',
    '利福平耐药': 'Tuberculosis (rifampicin-resistant)',
    '无病原学结果': 'Tuberculosis (unclassified)',
    '病原学阳性': 'Tuberculosis (positive)',
    '病原学阴性': 'Tuberculosis (negative)',
    '血吸虫病': 'Schistosomiasis',
    '包虫病': 'Echinococcosis',
    '麻风病': 'Leprosy',
    '流行性感冒': 'Influenza',
    '流行性腮腺炎': 'Mumps',
    '风疹': 'Rubella',
    '非淋菌性尿道炎': 'Nongonococcal urethritis',
    '其它感染性腹泻病': 'Infectious diarrhea',
    '急性出血性结膜炎': 'Acute hemorrhagic conjunctivitis',
    '尖锐湿疣': 'Condyloma acuminatum',
    '生殖器疱疹': 'Genital herpes',
    '手足口病': 'Hand foot and mouth disease',
    '皮肤炭疽': 'Cutaneous anthrax',
    '其它': 'Other',
    '甲肝': 'Hepatitis A',
    '乙肝': 'Hepatitis B',
    '丙肝': 'Hepatitis C',
    '丁肝': 'Hepatitis D',
    '戊肝': 'Hepatitis E',
    '肝炎（未分型）': 'Other hepatitis',
    '肝炎': 'Hepatitis',
    '水痘': 'Chickenpox',
    '人感染猪链球菌': 'Streptococcus suis',
    '生殖道沙眼衣原体感染': 'Chlamydia trachomatis',
    '肝吸虫病': 'Fascioliasis',
    '恙虫病': 'Typhus',
    '脊灰': 'Poliomyelitis',
    '白喉': 'Diphtheria',
    '非典临床诊断': 'SARS-CoV'
}


diseaseIds = [3, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 40, 45, 120, 121, 122, 123, 124, 125, 126, 127, 128, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 147, 160, 198, 199, 200, 201, 204, 205, 206, 220, 240, 241, 243, 318, 319, 320, 321, 322, 323, 324, 346, 347, 366, 367, 368]


need_update = False # 是否需要更新数据
# diseaseIds = [21] # 脊髓灰质炎
# diseaseIds = [24] # 白喉
# diseaseIds = [45] # SARS
diseaseIds = [136] # 丝虫病

for diseaseId in diseaseIds:
    for year in years:
        for month in months:
            Month = Months[month - 1]        
            file_name = f"{year} {Month} {diseaseId}.xls"
            file_path = os.path.join("DatacenterReport", file_name)

            if os.path.exists(file_path):
                continue

            url = f"https://www.phsciencedata.cn/Share/frameset?__report=ReportZoneMonth.rptdesign&__title=&__showtitle=false&__toolbar=true&__navigationbar=true&&__format=xls&__locale=zh_CN&__clean=true&__filename=get_ipython().run_line_magic("E5%8D%A0%E4%BD%8D%E7%AC%A6&years={year}&diseaseId={diseaseId}&months={month}&&__dpi=96&__asattachment=true&__overwrite=false"", "")
            r = requests.get(url)        
            if r.status_code == 200:
                with open(file_path, "wb") as code:
                    code.write(r.content)
                print(f"文件下载成功：{file_path}")
                need_update = True # 有新数据需要更新
                # time.sleep(random.uniform(3, 5))
            else:
                print(f"访问失败：{url}")


need_update = True


# 定义文件夹路径
folder_path = 'DatacenterReport'

# 获取文件夹中所有的 XLS 文件
xls_files = glob.glob(os.path.join(folder_path, '*.xls'))
# 升序排列
xls_files.sort()
# xls_files = "DatacenterReport/2018 September 243.xls"

if need_update:    
    # 创建进程池，使用多个进程进行并行处理
    with multiprocessing.Pool(60) as pool:
        # 遍历文件夹中所有的 XLS 文件
        for xls_file in xls_files:
        # for xls_file in xls_files:
            # 判断文件大小，小于6kb则结束本轮循环
            if os.path.getsize(xls_file) < 6 * 1024:
                continue
            else:
                # 根据文件名获取年月
                file_name = os.path.basename(xls_file)
                YearMonth = file_name.split(' ')[0] + " " + file_name.split(' ')[1]
                # 转为日期格式
                date_obj = datetime.datetime.strptime(YearMonth, 'get_ipython().run_line_magic("Y", " %B')")
                # 转为字符串格式     
                formatted_date = date_obj.strftime("get_ipython().run_line_magic("Y/%m/%d")", "")
                # 读取 XLS 文件
                tree = ET.parse(xls_file)
                root = tree.getroot()

                # 创建一个空的DataFrame对象
                data = pd.DataFrame()

                # 遍历Worksheet元素
                for worksheet in root.iter('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):
                    # 创建一个空的列表，用于存储每个单元格的数据
                    worksheet_data = []

                    # 遍历Table元素
                    table = worksheet.find('{urn:schemas-microsoft-com:office:spreadsheet}Table')

                    # 跳过前2行
                    row_counter = 0
                    for row in table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
                        if row_counter < 1:
                            row_counter += 1
                            continue

                        # 创建一个空的字典，用于存储每个单元格的数据
                        row_data = {}

                        # 遍历Cell元素
                        for cell in row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell'):
                            # 获取Cell的数据
                            data_elem = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
                            cell_data = data_elem.text if data_elem is not None else ''
                            cell_data = cell_data.replace(' ', '').replace('省', '').replace('市', '').replace('\t', '')

                            # 将单元格数据添加到字典中
                            row_data[cell.attrib.get('{urn:schemas-microsoft-com:office:spreadsheet}Index', '')] = cell_data

                        # 将每行数据添加到列表中
                        worksheet_data.append(row_data)

                    # 删除最后一行的数据
                    if worksheet_data:
                        worksheet_data.pop()

                    # 将每个Worksheet的数据转换为DataFrame，并将其添加到总的数据中
                    df = pd.DataFrame(worksheet_data)
                    df = df.iloc[:, 1:]  # 删除第一列
                    # 将列名转换为数值，并按照升序排列
                    df.columns = pd.to_numeric(df.columns, errors='coerce')
                    df = df.sort_index(axis=1)
                    # 第一行空值填充
                    df.iloc[0, :] = df.iloc[0, :].fillna(method='ffill')

                    # 获取第一行的unique值，并去除""
                    diseases = df.iloc[0, :].unique()
                    diseases = diseases[diseases get_ipython().getoutput("= '']")
                    # print(diseases, xls_file)
                    # 使用for循环按照第一行的unique值，将数据分割成多个DataFrame
                    for disease in diseases:
                        # 获取每个疾病的数据
                        # print(disease)
                        # 第一行为疾病名称或者""
                        df_disease = df.loc[:, (df.iloc[0, :] == disease) | (df.iloc[0, :] == '')]
                        # 删除第一行
                        df_disease = df_disease.iloc[1:, :]
                        # 删除空值的列
                        df_disease = df_disease.dropna(axis=1, how='all')
                        # 删除空值的行
                        df_disease = df_disease.dropna(axis=0, how='all')
                        # 将第一行的数据作为列名
                        df_disease.columns = df_disease.iloc[0, :]
                        # 删除第一行
                        df_disease = df_disease.iloc[1:, :]
                        # 将年月作为一列
                        df_disease['Date'] = date_obj.strftime("get_ipython().run_line_magic("Y-%m-%d", " %H:%M:%S\")")
                        df_disease['YearMonthDay'] = formatted_date
                        df_disease['YearMonth'] = YearMonth
                        # 将疾病名称作为一列
                        df_disease['Diseases'] = disease
                        df_disease = df_disease.reset_index(drop=True)
                        # 将疾病数据添加到总的数据中
                        data = data.append(df_disease)
                # 修改列名 地区 -> Province，发病数 -> Cases，死亡数 -> Deaths, 发病率(1/10万) -> Incidence, 死亡率(1/10万) -> Mortality
                data = data.rename(columns={'地区': 'ProvinceCN', '发病数': 'Cases', '死亡数': 'Deaths', '发病率(1/10万)': 'Incidence', '死亡率(1/10万)': 'Mortality'})
                # print(data['ProvinceCN'])
                # 将省份名称转换为英文
                data['Province'] = data['ProvinceCN'].replace(provinceName2Code)
                # 将省份名称转换为邮政编码
                data['ADCode'] = data['ProvinceCN'].replace(provinceName2ADCode)
                # 将疾病名称转换为英文
                data['DiseasesCN'] = data['Diseases']
                data['Diseases'] = data['Diseases'].replace(diseaseName2Code)
                # 增加DOI
                data['DOI'] = ''
                # 增加数据来源
                data['URL'] = 'https://www.phsciencedata.cn/Share/ky_sjml.jsp'
                data['Source'] = 'The Data-center of China Public Health Science'
                # 重新排列列的顺序
                data = data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

                # 将数据保存为UTF-8编码的CSV文件
                output_file = os.path.splitext(xls_file)[0] + '.csv'
                data.to_csv(output_file, index=False, encoding='utf-8', header=True)


# 获取文件夹中所有的 csv 文件
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# 读取所有文件
data = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

# 删除重复数据
data = data.drop_duplicates()

# 读取CDC weekly list
cdc_weekly_list = pd.read_csv('../GetData/reportdata/All_data_last.csv')
diseases = cdc_weekly_list['Diseases'].unique()

# 筛选data为diseases中的疾病
data = data[data['Diseases'].isin(diseases)]


# in diseases and not in data
list(set(diseases) - set(data['Diseases'].unique()))


list(set(data['Diseases'].unique()) - set(diseases))
