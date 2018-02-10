


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

REPEAT_DICT = {}
VALUES_DICT = {}


# Some preprocessing and checking if inputs are ok
def check_valid_input(record):
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


# Checks if repeat donor by key (NAME, ZIP)
def check_repeat(record):
    key = (record[1], record[2])
    date_exists = REPEAT_DICT.get(key, 0)
    if not date_exists or record[3] < date_exists:
        REPEAT_DICT[key] = record[3]
        return False
    else:
        return True


# Appends to list then sort by key (CMTE, ZIP, YEAR)
def add_to_outputs(record, percentile):
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
        curr_value[0].append(record[4])
        curr_value[0].sort()
        update_value = [curr_value[0], curr_value[1]+int(record[4]), curr_value[2]+1]
        VALUES_DICT[key] = list(update_value)
        out = list(key)
        update_value[0] = calc_and_format_output(update_value[0], update_value[2], percentile)
        out.extend(update_value)
        return out
        

# Calculates the percentile number        
def calc_and_format_output(arr, length, percentile):
    index = math.ceil(percentile * length * 0.01)
    num = arr[index-1]
    return num    




if __name__ == '__main__':

    with open(sys.argv[2]) as perc:
        percentile = int(perc.read())
    with open(sys.argv[1],'r') as records, open(sys.argv[3], 'w') as output:
        reader = csv.DictReader(records, fieldnames=HEADER_NAMES, delimiter='|')
        writer = csv.writer(output, delimiter='|')
        for row in reader:
            raw_data = [row['CMTE_ID'], row['NAME'], row['ZIP_CODE'], row['TRANSACTION_DT'], row['TRANSACTION_AMT'], row['OTHER_ID']]
            if check_valid_input(raw_data):
                is_repeat = check_repeat(raw_data)
                if is_repeat:
                    record = add_to_outputs(raw_data, percentile)
                    writer.writerow(record)