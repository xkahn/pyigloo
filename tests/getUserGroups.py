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

def print_usergroup (group):
    print ("{0}: {1} - {2}".format(group["id"],
                                   group["spaceTitle"],
                                   group["name"],
                                   group["numMembers"]))

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

ids = igloo.apisync_view_usergroups([args.userid])
groups = ids[0]['Value']
[print_usergroup (igloo.community_usergroups_view(x)) for x in groups]
