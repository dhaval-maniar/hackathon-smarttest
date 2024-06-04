# Classification Model

This Python script is used for feature extraction and text classification. It uses regular expressions and TF-IDF for text preprocessing and feature extraction.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python 3 installed on your machine. The script uses the following Python libraries:

- os
- time
- json
- requests
- joblib
- urllib3

You can install these libraries using pip:

bash
```pip install install requests joblib urllib3```

Installing
Clone the repository to your local machine:

```git clone https://github.com/nutanix-engineering/hack2024-interns-team6```
Navigate to the project directory:
```cd hack2024-interns-team6```

Usage
- Run the script to train the model ``` python3 classification_model.py``
- Now the model ```feature_predictor.joblib``` is generated 
- Start the slack server ```python3 server.py```
- Now the Bot is listening for Gerrit links
