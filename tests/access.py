# -*- coding: utf-8 -*-
# Get the list of groups and people who have (at least) read access to this object

import sys
import os
import json
import re

from bs4 import BeautifulSoup

from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

import pyigloo


def print_sub(sub):
    title = sub.parent.contents[0]
    if 'icon-group' not in sub.parent.get('class'):
        curr = sub.parent.parent.parent
        while len(curr.find_all("div", class_="icon-group")) == 0: curr = curr.previous_sibling
        title = curr.find_all("div", class_="icon-group")[0].contents[0] + ">" + title
    print ("{0}: {1} ({2}): {3}".format(sub.parent.parent.get('id')[3:], 
                                        title, 
                                        sub.parent.contents[1].text, 
                                        sub.parent.contents[2].text))

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("uri", help="Partial URL (URI) path to get acess list for")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

access_req = igloo.get_web_uri(args.uri + "?action=access")
soup = BeautifulSoup(access_req.text, features="lxml")
access_req_js = re.search(r'Igloo.asset_app_access = (.*)', access_req.text)

print ("{")

# Let's get any inherited groups (like All Members)
inherited = soup.select('.ig-accessEveryone span[class$="name"]')
if len(inherited):
    print ('"inherited_groups":')
    print ('["]' + inherited[0]["class"][0][3:-5] + '"]')
    print (",")

# Let's get the assigned groups
groups = soup.select('a[id*="details_inherited"],a[id*="details_exclusive"]')
id_groups = [x["id"][18:] for x in groups]
print ('"groups":')
print (str(id_groups).replace("'", '"'))
print (",")

# Let's get the admin groups
access_req_js_object = json.loads(access_req_js.group(1)[:-2].replace("'", '"'))
admin_groups = access_req_js_object["access"]["groupList"]["administrators"]
id_admin_groups = [x["id"] for x in admin_groups]
print ('"admin_groups":')
print (str(id_admin_groups).replace("'", '"'))
print (",")

# Let's get the specifically assigned users
users = soup.select('.ig-accessSingle span')
id_users = [x["class"][0][3:-5] for x in users]
print ('"users":')
print (str(id_users).replace("'", '"'))

print ("}")