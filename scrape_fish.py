from bs4 import BeautifulSoup
from PIL import Image
import requests, csv

# Config
source_url = 'https://animalcrossing.fandom.com/wiki/Fish_(New_Horizons)#Southern%20Hemisphere'
get_from_source = False
get_images = False
file_html = 'data/fish_south.html'
file_data = 'data/fish_south.csv'
images_dir = 'static/images/fish'

if get_from_source is True:
    source = requests.get(source_url).text
    s = BeautifulSoup(source, 'html.parser')
    table = s.find_all('table', attrs={'class':'roundy sortable'})[1]
    with open(file_html, "w") as fo:
        fo.write(table.prettify())
        print("acquired table")

source = open(file_html).read()

s = BeautifulSoup(source, 'html.parser')

table = s.find('table')

# Append each row to this list
data = []

# Scrape table headings 
row = [elem.text.strip() for elem in table.find_all('th')]
del row[1]
data.append(row)

# Iterate over <tr>
for tr in table.find_all('tr'):

    # Append data to this list
    row = []
    
    for i, elem in enumerate(tr.find_all('td')):
        #print(i, elem.text.strip())
        
        elem_raw = elem.text.strip()
        
        if i == 0:
            name = elem_raw

        if i == 1:
            # Scrape image
            if get_images is True:
                image = elem.find('img')
                image_url = image['data-src']
                img = Image.open(requests.get(image_url, stream = True).raw)
                img.save(images_dir+'/'+name+'.png')
            continue
        
        if i == 2:
            if elem_raw[0:1].isnumeric() is False:
                print('element', elem_raw, 'not formatted for integer')
                elem_raw = ''
            else:
               elem_raw = int(elem_raw.replace(',',''))
        
        if i == 5:
            if elem_raw == 'All day':
                elem_raw = '0,23'
            else:
                start_time, finish_time = elem_raw.split(' - ')
                
                row.append(start_time)
                row.append(finish_time)
                continue
        
        row.append(elem_raw)
    
    data.append(row)

with open(file_data, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)

print("fin")