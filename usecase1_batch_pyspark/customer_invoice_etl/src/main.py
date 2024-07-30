from utils.functions import create_spark_session, load_config, extract_data, load_data
from models.intermediate import intermediate_invoice_details, intermediate_account_details
from models.fact import fact_sales, fact_monthly_sales_summary, fact_sales_processed

def run_etl(spark, config):
    # data extraction and temporary view creation here
    extract_data(spark, config)

    # intermediate table generation
    intermediate_save_path = config["paths"]["intermediate_output"]
    load_data(intermediate_invoice_details(spark, config["earliest_entry_date"]), intermediate_save_path, "invoice_details")
    load_data(intermediate_account_details(spark, config["earliest_entry_date"]), intermediate_save_path, "account_details")

    # final fact table generation
    fact_save_path = config["paths"]["fact_output"]
    load_data(fact_sales(spark, config["overdue_days"]), fact_save_path, "fact_sales")
    load_data(fact_monthly_sales_summary(spark), fact_save_path, "fact_monthly_sales_summary")
    load_data(fact_sales_processed(spark), fact_save_path, "fact_sales_processed")



if __name__ == "__main__":
    config = load_config("configs/config.yml")
    spark = create_spark_session()

    # Run the ETL process, add test and try except error handling here
    run_etl(spark, config)

    spark.stop()
