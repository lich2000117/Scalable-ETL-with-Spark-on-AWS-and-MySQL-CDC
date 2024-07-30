## Test entry here, can define as many test_xxx.py as you want, then use this script to call them, as an entry point.
from test_date_constraint import *

if __name__ == "__main__":
    test = TestETLModule()
    test.setUp()
    test.test_transform_data_correctness()
    test.tearDown()
    print("== Test Complete ==")
