import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
from train import process_dataset, LoopPragmaDataset, MLP

# Load dataset
dataset_path = 'database.jsonl'
X, y = process_dataset(dataset_path)

# Convert to PyTorch dataset and dataloader
dataset = LoopPragmaDataset(X, y)
dataloader = DataLoader(dataset, batch_size=32)

# Initialize and load model
model = MLP(input_size=X.shape[1], output_size=1)
model.load_state_dict(torch.load('model_weights.pth'))
model.eval()  # Set model to evaluation mode

# Evaluate the model
all_preds = []
all_labels = []

with torch.no_grad():  # Disable gradient calculation
    for inputs, labels in dataloader:
        outputs = model(inputs)  # Get the model's predictions
        preds = (outputs.squeeze() > 0.5).int()  # Binary threshold at 0.5
        all_preds.extend(preds.tolist())  # Collect predictions
        all_labels.extend(labels.tolist())  # Collect true labels

# Calculate accuracy
acc = accuracy_score(all_labels, all_preds)
print(f"Accuracy: {acc:.4f}")
