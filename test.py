#!/usr/bin/env python3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import time
import requests
from requests.auth import HTTPBasicAuth
import json
import re

from joblib import load

model = load("feature_predictor.joblib")
test_case_name = "anti_affinity_test_case_1"
change_url = "https://gerrit.eng.nutanix.com/c/prismui/+/882755"

import os

#oid = "665da081d24d8242019fd446"
feature = ""
jp_name = "test-jp-image-final-3"
test_set_name = "testset-final-3"

def get_files(change_url):
    username = "dhaval.maniar"
    password = "LQ7l3K0gHvQdWqXDOcOFXApsFB184TvREmPm3qFfFQ"
 
    change_number  = change_url.split("/")[-1]  
 
    response = requests.get(f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/files", auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = json.loads(response.text[5:])
        pretty_data = json.dumps(data, indent=4)
        print("Files changed: " + pretty_data)
        return data
    else:
        print("Error while fetching files: \n" + response.text)
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
        print("Title of Change:" + title)
        print("Commit message:" + message)
    else:
        print("Error while getting commit message: \n" + response.text)

def predict_feature(file_changes):
    paths_concatenated = " ".join(file_changes.keys())
    return model.predict([paths_concatenated])[0]

# def parse_filepath(file_path):
#     match = re.search(r'/src/pages/([^/]+)/', file_path) or re.search(r'/src/([^/]+)/', file_path)
#     if match:
#         return match.group(1)
#     return None
 
def read_from_file(file_path):
    with open(file_path,'r') as file:
        data=file.read()
        # print(data)
        return data
 
# def extract_feature(files):
#     features = ""
#     for file in files:
#         feature = parse_filepath(file)
#         if feature:
#             features = feature
#     return features
 
# create_testset()

def caller():
    files = get_files(change_url)
    get_commitmsg(change_url)
    jp_name = f"anti_affinity_test_jp_final"
    if files:
        # feature = predict_feature(files)
        feature = "anti_affinity"
        print("Predicted Feature: " + feature)
    create_testset()
    yield f"Created Testset with Anti Affinity test cases"
    id=create_jp()
    job_id=trigger_jp(id)
    yield "Triggered the Job Profile: " + jp_name
    result=get_test_results(job_id)
    yield result

def create_testset():
    username = "dhaval.maniar@nutanix.com"
    password=os.getenv("JITA_PASSWORD")

    # Load the JSON file
    with open('create_test_set.json', 'r') as f:
        data = json.load(f)

    # Modify the 'name' field
    data['name'] = "anti_affinity_test_set_final"

    # Write the JSON back to the file
    with open('create_test_set.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    response = requests.post(f"https://jita.eng.nutanix.com/api/v1/agave_test_sets",data=read_from_file("create_test_set.json"),auth=(username, password), verify=False)
    if response.status_code == 200:
        print("TestSet Created for feature Anti Affinity")
    else:
        print("Error while creating testset: \n" + response.text)

def get_testset():
    username = "dhaval.maniar@nutanix.com"
    password=os.getenv("JITA_PASSWORD") 
    name = "anti_affinity_test_set_final"
    response = requests.get(f"https://jita.eng.nutanix.com/api/v2/agave_test_sets?only=name,tests.framework_version,tests.name&start=0&limit=25&raw_query=%7B%22name%22:%7B%22$regex%22:%22{name}%22,%22$options%22:%22i%22%7D%7D",auth=(username, password), verify=False)
    if response.status_code == 200:
        response_dict = json.loads(response.text)
        for item in response_dict['data']:
            oid = item['_id']['$oid']
            return oid
    else:
        print("Error while getting testset: \n" + response.text)
        return ""


def create_jp():
    oid=get_testset()
    username = "dhaval.maniar@nutanix.com"
    password=os.getenv("JITA_PASSWORD")
    # print(oid)
    # Load the JSON file
    with open('create_jp.json', 'r') as f:
        data = json.load(f)

    # Modify the name and $oid value in create_jp.json
    data['name'] = "anti_affinity_jp_final"
    for test_set in data['test_sets']:
        test_set['$oid'] = oid

    # Write the modified JSON back to the file
    with open('create_jp.json', 'w') as f:
        json.dump(data, f, indent=4)

    response = requests.post(f"https://jita.eng.nutanix.com/api/v2/job_profiles",data=read_from_file("create_jp.json"),auth=(username, password), verify=False)
    if response.status_code == 200:
        response_dict = json.loads(response.text)
        print(f"Job Profile Created with name: anti_affinity_jp_final \n")
        return response_dict['id']
    else:
        print("Error while creating Job Profile: \n" + response.text)
        return None


def trigger_jp(oid):
    username = "dhaval.maniar@nutanix.com"
    password=os.getenv("JITA_PASSWORD")
    
    response = requests.post(f"https://jita.eng.nutanix.com/api/v2/job_profiles/{oid}/trigger", data="{}", auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = json.loads(response.text)
        job_id=data["task_ids"][0]["$oid"]
        print("Job profile with id: " + job_id + "triggered successfully")
        return job_id
    else:
        print("Error while triggering jp: " + response.text)
        return None


# trigger_jp("6658b9cad24d8241fcef81ff")

def get_test_results(oid):
    username = "dhaval.maniar@nutanix.com"
    password = os.getenv("JITA_PASSWORD")

    # Load the JSON file
    with open('trigger_jp.json', 'r') as f:
        data = json.load(f)

    # Modify the $oid value
    data['raw_query']['agave_task_id']['$in'][0]['$oid'] = oid

    # Write the modified JSON back to the file
    with open('trigger_jp.json', 'w') as f:
        json.dump(data, f, indent=4)

    while True:
        response = requests.post(f"https://jita.eng.nutanix.com/api/v2/reports/agave_test_results",data=read_from_file("trigger_jp.json"), auth=HTTPBasicAuth(username, password), verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            statuses = [item['status'] for item in data['data']]
            check = False
            for status in statuses:
                if "Pending" in status or "Running" in status:
                    check = True  
                    break               
            if not check:
                print("All tests completed")
                passed = 0
                failed = 0
                for status in statuses:
                    if "Failed" in status:
                        failed += 1
                    elif "Passed" in status:
                        passed += 1
                failed_tests = []
                for item in data['data']:
                    if "Failed" in item['status']:
                        failed_tests.append({"name": item['test']['name'],"url": item['test_log_url']})
                return {"passed": passed, "failed": failed, "failed_test_cases": failed_tests}
            else:
                check=False
                print("Waiting for tests to complete")
                time.sleep(600)
        
# def edit_json_file(json_file, key_to_edit, new_value):
#     # Read the JSON file
#     with open(json_file, 'r') as file:
#         data = json.load(file)
#     # Modify the dictionary
#     if key_to_edit in data:
#         data[key_to_edit] = new_value
#         print(f"Key '{key_to_edit}' updated with new value '{new_value}'.")
#     else:
#         print(f"Key '{key_to_edit}' not found in the JSON file.")
#     # Write the modified dictionary back to the JSON file
#     with open(json_file, 'w') as file:
#         json.dump(data, file, indent=4)

caller()

