# Libraries
import pandas as pd
import re
import numpy as np
from geopy.geocoders import Nominatim
import cpi

geolocator = Nominatim(user_agent="Building Permits San Francisco")

db_v1='https://drive.google.com/file/d/1XoqPujIOGHQStuAqM6Gzyqbkha4c5Y96/view?usp=sharing'
fname1 = db_v1
fname1 = 'https://drive.google.com/uc?id=' + fname1.split('/')[-2]
dataset = pd.read_csv(fname1)

# Delete 10 last columns that we won't use
dataset = dataset.iloc[:,:-10]

# We only want to work on permit of type 1 & 2
permit_type_mask = dataset["Permit Type"] < 3
dataset = dataset.loc[permit_type_mask, :]

# We only want to keep permit with complete status
permit_complete_mask = dataset["Current Status"] == "complete"
dataset = dataset.loc[permit_complete_mask, :]

# Deletion of features with 90% of missing value
useless_features = [feature for feature in dataset if (dataset[feature].isnull().sum()/len(dataset) > 0.9)]
dataset.drop(useless_features, axis=1, inplace=True)

# Delete unknown Estimated Costs
dataset.dropna(subset=['Estimated Cost'], inplace= True)

# Formating the [street name] feature to fit with Nominatim call
for row in range(len(dataset.values)):
    if dataset["Street Name"].iloc[row][0] == "0":
        dataset["Street Name"].iloc[row] = dataset["Street Name"].iloc[row][1:]
    if dataset["Street Suffix"].iloc[row] == "Bl":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Bl","Blvd")
    if dataset["Street Suffix"].iloc[row] == "Tr":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Tr","Terrace")
    if dataset["Street Suffix"].iloc[row] == "Cr":
        dataset["Street Suffix"].iloc[row] = dataset["Street Suffix"].iloc[row].replace("Cr","Circle")

# Replace "nan" values inside [Street Suffix] by an empty string " "
dataset["Street Suffix"].fillna(" ", inplace=True)

# Formate [street Suffix] for rows with [Street Name] = "La Play" to fit Geopy
mask = dataset["Street Name"] == "La Playa"
dataset.loc[mask, "Street Suffix"] = "Street"

# Create [Address] feature
dataset["Address"] = dataset["Street Number"].astype(str) + " " + dataset["Street Name"] + " " + dataset["Street Suffix"]

# Split our initial dataset in 2 distinct datasets : "permit with no location" and "permit with location"
missingLoc = dataset["Location"].isna()
permit_noLoc = dataset.loc[missingLoc, :]
permit_withLoc = dataset.drop(permit_noLoc.index)

# Delete rows with unknown ["Street Name"], we won't be able to obtain the coordinates
permit_noLoc = permit_noLoc[permit_noLoc["Street Name"] != "Unknown"]

# Get coordinates between ( ) to create ou ["Lat"] and ["Lon"] Features
pattern = "\((.*)\)"
lat_list = []
lon_list = []
for row in permit_withLoc["Location"].values:
    lat_list.append(re.search(pattern, row).group(1).split(" ")[0])
    lon_list.append(re.search(pattern, row).group(1).split(" ")[1])

# create the lat and lon features for [permit_withLoc] dataset
permit_withLoc["Lat"] = lat_list
permit_withLoc["Lon"] = lon_list

print('Get ["Lat"] and ["Lon"] from Nominatim')
# Get ["Lat"] and ["Lon"] from Nominatim
lat_list = []
lon_list = []
for row in range(len(permit_noLoc.values)):
    address = permit_noLoc["Address"].iloc[row] + " SF US"
    try:
        location = geolocator.geocode(address, language="en")
        lat_list.append(location.latitude)
        lon_list.append(location.longitude)
    except:
        try :
            address = str(permit_noLoc["Street Number"].iloc[row]) +" "+ permit_noLoc["Street Name"].iloc[row] + " SF US"
            location = geolocator.geocode(address, language="en")
            lat_list.append(location.latitude)
            lon_list.append(location.longitude)
        except:
            # If Nominatim doesn't find the information so we fill with nan value
            lat_list.append(np.nan)
            lon_list.append(np.nan)        

# Create the lat and lon features for [permit_noLoc] dataset
permit_noLoc["Lat"] = lat_list
permit_noLoc["Lon"] = lon_list

# We remove all permits where we didn't success to retrive coordinates
loc_isna = ~permit_noLoc["Lat"].isna()
permit_noLoc = permit_noLoc.loc[loc_isna,:]

# We concat our 2 splited datasets
cleaned_dataset = pd.concat([permit_withLoc, permit_noLoc], axis=0)

# We delete the ['Location'] Feature because we don't need it anymore
cleaned_dataset.drop(['Location'], axis=1, inplace=True)

# Export the dataset to csv version 3 (do not delete)
cleaned_dataset.to_csv('Building_Permits_v3.csv',index=False)

"""
    Database version 4 - 12/08/22
"""
db_v3= 'https://drive.google.com/file/d/1W1V3_hl7yqbWyXF8w7mZSDTxCOx3GMzf/view?usp=sharing'
fname1 = db_v3
fname1 = 'https://drive.google.com/uc?id=' + fname1.split('/')[-2]
dataset = pd.read_csv(fname1)

def re_category (ds,counts, repl_ ):
    #It replaces the categories that are not sufficiently presented in the dataseries
    #It also fills NaN values with the defined category value
    n_count = ds.value_counts()
    m_ng = ds.isin (n_count.index[n_count.values < counts])
    ds[m_ng] = repl_
    ds.fillna(repl_,inplace=True)
    return ds.astype('str')

#Adjusting date columns to datetime
date_cols = [col for col in dataset.columns if 'date' in col.lower()]

for col in date_cols:
    dataset.loc[:,col] = pd.to_datetime(dataset[col], errors = 'coerce')
    #we used errors = coerce, as there are some values/outliers out of the bound 

#calculating estimated construction duration in days and process time of permit demands of city of SF in days    
dataset['Duration_construction_days'] = (dataset['Completed Date'] - dataset['Issued Date']).dt.days
dataset['Process_time_days'] = (dataset['Issued Date'] - dataset['Filed Date']).dt.days

#adding a year column
dataset['Year']=dataset['Permit Creation Date'].dt.year

#adding new columns with adjusted prices according to US dollar inflation
#note: cpi quickly adjusts US dollars for inflation using the consumer price index CPI
#see ref. https://towardsdatascience.com/the-easiest-way-to-adjust-your-data-for-inflation-in-python-365490c03969
cpi.update()

dataset["Est_Cost_Infl"] = dataset.apply(lambda x: cpi.inflate(x["Estimated Cost"], x["Year"]), axis=1)
dataset["Rev_Cost_Infl"] = dataset.apply(lambda x: cpi.inflate(x["Revised Cost"] , x["Year"]), axis=1)

#creating new features with logarithmic of estimated cost + inflation
dataset["Est_Cost_Infl_log10"] = np.log10(dataset["Est_Cost_Infl"])
dataset["Est_Cost_Infl_loge"] = np.log(dataset["Est_Cost_Infl"])

#creating a new feature with lat times lon
dataset['lat_lon']=dataset['lat']*dataset['lon']

#for neighborhood categoriess less than 20 data, we use category 'other'
col_ = "Neighborhoods - Analysis Boundaries"
dataset[col_+'_']=re_category (dataset[col_] , 20, 'Other' )

#for category of proposed construction type with less than 20 data, we use category '99'
col_ = 'Proposed Construction Type'
dataset[col_+'_']=re_category (dataset[col_] , 20, '99' )

#proposed construction type has values of '5.0', '1.0', '5', '2.0', '3.0', '4.0', '1', '3', '2', '4', 'III'
#values for proposed construction type are modifed below in three steps
# 1 - change cat. III to 3
# 2 - fillna values with 99
# 3 - group float and integer values together and save it as str since they are categories
col_ = 'Proposed Construction Type'
dataset[col_]=dataset[col_].apply(lambda x : 3  if x =='III' else x)
dataset[col_]= dataset[col_].fillna('99')
dataset[col_]=dataset[col_].astype(float).astype(int).astype(str)

#Export to dataset to csv v4
#dataset.to_csv('Building_Permits_v4.csv',index=False)


"""
    Database version 7 - 17/08/22
"""
db_v4= 'https://drive.google.com/file/d/19ERs5bmAdxEfgUmTxgfIBhUoT6xPHzZy/view?usp=sharing'
fname1 = db_v4
fname1 = 'https://drive.google.com/uc?id=' + fname1.split('/')[-2]
dataset = pd.read_csv(fname1)


#for categories of proposed use with less than 20 data, we use category 'Other'
col_ = 'Proposed Use'
dataset[col_+'_']=re_category (dataset[col_] , 20, 'Other' )

#for categories of zipcode with less than 20 data, we use category 'Other'
col_ = 'Zipcode'
dataset[col_+'_']=re_category (dataset[col_] , 20, 'Other' )

#Manipulations on Number of Proposed Stories column
#there are some mistaken values in number of proposed stories. we will use description column to fix some of them
#let's take rows where there less than 1 and more than 15 stories
m_ps1 = dataset['Number of Proposed Stories'] > 15 
m_ps2 = dataset['Number of Proposed Stories'] < 1
m_ps3 = dataset['Number of Proposed Stories'].isna()
#let's find description rows where we have 'story' word
m_ps4 = dataset['Description'].fillna('empty').str.contains('story')
#taking rows (m_ps1 or m_ps1) and m_ps3
m_ps = ( m_ps1 | m_ps2 | m_ps3 ) & m_ps4

def text_split(x):
  #x will be sth similar to 'erect a two story 88 unit residential structure'
  #we do text partition with 'story' 
  #it returns tuple ('erect a two ', 'story', ' 88 unit residential structure')
  #then, we take the first value of tuple 
  #and then apply string manipulations to obtain floor number in text
  return x.partition('story')[0].replace('-',' ').split(' ')[-2]

def text2int (x):
  #converting text to number for the possible cases
  x = x.lower()
  if 'one' in x:
    y = 1
  elif 'two' in x:
    y= 2
  elif 'three' in x:
    y=3
  elif 'four' in x:
    y = 4
  elif 'five' in x:
    y = 5
  elif 'six' in x:
    y = 6
  elif 'seven' in x:
    y = 7
  elif 'eight' in x:
    y = 8
  elif 'nine' in x:
    y = 9
  elif  'ten' in x:
    y = 10
  elif  'eleven' in x:
    y = 11
  else:
    try : 
      y = int(x)
    except :
      y = np.nan
  return y

col_ = 'Number of Proposed Stories'
#a new columns for the manipulation
dataset[col_+ '_'] = dataset[col_]

#adding story numbers on the masked rows
dataset.loc[m_ps,col_+ '_']=   dataset.loc[m_ps,'Description'].apply(lambda x:text_split(x) )
dataset.loc[m_ps,col_+ '_']=   dataset.loc[m_ps,col_+ '_'].apply(lambda x : text2int(x))
dataset.loc[:,col_+ '_']= dataset.loc[:,col_+ '_'].astype(float)

#adding a column with story number categories
def cat_stories (st): 
    if st < 3 :
      y = '0-2 stories'
    elif st< 5 :
      y = '3-4 stories'
    elif st < 8 :
      y = '5-7 stories'
    elif st < 10 :
      y = '8-9 stories'
    else:
      y = 'More than 10 stories'
    return y

col_ ='Number of Proposed Stories'
dataset[col_+'_cat'] = dataset[col_].apply(lambda x: cat_stories(x)).astype(str)


#Adding columns with boxcox transformation
#from scipy import stats
#from scipy.stats import norm, skew
from scipy.special import boxcox1p

dataset['Number of Proposed Stories_cat_f']=pd.factorize(dataset['Number of Proposed Stories_cat'])[0]
dataset['Proposed Use_cat_f']=pd.factorize(dataset['Proposed Use_cat'])[0]

skewed_features = ['Number of Proposed Stories', 'Number of Proposed Stories_cat_f',
         'Proposed Construction Type',  'Proposed Units', 'Proposed Use_cat_f',
         'Duration_construction_days']

lam = 0.10 #value obtained after trial and error. If 0 is used, boxcox1p becomes same with np.log1p 
for feat in skewed_features:
    dataset[feat+'_bct'] = boxcox1p(dataset[feat].fillna(dataset[feat].mean()), lam)

#following masks have been applied after having data analyses performed.
# see the notebok on exploratory data analysis for more details
m_out0 = dataset['Est_Cost_Infl_log10'] <= 8.0
m_out1 = dataset['Est_Cost_Infl_log10'] >= 3.5
m_out2 = dataset['Proposed Units'] <= 200
m_out3 = dataset['Proposed Units'] > 0
m_out4 = dataset['Number of Proposed Stories_'] <= 15
m_out = m_out0 & m_out1 & m_out2 & m_out3 & m_out4
#removing outliers
dataset=dataset.loc[m_out,:]

#Export to dataset to csv v7
dataset.to_csv('Building_Permits_v7.csv',index=False)