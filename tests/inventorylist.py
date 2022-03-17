# -*- coding: utf-8 -*-

import sys
import os
import csv
from datetime import datetime, timezone
from typedate import TypeZone

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

def display_container (writer, containerid, tz):
    info = igloo.objects_view(containerid)
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + info["href"] + '","' + info["title"] + '")',
        info["href"],
        pyigloo.igloodates.date(info["created"]["date"], tz).local,
        pyigloo.igloodates.date(info["modified"]["date"], tz).local,
        pyigloo.iglootypes.types(info),
        None,
        get_userinfo(info["created"]),
        get_userinfo(info["modified"]),
        info["statistics"]["views"]["views"],
        None,
        None,
        None
    ])

    children = igloo.get_all_children_from_object(containerid)
    for child in children:
        childtype = pyigloo.iglootypes.types(child)
        if childtype.info["type"] == "container":
            display_container (writer, child["id"], tz)
        elif childtype.info["type"] == "channel":
            display_channel (writer, child["id"], tz)

def display_channel (writer, channelid, tz):
    info = igloo.objects_view(channelid)
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + info["href"] + '","' + info["title"] + '")',
        info["href"],
        pyigloo.igloodates.date(info["created"]["date"], tz).local,
        pyigloo.igloodates.date(info["modified"]["date"], tz).local,
        pyigloo.iglootypes.types(info),
        None,
        get_userinfo(info["created"]),
        get_userinfo(info["modified"]),
        info["statistics"]["views"]["views"],
        info.get("version"),
        info.get("numAttachments"),
        info["statistics"]["contents"]["comments"]
    ])

    if "numAttachments" in info and info.get("numAttachments") > 0:
        display_attachments (writer, info, tz)
    
    children = igloo.get_all_children_from_object(channelid)
    for article in children:
        display_article (writer, article, tz)

def get_userinfo (user):
    if user:
        return user["user"]["name"]["fullName"]
    else:
        return None

def display_comment (writer, comment, tz):
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT") + "/".join(comment["href"].split("/")[2:-1]) + "#anchor_" + comment["href"].split("/")[-1] + '","    ' + get_userinfo(comment["created"]) + ' replied")',
        "/" + "/".join(comment["href"].split("/")[2:-1]) + "#anchor_" + comment["href"].split("/")[-1],
        pyigloo.igloodates.date(comment["created"]["date"], tz).local,
        pyigloo.igloodates.date(comment["modified"]["date"], tz).local,
        pyigloo.iglootypes.types(comment),
        None,
        get_userinfo(comment["created"]),
        get_userinfo(comment["modified"]),
        None,
        comment.get("version"),
        comment.get("numAttachments"),
        None
    ])

def display_article (writer, article, tz):
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + article["href"] + '","  ' + article["title"] + '")',
        article["href"],
        pyigloo.igloodates.date(article["created"]["date"], tz).local,
        pyigloo.igloodates.date(article["modified"]["date"], tz).local,
        pyigloo.iglootypes.types(article),
        article["IsArchived"] and article["isPublished"],
        get_userinfo(article["created"]),
        get_userinfo(article["modified"]),
        article["statistics"]["views"]["views"],
        article.get("version"),
        article.get("numAttachments"),
        article["statistics"]["contents"]["comments"]
    ])
    if "numAttachments" in article and article.get("numAttachments") > 0:
        display_attachments (writer, article, tz)
    if article["statistics"]["contents"]["comments"] > 0:
        comments = igloo.get_all_comments_from_object(article["id"])
        for comment in comments:
            display_comment (writer, comment, tz)

def display_attachments (writer, article, tz):
    attachments = igloo.attachments_view(article["id"])
    for attachment in attachments["items"]:
        display_attachment (writer, article, attachment, tz)

def display_attachment (writer, article, attachment, tz):
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + attachment["RelationHref"] + '","   ' + attachment["RelationTitle"] + '")',
        article["href"],
        pyigloo.igloodates.date(attachment["Created"], tz).local,
        None,
        pyigloo.iglootypes.types(attachment),
        attachment["IsHidden"],
        get_userinfo(attachment["CreatedBy"]),
        None,
        None,
        None
    ])

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

localtz = datetime.now(timezone.utc).astimezone().tzinfo

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("uri", help="Partial URL (URI) path of wiki channel")
parser.add_argument('-w', '--writefile', type=argparse.FileType('w'), default='-', help="Filename to write into")
parser.add_argument('-t', '--timezone', type=TypeZone(), default=localtz, help="Specify a timezone for date/time objects")
parser.add_argument("-v", "--verbose", help="Be more verbose in output", action="store_true")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

root = igloo.objects_bypath(args.uri)
mytype = pyigloo.iglootypes.types(root)

writer =  csv.writer(args.writefile, quoting=csv.QUOTE_NONNUMERIC)

writer.writerow(["Title",
                "URI",
                "Created",
                "Last Updated",
                "Content type",
                "Hidden?",
                "Creator",
                "Modifier",
                "Total views",
                "Version",
                "Attachments",
                "Comments",
                "Notes"])

if mytype.info["type"] == "channel":
    display_channel (writer, root["id"], args.timezone)
elif mytype.info["type"] == "article":
    article = igloo.objects_view(root["id"])
    display_article (writer, article, args.timezone)
elif mytype.info["type"] == "container":
    display_container (writer, root["id"], args.timezone)

args.writefile.close()

