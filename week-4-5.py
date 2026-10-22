# %% [markdown]
# 
# Tasks
# Remove unnecessary or redundant columns
# Handle missing values appropriately
# Ensure numeric fields are properly typed
# 
# 
# Submit a cleaned, analysis-ready dataset as a CSV, plus a .py script documenting every transformation made and why. Include before/after row counts, data type confirmations, date consistency flag counts, and a geographic data quality summary noting any invalid coordinate records.
# 
# 

# %%
import pandas as pd

# %%
sold = pd.read_csv('data/sold_filtered_3.csv', low_memory = False)
listing = pd.read_csv('data/listing_filtered_3.csv', low_memory = False)

# %%
print("sold dimensions:", sold.shape, "     listing dimensions:", listing.shape)

# %% [markdown]
# ### Date Conversion and Consistency

# %%


def format_dates(df):
    # Convert all dates from string to datetime
    
    dates = ['CloseDate','ContractStatusChangeDate','PurchaseContractDate','ListingContractDate']
    
    for col in dates:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# %%
sold = format_dates(sold)
listing = format_dates(listing)

# %%
def column_types(df):
    # Confirm data types
    return pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
    }).reset_index(drop=True)

# %%
column_types(sold)
column_types(listing)

# %% [markdown]
# I see some duplicate columns are appearing in the listing dataset, so I want to remove those later on.

# %%
#flag columns with timeline inconsistencies

def timeline_flags(df):
    
    df['listing_after_close_flag'] = (
        df['ListingContractDate'] > df['CloseDate']
    )
    df['purchase_after_close_flag'] = (
        df['PurchaseContractDate'] > df['CloseDate']
    )

    #flag any entry that violates the correct sequence
    df['negative_timeline_flag'] = (
        (df['ListingContractDate'] > df['PurchaseContractDate']) |
        (df['PurchaseContractDate'] > df['CloseDate']) |
        (df['ListingContractDate'] > df['CloseDate'])
    )
    
    df['invalid_dom_flag'] = (
        df['DaysOnMarket'] < 0
    )
    
    return df

# %%
def flag_summary(df, flag_cols):
    # Count and percent of rows flagged for each flag column.
    summary = pd.DataFrame({
        "n_flagged": df[flag_cols].sum(),
        "pct_flagged": (df[flag_cols].mean() * 100).round(2),
    })
    return summary

flag_cols = ['listing_after_close_flag', 'purchase_after_close_flag', 'negative_timeline_flag', 'invalid_dom_flag']

# %%
sold = timeline_flags(sold)
flag_summary(sold, flag_cols)

# %%
listing = timeline_flags(listing)
flag_summary(listing, flag_cols)

# %%
#flag missing close price only for sold dataset

sold['invalid_closeprice_flag'] = (
    (sold['ClosePrice'] <= 0) | sold['ClosePrice'].isna() )

print(sold[['invalid_closeprice_flag']].sum())

# %%
def house_flag(df):    
    #flag invalid numeric values for house layout
    df['invalid_house_flag'] = (
        (df['LivingArea'] <= 0) |
        (df['BedroomsTotal'] < 0) |
        (df['BathroomsTotalInteger'] < 0)
    )
    
    return df

# %%
flag_cols = ['invalid_house_flag']

# %%
sold = house_flag(sold)
flag_summary(sold, flag_cols)

# %%
listing = house_flag(listing)
flag_summary(listing, flag_cols)

# %% [markdown]
# ### Geographic Data Checks

# %%
#flag rows with invalid geographic values

def geo_check(df):
    df['missing_geo_flag'] = (
        (df['Latitude'].isna()) |
        (df['Longitude'].isna()) |
        (df['Latitude'] == 0) |
        (df['Longitude'] == 0)
    )
    #flag for explicitly outside of california
    df['outofbounds_flag'] = (
        (df['Latitude'] < 32) | 
        (df['Latitude'] > 42) |
        (df['Longitude'] < -125) |
        (df['Longitude'] > -114) |
        (df['StateOrProvince'] != 'CA')
    )
    return df

# %%
flag_cols = ['outofbounds_flag','missing_geo_flag']

# %%
sold = geo_check(sold)
flag_summary(sold, flag_cols)

# %%
listing = geo_check(listing)
flag_summary(listing, flag_cols)

# %%
#counting % nulls per column
sold_null_pct = sold.isna().mean() * 100

sold_null_pct.to_frame(name='pct_null')
sold_null_pct = sold_null_pct.sort_values(ascending=False)


# %%
#counting % nulls per column
listing_null_pct = listing.isna().mean() * 100

listing_null_pct.to_frame(name='pct_null')
listing_null_pct = listing_null_pct.sort_values(ascending=False)

# %% [markdown]
# ### Removing unnecessary or redundant columns

# %% [markdown]
# Many categorical, metadata, and high missing columns won't be conductive to analysis. Checking rows >70% missing, much of this data is covered by other columns (latfilled, lonfilled, Highschool) or not paramount to analysis (compensation and names of colist agents).

# %%
sold_clean = sold
listing_clean = listing

# %%
# removing duplicated columns from listing data
listing_clean = listing_clean.drop(list(listing_clean.filter(regex='.1')), axis=1)

# %%
#removing sold columns over 70% missing
over70_cols = sold_null_pct[sold_null_pct > 70].index.tolist()

# %%
#manually checking columns to confirm no important key fields are included
print(sold_null_pct[over70_cols])

# %%
listing_null_pct

# %%
sold_clean = sold_clean.drop(columns= over70_cols)

# %%
#removing listing columns over 75% missing ONLY after manually confirming key fields are in tact
l_over75_cols = listing_null_pct[listing_null_pct > 75].index.tolist()

# %%
listing_clean = listing_clean.drop(columns= l_over75_cols)

# %%
#remove 3 rows from sold missing close price
sold_clean = sold_clean[sold_clean['invalid_closeprice_flag'] == 0]


# %%
# removing listings from both datasets where home layout is invalid or missing

def remove_invalid_layouts(df):
    df = df[df['invalid_house_flag'] == 0]
    return df

# %%
sold_clean = remove_invalid_layouts(sold_clean)

# %%
print("Dimensions of sold data before cleaning:", sold.shape)
print("Dimensions of sold data after cleaning:",sold_clean.shape)

# %%
listing_clean = remove_invalid_layouts(listing_clean)

# %%
print("Dimensions of listing data before cleaning:", listing.shape)
print("Dimensions of listing data after cleaning:",listing_clean.shape)

# %%
#send to new csv
sold_clean.to_csv('data/sold_clean.csv', index = False)

# %%
#send to new csv
listing_clean.to_csv('data/listing_clean.csv', index = False)


