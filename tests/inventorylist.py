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

import xlsxwriter

class file_writer:
    levels = {}

    def __init__(self, workbook=None, csv=None, doGroup=False):
        self.row = 0
        self.workbook = workbook
        self.doGroup = doGroup
        if workbook:
                self.worksheet = workbook.add_worksheet()
        else:
                self.worksheet = None
        self.csv = csv
        if workbook:
            self.setup_styles()

    def setup_styles (self):
        self.worksheet.freeze_panes(1, 0)

        self.levels[0] = self.workbook.add_format()
        self.levels[1] = self.workbook.add_format()
        self.levels[2] = self.workbook.add_format()
        self.levels[3] = self.workbook.add_format()
        self.levels[4] = self.workbook.add_format()
        self.levels[5] = self.workbook.add_format()
        self.levels[6] = self.workbook.add_format()
        self.levels[7] = self.workbook.add_format()

        self.levels[0].set_font_name('Red Hat Text')

        self.levels[1].set_indent(1)
        self.levels[1].set_num_format("   >> @")
        self.levels[1].set_font_name('Red Hat Text')

        self.levels[2].set_indent(2)
        self.levels[2].set_num_format("      -- @")
        self.levels[2].set_font_name('Red Hat Text')

        self.levels[3].set_font_color("#777777")
        self.levels[3].set_font_name('Red Hat Text')

        self.levels[4].set_num_format('yyyy/mm/dd')
        self.levels[4].set_font_name('Courier New')

        self.levels[5].set_num_format('yyyy/mm/dd')
        self.levels[5].set_font_name('Courier New')
        self.levels[5].set_font_color('#cccccc')

        self.levels[6].set_font_color('#cccccc')
        self.levels[6].set_font_name('Red Hat Text')

        self.levels[7].set_bold()
        self.levels[7].set_font_name('Red Hat Text')

        self.worksheet.set_column(0, 0, 40)
        self.worksheet.set_column(1, 1, 40)
        self.worksheet.set_column(2, 7, 15)
        self.worksheet.set_column(8, 8, 15)
        self.worksheet.set_column(10, 11, 25)

    def writerow (self, data, indent=0, outline=0, collapse=False):
        if self.worksheet:
            self.worksheet.write_row(self.row, 0, data, self.levels[0])
            if self.row > 0:
                self.worksheet.write(self.row, 0, data[0], self.levels[7])
                self.worksheet.write(self.row, 1, data[1], self.levels[3])
            self.write_datevalue(data, 2, outline != 0) # channel create
            self.write_datevalue(data, 3, outline != 1) # article create
            self.write_datevalue(data, 4, outline != 2) # comment create
            self.write_datevalue(data, 5, outline != 0) # channel update
            self.write_datevalue(data, 6, outline != 1) # article update
            self.write_datevalue(data, 7, outline != 2) # comment update
            if self.doGroup and outline > 0:
                self.worksheet.set_row(self.row, None, None, {'level': outline, 'hidden': collapse})
            if indent > 0:
                self.worksheet.write(self.row, 0, data[0], self.levels[indent])
            if outline > 0:
                self.worksheet.write_number(self.row, 12, data[12], self.levels[6])
            if outline > 1:
                self.worksheet.write_number(self.row, 13, data[13], self.levels[6])

        if self.csv:
            self.csv.writerow(data)
        self.row = self.row+1

    def write_datevalue (self, data, column, hidden):
        if type(data[column]) == datetime and hidden == False:
            self.worksheet.write_datetime(self.row, column, data[column], self.levels[4])
        elif type(data[column]) == datetime and hidden == True:
            self.worksheet.write_datetime(self.row, column, data[column], self.levels[5])


def display_container (writer, containerid, tz, traffic=False):
    info = igloo.objects_view(containerid)
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + info["href"] + '","' + info["title"] + '")',
        info["href"],
        pyigloo.igloodates.date(info["created"]["date"], tz).local,
        None, # article created
        None, # comment created
        pyigloo.igloodates.date(info["modified"]["date"], tz).local,
        None, # article updated
        None, # comment updated
        pyigloo.iglootypes.types(info).__str__(),
        None,
        get_userinfo(info["created"]),
        get_userinfo(info["modified"]),
        info["statistics"]["views"]["views"],
        None, # article views
        None, # version
        None, # attachments
        None, # comments
        info["statistics"]["contents"]["children"],
        None # Notes
    ])

    children = igloo.get_all_children_from_object(containerid)
    for child in children:
        childtype = pyigloo.iglootypes.types(child)
        if childtype.info["type"] == "container":
            display_container (writer, child["id"], tz, traffic)
        elif childtype.info["type"] == "channel":
            display_channel (writer, child["id"], tz, traffic)

def display_channel (writer, channelid, tz, traffic=False):
    info = igloo.objects_view(channelid)
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + info["href"] + '","' + info["title"] + '")',
        info["href"],
        pyigloo.igloodates.date(info["created"]["date"], tz).local,
        None, # article created
        None, # comment created
        pyigloo.igloodates.date(info["modified"]["date"], tz).local,
        None, # article updated
        None, # comment updated
         pyigloo.iglootypes.types(info).__str__(),
        None,
        get_userinfo(info["created"]),
        get_userinfo(info["modified"]),
        info["statistics"]["views"]["views"],
        None, #article views
        info.get("version"),
        info.get("numAttachments"),
        info["statistics"]["contents"]["comments"],
        info["statistics"]["contents"]["children"],
        None #notes
    ])

    if "numAttachments" in info and info.get("numAttachments") > 0:
        display_attachments (writer, info, tz, 
                             (info["created"]["date"], info["modified"]["date"], info["statistics"]["views"]["views"]), 
                             (None, None, None))
    
    children = igloo.get_all_children_from_object(channelid)

    # This is a generator... We need to make it a list.
    children = [child for child in children]

    # It's possible that we have a channel of channels (only folderChannel or folder?)
    subchannels = [child for child in children if pyigloo.iglootypes.types(child).__str__() == "Folder"]
    children = [child for child in children if pyigloo.iglootypes.types(child).__str__() != "Folder"]

    if len(subchannels) > 0:
        for subchannel in subchannels:
            display_channel (writer, subchannel['id'], tz, traffic)

    if traffic:
        traffic = pyigloo.iglootraffic.igtraffic(igloo, igtype=pyigloo.iglootypes.types(info).__str__(), ids=[child['id'] for child in children])
        t = traffic.get_traffic()
        t = traffic.get_latest_views()
        traffic.half_hour_to_date()

        for article in children:
            if article['id'] in t:
                display_article (writer, article, tz,
                                 (info["created"]["date"], info["modified"]["date"], info["statistics"]["views"]["views"]),
                                 traffic=traffic, t=t[article['id']])
            else:
                display_article (writer, article, tz,
                                 (info["created"]["date"], info["modified"]["date"], info["statistics"]["views"]["views"]))
    else:
        for article in children:
            display_article (writer, article, tz,
                             (info["created"]["date"], info["modified"]["date"], info["statistics"]["views"]["views"]))

def get_userinfo (user):
    if user:
        return user["user"]["name"]["fullName"]
    else:
        return None

def display_article (writer, article, tz, channel_info, traffic=None, t=None):
    row = [
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + article["href"] + '","' + article["title"] + '")',
        article["href"],
        pyigloo.igloodates.date(channel_info[0], tz).local,
        pyigloo.igloodates.date(article["created"]["date"], tz).local,
        None,
        pyigloo.igloodates.date(channel_info[1], tz).local,
        pyigloo.igloodates.date(article["modified"]["date"], tz).local,
        None,
        pyigloo.iglootypes.types(article).__str__(),
        article["IsArchived"] and article["isPublished"],
        get_userinfo(article["created"]),
        get_userinfo(article["modified"]),
        channel_info[2],
        article["statistics"]["views"]["views"],
        article.get("version"),
        article.get("numAttachments"),
        article["statistics"]["contents"]["comments"],
        article["statistics"]["contents"]["children"] + int(article.get("numAttachments", 0))
    ]

    if traffic:
        [row.append(t[d]) for d in traffic.dates]
        row.append(t["last_view"])

    writer.writerow(row, indent=1, outline=1)
    if "numAttachments" in article and article.get("numAttachments") > 0:
        display_attachments (writer, article, tz,
                             channel_info,
                             (article["created"]["date"], article["modified"]["date"], article["statistics"]["views"]["views"])
                             )
    if article["statistics"]["contents"]["comments"] > 0:
        comments = igloo.get_all_comments_from_object(article["id"])
        for comment in comments:
            display_comment (writer, comment, tz, 
                             channel_info,
                             (article["created"]["date"], article["modified"]["date"], article["statistics"]["views"]["views"])
                             )

def display_comment (writer, comment, tz, channel_info, article_info):
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT") + "/".join(comment["href"].split("/")[2:-1]) + "#anchor_" + comment["href"].split("/")[-1] + '","' + get_userinfo(comment["created"]) + ' replied")',
        "/" + "/".join(comment["href"].split("/")[2:-1]) + "#anchor_" + comment["href"].split("/")[-1],
        pyigloo.igloodates.date(channel_info[0], tz).local,
        pyigloo.igloodates.date(article_info[0], tz).local,
        pyigloo.igloodates.date(comment["created"]["date"], tz).local,
        pyigloo.igloodates.date(channel_info[1], tz).local,
        pyigloo.igloodates.date(article_info[1], tz).local,
        pyigloo.igloodates.date(comment["modified"]["date"], tz).local,
        pyigloo.iglootypes.types(comment).__str__(),
        None,
        get_userinfo(comment["created"]),
        get_userinfo(comment["modified"]),
        channel_info[2],
        article_info[2],
        comment.get("version"),
        comment.get("numAttachments"),
        None,
        None
    ], indent=2, outline=2, collapse=True)

def display_attachments (writer, article, tz, channel_info, article_info):
    attachments = igloo.attachments_view(article["id"])
    for attachment in attachments["items"]:
        display_attachment (writer, article, attachment, tz, channel_info, article_info)

def display_attachment (writer, article, attachment, tz, channel_info, article_info):
    writer.writerow([
        '=HYPERLINK("' + os.getenv("API_ENDPOINT")[:-1] + attachment["RelationHref"] + '","' + attachment["RelationTitle"] + '")',
        article["href"],
        pyigloo.igloodates.date(channel_info[0], tz).local,
        pyigloo.igloodates.date(article_info[0], tz).local,
        pyigloo.igloodates.date(attachment["Created"], tz).local,
        pyigloo.igloodates.date(channel_info[1], tz).local,
        pyigloo.igloodates.date(article_info[1], tz).local,
        None,
        pyigloo.iglootypes.types(attachment).__str__(),
        attachment["IsHidden"],
        get_userinfo(attachment["CreatedBy"]),
        None,
        channel_info[2],
        article_info[2],
        None,
        None,
        None,
        None
    ], indent=2, outline=2, collapse=True)

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
parser.add_argument('-x', '--excel', help="Write output as specified Excel file")
parser.add_argument('-t', '--timezone', type=TypeZone(), default=localtz, help="Specify a timezone for date/time objects")
parser.add_argument('-g', '--group', help="Use row groups in Excel output. May break sorting operations.", action="store_true")
parser.add_argument('-r', '--traffic', help="Pull view data for articles", action="store_true")
parser.add_argument("-v", "--verbose", help="Be more verbose in output", action="store_true")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

root = igloo.objects_bypath(args.uri)
mytype = pyigloo.iglootypes.types(root)

if args.excel:
    workbook = xlsxwriter.Workbook(args.excel, {'default_date_format': 'yy/mm/dd'})
else:
    workbook = None

csvwriter = csv.writer(args.writefile, quoting=csv.QUOTE_NONNUMERIC)

writer = file_writer (workbook, csvwriter, doGroup=args.group)

columns = ["Title",
                "URI",
                "Created (channel)",
                "Created (article)",
                "Created (comment)",
                "Updated (channel)",
                "Updated (article)",
                "Updated (comment)",
                "Content type",
                "Hidden?",
                "Creator",
                "Modifier",
                "Views (channel)",
                "Views (article)",
                "Version",
                "Attachments",
                "Comments",
                "Children"]

if args.traffic:
    import pyigloo.iglootraffic
    columns.append("Week Traffic")
    columns.append("Quarter Traffic")
    columns.append("Year Traffic")
    columns.append("Last Viewed")

columns.append("Notes")

writer.writerow(columns)

if mytype.info["type"] == "channel":
    display_channel (writer, root["id"], args.timezone, traffic=args.traffic)
elif mytype.info["type"] == "article":
    article = igloo.objects_view(root["id"])
    if args.traffic:
        traffic = pyigloo.iglootraffic.igtraffic(igloo, igtype=pyigloo.iglootypes.types(info).__str__(), ids=[article['id']])
        t = traffic.get_traffic()
        t = traffic.get_latest_views()
        traffic.half_hour_to_date()

        display_article (writer, article, args.timezone, (None, None, None), traffic=traffic, t=t[article['id']])
    else:
        display_article (writer, article, args.timezone, (None, None, None))
elif mytype.info["type"] == "container":
    display_container (writer, root["id"], args.timezone, traffic=args.traffic)

args.writefile.close()

if workbook:
    workbook.close()
