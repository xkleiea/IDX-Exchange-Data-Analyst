# %%
import pandas as pd
from pathlib import Path
import glob
import os
import matplotlib.pyplot as plt


# %%
#load the data ensuring data types are kept
sold = pd.read_csv("sold_filtered.csv", low_memory = False)
sold = sold.convert_dtypes()


# %%
#convert all date columns from strings to datetime
dates = ['CloseDate','ContractStatusChangeDate','PurchaseContractDate','ListingContractDate']

for col in dates:
    sold[col] = pd.to_datetime(sold[col], errors='coerce')

# %%
#identifying rows and columns
sold.shape

# %%
#review column data types
for i in sold.columns:
    print(i, sold[i].dtype)

# %%
# Check property categories
sold['PropertyType'].unique()

# %%
#proportions selling higher, lower, and equal to list
higher_sold = (sold['ClosePrice'] > sold['ListPrice']).sum()
higher_list = (sold['ClosePrice'] < sold['ListPrice']).sum()
equal = (sold['ClosePrice'] == sold['ListPrice']).sum()

total = len(sold)

print("Sold higher than list:", higher_sold / total * 100, "%")
print("List higher than sold:", higher_list / total * 100, "%")
print("Equal:", equal / total * 100, "%")

# %%
cols = sold.columns.tolist()

print(len(cols))         #84 columns
print(cols)             


# %%

#declaring fields for histogram and summaries
key_num_fields = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
"LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"]

for col in key_num_fields:
    print(col, sold[col].dtype)

# %%
   
#print summary statistics and percentiles for each key numeric field
for col in key_num_fields:
    print(sold[col].describe())

# %%
#plotting histograms of the 9 key numeric fields minus major outliers
fig, axes = plt.subplots(3, 3, figsize=(12, 10))
axes = axes.flatten()

for i, col in enumerate(key_num_fields):
    lower = sold[col].quantile(0.01)
    upper = sold[col].quantile(0.99)
    
    axes[i].hist(sold[col], range=(lower, upper))
    axes[i].set_title(col)

plt.tight_layout()
plt.show()

# %%
#boxplots grid with extreme outliers. highly skewed data, so its not interpretable at this stage
fig, axes = plt.subplots(3, 3, figsize=(12, 10))
axes = axes.flatten()

for i, col in enumerate(key_num_fields):
    axes[i].boxplot(sold[col].dropna())
    axes[i].set_title(col)

plt.tight_layout()
plt.show()



# %%
#counting % nulls per column
null_pct = sold.isna().mean() * 100
null_pct.sort_values(ascending=False)
print(null_pct)


#flagging columns >90% missing
flagged_cols = null_pct[null_pct > 90].index.tolist()
print(flagged_cols)


# %%
sold = sold.drop(columns= 'PropertyType')

# %%
sold.shape

# %%
#send to new csv
sold.to_csv('data/sold_filtered_2.csv', index = False)

# %% [markdown]
# ### repeat for listing 

# %%
#load the data ensuring data types are kept
listing = pd.read_csv("listing_filtered.csv", low_memory = False)
listing = listing.convert_dtypes()


# %%
#convert all date columns from strings to datetime
dates = ['CloseDate','ContractStatusChangeDate','PurchaseContractDate','ListingContractDate']

for col in dates:
    listing[col] = pd.to_datetime(listing[col], errors='coerce')

# %%
#review column data types
for i in listing.columns:
    print(i, listing[i].dtype)

# %%
# Check property categories
listing['PropertyType'].unique()

# %%

#declaring fields for histogram and summaries
key_num_fields = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
"LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"]

for col in key_num_fields:
    print(col, listing[col].dtype)

# %%
#print summary statistics and percentiles for each key numeric field
for col in key_num_fields:
    print(listing[col].describe())

# %%
#plotting histograms of the 9 key numeric fields minus major outliers
fig, axes = plt.subplots(3, 3, figsize=(12, 10))
axes = axes.flatten()

for i, col in enumerate(key_num_fields):
    lower = listing[col].quantile(0.01)
    upper = listing[col].quantile(0.99)
    
    axes[i].hist(listing[col], range=(lower, upper))
    axes[i].set_title(col)

plt.tight_layout()
plt.show()

# %%
#boxplots grid with extreme outliers. highly skewed data, so its not interpretable at this stage
fig, axes = plt.subplots(3, 3, figsize=(12, 10))
axes = axes.flatten()

for i, col in enumerate(key_num_fields):
    axes[i].boxplot(listing[col].dropna())
    axes[i].set_title(col)

plt.tight_layout()
plt.show()

#extreme outliers inlist price, living area, lot size, bathrooms

# %%
#counting % nulls per column
null_pct = listing.isna().mean() * 100
null_pct.sort_values(ascending=False)
print(null_pct)




# %%
#flagging columns >90% missing
flagged_cols = null_pct[null_pct > 90].index.tolist()
print(flagged_cols)

# %%
#send to new csv
listing.to_csv('data/listing_filtered_2.csv', index = False)


