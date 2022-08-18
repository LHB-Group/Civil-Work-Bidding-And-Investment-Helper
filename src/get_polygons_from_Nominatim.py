import pandas as pd
import numpy as np
import requests
import time
import json
import concurrent.futures # for multi-threading

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

ENDPOINT_NOMINATIM =  'https://nominatim.openstreetmap.org/'
geolocator = Nominatim(user_agent="Building Permits San Francisco")

db_v5 = 'https://drive.google.com/file/d/1JSHTegHKvchjXDe4SkFzR07iRNVbZU5K/view?usp=sharing'

file_name = 'https://drive.google.com/uc?id=' + db_v5.split('/')[-2]

def get_geojson_list(addresses):
    """
        Get the features from Nominatim API
    """
    geojson_list = []

    for address in addresses:
      print(f'geojson_list taille = {len(geojson_list)}')
      print(f'{address}')
      try:
        response = requests.get(ENDPOINT_NOMINATIM + 'search', params={'q':address, 'format': 'geojson', 'polygon_geojson':'1'}).json()['features'][0]
        if "polygon" in response['geometry']['type'].lower() : 
          print(response['geometry']['type'].lower())
          geojson_list.append(json.dumps(response['geometry']))
        else:
          print("pas de polygon")
          geojson_list.append(np.nan)
      except:
        print("echec")
        geojson_list.append(np.nan)
      print('\n')
    return geojson_list

def main():
  dataset = pd.read_csv(file_name, low_memory=False)

  """ 
    We keep only : 1 family dwelling, 2 family dwelling and apartments for the feature ["Proposed Use"]
  """
  idx = np.where((dataset["Proposed Use"]=="1 family dwelling") | (dataset["Proposed Use"]=="2 family dwelling") | (dataset["Proposed Use"]=="apartments"))
  dataset = dataset.loc[idx]

  """
    Tallest buildings in SF = 61 floors
    [source wikipedia](https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_San_Francisco)
  """
  outliers_floors = dataset["Number of Proposed Stories"] < 61
  dataset = dataset[outliers_floors]

  """
    Delete Estimated cost Outliers
    cost <= 5 000 $
  """
  mask_cost = dataset["Est_Cost_Infl"] >= 5000
  dataset = dataset[mask_cost]

  #print(f'length dataset = {dataset.shape}')

  # refactoring Zipcode feature
  dataset['Zipcode'] = dataset['Zipcode'].replace(np.nan, 0.0).astype(str)
  dataset['Zipcode'] = dataset['Zipcode'].apply(lambda x: x[:-2])
  dataset['Zipcode'] = dataset['Zipcode'].replace('0','')

  # create the new feature that represent the complete address
  dataset['full_address'] = dataset['address'] + ', San Francisco, CA ' + dataset['Zipcode'].astype(str)

  # we split our dataset to use it inside multi-threading
  splited_address = np.split(dataset['full_address'].values, [500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000], axis=0)

  """
    We retrieve geojson thanks to Nominatim API
  """

  start_time = time.time()
  with concurrent.futures.ThreadPoolExecutor() as e:
      locations = list(e.map(get_geojson_list, splited_address))
  print("--- %s seconds ---" % (time.time() - start_time))

  print(f'splited list size {len(locations)}')

  """
    at the begining we splited our dataset in several list to optimise multi-trheading, so now we need to get our original shape list back
  """
  geojson_list = [feature for result in locations for feature in result]

  print(f'geojson_list size {len(geojson_list)}')

  # Add feature to our dataset
  dataset["geometry"] = geojson_list

  # Generate our dataset.csv
  dataset.to_csv('Building_Permits_v6.csv',index=False)

if __name__ == '__main__':
    main()