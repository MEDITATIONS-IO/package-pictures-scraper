# -*- coding: utf-8 -*-
"""Crawl and scrape Reuters image packages."""
import json
import requests
from bs4 import BeautifulSoup

url = 'http://pictures.reuters.com/C.aspx?VP3=SearchResult&VBID=\
2C0BXZ3HH3DOG&SMLS=1&RW=1280&RH=678&PN=1'

filename = 'test.json'

# Get first page: search result.
res = requests.get(url)
dom = BeautifulSoup(res.text, 'lxml')

# Get number of page according to displayed pagination.
# Expected DOM fragment looks like:
#  <span class="Lbl" id="a2.1.2.8:TotalPageCount_Lbl"> of 7</span>
pagination_fragment = dom.select('#a2.1.2.8:TotalPageCount_Lbl')
num_page = 0
if len(pagination_fragment) > 0:
    elm = str(pagination_fragment[0])
    if '</span>' in elm:
        num_page = int(elm[elm.rfind('</span>') - 1:elm.rfind('</span>')])

# In search URL, argument "PN" is the current page (from pagination system).
# Get search page results recursively.
raw_url = url[:url.rfind('&PN=')]


def parse_package_info(dom):
    """Scrape ID, category, date and number of pics."""
    media_count = dom.select('[id*="MediaCount_Lbl"]')[0].text
    media_count = int(media_count[:media_count.find(' ')])
    return {
        'caption': dom.select('[id*="CpationShort_Lbl"]')[0].text,
        'title': dom.select('[id*="Title2_Lbl"]')[0].text,
        'media_count': media_count
    }


def get_package_pics(dom):
    """Crawl inside package to acquire images."""
    stem = 'http://pictures.reuters.com'
    hyperlinks = dom.select('a[href*="Package/"]')
    payload = []

    count = 0
    for hyperlink in hyperlinks:
        if count < 1:
            count += 1
            uri = '%s/%s' % (stem, hyperlink['href'])
            print('Fetching data for %s' % uri)

            res = requests.get(uri)
            dom = BeautifulSoup(res.text, 'lxml')

            # Result for this badboy.
            result = None

            # Get metadata.
            try:
                panel = dom.select('[id*="MainPnl"]')[0]
                id = panel.select('[id*="Identifier_Lbl"]')[0].text
                date = panel.select('[id*="DocDate_Lbl"]')[0].text
                caption = panel.select('[id*="CaptionLong_Lbl"]')[0].text
                result = {
                    'id': id,
                    'date': date,
                    'caption': caption
                }
            except Exception as e:
                print(e)

            # Get image URL.
            # Find enough data to trigger a popup. Follow the link.
            # Scrape the image there.
            popup_link = dom.select('a[target*="_MatrixPopup"]')
            try:
                href = popup_link[0]['href']
                uri = '%s/%s' % (stem, href)
                res = requests.get(uri)
                dom = BeautifulSoup(res.text, 'lxml')

                img = dom.select('[id*="I_img"]')[0]['src']
                img = '%s%s' % (stem, img)

                result['img'] = img
            except Exception as e:
                print(e)

            payload.append(result)

    return payload

payload = []

for i in range(1):
    pn = i + 1
    res = requests.get('%s&PN=%s' % (raw_url, pn))
    dom = BeautifulSoup(res.text, 'lxml')
    info = parse_package_info(dom)
    pics = get_package_pics(dom)
    payload.append({'info': info, 'pics': pics})

with open(filename, 'w') as json_file:
    json.dump(payload, json_file)
