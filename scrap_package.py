#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TEST:
#   2C0408TFYF7UZ 45 images
#   2C0BF1FZJAJAJ 16 images

import sys, requests, re

def get_images_list(package_id, cache={}):
    print >> sys.stderr, package_id
    req = requests.get("http://pictures.reuters.com/Package/%s" % package_id)
    imgs = re.findall(r'<a href="archive/([^"]+?).html', req.text)
    res = []
    for i in set(imgs):
        if i not in cache:
            img = get_image(i)
            if img["id"] in cache:
                continue
            cache[i] = True
            cache[img["id"]] = True
            res.append(img)
    return res

fields = [
    ("url", re.compile(r'I_img" src="([^"]+)" onerror'), lambda x: "http://pictures.reuters.com" + x),
    ("date", re.compile(r'property="dateCreated">(\d+ \w+, \d{4})</span>'), None),
    ("location", re.compile(r'LocationName_Lbl">([^<]+)</span>'), None),
    ("description", re.compile(r'1.2:CaptionLong_Lbl">(.*?)</span>'), None),
    ("id", re.compile(r'IdClient_Lbl">(.*?)</span>'), None),
    ("sysid", re.compile(r':Identifier_Lbl">(.*?)</span>'), None),
    ("author", re.compile(r'property="author">(.*?)</a>'), None)
]
re_packages = re.compile(r'&ALID=([^"]+)">(.*?)</a>')
re_keywords = re.compile(r'&KWID=([^"]+)">(.*?)</a>')

def get_image(img_id):
    source_url = "http://pictures.reuters.com/archive/%s.html" % img_id
    req = requests.get(source_url)

    metas = {
      "source": source_url,
    }

    for fieldname, regexp, freduce in fields:
        res = regexp.search(req.text)

        if not res:
            found = ""
        else:
            found = res.group(1)

        if not freduce:
            freduce = lambda x: x

        metas[fieldname] = freduce(found)

    metas["keywords"] = re_keywords.findall(req.text)
    metas["packages"] = re_packages.findall(req.text)

    return metas

def format_csv(row, field):
    val = format_field(row, field)
    return '"%s"' % val.replace('"', '""') if (',' in val or '"' in val) else val

def format_field(row, field):
    if field not in row and field.endswith("_ids"):
        return "|".join([a for a, b in row[field[:-4]]])
    if field.endswith('s'):
        return "|".join([b for a, b in row[field]])
    return row[field]

def print_csv(data):
    headers = "id,sysid,url,source,date,location,author,description,keywords_ids,keywords,packages_ids,packages"
    print headers
    for row in sorted(data, key=lambda x: x['id']):
        print ",".join([format_csv(row, h).encode('utf-8') for h in headers.split(',')])

if __name__ == '__main__':
    try:
        package_ids = sys.argv[1:]
    except:
        package_ids = ["2C0408TFYF7UZ", "2C0BF1FZJAJAJ", "2C0408WHSULP3"]
    imgs = []
    cache = {}
    listpackages = list(package_ids)
    for pid in package_ids:
        imgs += get_images_list(pid, cache)
    print_csv(imgs)
