# -*- coding: utf-8 -*-

import sys
import os
import csv


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
args = parser.parse_args()

igloo = pyigloo.igloo(params)

header = ['fullName', 'email', 'id', 'isEnabled', 'hasPhoto', 'sendEmailOnMessage', 'lastvisit', 'probablyhat']

# open the file in the write mode
with open('members.csv', 'w', encoding='UTF8') as f:
    # create the csv writer
    writer = csv.writer(f)

    # write the header to the csv file
    writer.writerow(header)

    users = igloo.get_all_community_members_viewsmall()
    for user in users:
        userdata = [user["name"]["fullName"], user.get("email"), user["id"], user["isEnabled"], user["hasPhoto"], user.get("sendEmailOnMessage")]
        if "lastvisit" in user["onlinestatus"]:
            userdata.append(user["onlinestatus"]["lastvisit"])
        else:
            userdata.append(None)
        if user["hasPhoto"]:
            photo = igloo.get_web_uri("/download-profile/{0}/profile/crxlarge".format(user["id"]))
            if "Content-Disposition" in photo.headers:
                print (photo.headers["Content-Disposition"])
                userdata.append(photo.headers["Content-Disposition"] == 'inline; filename=photo.png; size=4698')
            else:
                userdata.append("ERROR")
        else:
            userdata.append(None)

        writer.writerow(userdata)

