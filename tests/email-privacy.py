import sys
import os
import pprint

from uuid import UUID

# shamelessly copied (after testing) from https://stackoverflow.com/a/33245493
# Martin Thoma @ Oct 20, 2015 at 19:43
def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


from dotenv import load_dotenv
if os.getenv("ENV") != None:
    load_dotenv('.env.' + os.getenv("ENV"))

load_dotenv()

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except NameError:
    sys.path.insert(0, "../")

import pyigloo

pp = pprint.PrettyPrinter(indent=4)

params = {
        "ACCESS_KEY":   os.getenv("ACCESS_KEY"),
        "API_KEY":      os.getenv("API_KEY"),
        "API_USER":     os.getenv("API_USER"),
        "API_PASSWORD": os.getenv("API_PASSWORD"),
        "API_ENDPOINT": os.getenv("API_ENDPOINT")
}

igloo = pyigloo.igloo(params)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--readfile', type=argparse.FileType('r'), default='-', help="Filename to read ids from")
args = parser.parse_args()

lines = args.readfile.readlines()

for user in lines:
    if not is_valid_uuid(user):
        find_users = igloo.search_members(user, 1)
        if len(find_users["value"]["hit"]) > 0:
            user = find_users["value"]["hit"][0]["id"]
    
    igloo.users_update(user, emailPrivacy="Members")
