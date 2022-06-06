# -*- coding: utf-8 -*-

import sys
import os
import datetime
import requests
import re
from datetime import datetime
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
import pyigloo.iglootypes
import pyigloo.igloodates

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
args = parser.parse_args()

igloo = pyigloo.igloo(params)

timezone = "us_eastern"
date_start = "2022-01-01T00:00:00Z"
date_stop = "2022-04-01T00:00:00Z"

# Get the # of working days in the date range
dt_start = datetime.strptime(date_start, '%Y-%m-%dT00:00:00Z')
dt_stop = datetime.strptime(date_stop, '%Y-%m-%dT00:00:00Z')

page = requests.get("https://www.timeanddate.com/date/workdays.html?d1={}&m1={}&y1={}&d2={}&m2={}&y2={}&ti=on&".format(dt_start.day, dt_start.month, dt_start.year, dt_stop.day, dt_stop.month, dt_stop.year))
soup = BeautifulSoup(page.content, 'html.parser')
days = int(re.search("\d+", soup.find('div', class_='re-result').find("h2").text).group())
abs_days = abs(dt_stop-dt_start).days
abs_weeks = abs_days//7
abs_months = round(abs(dt_stop-dt_start).days/30)

time_start = "{}_dt eq {}".format(timezone, date_start)
time_stop  = "{}_dt eq {}".format(timezone, date_stop)
time_query = [("$filter"," or ".join([time_start, time_stop]))]

result = igloo.get_odata_url('dUtcHalfHour', time_query)
time_start_key = result[0]["utc_half_hour_key"]
time_stop_key = result[1]["utc_half_hour_key"]

# $apply=filter(last_visit_utc_half_hour_key ge 302209)/groupby((user_key),aggregate(community_key with sum as community_key))
filter = "filter(last_visit_utc_half_hour_key ge {} and last_visit_utc_half_hour_key lt {})/groupby((user_key),aggregate(community_key with sum as community_key))".format(time_start_key, time_stop_key)
traffic_stats = igloo.get_all_odata_url("fCommunityConcurrentUsers", [("$apply", filter)])
data = [min(int(x["community_key"]/4), days) for x in traffic_stats]
data1 = [min(x, days) for x in data]

import numpy as np

hist, bins = np.histogram(data1, bins=[1,4,12,30,60])
print ("Once:               " + str(hist[0]))
print ("Monthly:            " + str(hist[1]))
print ("Weekly:             " + str(hist[2]))
print ("Daily:              " + str(hist[3]))

import matplotlib.pyplot as plt

_ = plt.hist(data1, bins=[0, 1,4,12,30,60], edgecolor="black")
plt.title("Number of logins per user per quarter")
plt.show()
