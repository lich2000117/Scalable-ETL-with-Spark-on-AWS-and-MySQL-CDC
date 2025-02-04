# Project Overview

The ETL pipeline is built using `Spark` API for Python, `pyspark`.

Designed to prepare and ETL data for sales analysis and potential downstream machine learning applications.

It transforms raw data from CSV files into structured tables that support both operational reporting and analytical decision-making.

This document provides an overview of the data modeling involved in the ETL process for the sales analytics project. It explains the tables created, their data sources, the lineage of the data, and the purposes of each table.

## Key Points:

1. A working **DockerFile** that **can run pyspark code** (on linux, macos, windows), in folder `./usecase1_batch_pyspark/customer_invoice_etl/Dockerfile`
2. **PySpark** and **SparkSQL** ETL jobs, with a complete software **suite** (deployment, testing).
3. **CICD** for setting up AWS cloud compute, with **Terraform**
4. **Architecture** Diagram for **AWS** cloud deployment, such as **EMS, GLUE, S3, EC2, Cloud Function, Pubsub** (usecase2).
5. **CDC** usecases on **AWS**, **Aurora MySQL** database(usecase2).


## Table of Contents
- [Project Overview](#project-overview)
  - [Key Points:](#key-points)
  - [Table of Contents](#table-of-contents)
  - [How to run (usecase1)](#how-to-run-usecase1)
- [Design Choices and Scaling](#design-choices-and-scaling)
  - [Tech Stack](#tech-stack)
    - [Spark](#spark)
    - [Deployment: Bare-metal, using this docker image (not recommended, doable, but complexity is way too much)](#deployment-bare-metal-using-this-docker-image-not-recommended-doable-but-complexity-is-way-too-much)
  - [Alternative Method: DBT](#alternative-method-dbt)
- [Data Modeling Documentation](#data-modeling-documentation)
  - [Tables Structures and Description](#tables-structures-and-description)
  - [Data Lineage](#data-lineage)
  - [1. Intermediate Tables](#1-intermediate-tables)
    - [account\_details](#account_details)
    - [invoice\_details](#invoice_details)
  - [2. Fact Tables](#2-fact-tables)
    - [FactSales](#factsales)
    - [FactSalesProcessed (for ML applications)](#factsalesprocessed-for-ml-applications)
    - [MonthlySalesSummary](#monthlysalessummary)
- [System Design and Implementing CDC changes](#system-design-and-implementing-cdc-changes)
  - [Overview](#overview)
  - [Key points need to consider:](#key-points-need-to-consider)
  - [Data Source: AWS Aurora MySQL](#data-source-aws-aurora-mysql)
  - [Data Processing and Workflow Management](#data-processing-and-workflow-management)
    - [Deploying Spark on AWS EMR](#deploying-spark-on-aws-emr)
    - [EMR Cluster Setup:](#emr-cluster-setup)
    - [Job Triggering:](#job-triggering)
        - [Real-Time:](#real-time)
        - [Batch, Scheduled:](#batch-scheduled)
    - [Data Storage and Querying: AWS RedShift](#data-storage-and-querying-aws-redshift)
    - [Version Control(Time Travel):](#version-controltime-travel)
    - [Visualisation and Reporting: AWS QuickSight](#visualisation-and-reporting-aws-quicksight)
    - [CDC, Incremental and Real-Time Data Management Strategies](#cdc-incremental-and-real-time-data-management-strategies)
      - [Change Data Capture (CDC):](#change-data-capture-cdc)
      - [Data Append Strategy (Redshift Connector):](#data-append-strategy-redshift-connector)
  - [Conclusion](#conclusion)



## How to run (usecase1)

This task build a pyspark application using docker, the dockerfile has been provided, specifically for setting up a spark environment.
This part takes most of the time as configuring and testing docker images/setup could be time consuming and challenging.

1. build the docker container
   `cd ./customer_invoice_etl`
   `docker build -t customer-invoice-etl . --platform linux/amd64`
2. running the container and attach current wdr to docker as a volume (make sure this dir is shared to docker)
   `docker run -t --rm -v ./:/etl_app customer-invoice-etl`
3. check `./output/` for output tables.
4. configurations are defined in `./configs/config.yml` file, this involves some variables that can be tweaked based on analytic team's preferences.
5. Optional: One-liner run

```
   sudo docker build -t customer-invoice-etl . --platform linux/amd64 &&
   docker run -t --rm -v ./:/etl_app customer-invoice-etl
```

6. Jupyter Notebook Debug:

   1. Edit Dockerfile so jupyter notebook is active
   2. Execute command to start jupyter notebook

   ```
   sudo docker build -t customer-invoice-etl . --platform linux/amd64 &&                                 ─╯
   docker run -t --rm -v ./:/etl_app -p 8888:8888 customer-invoice-etl
   ```

   3. Access jupyter notebook `http://127.0.0.1:8888/lab` with token `token`



# Design Choices and Scaling

  Since this task one specifically requires the usage of spark engine, so I have containerised everything using docker.
  This is a one node configruation for simple testing. The data and project spec provided can be both setup as a batched scheduled job or as a real-time data ETL, which will be explained in task two.

  Here are my ideas/thoughts to implement them, and alternative way to achieve nearly the same thing, but using different tools.

## Tech Stack

- Docker
- Spark
- Python
- Terraform Demo (CI/CD)
- Parquet (Save format)

### Spark

- Spark is great for both batched jobs and streamed real-time jobs, so this project is very versatile and can be applied in both scenarios.
- The codebase have been divided into different components, folders, ensure a very organised style and best practices.
- **All transformations are written in SQL**, in `src/models/xxx.py` files, so DS, DA and other DE can easily work/edit/add those new tables in those file.
- Simple test cases have been provided to ensure the spark engine is running well inside docker environment.
- Added `configs` components so DA,DS,DE can easily edit the `yaml` file without diving into code, to make changes to exclude data, define new models, where to save etc (in cloud environment, this would be the project path and schema path for source tabels on specific cloud platform such as AWS redshift or Google Bigquery).
- Output has been saved as a parquet file. On cloud, parquet output can be saved to a S3 bucket, Google Cloud Storage.
- Spark uses in memory processing, so it is fast, but in return we need to ensure a large memory allocation can ensure job run successfully.

### Deployment: Bare-metal, using this docker image (not recommended, doable, but complexity is way too much)

This way, we can directly deploy this application I wrote, using docker image, to deploy on cloud compute engine, but it is not recommended, as AWS natively supports spark applications using EMS, it would be best to setup this job using EMS instead.

1. setup 1st docker image to host a driver node.
2. setup 2nd docker image to host a slave node.
3. use CICD pipeline to setup AWS EC2 compute instance, 1 uses driver docker image, others uses slave docker images.
4. use CICD pipeline to configure network connections so EC2 instances can communicate with each other.
5. trigger the run using CICD pipeline.

## Alternative Method: DBT

DBT is a data modelling tool based on sql, I have used in my career. It is very good for data modelling, table linkage, processing and applying SQL conditon. By setting up DBT connection to Redshift or Bigquery data warehouse, this would ensure a very simple setup and usage for other DAs.

1. all existing `intermediate` and `fact` spark sqls can be directly translated to DBT langauges.
2. use DBT model to define above code, so each model represents the generation of an `intermediate` or `fact` table.
3. setup DBT profile connections, so the DBT can connect directly to AWS Reshift/Databricks Delta Lake/Google Bigquery Datawarehouse, so they can directly use cloud tables as input, and output tables into relevant schemas.
4. use DBT variable to replace variables defined in `config.yml`
5. use DBT seed to incorporate any external csv file (google sheet)
6. use DBT test to replace unit testings, in DBT, if a test is successful, the sql result should be `Null`, without any return.
7. setting up cloud scheduled run (Google Cloud Run) or (AWS AppRunner) to schedule this run `every week` or `every day`.





# Data Modeling Documentation

## Tables Structures and Description

This demo is executed on local environment, if on cloud, equivalently would be:

    In Databricks, this would be a delta table, which can be simply accessed by other squad (with sufficient permission) as`SELECT * From "databricks_project.databricks_schema.account_details`

    In GCP Google, this would be saved in a Bigquery project, which is a data warehouse, can also be accessed by other squad simply as``SELECt * From `gcp-[COMPANY]-dataplatform-acil-prod.customer-analytics.account_details` ``

    In AWS, this would be saved in a Redshift project(similar to Bigquery), data warehouse, can be queried by SQL directly.``SELECT * FROM redshift_project_schema.account_details;``

## Data Lineage

The data flows from raw CSV files into the `IntermediateDetails` table, where all necessary details are combined to minimize redundant processing in subsequent steps. From this intermediate table, data branches out into two distinct paths:

1. **FactSales**: Utilizes the intermediate data to provide detailed transaction records.
2. **MonthlySalesSummary**: Aggregates data from the intermediate table to provide monthly sales metrics.

![plot](./usecase1_batch_pyspark/customer_invoice_etl/lineage_graph.png)

## 1. Intermediate Tables

The intermediate tables contain information about some "mid-level" aggregated data.

That is, they transformed raw source table, with some join and conditions filtering, to produce a table.

**These tables are meant to be shared with external squads.**

### account_details

```{sql}
    SELECT 
        a.account_id,
        a.company_name,
        a.company_address,
        a.contact_person,
        a.contact_phone,
        i.invoice_id,
        i.date_issued,
        DATEDIFF(current_date(), i.date_issued) AS days_since_invoice
    FROM accounts a
    JOIN invoices i ON a.account_id = i.account_id
    WHERE i.date_issued > {earliest_entry_date}
```

- **Source**: Joins data from `invoices`, `accounts`.
- **Description**: This table serves as a central repository of all account-transaction-related data, enriched with account details. It is used as a foundation for creating both detailed and aggregated fact tables for other users.
- **Purpose**:
  - High-Level info: To simplify and optimise the creation of analytical tables by providing all necessary account-related transaction details in one place
  - Cost saving: Reducing the need for multiple joins in downstream processing.
  - This would be useful if the analytics team wants to find relationship between issue dates and company details, or simply grab company details using invoice ids.
- **Fields**:
  - `days_since_invoice`: Days elapsed since the invoice date.
  - `ingest_ts`: Day of last run, this would be particularly helpful to determine the freshness of the table.
  - `earliest_entry_date`: An external parameter defined in `configs/config.yml`, so we can avoid invoices issued before this date.

### invoice_details

```
    SELECT 
        i.invoice_id,
        i.account_id,
        i.date_issued,
        il.item_id,
        il.quantity,
        s.item_name,
        s.item_cost_price,
        s.item_retail_price,
        il.quantity * s.item_retail_price AS total_sale_value,
        il.quantity * s.item_cost_price AS total_cost_value
    FROM invoices i
    JOIN invoice_line_items il ON i.invoice_id = il.invoice_id
    JOIN skus s ON il.item_id = s.item_id
    WHERE i.date_issued > {earliest_entry_date}
```

- **Source**: Joins data from `invoices`, `invoice_line_items` and `skus`.
- **Description**: This table serves as a central repository of all item-transaction-related data, enriched with sku details. It is used as a foundation for creating both detailed and aggregated fact tables for other users.
- **Purpose**:
  - High-Level info: This table provides level of details that can be used to analyse total revenue, sales, regardless whom the sales went to.
  - Cost saving: didn't use account table so saved processing and storage cost for account details.
  - This would be particularly helpful if the other external analytics team (sales or sku item related teams) wants to find relationship between invoices details and item details.
- **Fields**:
  - `days_since_invoice`: Days elapsed since the invoice date.
  - `ingest_ts`: Day of last run, this would be particularly helpful to determine the freshness of the table.
  - `earliest_entry_date`: An external parameter defined in `configs/config.yml`, so we can avoid invoices issued before this date.

## 2. Fact Tables

The intermediate tables contain information about some "fine-level" aggregated data.

That is, they transformed intermediate staging table, with additional special business use case join and conditions filtering, to produce a table that is specifically designed for our analytics usecase.

**These tables are mainly targeted our own squad/team usages, but it can also be shared with external squads.**

### FactSales

```
    SELECT 
        invoice_id,
        account_id,
        item_id,
        date_issued,
        item_name,
        quantity,
        item_cost_price,
        item_retail_price,
        total_sale_value,
        total_cost_value,
        total_sale_value - total_cost_value AS gross_profit,
        CASE WHEN DATEDIFF(current_date(), date_issued) > {overdue_days} THEN 'Overdue' ELSE 'Due' END AS overdue_status,
        current_timestamp() as  ingest_ts
    FROM IntermediateInvoiceDetails
```

- **Source**: Derived from the `IntermediateInvoiceDetails` view, this could also be converted to one of the source tables (if on cloud platforms, like mentioned earlier).
- **Description**: A detailed fact table focusing on sales transactions.
- **Purpose**: To provide a detailed view of each sale transaction, including profitability metrics and overdue statuses, useful for in-depth financial analysis and operational reporting, this can be directly fed into Google Looker or PowerBI dashboard depending on the specific cloud to use.
- **Fields**:
  - Includes all fields from `IntermediateInvoiceDetails`.
  - `gross_profit`: Calculated as the difference between total sales value and total cost value.
  - `overdue_status`: Indicates whether the invoice is overdue based on a predetermined threshold, this is a label, can be colour matched for dashboard usage.

### FactSalesProcessed (for ML applications)

```
    CREATE OR REPLACE TEMP VIEW FactSalesProcessed AS
        SELECT 
            acc.company_name,
            acc.contact_person,
            fs.date_issued,
            fs.item_id,
            sku.item_name,
            sku.item_description,
            sku.item_cost_price,
            sku.item_retail_price,
            fs.quantity,
            fs.total_sale_value,
            ROUND(fs.total_sale_value - (fs.quantity * sku.item_cost_price), 2) AS gross_profit,   -- This could be a ML predicting label
            fs.overdue_status               -- This could also be a ML predicting label
            -- [[ Fill ]]                   -- Fill in this field to use in machine learning models. 
            ,
            current_timestamp() as  ingest_ts
        FROM FactSales fs
        JOIN accounts acc ON fs.account_id = acc.account_id
        JOIN skus sku ON fs.item_id = sku.item_id
        -- WHERE: add conditions to filter data to use in ML models.
```

- **Source**: Derived from the `FactSales` view, this could also be converted to one of the source tables (if on cloud platforms, like mentioned earlier).
- **Description**: A detailed fact table focusing on sales transactions, with some processinges done for prediction.
- **Purpose**:
  - Can further integrate with "one-hot-encoding", outlier removal, feature engineering such as using `X` cross product for two features, to produce a finetuned table for Machine Learning use cases.
  - On **GCP VertexAI**, this can be directly fed into a prebuild AutoML model, to produce insights
  - "overdue_status" can be treated as labels, for the ML model to predict.
  - Given large volume of data from different countries, based on [COMPANY] business context, this could potentially achieve a good accuracy and result.

### MonthlySalesSummary

```
        SELECT 
            YEAR(date_issued) AS year,
            MONTH(date_issued) AS month,
            SUM(total_sale_value) AS total_sales,
            SUM(total_cost_value) AS total_costs,
            SUM(gross_profit) AS total_gross_profit,
            COUNT(DISTINCT account_id) AS unique_customers,
            SUM(quantity) AS total_items_sold,
            current_timestamp() as  ingest_ts
        FROM FactSales
        GROUP BY YEAR(date_issued), MONTH(date_issued)
```

- **Source**: Derived from the `FactSales` view.
- **Description**: An aggregated table that summarises sales data on a monthly basis.
- **Purpose**:
  - To support our Analytics team for trend analysis and monthly performance reviews by providing a high-level view of sales metrics.
  - Can also be done on a year level, or
  - Aggregated based on account/company/client details, so we can profile each clients
- **Fields**:
  - `year`, `month`: Time dimensions for the aggregation.
  - `total_sales`, `total_costs`, `total_gross_profit`: Aggregate financial metrics.
  - `unique_customers`: The count of unique accounts making transactions within the month.
  - `total_items_sold`: Total quantity of items sold in the month.




# System Design and Implementing CDC changes


## Overview

After successfully developing an ETL job, our focus now shifts to architecting a robust production system capable of consistently extracting data from the source systems and providing up-to-date and historical data to data analysts (mainly SQL focused).

## Key points need to consider:
- Data Storage: Current data is stored in AWS Aurora MySQL databases.
- Change Data Capture (CDC): Planned to be enabled within the next 12 months, with CDC events to be streamed to Kafka (Kafka API supports).
- Analytical Needs: Analysts require access to historical views of data and features (e.g., comparisons between data from one month ago and today).
- External Squad (Finance Team) Requirements: Interested primarily in invoice data and proficient only in SQL.




![plot](./usecase2_streaming_cdc/flowchart.png)



## Data Source: AWS Aurora MySQL
AWS Aurora MySQL is a third-party SQL database integration on AWS (similar to Google Cloud SQL for MySQL). I will consider based on the fact that AWS supports integrations well with MySQL databases with multiple AWS supplied features.

## Data Processing and Workflow Management
### Deploying Spark on AWS EMR

- AWS Elastic MapReduce (EMR): Native support for environment configurations, auto-scaling, and executions. EMR is ideal for deploying our PySpark application developed in Task One.
- Local Testing: Docker (provided in task one) will be utilised for local testing environments to ensure consistency, though it is not required for cloud execution due to the managed nature of AWS EMR services.


### EMR Cluster Setup:
- Initialize an EMR cluster to host our PySpark application.
  ```bash
  aws emr create-cluster --name "Spark Cluster" --use-default-roles
  ```


### Job Triggering:

##### Real-Time:
- Real-Time execution can be costly, depends on update frequency, need to ensure long run cost is with-in budget.
- Overhead in spinning up Spark cluster and setup.
- AWS Lambda: Trigger EMR jobs using Lambda functions (similar to cloud function on GCP), enabling responsive data processing based on event, which can be setup to fire from Aurora MySQL database.
- Amazon Pub/Sub: (Google Pub/Sub) to trigger Lambda functions, ensures real-time data processing and spark execution as soon as updates occur in Aurora MySQL.
  

##### Batch, Scheduled:
- Scheduled Tasks: AWS App Runner for regularly scheduled jobs (Google Cloud Run), that automatically run our spark application every x days.


### Data Storage and Querying: AWS RedShift
- AWS RedShift (Bigquery on Google, Delta lake on Databricks) will serve as our data warehouse, providing extensive SQL query capabilities for external squad (such as finance teams). 
- Setting up IAM and project access to ensure external access is controlled.
- Can also setup `dev, test, prod` environment so we can safely test new features without interrupting other squad's work.


### Version Control(Time Travel): 
- Use table snapshots, time-travel features.
- Use an ingest_ts column for managing incremental updates effectively.
- Use Amazon SageMaker Feature Store.
    - Store processed features independently, allowing shared access across different teams (finance team).
    - Automate feature updates upon new data arrivals, integrating with RedShift for ML model training or dashboard serving.

### Visualisation and Reporting: AWS QuickSight
- QuickSight (Looker, Tableau alternative)
- Provided on AWS can be directly integrated with RedShift, UI select tables to connect etc, to meet the reporting needs of our teams.


### CDC, Incremental and Real-Time Data Management Strategies

#### Change Data Capture (CDC):

Once the data platform team enabled CDC to capture data changes incrementally, we will have continuously supplied new data.
Please see `cdc_demo.py` for high-level logic overview and sample code.


The demo uses DBT and Spark for merging and appending data rather than overwriting all existing data, which optimised resource usage and operational costs.

#### Data Append Strategy (Redshift Connector):

```python
# Append data to RedShift using PySpark
redshift_url = "jdbc:redshift://<cluster-endpoint>:5439/<database>"
redshift_properties = {
    "user": "<username>",
    "password": "<password>",
    "driver": "com.amazon.redshift.jdbc.Driver"
}
df_result.write.jdbc(url=redshift_url, table="intermediate_invoices", mode="append", properties=redshift_properties)
```

## Conclusion

The proposed system architecture is meticulously designed to address both the current and future data processing needs of the organization. By leveraging AWS's powerful suite of services, this solution ensures scalability, flexibility, and efficiency, positioning us to dynamically adapt to changing data volumes and processing requirements.




Shield: [![CC BY-NC 4.0][cc-by-nc-shield]][cc-by-nc]

This work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png
[cc-by-nc-shield]: https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg