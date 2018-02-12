This program was written all to donation-analytics.py.

The program reads the input file line by line, checking each record for validity and only continuing to process if it is valid. 

There are two global dictionaries, one which stores years based on (Name, Zip) keys to check for repeats, and one which stores the actual contribution amount data based on (CMTE_ID, Zip, Year) keys.

It first passes the record through a function to check for its existence in the repeat donor dictionary. If it passes this test, it then adds the record's information to the contribution values dictionary, where it retrieves and calculates the necessary data, returning the list of values to be written to the output file. 

The output is written line by line based on the above criteria.



Python Version: 3.6

@Author: Lei(Laney) Huang