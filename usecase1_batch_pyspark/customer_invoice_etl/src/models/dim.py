def intermediate_invoice_details(spark, earliest_entry_date):
    """An intermediate table that produces and stores invoice and line item details.
    Note that this intermediate table is meant to be saved to Bigquery or Redshift, that 
    can be directly SQL accessed by other DA, and if granted permission, to other squads as well.
        Input:
            @earliest_entry_date: days to look at, save time costs and computational costs, note that it would be best to apply
                                    at fact table level instead, as this intermediate table might be used by other squads.
    """
    spark.sql(f"""
        CREATE OR REPLACE TEMP VIEW IntermediateInvoiceDetails AS
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
        -- WHERE date(i.date_issued) > date('{earliest_entry_date}')
    """)
    return spark.table("IntermediateInvoiceDetails")


def intermediate_account_details(spark, earliest_entry_date):
    """An intermediate table for account and invoice relationship details.
        Input:
            @earliest_entry_date: days to look at, save time costs and computational costs, note that it would be best to apply
                                    at fact table level instead, as this intermediate table might be used by other squads.
    """
    spark.sql(f"""
        CREATE OR REPLACE TEMP VIEW IntermediateAccountDetails AS
        SELECT 
            a.account_id,
            a.company_name,
            a.company_address,
            a.contact_person,
            a.contact_phone,
            i.invoice_id,
            i.date_issued,
            DATEDIFF(current_date(), i.date_issued) AS days_since_invoice,
            current_timestamp() as  ingest_ts
        FROM accounts a
        JOIN invoices i ON a.account_id = i.account_id
        WHERE date(i.date_issued) > date('{earliest_entry_date}')
    """)
    return spark.table("IntermediateAccountDetails")