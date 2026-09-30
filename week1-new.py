import pandas as pd
from pathlib import Path
import glob
import os
import matplotlib.pyplot as plt


files = glob.glob('data/CRMLSSold*.csv')

#read all sold files and add to a list
data = [pd.read_csv(i, low_memory=False) for i in files]

#count the length of each list and sum for total row number
row_num = sum(len(df) for df in data)
print("Number of rows before concat:", row_num)

#concatenate datasets and count length for row number
total_sold = pd.concat(data, ignore_index=True)

row_num = len(total_sold)
print("Number of rows after concat:", row_num)

#filter for Residential and count row numbers after filter
sold_filtered = total_sold[total_sold['PropertyType'] == 'Residential']
row_num = len(sold_filtered)
print("Number of rows after filtering for Residential:", row_num)

#send to new csv
sold_filtered.to_csv('sold_filtered.csv', index = False)



#repeat for listings

files = glob.glob('data/CRMLSListing*.csv')

#read all files and add to a list
data = [pd.read_csv(i, low_memory=False) for i in files]

#count the length of each list and sum for total row number
row_num = sum(len(df) for df in data)
print("Number of rows before concat:", row_num)

#concatenate datasets and count length for row number
total_listing = pd.concat(data, ignore_index=True)

row_num = len(total_listing)
print("Number of rows after concat:", row_num)

#filter for Residential and count row numbers after filter
listing_filtered = total_listing[total_listing['PropertyType'] == 'Residential']
row_num = len(listing_filtered)
print("Number of rows after filtering for Residential:", row_num)

#send to new csv
listing_filtered.to_csv('listing_filtered.csv', index = False)