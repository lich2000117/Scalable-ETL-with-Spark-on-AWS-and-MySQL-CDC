
def fact_sales(spark, overdue_days):
    """comprehensive fact final output table for sales analytics, including total cost and total revenue, gross profit.
        Input:
            @overdue_days: days to determine if it is overdue.
    """
    spark.sql(f"""
       CREATE OR REPLACE TEMP VIEW FactSales AS
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
    """)
    return spark.table("FactSales")


def fact_sales_processed(spark):
    """
    Create a processed fact final table for sales that includes SKU details and account details this table maybe suitable for direct Machine Learning
    Applications, such as model training, model inference, this can be done using Vertex AI machine learning models if on GCP, sageMaker if on AWS.

    Note that this is a demo only, might need further processing such as one hot encoding, normalisation, outlier removal before proper ML usage.
    """
    # Create the processed fact table by joining with accounts and SKU details
    spark.sql("""
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
    """)
    return spark.table("FactSalesProcessed")

def fact_monthly_sales_summary(spark):
    """A monthly aggregated table for sales. This is a demo table that uses group by, can be used by DA, DS for analysis and dashboard building,
    The dashboard can be connected to Google Looker, or Tableau, or PowerBI.
    """
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW MonthlySalesSummary AS
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
    """)
    return spark.table("MonthlySalesSummary")



