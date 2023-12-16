## Introduction

**CNIDS: Chinese Notifiable Infectious Diseases Surveillance Project**

CNIDS is a project aimed at monitoring notifiable infectious diseases in mainland China. The project utilizes automated technology and data analysis methods to enhance the monitoring and early warning capabilities for infectious diseases, enabling timely measures to be taken to address potential public health risks.

The primary objective of the CNIDS project is to establish an efficient infectious disease Surveillance system that enables real-time monitoring and prediction of legally notifiable infectious diseases. It provides decision-makers with timely information and recommendations to facilitate appropriate measures for disease control and prevention.

## Usage Example

### **Data Sharing**

1. [`GetData`](./Data/GetData): All original files automatically crawled by the program.
2. [`CleanData`](./Data/CleanData): Cleaned data files, available for download as needed.
3. [`AllData`](./Data/AllData): Structured merged file for data analysis.

### **Dynamic Surveillance**

1. After data updates, use ChatGPT-3.5 to automatically generate [reports](./Report).
2. After report generation, ChatGPT-3.5 automatically generates email content (including data update information and important highlights), sends email notifications to subscribed users, and attaches the report as an attachment.

[Subscribe|Unsubscribe](https://forms.office.com/r/V6vH7rRfeq)

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

  b. Microsoft Graph Settings:

   `MS_client_id`: Microsoft Graph client id.

   `MS_client_secret`: Microsoft Graph client secret.

   `MS_sender_email`: Microsoft Graph sender email.

   `MS_subscribe`: Microsoft OneDrive file share link.

   `MS_tenant_id`: Microsoft Graph tenant id.

    > You can get the above information by registering an application in [Azure Active Directory](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).

  c. OpenAI Settings:

   `OPENAI_api`: OpenAI API key.

   `OPENAI_url`: OpenAI API url.

    > You can get the above information by registering an application in [OpenAI](https://beta.openai.com/).
    > example: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxx`and `https://api.openai.com/v1/chat/completions`

3. Set up Actions variables.

  a. `test`: Whether to test getting data from the China CDC Monthly Report. Default: `False`.

  b. `test_analysis`: Whether to test the analysis program, if `True` only create report for two disease. Default: `False`.

  c. `cite`: Citation information. Default: `Cite Us: CNIDs: Chinese Notifiable Infectious Diseases Surveillance Project. <u><a href='https://github.com/xmusphlkg/CNID'>Github</a></u>'

  d. `test_dc`: Whether to test getting data from the Public Health Scientific Data Center. Default: `False`.

  e. `test_mail`: Whether to display the test content in email. Default: `True`.

  f. `send_mail`: Whether to send email. Default: `True`.

  g. `update_info`: Whether to display the update information of each disease in the repository. Default: `False`.

4. Run Github Action.

## Notice

1. Monthly NID Report Cases Data of 2013.4 and 2013.8 may be unreliable, because images are not clear enough to recognize.

2. Monthly NID Report Cases Data of 2013.1 and 2013.2 may be unreliable, because image of website is not available.

## Update Log

### China CDC Monthly Report

#### 2023 October

Date: 20231216

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

#### 2019

Date: 20230928

Updated: ['2019']

#### 2023 April

Date: 20230906

Updated: Initial
