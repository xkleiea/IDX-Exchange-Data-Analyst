

# %%
import pandas as pd

# %%
df = pd.read_csv('data/sold_filtered_3.csv', low_memory = False)

# %%
df.shape

# %%
#convert all date columns from strings to datetime
dates = ['CloseDate','ContractStatusChangeDate','PurchaseContractDate','ListingContractDate']

for col in dates:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# %%
#flag columns with timeline inconsistencies

df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']

#list after purchase flag
df['negative_timeline_flag'] = (df['ListingContractDate'] > df['PurchaseContractDate'])

#printing totals for the flagged cols
print(df[['listing_after_close_flag', 'purchase_after_close_flag', 'negative_timeline_flag']].sum())

# %%
#flag missing close price

df['invalid_closeprice_flag'] = (
    (df['ClosePrice'] <= 0) | df['ClosePrice'].isna() )

print(df[['invalid_closeprice_flag']].sum())

# %%
#flag invalid numeric values for house layout

df['invalid_house_flag'] = (
    (df['LivingArea'] <= 0) |
    (df['BedroomsTotal'] < 0) |
    (df['BathroomsTotalInteger'] < 0)
)

print(df[['invalid_house_flag']].sum())

# %%
#flag rows with invalid geographic values

df['missing_geo_flag'] = (
    (df['Latitude'].isna()) |
    (df['Longitude'].isna()) |
    (df['Latitude'] == 0) |
    (df['Longitude'] == 0)
)
df['outofbounds_flag'] = (
    (df['Latitude'] < 32) | 
    (df['Latitude'] > 42) |
    (df['Longitude'] < -125) |
    (df['Longitude'] > -114) |
    (df['StateOrProvince'] != 'CA')
)

print(df[['missing_geo_flag']].sum())
print(df[['outofbounds_flag']].sum())

# %%
#counting % nulls per column
null_pct = df.isna().mean() * 100

null_pct.to_frame(name='pct_null')
null_pct = null_pct.sort_values(ascending=False)


# %%


# %%


# %%


# %% [markdown]
# Making a cleaned df dataset while dropping some high missing columns, imputing some missing values, and removing columns not to be used for analysis. columns missing >70% of data had little information that was not already covered by similar categories.

# %%
df_imp = df

# %%
#removing columns over 70% missing
over70_cols = null_pct[null_pct > 70].index.tolist()

# %%
df_imp = df_imp.drop(columns= over70_cols)

# %%
#remove 3 rows missing close price
df_imp = df_imp[df_imp['invalid_closeprice_flag'] == 0]

# %%
#remove 103 rows with latlong outside CA or state not CA 
df_imp = df_imp[df_imp['outofbounds_flag']==0]

# %%
print(df.shape)
print(df_imp.shape)

# %%
#Impute the mean for living area, bedrooms, bathrooms when missing or invalid
invalid_rules = {
    'LivingArea': df_imp['LivingArea'] <= 0,
    'BedroomsTotal': df_imp['BedroomsTotal'] < 0,
    'BathroomsTotalInteger': df_imp['BathroomsTotalInteger'] < 0,
}

for col, invalid in invalid_rules.items():
    good = df_imp[col].where(~invalid)     # invalid values become NaN
    mean_val = good.mean()                   # mean() skips NaN, so only valid values count
    df_imp[col] = good.fillna(mean_val)    # fills invalid aand originally missing values

    print(col, "| mean used:", round(mean_val, 2), "| replaced:", invalid.sum())

#rounding bedrooms and bathrooms    
for col in ['BedroomsTotal', 'BathroomsTotalInteger']:
    df_imp[col] = df_imp[col].round()

# %%

#assuming that missing on yes/no category means "no"

yn_cols = ["PoolPrivateYN", "ViewYN", "NewConstructionYN"]

# Flag which rows were originally blank
for col in yn_cols:
    df_imp[col + "_was_missing"] = df_imp[col].isna()

df_imp[yn_cols] = df_imp[yn_cols].fillna(False)

# %%
#imputing missing stories with median of each subtype

df_imp["Stories_was_missing"] = df_imp["Stories"].isna()

# Median within each property type
df_imp["Stories"] = df_imp["Stories"].fillna(
    df_imp.groupby("PropertySubType")["Stories"].transform("median")
)

#any property type with no stories data at all gets the overall median
df_imp["Stories"] = df_imp["Stories"].fillna(df_imp["Stories"].median())

# %%
print(df_imp[["PoolPrivateYN", "ViewYN", "NewConstructionYN", "Stories"]].isna().sum())

# %%
#recounting % nulls per column
null_new = df_imp.isna().mean() * 100

null_new.to_frame(name='pct_null')
null_new = null_new.sort_values(ascending=False)

# %%
null_new.head(60)


