# -*- coding: utf-8 -*-

import sys
import os

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
parser.add_argument("uri", help="Partial URL (URI) path to get subscriptions for")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

subs_req = igloo.get_web_uri(args.uri + "?action=subscriptions")
soup = BeautifulSoup(subs_req.text, features="lxml")

monthly = soup.find_all("span", class_="ig-currentState", string="Monthly")
weekly = soup.find_all("span", class_="ig-currentState", string="Weekly")
daily = soup.find_all("span", class_="ig-currentState", string="Daily")
instant = soup.find_all("span", class_="ig-currentState", string="Instant")

[print_sub(x) for x in monthly]
[print_sub(x) for x in weekly]
[print_sub(x) for x in daily]
[print_sub(x) for x in instant]
