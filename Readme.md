
# Project Discontinuation Notice

This project is no longer being updated. We have transitioned to a new platform to continue our efforts more focused and comprehensively.

Please visit our new project at [Global Infectious Disease](https://globalinfectiousdisease.com/CN/) for the latest updates and more information.

Thank you for your support and understanding.


## Introduction

**CNIDS: Chinese Notifiable Infectious Diseases Surveillance Project**

CNIDS is a project aimed at monitoring notifiable infectious diseases in Chinese mainland. The project utilizes automated technology and data analysis methods to enhance the monitoring and early warning capabilities for infectious diseases, enabling timely measures to be taken to address potential public health risks.

The primary objective of the CNIDS project is to establish an efficient infectious disease Surveillance system that enables real-time monitoring and prediction of legally notifiable infectious diseases. It provides decision-makers with timely information and recommendations to facilitate appropriate measures for disease control and prevention.

Subscribe e-mail to receive the latest report: [Subscribe](https://forms.office.com/r/EJUEfKkttK)

## Usage Example

### **Data Sharing**

1. [`GetData`](./Data/GetData): All original files automatically crawled by the program.
2. [`CleanData`](./Data/CleanData): Cleaned data files, available for download as needed.
3. [`AllData`](./Data/AllData): Structured merged file for data analysis.

### **Dynamic Surveillance**

1. After data updates, use AI to automatically generate [reports](./Report).
2. After report generation, AI automatically generates email content (including data update information and important highlights), sends email notifications to subscribed users, and attaches the report as an attachment.

### **Dashboard Session**

1. Shiny Dashboard automatically reads the latest report data and presents it interactively.

[CNIDS (EN)](https://lkg1116.shinyapps.io/CNIDS/)

[CNIDS (EN & CN)](https://xmusphlkg.github.io/CNID/)

2. It also supports local Docker deployment.

Get the latest image:

```
docker push kanggle/cnids:latest
```

Run the image:

```
docker run -d -p 3838:3838 kanggle/cnids:latest
```

Open the browser and enter the address:

```
http://localhost:3838
```

## **Local Deployment**

1. Fork this directory.

2. Set up Actions secrets.

a. Docker Hub Settings:

`DOCKERHUB_TOKEN`: Docker Hub token.
`DOCKERHUB_USERNAME`: Docker Hub username.

b. SMTP Settings:

`smtp_sender`: Email address of the sender.
`smtp_password`: Email password of the sender.
`smtp_server_url`: Email server url.
`smtp_server_port`: Email server port.

c. OpenAI Settings:

`OPENAI_API_KEY`: OpenAI API key (sk-xxxxxxxx).

`OPENAI_API_BASE`: OpenAI API url (https://api.openai.com/v1).

    > You can get the above information by registering an application in [OpenAI](https://beta.openai.com/).
    > example: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxx`and `https://api.openai.com/v1`.

d. OneDrive Settings:

`onedrive_url`: OneDrive share file url which contains subscriber list.

3. Set up Actions variables.

a. `test`: Whether to test getting data from the China CDC Monthly Report. Default: `False`.

b. `cite`: Citation information. Default: `Cite Us: CNIDs: Chinese Notifiable Infectious Diseases Surveillance Project. <u><a href='https://github.com/xmusphlkg/CNIDS'>Github</a></u>'

c. `test_dc`: Whether to test getting data from the Public Health Scientific Data Center. Default: `False`.

d. `test_mail`: Whether to display the test content in email. Default: `True`.

e. `send_mail`: Whether to send email. Default: `True`.

4. Set up config file (optional).

a. [`config.yml`](./config.yml): Configuration file for data source and AI models.

5. Run Github Action.

## Notice

1. Monthly NID Report Cases Data of 2013.4 and 2013.8 may be unreliable, because images are not clear enough to recognize.

2. Monthly NID Report Cases Data of 2013.1 and 2013.2 may be unreliable, because image of website is not available.

## Update Log

### China CDC Monthly Report

#### 2024 April

Date: 20240531

Updated: ['2024 April']



#### 2024 March

Date: 20240424

Updated: ['2024 March']



#### 2024 February

Date: 20240320

Updated: ['2024 February']



#### 2024 January

Date: 20240304

Updated: ['2024 January']

#### 2023 December

Date: 20240116

Updated: ['2023 December']

#### 2023 November

Date: 20240107

Updated: ['2023 November']

#### 2023 October

Date: 20231224

Updated: ['2023 October']

#### 2023 September

Date: 20231116

Updated: ['2023 September']

#### 2023 August

Date: 20231025

Updated: ['2023 August']

#### 2023 July

Date: 20230929

Updated: ['2023 May']

#### 2023 July

Date: 20230929

Updated: ['2023 June']

#### 2023 July

Date: 20230929

Updated: ['2023 July', '2023 June']

#### 2023 April

Date: 20230928

Updated: ['2023 March']

#### 2023 April

Date: 20230906

Updated: Initial

### Public Health Scientific Data Center

#### 2020

Date: 20240116

Updated: ['2020']

#### 2019

Date: 20230928

Updated: ['2019']

#### 2023 April

Date: 20230906

Updated: Initial
