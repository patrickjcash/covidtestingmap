 #! /usr/bin/python3

import os
import sys
import requests
import re
import json
import geojson
from geojson import Feature, Point, FeatureCollection
from bs4 import BeautifulSoup

print("Starting...")

# CHANGE current working directory to local folder where script resides

if os.path.dirname(sys.argv[0]):
	os.chdir(os.path.dirname(sys.argv[0]))


# SET CONSTANTS

API_KEY = 'YOUR_API_KEY'
REQUEST_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?'
URL = 'https://www.nychealthandhospitals.org/covid-19-testing-sites/'
ADDRESS_REGEX = '(.*)\n(.*)\s+(NY|New York)[,\s]+(\d{5})'
ADDRESS_REGEX_BACKUP = '(.*)(?:\nMonday)'
BOUNDS = '40.9532067,-74.222055|40.5015477,-73.5560226'


# PARSE WEBSITE AND UPDATE GEOJSON FILE

print("Getting HTML data from NYC H+H site...")

# parse html into soup
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')


print("Parsing sites and addresses from HTML data...")

# remove all a tags/links
for a in soup.findAll('a'):
	a.replaceWithChildren()
site_candidates = soup.find_all('p',class_='m-b-20')

sites = []

for site_candidate in site_candidates:
	# parse soup data 
	name = site_candidate.get_text().strip().partition('\n')[0]
	detail = str(site_candidate)

	address_search = re.search(ADDRESS_REGEX,site_candidate.get_text())
	if address_search is None:
		address_search = re.search(ADDRESS_REGEX_BACKUP,site_candidate.get_text())

	if address_search is None:
		print("Couldn't find address for " + name)
		continue
	else:
		address = ' '.join(address_search.groups())
		site = {}
		site['name'] = name
		site['address'] = address
		site['detail'] = detail
		site['color'] = 'ltblue'
		sites.append(site)
		print("Found site: " + name)


print("Geocoding addresses...")

features = []

for site in sites:
	try:
		# request geocoding data
		payload = {'address' : site['address'], 'bounds' : BOUNDS, 'key' : API_KEY}
		response = requests.get(REQUEST_BASE_URL, params=payload)
	except:
		print("Google Maps API request failed for " + site['name'])
	else:
		# parse Google Maps data
		try:
			json_data = response.json()
			lat = json_data["results"][0]["geometry"]["location"]["lat"]
			lng = json_data["results"][0]["geometry"]["location"]["lng"]

			my_point = geojson.Point((lng, lat))
			features.append(Feature(geometry=my_point, properties=site))
			print("Retrieved lat/lng data for: " + site['name'])
		except:
			print("No lat/lng data returned for " + site['name'])


collection = FeatureCollection(features)
# print(collection)

# Serializing json  
json_object = json.dumps(collection, indent = 4)


print("Exporting site data to JSON file...") 
  
# Writing to sample.json 
with open("./sites.json", "w") as outfile:
	outfile.write(json_object)

print("Done!") 
