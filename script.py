#!/usr/bin/env python3
import os
import time
import json
import requests
from requests.auth import HTTPBasicAuth
from joblib import load
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username = os.getenv("JITA_USERNAME")
password = os.getenv("JITA_PASSWORD")
model = load("feature_predictor.joblib")
change_url = "https://gerrit.eng.nutanix.com/c/prismui/+/882755"

def get_data_from_url(url, username, password):
    response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        return json.loads(response.text[5:])
    else:
        print(f"Error while fetching data from {url}: \n" + response.text)
        return None

def get_files(change_url):
    change_number  = change_url.split("/")[-1]  
    url = f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/files"
    return get_data_from_url(url, "dhaval.maniar", os.getenv("GERRIT_PASSWORD"))

def get_commitmsg(change_url):
    change_number = change_url.split("/")[-1]
    url = f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/commit"
    return get_data_from_url(url, "dhaval.maniar", os.getenv("GERRIT_PASSWORD"))

def predict_feature(file_changes):
    paths_concatenated = " ".join(file_changes.keys())
    return model.predict([paths_concatenated])[0]

def read_from_file(file_path):
    with open(file_path,'r') as file:
        return file.read()

def modify_json_file(file_path, modifications):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for key, value in modifications.items():
        data[key] = value
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    return data

def post_data(url, data, username, password):
    response = requests.post(url, data=data, auth=(username, password), verify=False)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Error while posting data to {url}: \n" + response.text)
        return None

def create_testset():
    data = modify_json_file('create_test_set.json', {'name': "anti_affinity_test_set_final"})
    return post_data("https://jita.eng.nutanix.com/api/v1/agave_test_sets", read_from_file("create_test_set.json"), username, password)

def get_testset():
    name = "anti_affinity_test_set_final"
    url = f"https://jita.eng.nutanix.com/api/v2/agave_test_sets?only=name,tests.framework_version,tests.name&start=0&limit=25&raw_query=%7B%22name%22:%7B%22$regex%22:%22{name}%22,%22$options%22:%22i%22%7D%7D"
    data = get_data_from_url(url, username, password)
    if data:
        return data['data'][0]['_id']['$oid']
    return None

def create_jp():
    oid = get_testset()
    if oid:
        data = modify_json_file('create_jp.json', {'name': "anti_affinity_jp_final", 'test_sets': [{'$oid': oid}]})
        return post_data("https://jita.eng.nutanix.com/api/v2/job_profiles", read_from_file("create_jp.json"), username, password)['id']
    return None

def trigger_jp(oid):
    if oid:
        data = post_data(f"https://jita.eng.nutanix.com/api/v2/job_profiles/{oid}/trigger", "{}", username, password)
        if data:
            return data["task_ids"][0]["$oid"]
    return None

def get_test_results(oid):
    if oid:
        data = modify_json_file('trigger_jp.json', {'raw_query': {'agave_task_id': {'$in': [{'$oid': oid}]}}})
        while True:
            data = post_data("https://jita.eng.nutanix.com/api/v2/reports/agave_test_results", read_from_file("trigger_jp.json"), username, password)
            if data:
                statuses = [item['status'] for item in data['data']]
                if all(status not in ["Pending", "Running"] for status in statuses):
                    return {"passed": statuses.count("Succeeded"), "failed": statuses.count("Failed"), "failed_test_cases": [{"name": item['test']['name'],"url": item['test_log_url']} for item in data['data'] if "Failed" in item['status']]}
                else:
                    print("Waiting for tests to complete")
                    time.sleep(600)

def run_the_script():
    files = get_files(change_url)
    commit_msg = get_commitmsg(change_url)
    if files and commit_msg:
        print("Title of Change:" + commit_msg["subject"])
        print("Commit message:" + commit_msg["message"])
        print("Files changed: " + json.dumps(files, indent=4))
        feature = predict_feature(files)
        print("Predicted Feature: " + feature)
        create_testset()
        print("Created Testset with Anti Affinity test cases")
        id = create_jp()
        if id:
            job_id = trigger_jp(id)
            print("Triggered the Job Profile: " + job_id)
            result = get_test_results(job_id)
            print(result)

run_the_script()