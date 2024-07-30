#!/bin/bash

## This is the entry point for our program to conduct
# 1. Unit test 
# 2. Run actual ETL jobs

# unit testing
bash /etl_app/scripts/run_unit_test.sh

# Run the ETL script
echo "Starting ETL job..."
python /etl_app/src/main.py
echo "Done ETL job..."