import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

from joblib import dump

# Preparing the data
data = [
    {
        'file_changes': {
            "prism/aphrodite/web/app/react/16/src/pages/image_throttling/ThrottlingPolicyForm/ThrottlingPolicyForm.jsx": {
                "lines_inserted": 10,
                "lines_deleted": 2,
                "size_delta": 50,
                "size": 1500
            }
        },
        'feature': "image_throttling"
    },
    {
        'file_changes': {
            "prism/aphrodite/web/app/react/16/src/pages/image_throttling/EnrolledClustersTable/EnrolledClustersTable.jsx": {
                "lines_inserted": 2,
                "lines_deleted": 1,
                "size_delta": 37,
                "size": 13360
            }
        },
        'feature': "image_throttling"
    },
    {
        'file_changes': {
            "prism/aphrodite/web/app/react/16/src/pages/image_throttling/BandwidthThrottlingPolicy/BandwidthThrottlingPolicyDetails.jsx": {
                "lines_inserted": 5,
                "lines_deleted": 3,
                "size_delta": 20,
                "size": 1400
            }
        },
        'feature': "image_throttling"
    },
    {
        'file_changes': {
            "/COMMIT_MSG": {
                "status": "A",
                "lines_inserted": 21,
                "size_delta": 821,
                "size": 821
            },
            "prism/aphrodite/web/app/extras/i18n/en-US/i18n.json": {
                "lines_inserted": 13,
                "size_delta": 464,
                "size": 1326557
            },
            "prism/aphrodite/web/app/react/16/src/image_placement/api/index.ts": {
                "lines_inserted": 2,
                "lines_deleted": 1,
                "size_delta": 25,
                "size": 258
            }
        },
        'feature': "image_placement"
    },
    {
        'file_changes': {
            "/COMMIT_MSG": {
                "status": "A",
                "lines_inserted": 26,
                "size_delta": 965,
                "size": 965
            },
            "prism/aphrodite/web/app/react/16/src/image_placement/components/PolicyForm/PolicyForm.tsx": {
                "lines_inserted": 103,
                "lines_deleted": 92,
                "size_delta": 577,
                "size": 18150
            }
        },
        'feature': "image_placement"
    },
    {
        'file_changes': {
            "prism/aphrodite/web/app/react/16/src/image_placement/api/index.ts": {
                "lines_inserted": 2,
                "lines_deleted": 1,
                "size_delta": 25,
                "size": 258
            }
        },
        'feature': "image_placement"
    }
]

# Extracting file paths and features
file_paths = []
features = []

for entry in data:
    for file_path in entry['file_changes'].keys():
        file_paths.append(file_path)
        features.append(entry['feature'])

df = pd.DataFrame({'file_path': file_paths, 'feature': features})

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['file_path'], df['feature'], test_size=0.2, random_state=42)

# Creating a pipeline with a CountVectorizer and a MultinomialNB classifier
model = make_pipeline(CountVectorizer(), MultinomialNB())

# Training the model
model.fit(X_train, y_train)

# Predicting and evaluating the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

dump(model, 'feature_predictor.joblib')
