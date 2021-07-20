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

def print_userinfo (user):
    print ("{0}: {1} ({2})".format(user.get('id'),
                                   user['name'].get('fullName'),
                                   user.get('namespace')))

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("userid", help="User ID")
args = parser.parse_args()

igloo = pyigloo.igloo(params)
ids = igloo.apisync_view_profile ([args.userid])
user = ids[0]['Value']
[print(x["Value"]) for x in user['items'] if x["Name"] == "customIdentifier"]
