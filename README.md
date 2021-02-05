# pyigloo

Beginnings of a python library to access the IGLOO API

## Building

You will need to use the python setup to install

## Using

You need to pass your igloo credentials to PyIgloo.

If you do not have the ACCESS_KEY and API_KEY for your Igloo site, you will need to contact [Igloo Developer Support](https://customercare.igloosoftware.com/support/developers/registration).

```python
import pyigloo

igloo = pyigloo.igloo({
        "ACCESS_KEY":   "11111111-1111-1111-1111-111111111111", 
        "API_KEY":      "MyAPIPassword",
        "API_USER":     "email@address.com",
        "API_PASSWORD": "password",
        "API_ENDPOINT": "https://yoursite.igloodigitalworkplace.ca/"
        })

print (igloo.community_view())
```

## Status

This is a proof of concept for the library. Feel free to try it out.

If you want to try `tests/login.py` you should create a `tests/.env` file that looks like this:

```python
ACCESS_KEY = "11111111-1111-1111-1111-111111111111"
API_KEY = "MyAPIPassword"
REPO_NAME = "yoursite.igloodigitalworkplace.ca"
API_USER = "email@address.com"
API_PASSWORD = "password"
API_ENDPOINT = "https://yoursite.igloodigitalworkplace.ca/"
```
