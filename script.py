#!/usr/bin/env python3
import os
import time
import json
import requests
from requests.auth import HTTPBasicAuth
from joblib import load
import urllib3

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables and model
username = os.getenv("JITA_USERNAME")
password = os.getenv("JITA_PASSWORD")
model = load("feature_predictor.joblib")
change_url = "https://gerrit.eng.nutanix.com/c/prismui/+/882755"

# Function to get data from a URL
def get_data_from_url(url, username, password):
    # Send a GET request to the URL with basic authentication
    response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        # If the response is successful, parse the JSON data and return it
        return json.loads(response.text[5:])
    else:
        # If the response is not successful, print an error message and return None
        print(f"Error while fetching data from {url}: \n" + response.text)
        return None

# Function to get files from a change URL
def get_files(change_url):
    # Extract the change number from the URL
    change_number  = change_url.split("/")[-1]  
    url = f"https://gerrit.eng.nutanix.com/a/changes/{change_number}/revisions/current/files"
    # Get the data from the URL and return it
    return get_data_from_url(url, "dhaval.maniar", os.getenv("GERRIT_PASSWORD"))

# Function to predict feature based on file changes
def predict_feature(file_changes):
    paths_concatenated = " ".join(file_changes.keys())
    # Use the model to predict the feature and return the result
    return model.predict([paths_concatenated])[0]

# Function to modify a JSON file
def modify_json_file(file_path, modifications):
    # Open the file and load the JSON data
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Apply the modifications to the data
    for key, value in modifications.items():
        data[key] = value
    # Write the modified data back to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    # Return the modified data
    return data

# Function to create a test set
def create_testset():
    # Modify the JSON file with the test set name
    data = modify_json_file('create_test_set.json', {'name': "anti_affinity_test_set_final"})
    # Post the data to the URL to create the test set and return the result
    return post_data("https://jita.eng.nutanix.com/api/v1/agave_test_sets", read_from_file("create_test_set.json"), username, password)

# Function to get test results
def get_test_results(oid):
    if oid:
        # Modify the JSON file with the task ID
        data = modify_json_file('trigger_jp.json', {'raw_query': {'agave_task_id': {'$in': [{'$oid': oid}]}}})
        while True:
            # Post the data to the URL to get the test results
            data = post_data("https://jita.eng.nutanix.com/api/v2/reports/agave_test_results", read_from_file("trigger_jp.json"), username, password)
            if data:
                # If the data is received, check the status of the tests
                statuses = [item['status'] for item in data['data']]
                # If all tests are not pending or running, return the results
                if all(status not in ["Pending", "Running"] for status in statuses):
                    return {"passed": statuses.count("Succeeded"), "failed": statuses.count("Failed"), "failed_test_cases": [{"name": item['test']['name'],"url": item['test_log_url']} for item in data['data'] if "Failed" in item['status']]}
                else:
                    # If some tests are still pending or running, wait for 10 minutes and then check again
                    print("Waiting for tests to complete")
                    time.sleep(600)

# Function to run the script
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

# Run the script
run_the_script()