from bs4 import BeautifulSoup
from PIL import Image
from datetime import datetime
import requests
import json
import os.path

# File locations
images_dir = 'static/images/assets'
source_url = 'https://www.animal-crossing.com/new-horizons/buy/'

source = requests.get(source_url).text
s = BeautifulSoup(source, 'html.parser')
images = s.find_all('img')

for image in images:
    image_url = image['src']
    image_url = image_url.replace(
        '../', 'https://www.animal-crossing.com/new-horizons/')
    image_url = image_url.replace(
        './', 'https://www.animal-crossing.com/new-horizons/')
    print(image, image_url)
    image_type = image_url[-3:]
    print(image_type)
    if image_type=='svg':
        print ('Skipping SVG')
        continue

    pos = image_url.rfind("/")
    image_name = image_url[pos:] #includes leading slash
    image_dst = images_dir+image_name
    if True == os.path.isfile(image_dst):
        continue
    
    print(image_name, image_dst)
    image_save = Image.open(requests.get(image_url, stream=True).raw)
    image_save.save(image_dst)

print('ok')
