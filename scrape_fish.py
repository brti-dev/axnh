from bs4 import BeautifulSoup
from PIL import Image
from datetime import datetime
import requests
import json
import os.path

# Config
get_from_source = False             # If true, scrape from source_url; If false, scrape from file_html
get_images = True                   # Scrape images?
hemispheres = ('north', 'south')
january_column_num = 6              # The column number where the months begin; 0=Leftmost column

# File locations
images_dir = 'static/images/fish'
source_url = 'https://animalcrossing.fandom.com/wiki/Fish_(New_Horizons)'
file_html = 'data/fish_{}.html'
file_data = 'data/fish_{}.json'

if get_from_source is True:
    source = requests.get(source_url).text
    s = BeautifulSoup(source, 'html.parser')
    table = {
        'north': s.find_all('table', attrs={'class':'roundy sortable'})[0],
        'south': s.find_all('table', attrs={'class':'roundy sortable'})[1]
    }
    for hemisphere in hemispheres:
        print(file_html.format(hemisphere))
        with open(file_html.format(hemisphere), "w") as fo:
            fo.write(table[hemisphere].prettify())
            print("Acquired table", hemisphere)

for hemisphere in hemispheres:

    source = open(file_html.format(hemisphere)).read()

    s = BeautifulSoup(source, 'html.parser')

    table = s.find('table')

    # Scrape table headings 
    th = [elem.text.strip().lower() for elem in table.find_all('th')]
    print(th)

    data = dict()
    row_i = 0

    def convertTime(timestr):
        timestr = timestr.strip()
        timestr = timestr.replace(' ', '')
        in_time = datetime.strptime(timestr.strip(), "%I%p")
        out_time = datetime.strftime(in_time, "%H")
        return int(out_time)


    # Iterate over <tr>
    for tr in table.find_all('tr'):
        
        row_i += 1

        # Skip <th>
        if row_i == 1:
            continue
        
        # Iterate over <td>
        for i, elem in enumerate(tr.find_all('td')):
            #print(i, elem.text.strip())
            
            elem_raw = elem.text.strip()
            heading = th[i]
            
            if heading == 'name':
                name = elem_raw
                print(name)
                data[name] = dict()
                continue

            if heading == 'image':
                # Scrape image
                if get_images is True:
                    img_dst = images_dir+'/'+name+'.png'
                    if False == os.path.isfile(img_dst):
                        image = elem.find('a')
                        image_url = image['href']
                        img = Image.open(requests.get(
                            image_url, stream=True).raw)
                        img.save(img_dst)
                continue
            
            if heading == 'price':
                if elem_raw[0:1].isnumeric() is False:
                    print('element', elem_raw, 'not formatted for integer')
                    elem_raw = None
                else:
                    elem_raw = int(elem_raw.replace(',',''))
                data[name]['price'] = elem_raw
                continue

            if heading == 'time':
                data[name]['times'] = []
                data[name]['times_readable'] = elem_raw
                
                if elem_raw == 'All day':
                    data[name]['times'] += range(24)
                    continue
                
                times = []
                if '&' in elem_raw:
                    times = [time for time in elem_raw.split('&')]
                else:
                    times.append(elem_raw)
                
                for time in times:
                    start, fin = [convertTime(x) for x in time.split('-')]
                    if start > fin:
                        data[name]['times'] += range(fin)
                        data[name]['times'] += range(start, 24)
                    else:
                        data[name]['times'] += range(start, fin)
                
                continue
            
            # Months
            if i == january_column_num:
                data[name]['months'] = []
            if i >= january_column_num:
                month = i - january_column_num + 1
                if elem_raw == '\u2713':
                    data[name]['months'].append(month)
                continue
            
            # Default append
            data[name][heading] = elem_raw

    with open(file_data.format(hemisphere), 'w') as jsonfile:
        json.dump(data, jsonfile)

    #print(json.dumps(data))
    print("Wrote JSON", hemisphere)
