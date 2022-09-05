"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        - This script apply some data cleaning and add some basics features to our dataset for future use.
          we work from official San Francisco dataset: https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9
          At the end of this script you should have a new csv file inside the Datasets folder, called Building_Permits.csv
    
    Note:
        - The official San Francisco dataset is updated weekly

"""

# LIBRARIES
import re # regex lib
import cpi # to apply inflation
import pandas as pd
import numpy as np
from functions import re_category, text_split, text2int, cat_stories
from scipy.special import boxcox1p

# We get San Francisco dataset from official source
# dataset source : https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9
print("Retrieving dataset from data.sfgov.org (this can take several minutes)")
source = 'https://data.sfgov.org/api/views/i98e-djp9/rows.csv?accessType=DOWNLOAD'
dataset = pd.read_csv(source, low_memory = False)

print("\nKeeping permit of type 1 & 2 ...\n")
# We only want to work on permit of type 1 & 2
permit_type_mask = dataset["Permit Type"] < 3
dataset = dataset.loc[permit_type_mask, :]

print("\nKeeping permit with complete status\n")
# We only want to want to keep permit with complete status
permit_complete_mask = dataset["Current Status"] == "complete"
dataset = dataset.loc[permit_complete_mask, :]

print("\nKeeping only : 1 family dwelling, 2 family dwelling and apartments for the feature [Proposed Use]\n")
# We keep only : 1 family dwelling, 2 family dwelling and apartments for the feature ["Proposed Use"]
family_dwelling_mask1 = dataset["Proposed Use"] == "1 family dwelling"
family_dwelling_mask2 = dataset["Proposed Use"] == "2 family dwelling"
appartments_mask = dataset["Proposed Use"] == "apartments"
Proposed_Use_mask = family_dwelling_mask1 | family_dwelling_mask2 | appartments_mask
dataset = dataset.loc[Proposed_Use_mask,:]

print("\nKeeping known Estimated Costs\n")
# We only want to keep known Estimated Costs
dataset.dropna(subset=['Estimated Cost'], inplace= True)

print("\nReformating Zipcode\n")
# Reformating Zipcode
dataset['Zipcode'] = dataset['Zipcode'].replace(np.nan, 0.0).astype(str)
dataset['Zipcode'] = dataset['Zipcode'].apply(lambda x: x[:-2])
dataset['Zipcode'] = dataset['Zipcode'].replace('0','')

print("\nFormating the [street name] feature\n")
# Format the [street name] feature to fit with Nominatim call
for row in range(len(dataset.values)):
    if dataset["Street Name"].iloc[row][0] == "0":
        dataset["Street Name"].iloc[row] = dataset["Street Name"].iloc[row][1:]

    if dataset["Street Suffix"].iloc[row] == "Bl":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Bl","Blvd")

    if dataset["Street Suffix"].iloc[row] == "Tr":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Tr","Terrace")
        
    if dataset["Street Suffix"].iloc[row] == "Cr":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Cr","Circle")

print("\nReplacing 'nan' values inside [Street Suffix] by an empty string " "\n")
# Replace "nan" values inside [Street Suffix] by an empty string " "
dataset["Street Suffix"].fillna(" ", inplace=True)

print("\nFormating [street Suffix] for rows with [Street Name] = 'La Play' to fit Geopy\n")
# Format [street Suffix] for rows with [Street Name] = "La Play" to fit Geopy
mask = dataset["Street Name"] == "La Playa"
dataset.loc[mask, "Street Suffix"] = "Street"

print("\nCreating [Address] feature\n")
# Creating [Address] feature
dataset['Address'] = dataset["Street Number"].astype(str) + " " + dataset["Street Name"] + " " + dataset["Street Suffix"] + ', San Francisco, CA ' + dataset['Zipcode']

print("\nReformating [Proposed Construction Type]\n")
# Proposed construction type has values of '5.0', '1.0', '5', '2.0', '3.0', '4.0', '1', '3', '2', '4', 'III'
# Values for proposed construction type are modifed below in three steps
# 1 - change cat. III to 3
# 2 - fillna values with 99
# 3 - group float and integer values together and save it as str since they are categories
col_ = 'Proposed Construction Type'
dataset[col_] = dataset[col_].apply(lambda x : 3  if x =='III' else x)
dataset[col_] = dataset[col_].fillna('99')
dataset[col_] = dataset[col_].astype(float).astype(int).astype(str)

print("\nFormating date feature to datetime type\n")
# Formating date feature to datetime
date_cols = [col for col in dataset.columns if 'date' in col.lower()]
for col in date_cols:
    dataset.loc[:,col] = pd.to_datetime(dataset[col], errors = 'coerce')
    #we used errors = coerce, as there are some values/outliers out of the bound 

print("\nCalculating estimated construction duration in days and process time of permit demands of city of SF in days\n")
# Calculating estimated construction duration in days and process time of permit demands of city of SF in days    
dataset['Duration_construction_days'] = (dataset['Completed Date'] - dataset['Issued Date']).dt.days
dataset['Process_time_days'] = (dataset['Issued Date'] - dataset['Filed Date']).dt.days


print("\nAdding a [Year] feature\n")
# Adding a [Year] feature
dataset['Year']=dataset['Permit Creation Date'].dt.year

print("\nApplying inflation\n")
# Adding new feature with adjusted prices according to US dollar inflation
#note: cpi quickly adjusts US dollars for inflation using the consumer price index CPI
#see ref. https://towardsdatascience.com/the-easiest-way-to-adjust-your-data-for-inflation-in-python-365490c03969
cpi.update()

dataset["Est_Cost_Infl"] = dataset.apply(lambda x: cpi.inflate(x["Estimated Cost"], x["Year"]), axis=1)
dataset["Rev_Cost_Infl"] = dataset.apply(lambda x: cpi.inflate(x["Revised Cost"] , x["Year"]), axis=1)

#creating new features with logarithmic of estimated cost + inflation
dataset["Est_Cost_Infl_log10"] = np.log10(dataset["Est_Cost_Infl"])

print("\nCreating [Lat] and [Lon] features\n")
# Split our initial dataset in 2 distinct datasets : "permit with no location" and "permit with location"
missingLocation_mask = dataset["Location"].isna()

dataset_noLocation = dataset.loc[missingLocation_mask, :]
dataset_withLocation = dataset.drop(dataset_noLocation.index)

# Delete rows with unknown ["Street Name"], we won't be able to obtain the coordinates
dataset_noLocation = dataset_noLocation[dataset_noLocation["Street Name"] != "Unknown"]

# Get coordinates between ( ) to create ou ["Lat"] and ["Lon"] Features
pattern = "\((.*)\)"
lat_list = []
lon_list = []
for row in dataset_withLocation["Location"].values:
    lat_list.append(re.search(pattern, row).group(1).split(" ")[0])
    lon_list.append(re.search(pattern, row).group(1).split(" ")[1])

# create the lat and lon features for [dataset_withLocation] dataset
dataset_withLocation["Lat"] = lat_list
dataset_withLocation["Lon"] = lon_list

# Get ["Lat"] and ["Lon"] from Nominatim
lat_list = []
lon_list = []
for row in range(len(dataset_noLocation.values)):
    address = str(dataset_noLocation["Street Number"].iloc[row]) + " " + dataset_noLocation["Street Name"].iloc[row] + dataset_noLocation["Street Suffix"].iloc[row] + ', San Francisco, CA ' + dataset_noLocation["Zipcode"].iloc[row]
    try:
        location = geolocator.geocode(address, language="en")
        lat_list.append(location.latitude)
        lon_list.append(location.longitude)
    except:
        try :
            address = str(dataset_noLocation["Street Number"].iloc[row]) +" "+ dataset_noLocation["Street Name"].iloc[row] + ', San Francisco, CA ' +  dataset_noLocation["Zipcode"].iloc[row]
            location = geolocator.geocode(address, language="en")
            lat_list.append(location.latitude)
            lon_list.append(location.longitude)
        except:
            # If Nominatim doesn't find the information so we fill with nan value
            lat_list.append(np.nan)
            lon_list.append(np.nan)        

# Create the lat and lon features for [dataset_noLocation] dataset
dataset_noLocation["Lat"] = lat_list
dataset_noLocation["Lon"] = lon_list

# We remove all permits where we didn't success to retrive coordinates
loc_isna = ~dataset_noLocation["Lat"].isna()
dataset_noLocation = dataset_noLocation.loc[loc_isna,:]

# We concat our 2 splited datasets
dataset = pd.concat([dataset_withLocation, dataset_noLocation], axis=0)
dataset['Lat'] = dataset['Lat'].astype(float)
dataset['Lon'] = dataset['Lon'].astype(float)

# Creating a new feature with Lat * Lon
dataset['lat_lon']=dataset['Lat']*dataset['Lon']

print("\nPreprocessing [Number of Proposed Stories] feature - Reverifying number of stories\n")
# Manipulations on Number of Proposed Stories feature
# there are some mistaken values in number of proposed stories. we will use description column to fix some of them
# let's take rows where there less than 1 and more than 15 stories
mask_ps1 = dataset['Number of Proposed Stories'] > 15 
mask_ps2 = dataset['Number of Proposed Stories'] < 1
mask_ps3 = dataset['Number of Proposed Stories'].isna()

# Let's find description rows where we have 'story' word
mask_ps4 = dataset['Description'].fillna('empty').str.contains('story')

# Taking rows (m_ps1 or m_ps1) and m_ps3
mask_ps = ( mask_ps1 | mask_ps2 | mask_ps3 ) & mask_ps4

col_ = 'Number of Proposed Stories'
#a new columns for the manipulation
dataset[col_+ '_'] = dataset[col_]

# Adding story numbers on the masked rows
dataset.loc[mask_ps,col_+ '_'] = dataset.loc[mask_ps,'Description'].apply(lambda x:text_split(x) )
dataset.loc[mask_ps,col_+ '_']= dataset.loc[mask_ps,col_+ '_'].apply(lambda x : text2int(x))
dataset.loc[:,col_+ '_']= dataset.loc[:,col_+ '_'].astype(float)

# Adding a column with story number categories
col_ ='Number of Proposed Stories_'
dataset[col_+'cat'] = dataset[col_].apply(lambda x: cat_stories(x)).astype(str)

#following masks have been applied after having data analyses performed.
# see the notebok on exploratory data analysis for more details
m_out0 = dataset['Est_Cost_Infl_log10'] <= dataset['Est_Cost_Infl_log10'].quantile(0.99)
m_out1 = dataset['Est_Cost_Infl_log10'] >= dataset['Est_Cost_Infl_log10'].quantile(0.01)
m_out2 = dataset['Proposed Units'] <= dataset['Proposed Units'].quantile(0.99)
m_out3 = dataset['Proposed Units'] >= dataset['Proposed Units'].quantile(0.01)
m_out4 = dataset['Number of Proposed Stories_'] <= 15
m_out = m_out0 & m_out1 & m_out2 & m_out3 & m_out4
#removing outliers
dataset=dataset.loc[m_out,:]

print("\nPreprocessing [Neighborhoods - Analysis Boundaries] feature - Adding 'other' category\n")
# Feature for neighborhood categoriess less than 20 data, we use category 'other'
col_ = "Neighborhoods - Analysis Boundaries"
dataset[col_+'_'] = re_category (dataset[col_] , 20, 'Other' )

print("\nPreprocessing [Proposed Construction Type] feature - Adding a category of '99'\n")
# For category of [proposed construction type] with less than 20 data, we use category '99'
col_ = 'Proposed Construction Type'
dataset[col_+'_'] = re_category (dataset[col_] , 20, '99' )

print("\nAdding featues with boxcox transformation\n")
# Adding columns with boxcox transformation
dataset['Number of Proposed Stories_cat_f']=pd.factorize(dataset['Number of Proposed Stories_cat'])[0]
dataset['Proposed Use_f']=pd.factorize(dataset['Proposed Use'])[0]
dataset['Proposed Construction Type_f']=pd.factorize(dataset['Proposed Construction Type_'])[0]

skewed_features = ['Number of Proposed Stories', 'Number of Proposed Stories_cat_f',
         'Proposed Construction Type_f',  'Proposed Units', 'Proposed Use_f',
         'Duration_construction_days']

lam = 0.10 #lan value obtained after trial and error. If 0 is used, boxcox1p becomes same with np.log1p 
for feat in skewed_features:
    dataset[feat+'_bct'] = boxcox1p(dataset[feat].fillna(dataset[feat].mean()), lam)

print("\nExporting cleaned dataset to csv\n")
#Export cleaned dataset to csv
try:
    dataset.to_csv('../Documents/Datasets/Building_Permits.csv',index=False)
except: #if folder was not created, output .csv file will be exported to the same folder.
    dataset.to_csv('Building_Permits.csv',index=False)
print("\nDataset available on Datasets folder\n")