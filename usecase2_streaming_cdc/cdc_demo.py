## This file contains pseudo code and data structures when the CDC happens in the upstream data ingestions.
# This will give a brief idea of how CDC would work in this project.

# Example CDC data extracted from Kafka source or log files of MySQL databases,
# this can be achieved using API, (native support by some SQL databases, or directly extract SQL databases's local raw logging file)


### 1. Capturing CDC events
columns = ["invoice_id", "account_id", "date_issued", "operation"]
cdc_data = [
    (1, 2, "2021-01-03", "insert"), 
    (2, 3, "2023-06-01", "update"),  
    (4, 5, "2023-07-01", "insert"), 
    (3, 4, None, "delete")        
]

# now we can create a spark dataframe using this CDC information.
df_cdc = spark.createDataFrame(cdc_data, columns)
df_cdc.createOrReplaceTempView("cdc_invoices")



### 2. Prepare changed table views 
# Use Spark functions to make changes to the database, this ensures scalability and efficiency.
df_inserts = df_cdc.filter(df_cdc.operation == "insert").drop("operation")
df_updates = df_cdc.filter(df_cdc.operation == "update").drop("operation")
df_deletes = df_cdc.filter(df_cdc.operation == "delete").select("invoice_id")

# Create view for above dataframe it is needed to alter the existing tables.
df_inserts.createOrReplaceTempView("staging_inserts_invoices")
df_updates.createOrReplaceTempView("staging_updates_invoices")
df_deletes.createOrReplaceTempView("staging_deletes_invoices")



### 3. Setup redshift connections (to data warehouse)
# Define Redshift connection properties
redshift_url = "jdbc:redshift://`<cluster-endpoint>`:5439/`<database>`"
redshift_properties = {
    "user": "`<username>`",
    "password": "`<password>`",
    "driver": "com.amazon.redshift.jdbc.Driver"
}


### 4. insert, update, delete.

# a. insert new entries.
df_inserts.write.jdbc(url=redshift_url, table="staging_inserts_invoices", mode="append", properties=redshift_properties)


# b. update existing entries
# For updates, cannot simply use "append", otherwise it wuld result in duplications and data inconsistency
sql = """
    UPDATE target_invoices
    SET 
        account_id = staging_updates_invoices.account_id,
        date_issued = staging_updates_invoices.date_issued
    FROM staging_updates_invoices
    WHERE target_invoices.invoice_id = staging_updates_invoices.invoice_id;
"""
spark.sql(sql)


# c. delete records
# for deleteing records, we need to write a query to filter out droped ids,
sql = f"""DELETE FROM target_invoices
USING staging_deletes_invoices
WHERE target_invoices.invoice_id = staging_deletes_invoices.invoice_id;
"""
spark.sql(sql)