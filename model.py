import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Sample data: replace with actual dataset
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

# Function to preprocess text
def preprocess_text(text):
    # Remove URLs and special characters, and convert to lowercase
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower().strip()

# Function to extract feature from file changes
def extract_feature(file_changes):
    features = set()
    for file_path in file_changes.keys():
        match = re.search(r'/src/pages/([^/]+)/', file_path) or re.search(r'/src/([^/]+)/', file_path)
        if match:
            features.add(match.group(1))
    return ' '.join(features)

# Prepare data
commit_messages = []
features = []

for item in data:
    file_feature = extract_feature(item['file_changes'])
    combined_text = file_feature
    commit_messages.append(combined_text)
    features.append(item['feature'])

# Vectorize text using TF-IDF
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(commit_messages)
y = features

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=1))

# Predict feature for new commit
new_file_changes = {
    "prism/aphrodite/web/app/react/16/src/image_placement/api/v3.js": {
                "lines_inserted": 22,
                "size_delta": 513,
                "size": 2971
            },
}

new_combined_text =extract_feature(new_file_changes)
new_X = vectorizer.transform([new_combined_text])
predicted_feature = label_encoder.inverse_transform(model.predict(new_X))
print("Predicted Feature:", predicted_feature[0])
