import requests
from bs4 import BeautifulSoup
import os
import shutil

website = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
r = requests.get("https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/")
data = r.text
soup = BeautifulSoup(data, "lxml")

urls=[]


for link in soup.find_all('a'):
	if( link.get('href').find('.csv.gz') != -1):
		urls.append( link.get('href'))
		
for link in urls:
	r = requests.get( website + link)
	with open( link, "wb") as file:
		file.write( r.content)

details_directory = './details'
fatalities_directory = './fatalities'
locations_directory = './locations'

for root, dirs, files in os.walk("."):
	for file in files:
		if file.find('details') != -1:
			shutil.move( file, details_directory)
		if file.find('fatalities') != -1:
			shutil.move( file, fatalities_directory)
		if file.find('locations') != -1:
			shutil.move( file, locations_directory)
	
