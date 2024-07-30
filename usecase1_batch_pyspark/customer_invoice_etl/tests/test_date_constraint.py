import unittest
from pyspark.sql import SparkSession, Row
class TestETLModule(unittest.TestCase):
    def setUp(self):
        """Start Spark session for testing."""
        self.spark = SparkSession.builder \
            .appName("Tests") \
            .getOrCreate()

    def test_transform_data_correctness(self):
        """Test if the spark instance is setup properly and can processes data correctly."""
        # Create test DataFrames simulating expected input
        earliest_entry_date = "2022-05-01"
        df_invoices = self.spark.createDataFrame([
            (1, 2, "2021-01-03"), 
            (2, 3, "2023-05-14"), 
            (1, 3, "2022-03-14")], 
            ["invoice_id", "account_id", "date_issued"]
        )
        df_invoices.createOrReplaceTempView("temp_test")

        # Apply transformation, using date condition and test it out
        df_result = self.spark.sql(f"""
                SELECT 
                    i.invoice_id,
                    i.account_id,
                    i.date_issued
                FROM temp_test i
                WHERE date(i.date_issued) > date('{earliest_entry_date}')
            """)

        # expected output DataFrame
        expected_data = [
            Row(invoice_id=2, account_id=3, date_issued="2023-05-14")
        ]
        df_expected = self.spark.createDataFrame(expected_data)
        
        print(df_result.collect())
        print("-----")
        print(df_expected.collect())
        
        # assertion to compare
        self.assertTrue(df_result.collect() == df_expected.collect(), "Data transformation does not match expected output")


    def tearDown(self):
        """Stop Spark session after testing."""
        self.spark.stop()
