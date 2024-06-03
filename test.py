#!/usr/bin/env python3

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from requests.auth import HTTPBasicAuth
import json
import re

from joblib import load

model = load("feature_predictor.joblib")

change_url = "https://gerrit.eng.nutanix.com/c/prismui/+/878523"

def get_files(change_url):
    username = "dhaval.maniar"
    password = "LQ7l3K0gHvQdWqXDOcOFXApsFB184TvREmPm3qFfFQ"

    change_number  = change_url.split("/")[-1]  

    response = requests.get(f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/files", auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = json.loads(response.text[5:])
        return data
    else:
        print(response.text)
        return None

def get_commitmsg (change_url):
    username = "dhaval.maniar"
    password = "LQ7l3K0gHvQdWqXDOcOFXApsFB184TvREmPm3qFfFQ"

    change_number = change_url.split("/")[-1]

    response = requests.get(f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/commit", auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = json.loads(response.text[5:])
        title = data["subject"]
        message = data["message"] 
        print(title)
        print(message)
    else:
        print(response.text)

def predict_feature(file_changes):
    paths_concatenated = " ".join(file_changes.keys())
    return model.predict([paths_concatenated])[0]
def parse_filepath(file_path):
    match = re.search(r'/src/pages/([^/]+)/', file_path) or re.search(r'/src/([^/]+)/', file_path)
    if match:
        return match.group(1)
    return None

def extract_feature(files):
    features = ""
    for file in files:
        feature = parse_filepath(file)
        if feature:
            features = feature
    return features

files = get_files(change_url)

if files:
    features = predict_feature(files)
    print(features)