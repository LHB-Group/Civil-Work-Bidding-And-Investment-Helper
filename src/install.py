"""
Python script to download and create all necessaries.
"""
# Standards imports
import zipfile
import glob
import os
from tqdm import tqdm  # Used for progress bar

# Personnal modules
from constants import DOCUMENTS, SHAPEOUTS, DATASETS, TRACKING
from functions import dl_progress_bar

# Urls for requests
url_SF_Buildings_Permits = 'https://data.sfgov.org/api/views/i98e-djp9/rows.csv?accessType=DOWNLOAD'
url_SF_Buildings_FootPrints = 'https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=Shapefile'

# the order is important for folders hierarchy
folders = [DOCUMENTS, SHAPEOUTS, DATASETS, TRACKING]

for folder in tqdm(folders, desc="Creating folders : "):
    try:
        os.mkdir(folder)
    except FileExistsError:
        print("Folder: " + folder + " already exist")
        pass

# Download San Francisco Buildings Permits
dl_progress_bar(url_SF_Buildings_Permits, folder=DATASETS,
                file="Building_Permits.csv", filesize=450_000_000) # Usually you should be able to get file size inside request.header if website owner provide it

# Download San Francisco Buildings Footprints
dl_progress_bar(url_SF_Buildings_FootPrints, folder=SHAPEOUTS,
                file="SF_Buildings_FootPrints.zip", filesize=80_000_000) # Usually you should be able to get file size inside request.header if website owner provide it

# Extracte SF_Buildings_FootPrints.zip
with zipfile.ZipFile(SHAPEOUTS + "SF_Buildings_FootPrints.zip") as zf:
    for member in tqdm(zf.infolist(), desc='Extracting : SF_Buildings_FootPrints.zip'):
        try:
            zf.extract(member, SHAPEOUTS)
        except zipfile.error as e:
            pass

os.chdir(SHAPEOUTS)
for file in tqdm(glob.glob("geo_export_*"), desc="Renaming :"):
    extension = file.split(".")[1]
    os.rename(file, 'SF_Buildings_FootPrints.' + extension)

# Delete zip folder
os.remove("SF_Buildings_FootPrints.zip")
os.chdir("../../src")

# Run script that will apply some data cleaning and add some basics features to our dataset
os.system("python building_permits.py")

# This Python script generate a building_permits_points.shp file, 
# that contain all geometry coordinates of our cleaned building permits dataset
os.system("python building_permits_points.py")

# We build the final building_permits.csv with area of each buildings
os.system("python building_permits_areas.py")

print("Project Installation is Done !!")

