# %%
import pandas as pd

#geopandas for high school district shapefile
import geopandas as gpd

# %%
sold = pd.read_csv('data/sold_clean.csv', low_memory = False)
listing = pd.read_csv('data/listing_clean.csv', low_memory = False)

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

# %% [markdown]
# ### Feature Engineering

# %%
def create_metrics(df):
    # Measures negotiation strength
    df['PriceRatio'] = (df['ClosePrice']/df['ListPrice'])
    
    # Normalizes price across sizes
    df['PPSF'] = (df['ClosePrice']/df['LivingArea'])
    
    # For Time Series Analysis
    df['Year'] = df['CloseDate'].dt.year
    df['Month'] = df['CloseDate'].dt.month
    df['YrMo'] = df['CloseDate'].dt.to_period('M')
    
    # Captures full price reduction history
    df['CloseListRatio'] = (df['ClosePrice']/df['OriginalListPrice'])
    
    # Measures time from listing to accepted offer
    df['ListToContractDays'] = (df['PurchaseContractDate'] - df['ListingContractDate'])
    
    # Escrow and closing period duration
    df['ContractToCloseDays'] = (df['CloseDate']- df['PurchaseContractDate'])
    
    return df

# %%
sold = create_metrics(sold)
listing = create_metrics(listing)

# %%
key_metrics = ['PriceRatio','PPSF','DaysOnMarket',
               'Year','Month','YrMo','CloseListRatio',
               'ListToContractDays','ContractToCloseDays']
#output to confirm new columns populated properly
sold[key_metrics].head(10)

# %% [markdown]
# ### Adding school districts by Longitude/Latitude

# %%
districts = gpd.read_file("data/DistrictAreas2425.shp")


# %%

def add_district(df):
    # 2. Turn each listing's lat/lon into a point
    points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",  # standard lat/lon (WGS84)
    )

    # 3. Match the point's coordinate system to the shapefile's
    points = points.to_crs(districts.crs)

    # 4. Spatial join: find which district polygon each point falls within
    joined = gpd.sjoin(
        points,
        districts[["DistrictNa", "geometry"]],
        how="left",
        predicate="within",
    )

    # 5. Clean up: remove the join index, drop duplicate rows if polygons overlap, rename
    joined = joined[~joined.index.duplicated(keep="first")]
    joined = joined.rename(columns={"DistrictNa": "SchoolDistrictFromShp"})

    # 6. Back to a regular DataFrame without the geometry column
    df = pd.DataFrame(joined.drop(columns=["geometry", "index_right"], errors="ignore"))
    
    return df

# %%
sold = add_district(sold)
listing = add_district(listing)

# %% [markdown]
# ### Segment Analysis
# PropertyType and PropertySubType
# CountyOrParish and MLSAreaMajor
# ListOfficeName and BuyerOfficeName (for competitive intelligence)
# 

# %%
#only comparing market times and not time of year for segment analysis
key_metrics = ['PriceRatio','PPSF','DaysOnMarket','CloseListRatio',
               'ListToContractDays','ContractToCloseDays']

# %%
sold.groupby("PropertySubType")[key_metrics].agg(["median"]).T

# %% [markdown]
# One single row in listing where PropertySubType = Apartment is causing a lot of NaN's in the summary table, So I remove it.

# %%
listing = listing[listing['PropertySubType'] != 'Apartment']

# %%
listing.groupby("PropertySubType")[key_metrics].agg(["median"]).T

# %%
sold.groupby("CountyOrParish")[key_metrics].agg(["median"]).T

# %%
sold.groupby("ListOfficeName")[key_metrics].agg(["median"]).T

# %%
sold.groupby("BuyerOfficeName")[key_metrics].agg(["median"]).T


