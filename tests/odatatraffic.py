# -*- coding: utf-8 -*-

import sys
import os
import datetime

from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

import pyigloo
import pyigloo.iglootypes
import pyigloo.igloodates
import pyigloo.iglootraffic

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("uri", help="Partial URL (URI) path to get traffic for")
parser.add_argument('-w', '--writefile', type=argparse.FileType('w'), default='-', help="Filename to write into")
args = parser.parse_args()

igloo = pyigloo.igloo(params)
root = igloo.objects_bypath(args.uri)

mytype = pyigloo.iglootypes.types(root)

if mytype.info["type"] != "channel":
    print ("Please pass a channel URI")
    exit()

articles = igloo.get_all_children_from_object(root["id"])
allarticles = [article for article in articles]
ids = [article["id"] for article in allarticles]

traffic = pyigloo.iglootraffic.igtraffic(igloo, igtype=pyigloo.iglootypes.types(root).__str__(), ids=ids)
t = traffic.get_traffic()
t = traffic.get_latest_views()
traffic.half_hour_to_date()

import csv
csvwriter = csv.writer(args.writefile, quoting=csv.QUOTE_NONNUMERIC)
headers = [
    "UUID",
    "Title",
    "URI",
    "Latest View"]
[headers.append("{} Traffic".format(d)) for d in traffic.dates]
csvwriter.writerow(headers)

for article in allarticles:
    row = [article['id'], article['title'], article['href']]
    if article['id'] in t:
        row.append(t[article['id']]["last_view"])
        [row.append(t[article['id']][d]) for d in traffic.dates]
    csvwriter.writerow(row)
