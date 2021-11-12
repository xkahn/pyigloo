# -*- coding: utf-8 -*-

import sys
import os

from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

import pyigloo

def list_wiki_articles(wiki):
    ""

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("uri", help="Partial URL (URI) path of wiki channel")
parser.add_argument("output", help="Directory to save files to")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

root = igloo.objects_bypath(args.uri)

if (root["__type"] != "Wiki:http://schemas.iglooplatform.com/Igloo.Old.Common"):
    print ("Not a wiki channel!")

wikis = igloo.get_all_children_from_object(root["id"])

# [print (wiki["title"]) for wiki in wikis]
for wiki in wikis:
    fn = os.path.basename(wiki["href"] + ".html")
    print (fn + " -> " + wiki["title"])
    with open(args.output + "/" + fn, 'w') as o:
        o.write(wiki["content"])
