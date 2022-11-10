"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        - This Python script generate a building_permits_points.shp file, 
          that contain all geometry coordinates of our cleaned building permits dataset
    
    Note:
        - This script is run during install.py script, but you can run it to update your shape file
"""
# Import ours constants
from constants import *

# Libraries
import fiona
import pandas as pd
from tqdm import tqdm

dataset = pd.read_csv(DATASETS+"Building_Permits.csv", low_memory=False)

# define schema
schema = {
    'geometry': 'Point',
    'properties': [('Address', 'str')]
}

# open a fiona object
pointShp = fiona.open(SHAPEOUTS + 'building_permits_points.shp', mode='w', driver='ESRI Shapefile',
                      schema=schema, crs="EPSG:4326")
# For now we use EPSG:4326, but later it would be better to transform it as EPSG:2227
# That fit with San Francisco Zone


# iterate over each row in the dataframe and save record
for index, row in tqdm(dataset.iterrows(), desc="Generating : building_permits_points.shp", total=len(dataset)):
    rowDict = {
        'geometry': {'type': 'Point',
                     'coordinates': (row.Lat, row.Lon)},
        'properties': {'Address': row.Address},
    }
    pointShp.write(rowDict)
# close fiona object
pointShp.close()
