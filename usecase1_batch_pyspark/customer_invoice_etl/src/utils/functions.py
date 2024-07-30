## This file contains important functions needed to run the ETL jobs.

from pyspark.sql import SparkSession
import yaml
import os

def create_spark_session():
    return SparkSession.builder \
        .appName("Customer Invoice ETL") \
        .config('job.local.dir', 'file:/etl_app/') \
        .getOrCreate()

def load_config(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_table_path(config, schema_name, table_name):
    source_path = config["paths"][schema_name]
    return os.path.join(source_path, config['source_tables'][table_name])

def extract_data(spark, config):
    """Extract data from local"""
    df_accounts = spark.read.option("inferSchema", True).option('multiline', True).csv(get_table_path(config, "source_directory", "accounts"), header=True)
    df_invoices = spark.read.option("inferSchema", True).option('multiline', True).csv(get_table_path(config, "source_directory", "invoices"), header=True)
    df_line_items = spark.read.option("inferSchema", True).option('multiline', True).csv(get_table_path(config, "source_directory", "invoice_line_items"), header=True)
    df_skus = spark.read.csv(get_table_path(config, "source_directory", "skus"), header=True)
    # add additional dim (source) table from here. 

    # Register DataFrames as a SQL temporary view, this would be easier for Data Scientists/Analysts to edit, view and testing
    df_accounts.createOrReplaceTempView("accounts")
    df_invoices.createOrReplaceTempView("invoices")
    df_line_items.createOrReplaceTempView("invoice_line_items")
    df_skus.createOrReplaceTempView("skus")
    print(" = All table views have been successfully created. ")
    return df_accounts, df_invoices, df_line_items

def load_data(df, path, df_name):
    if not os.path.exists(path):
        os.mkdir(path)
    save_path = os.path.join(path, df_name)
    df.write.mode('overwrite').parquet(save_path)
    print(f" - {df_name} Successfully loaded to {save_path}")