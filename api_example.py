import requests
import json # parses json into a python object for us

status = requests.get("insert your url here")
py_obj = json.loads(status.text) # parse the text as a json and return a python object