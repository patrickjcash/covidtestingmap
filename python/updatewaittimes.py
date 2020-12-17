 #! /usr/bin/python3

import os
import sys
import requests
import re
import json
import PyPDF2
import csv

print("Starting...")

# CHANGE current working directory to local folder where script resides

if os.path.dirname(sys.argv[0]):
	os.chdir(os.path.dirname(sys.argv[0]))

# SET CONSTANTS

WAIT_URL = 'https://hhinternet.blob.core.windows.net/wait-times/testing-wait-times.pdf'
WAIT_TIME_REGEX = '.*(?:\n.*){2}Last Reported Time:(?:\s*\d+:\d+\s*.M)?'


# DOWNLOAD PDF

print("Downloading wait times PDF...")

response = requests.get(WAIT_URL)
with open('./testing-wait-times.pdf', 'wb') as f:
	f.write(response.content)


# PARSE PDF

# creating a pdf file object  
pdfFileObj = open('testing-wait-times.pdf', 'rb')  
# creating a pdf reader object  
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)  
# creating a page object  
pageObj = pdfReader.getPage(0)  
# extracting text from page  
text = pageObj.extractText()

print("Scraping data from PDF...")

# parse data
raw_match_list = re.findall(WAIT_TIME_REGEX,text)
sites_list = [item.split('\n') for item in raw_match_list]

# create nested dictionary for later data lookups
sites = {}
for i in sites_list:
	name = i[0]
	wait = i[1]

	if len(i) == 4:
		reported = i[3]
	else:
		reported = "Not Reported Yet"

	if wait.startswith('No Wait Time'):
		color = 'green'
	elif wait.startswith('0-30 Minutes'):
		color = 'yellow'
	elif wait.startswith('30-60 Minutes'):
		color = 'yellow'
	elif wait.startswith('1-1.5 Hours'):
		color = 'orange'
	elif wait.startswith('1.5-2 Hours'):
		color = 'orange'
	elif wait.startswith('More Than 2 Hours'):
		color = 'red'
	else:
		color = 'ltblue'

	sites[name] = {}
	sites[name]['wait'] = wait
	sites[name]['reported'] = reported
	sites[name]['color'] = color

# closing the pdf file object  
pdfFileObj.close()

# IMPORT MAPPING

print("Importing PDF-website data mapping from CSV file...")

namemap = {}

with open('./namemap.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
         namemap[row['list_name']] = row['wait_name']

# UPDATE site wait data

print("Updating sites with PDF data...")


with open('./sites.json') as f:
	all_sites = json.load(f)

for site in all_sites['features']:
	site.pop('color',None)
	site.pop('wait',None)
	site.pop('reported',None)

	name = site['properties']['name']

	try:
		site['properties']['color'] = sites[namemap[name]]['color']
		site['properties']['wait'] = '<br/>Wait time: ' + sites[namemap[name]]['wait']
		site['properties']['reported'] = '<br/>Reported time: ' + sites[namemap[name]]['reported']
	except:
		site['properties']['color'] = 'ltblue'
		site['properties']['wait'] = ''
		site['properties']['reported'] = ''

print("Parsing data into geojson file...") 

# serialize json  
json_object = json.dumps(all_sites, indent = 4)

print("Writing geojson data to file...") 

# write json to file
with open("../sites_with_waits.json", "w") as outfile:
	outfile.write(json_object)

# write json to file with JS helper function wrapper
with open("../cvmap.json", "w") as outfile:
	outfile.write("cvfeed_callback(")
	outfile.write(json_object)
	outfile.write(");")

print("Done!") 