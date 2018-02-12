'''
Main file of the data processing module. 

Task is broken down a few simple functions: 
    -Checking if the input is valid
    -Checking if the donor is a repeat
    -Updating current data on the contributions, and output the necessary details 

Python version used: 3.6



@author Lei Huang
'''

import sys
import csv 
from datetime import datetime
import re
import bisect
import math


HEADER_NAMES = ['CMTE_ID', 'AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', 'IMAGE_NUM',
                        'TRANSACTION_TP', 'ENTITY_TP', 'NAME', 'CITY', 'STATE',
                        'ZIP_CODE', 'EMPLOYER', 'OCCUPATION', 'TRANSACTION_DT', 'TRANSACTION_AMT',
                        'OTHER_ID', 'TRAN_ID', 'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT,SUB_ID']

REPEAT_DICT = {} # Key: (Name, Zip) Value: Earliest date contribution (datetime format)
VALUES_DICT = {} # Key: (CMTE_ID, Zip, Year) Value: [List of sorted contributions, Sum of contributions, Count of contributions]


def check_valid_input(record):
    '''
    Takes in a record of the format [CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID] 

    Checks if it is an individual contribution. 
    Checks if the other fields are empty.
    Checks if the Name field is malformed in that it contains a digit
    Truncates the ZIP field to the first 5 digits and checks if it is 5 digits.
    Checks if the Date field can be formatted properly.

    Returns if the record is valid.
    '''
    if record[5]:
        return False
    if not record[0] or not record[1] or not record[2] or not record[3] or not record[4]:
        return False
    if re.search(r'\d', record[1]):
        return False
    record[2] = record[2][:5]
    if len(record[2]) < 5:
        return False
    try:
        record[3] = datetime.strptime(record[3], '%m%d%Y')
    except ValueError:
        return False
    return True


def check_repeat(record):
    '''
    Takes in a formatted, vetted input

    Forms a dictionary key based on (NAME, ZIP) to identify repeat donors.
    Checks the global dictionary REPEAT_DICT if this donor has appeared previously
    Adds to dictionary if it is a new donor, or updates the date to an earlier date 
    in the case of an out of order entry.

    Returns if the donor is a repeat donor
    '''
    key = (record[1], record[2])
    date_exists = REPEAT_DICT.get(key, 0)
    if not date_exists or record[3] < date_exists:
        REPEAT_DICT[key] = record[3]
        return False
    else:
        return True


def add_to_outputs(record, percentile):
    '''
    Takes in a record and the percentile read in the main function.

    Updates the VALUES_DICT with key (CMTE_ID, Zip, Year), or creates a new entry
    The values associated with the key is an array:
        -List of sorted contribution values for the given key
        -Sum of contribution values for the given key
        -Count of contributions for the given key
    The list of values are maintained sorted after insertion through the use of the bisect module.
    This list of values is passed into a helper function to find the value at a specific percentile.

    Returns a list of the correctly formatted values
    '''
    key = (record[0], record[2], datetime.strftime(record[3], '%Y'))
    output_exists = VALUES_DICT.get(key, 0)
    if not output_exists:
        new_value = [[record[4]], int(record[4]), 1]
        VALUES_DICT[key] = list(new_value)
        out = list(key)
        new_value[0] = record[4]
        out.extend(new_value)
        return out
    else:
        curr_value = VALUES_DICT[key]
        bisect.insort(curr_value[0], record[4])
        update_value = [curr_value[0], curr_value[1]+int(record[4]), curr_value[2]+1]
        VALUES_DICT[key] = list(update_value)
        out = list(key)
        update_value[0] = calc_and_format_output(update_value[0], update_value[2], percentile)
        out.extend(update_value)
        return out
        

     
def calc_and_format_output(arr, length, percentile):
    '''
    Helper function to calculate the member of the sorted array that corresponds to the specified percentile.
    '''
    index = math.ceil(percentile * length * 0.01)
    num = arr[index-1]
    return num    




if __name__ == '__main__':

    with open(sys.argv[2]) as perc:
        percentile = int(perc.read())
    with open(sys.argv[1],'r') as records, open(sys.argv[3], 'w') as output:
        reader = csv.DictReader(records, fieldnames=HEADER_NAMES, delimiter='|')
        writer = csv.writer(output, delimiter='|', lineterminator = '\n')
        for row in reader:
            raw_data = [row['CMTE_ID'], row['NAME'], row['ZIP_CODE'], row['TRANSACTION_DT'], row['TRANSACTION_AMT'], row['OTHER_ID']]
            if check_valid_input(raw_data):
                if check_repeat(raw_data):
                    record = add_to_outputs(raw_data, percentile)
                    writer.writerow(record)