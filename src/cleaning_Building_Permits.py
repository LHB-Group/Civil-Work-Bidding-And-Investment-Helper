# Libraries
import pandas as pd
import re
import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="Building Permits San Francisco")

dataset = pd.read_csv("../documents/Building_Permits.csv")

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


