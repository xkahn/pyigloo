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
parser.add_argument("--community_key", help="Community Key")
parser.add_argument("--user_id", help="User ID")
parser.add_argument("--file", help="Path to the image")
parser.add_argument("--content_type", help="Content Type of the image", required=False)
args = parser.parse_args()

igloo = pyigloo.igloo(params)
igloo.communityKey = args.community_key

allowedContentType = ['image/png', 'image/jpg']

if args.content_type is None:
    args.content_type = magic.detect_from_filename(args.file).mime_type

if args.content_type not in allowedContentType:
    print("Allowed contentTypes "+str(" ".join(allowedContentType)))


igloo.update_profile_picture(args.user_id, args.file, args.content_type)