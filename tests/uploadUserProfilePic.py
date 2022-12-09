# -*- coding: utf-8 -*-

import sys
import os
import pathlib
import magic


from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

import pyigloo


params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("communityKey", help="Community Key")
parser.add_argument("userid", help="User ID")
parser.add_argument("filePath", help="Path to the image")
parser.add_argument("contentType", help="Content Type of the image")
args = parser.parse_args()

igloo = pyigloo.igloo(params)

allowedContentType = ['image/png', 'image/jpg']

if args.contentType is None:
    contentType = magic.detect_from_filename(args.filePath).mime_type

if args.contentType not in allowedContentType:
    print("Allowed contentTypes "+str(" ".joing(allowedContentType))
    exit()


update_profile_picture(self, args.communityKey, args.userId, args.filePath, args.contentType)