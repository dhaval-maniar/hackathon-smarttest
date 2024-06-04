# SmartTest: Streamlined Regression for Agile Development - Team 6

SmartTest is an advanced AI-driven regression checker Slack bot designed to streamline the testing process and reduce overhead cycles. When a developer merges a change request (CR), they input the CR link into the bot. In the background, a robust machine learning model analyses the CR changes, including affected files, titles, commit message, etc, to identify which entity might be impacted.

Once the analysis is complete, JITA runs are triggered, executing only the selected tests that are likely to be affected by the change. After all tests are executed, a detailed report highlighting the number of passed and failed tests, along with failure logs, is sent back to the developer and QA team. This allows for immediate rectification of any issues, eliminating the need to wait for the bi-weekly regression cycles.

This real-time feedback mechanism created by the bot significantly reduces overhead cycles, increases efficiency, and maintains a high quality index (QI) for the product. By avoiding delays in important releases, SmartTest ensures that the development process is both efficient and reliable.
You added SmartTest to this workspace.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python 3 installed on your machine. The script uses the following Python libraries:

- pandas
- sklearn
- os
- time
- json
- requests
- joblib
- urllib3

You can install these libraries using pip:

```pip install install requests joblib urllib3```

Installation:

Clone the repository to your local machine:

```git clone https://github.com/nutanix-engineering/hack2024-interns-team6```
Navigate to the project directory:
```cd hack2024-interns-team6```

Usage
- Run the script to train the model ```python3 classification_model.py```
- Now the model ```feature_predictor.joblib``` is generated 
- Start the slack server ```python3 server.py```
- Now the Bot is listening for Gerrit links
