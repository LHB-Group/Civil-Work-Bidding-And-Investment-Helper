"""
    authors: 
        - Baptiste Cournault
        - Hicham Mrani
        - Levent Isbiliroglu
    
    Description:
        - This Python script compute all steps needed to generate area feature
    
    Note:
        - for the following computer configuration, the matching polygon step take 1:30 hours:
            RAM: 8 Go
            Processor: Intel® Core™ i7-10750H CPU @ 2.60GHz x 12 
          we go through 6712 lines * 177 023 lines that why it's take a lot of time
          we optimised this steps with multi-threading
"""


import time
import json
import pandas as pd
import geopandas as gpd
import numpy as np
import fiona
import concurrent.futures
from shapely.geometry import shape, Polygon, Point
from functions import get_polygon_list


# Get geometry files
building_permits_locations = gpd.read_file(
    '../Documents/ShapeOuts/building_permits_points.shp')
footprint_buildings = gpd.read_file(
    '../Documents/ShapeOuts/SF_Buildings_FootPrints.shp')

# Convert points list in points serie
points_serie = gpd.GeoSeries(building_permits_locations["geometry"])
# Convert polygons list in polygons serie
polygons_serie = gpd.GeoSeries(footprint_buildings["geometry"])

# For both series we use the same CRS, the one used for San Francisco buildings footprints
# CRS: https://docs.qgis.org/2.8/en/docs/gentle_gis_introduction/coordinate_reference_systems.html
# SF CRS -> WGS84: https://en.wikipedia.org/wiki/World_Geodetic_System#WGS84
points_serie = points_serie.to_crs(polygons_serie.crs)

# Split our serie of points in several samples
splited_points = np.split(points_serie, [
                          500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000], axis=0)

# We Retrieve the polygon matching with a determined building permit point
print('We Retrieve the polygon matching with a determined building permit point (can take several hours)')
polygons = []
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor() as e:
    polygons = list(e.map(get_polygon_list, splited_points)) 
print("--- %s seconds ---" % (time.time() - start_time))

geometry_polygons_list = [feature for result in polygons for feature in result]

# Convert polygon to crs 2227 to work with foots metrics in the area of San Francisco
# Source: https://maps.omniscale.com/en/openstreetmap/epsg-2227

# [Example map in EPSG:2227 – NAD83 / California zone 3 (ftUS)](https://maps.omniscale.com/en/openstreetmap/epsg-2227)

# Area may be invalid for a geographic CRS using degrees as units; 
# So we use GeoSeries.to_crs() to project geometries to a planar CRS before calculating the area

# Transform the polygons with foots metrics based on EPSG:2227
print('transform the polygons with foots metrics based on EPSG:2227')
geometry_polygons_list = [geometry.to_crs(epsg=2227) for geometry in geometry_polygons_list]

# Calculate the area of each polygons
# In metric terms a square foot is a square with sides 0.3048 metres in length. One square foot is the equivalent to 0.09290304 square metres.
print('calculate the area of each polygons')
geometry_area_m2_list = [geometry.area * 0.09290304 for geometry in geometry_polygons_list]

# On évite de stocker l'objet geometrie et on récupère uniquement la valeur numérique
area_m2_list = []
for index in range(len(geometry_area_m2_list)):
    try:
        area_m2_list.append(geometry_area_m2_list[index].values[0])
    except IndexError:
        area_m2_list.append(np.nan)

# On évite de stocker l'objet geometrie et on récupère uniquement le shapely
polygons_list = []
for index in range(len(geometry_polygons_list)):
    try:
        polygons_list.append(geometry_polygons_list[index].values[0])
    except IndexError:
        polygons_list.append(np.nan)

# Feature creation
building_permits = pd.read_csv('../documents/Building_Permits.csv')
building_permits['Polygon'] = polygons_list
building_permits['Area_m2'] = area_m2_list


building_permits.to_csv('../documents/Building_Permits.csv', index=False)
