## Introduction

**CNIDs: Chinese Notifiable Infectious Diseases Sensing Project**

CNIDs is a project aimed at monitoring and sensing legally notifiable infectious diseases in mainland China. The project utilizes automated technology and data analysis methods to enhance the monitoring and early warning capabilities for infectious diseases, enabling timely measures to be taken to address potential public health risks.

The primary objective of the CNIDs project is to establish an efficient infectious disease sensing system that enables real-time monitoring and prediction of legally notifiable infectious diseases. The system leverages advanced technologies, including artificial intelligence, machine learning, and big data analytics, to rapidly identify and track outbreaks and transmission trends of infectious diseases. It provides decision-makers with timely information and recommendations to facilitate appropriate measures for disease control and prevention.

## Usage Example

### **Data Sharing**

1. [`GetData`](./Data/GetData): All original files automatically crawled by the program.
2. [`CleanData`](./Data/CleanData): Cleaned data files, available for download as needed.
3. [`AllData`](./Data/AllData): Structured merged file for data analysis.

### **Dynamic Sensing**

1. After data updates, use ChatGPT-3.5 to automatically generate [reports](./Report).
2. After report generation, ChatGPT-3.5 automatically generates email content (including data update information and important highlights), sends email notifications to subscribed users, and attaches the report as an attachment.

[Subscribe|Unsubscribe](https://forms.office.com/r/V6vH7rRfeq)

### **Dashboard Session**

1. Shiny Dashboard automatically reads the latest report data and presents it interactively.

[CNIDs (EN)](https://lkg1116.shinyapps.io/CNIDs/)

[CNIDs (EN & CN)](https://xmusphlkg.github.io/CNID/)

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
2. Set up Actions secrets and variables.
3. Run Github Action.


## Notice

1. Monthly NID Report Cases Data of 2013.4 and 2013.8 may be unreliable, because images are not clear enough to recognize.

2. Monthly NID Report Cases Data of 2013.1 and 2013.2 may be unreliable, because image of website is not available.
## Update Log

### China CDC Monthly Report


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