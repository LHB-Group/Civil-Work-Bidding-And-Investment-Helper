"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        - This Python script generate a building_permits_points.shp file, 
          that contain all geometry coordinates of our cleaned building permits dataset
    
    Note:
        - You don't need to run this script if the file exists or already updated
"""

#Libraries
import fiona
import pandas as pd
import geopandas as gpd
import numpy as np

dataset = pd.read_csv("../Documents/Datasets/Building_Permits.csv")

# define schema
schema = {
    'geometry':'Point',
    'properties':[('Address','str')]
}

#open a fiona object
pointShp = fiona.open('../Documents/ShapeOuts/building_permits_points.shp', mode='w', driver='ESRI Shapefile',
          schema = schema, crs = "EPSG:4326")

#iterate over each row in the dataframe and save record
for index, row in dataset.iterrows():
    rowDict = {
        'geometry' : {'type':'Point',
                     'coordinates': (row.Lat,row.Lon)},
        'properties': {'address' : row.Address},
    }
    pointShp.write(rowDict)
#close fiona object
pointShp.close()