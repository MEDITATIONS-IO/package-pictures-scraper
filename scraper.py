# -*- coding: utf-8 -*-
"""Crawl and scrape Reuters image packages."""
import requests
from bs4 import BeautifulSoup

url = 'http://pictures.reuters.com/C.aspx?VP3=SearchResult&VBID=\
2C0BXZ3HH3DOG&SMLS=1&RW=1280&RH=678&PN=1'

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
    pass


payload = []

for i in range(num_page):
    pn = i + 1
    res = requests.get('%s&PN=%s' % (raw_url, pn))
    dom = BeautifulSoup(res.text, 'lxml')
    info = parse_package_info(dom)
    pics = get_package_pics(dom)
    payload.append({'info': info, 'pics': pics})

print(payload)
