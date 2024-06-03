import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

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

# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)  # Assuming binary classification

# Prepare data
X = []
y = []

for item in data:
    feature = item['feature']
    file_changes = item['file_changes']
    file_paths = list(file_changes.keys())
    concatenated_file_paths = ' '.join(file_paths)  # Concatenate file paths into a single string
    X.append(concatenated_file_paths)
    y.append(feature)

# Tokenize and encode text data
encoded_data = tokenizer(X, return_tensors='pt', padding=True, truncation=True, max_length=512)

# Split data into train and test sets
train_inputs, test_inputs, train_labels, test_labels = train_test_split(encoded_data, y, test_size=0.2, random_state=42)

# Convert labels to tensors
train_labels = torch.tensor(train_labels)
test_labels = torch.tensor(test_labels)

# Define optimizer and loss function
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
criterion = torch.nn.CrossEntropyLoss()

# Training loop
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

num_epochs = 5
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(**train_inputs, labels=train_labels)
    loss = outputs.loss
    loss.backward()
    optimizer.step()

    # Evaluation
    model.eval()
    with torch.no_grad():
        outputs = model(**test_inputs)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1)
        acc = accuracy_score(test_labels.cpu(), preds.cpu())
        precision = precision_score(test_labels.cpu(), preds.cpu(), average='weighted')
        recall = recall_score(test_labels.cpu(), preds.cpu(), average='weighted')
        f1 = f1_score(test_labels.cpu(), preds.cpu(), average='weighted')

    print(f'Epoch {epoch + 1}/{num_epochs}, Test Accuracy: {acc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}')

# Save the trained model and tokenizer
output_dir = './saved_model/'
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

tokenizer = BertTokenizer.from_pretrained(output_dir)
model = BertForSequenceClassification.from_pretrained(output_dir)

# Define function to make predictions
def predict(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_label_id = torch.argmax(outputs.logits).item()
    return predicted_label_id

# Example usage
text = "prism/aphrodite/web/app/react/16/src/pages/image_throttling/ThrottlingPolicyForm/ThrottlingPolicyForm.jsx"
predicted_feature_id = predict(text)
print("Predicted Feature ID:", predicted_feature_id)