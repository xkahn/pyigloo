# -*- coding: utf-8 -*-

import sys
import os
import pprint

from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

pp = pprint.PrettyPrinter(indent=4)

import pyigloo

def print_usergroup (group):
    print ("{0}: {1} - {2}".format(group["id"],
                                   group["spaceTitle"],
                                   group["name"],
                                   group["numMembers"]))

def lookup_user (igloo, id):
    u = igloo.user_get(id)
    return u["FullName"] + ' <' + u["Username"] + '>'

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("namespace", help="Namespace of user")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

id = igloo.search_members(args.namespace, 1)['value']['hit'][0]['id']
print (igloo.user_get(id)["Username"])