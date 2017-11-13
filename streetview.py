import random
import time
import google_streetview.api
from google_streetview import helpers
from os import path, makedirs
from pprint import pprint
try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode

import json
import requests
import math
from motionless import CenterMap
import urllib

random.seed(time.time())

retrieved = 0
search_count = 0 
def add_noise(x0, y0, error):
	# r = error / 111300 #convert coordinate to meter
	# u = random.uniform(0,1)
	# v = random.uniform(0,1)
	# w = r * math.sqrt(u)
	# t = 2 * math.pi * v
	# x = w * math.cos(t)
	# x1 = x / math.cos(y0)
	# y = w * math.sin(t)
	x1 = random.gauss(0,0.00005)
	y1 = random.gauss(0,0.00005)
	return (x0+x1, y0+y1)

def newpoint():
	location = (random.uniform(-90,90),random.uniform(-180,180))
	heading = random.randint(0,359)
	fov = 120
	return location,heading,fov
def download_links(results, dir_path, metadata_file='metadata.json', metadata_status='status', status_ok='OK'):
    """Download Google Street View images from parameter queries if they are available.
    
    Args:
      dir_path (str):
        Path of directory to save downloads of images from :class:`api.results`.links
      metadata_file (str):
         Name of the file with extension to save the :class:`api.results`.metadata
      metadata_status (str):
        Key name of the status value from :class:`api.results`.metadata response from the metadata API request.
      status_ok (str):
        Value from the metadata API response status indicating that an image is available.
    """
    metadata = results.metadata
    location = metadata[0]['location']
    if not path.isdir(dir_path):
      makedirs(dir_path)
    
    # (download) Download images if status from metadata is ok
    for i, url in enumerate(results.links):
      if metadata[i][metadata_status] == status_ok:
        file_path = path.join(dir_path, str(location['lat'])+','+str(location['lng']) + '.jpg')
        metadata[i]['_file'] = path.basename(file_path) # add file reference
        helpers.download(url, file_path)
    
    # (metadata) Save metadata with file reference
    metadata_file = str(location['lat'])+','+str(location['lng']) + '.json'
    metadata_path = path.join(dir_path, metadata_file)
    with open(metadata_path, 'w') as out_file:
      json.dump(metadata, out_file)


while retrieved < 10:
	location, heading, fov = newpoint()
	#print str(location[0])+","+str(location[1])
	params = [{
	  'size': '640x640', # max 640x640 pixels
	  'location': str(location[0])+","+str(location[1]),
	  'heading': str(heading),
	  'fov': str(fov),
	  'key': 'AIzaSyDZa9UFclWNhK1SJgg9LqFnLlUE7PRHiDg'
	}]
	# params = [{
 #  	'size': '640x640', # max 640x640 pixels
 #  	'location': '46.414382,10.013988',
 #  	'heading': '151.78',
 # 	'fov': str(fov),
 #  	'key': 'AIzaSyDZa9UFclWNhK1SJgg9LqFnLlUE7PRHiDg'
	# }]

	results = google_streetview.api.results(params)
	results.metadata[0]['heading'] = heading
	#print results.metadata
	search_count += 1
	if results.metadata[0]['status'] == 'OK':
		retrieved += 1
		print "Searched: ",search_count
		print "Retrieved: ",retrieved
		results.preview()
		location = results.metadata[0]['location']
		noisy_location = add_noise(location['lat'],location['lng'],1000)
		print noisy_location
		cmap = CenterMap(size_x=640,size_y=640,lat=noisy_location[0],lon=noisy_location[1],maptype='roadmap')
		cmap.format = 'jpg'
		print(cmap.generate_url())
		urllib.urlretrieve (cmap.generate_url(), "streetview/map_"+str(location['lat'])+','+str(location['lng'])+".jpg") #download static map
		download_links(results,'streetview') #download streetview
		#break

#results.preview()
#results.download_links('streetview')
