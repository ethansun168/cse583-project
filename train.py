import json
import os
import re
import pandas as pd
from extract import static

import torch
from transformers import get_linear_schedule_with_warmup
from torch.utils.data import RandomSampler, DataLoader
from tqdm import tqdm
import numpy as np
import logging

from torch.utils.data import Dataset
class LoopPragmaDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features.values
        self.labels = labels.values

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        x = torch.tensor(self.features[idx], dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.long)  # long for classification
        return x, y

# def parse_pragma(pragma_str):
#     """
#     Extracts pragma fields from a string like:
#     "#pragma omp parallel for collapse(2) schedule(static, 4)"
#     """
#     collapse = re.search(r'collapse\((\d+)\)', pragma_str)
#     schedule = re.search(r'schedule\((\w+),\s*(\d+)\)', pragma_str)
    
#     return {
#         'collapse': int(collapse.group(1)) if collapse else 1,
#         'schedule_type': schedule.group(1) if schedule else 'static',
#         'chunk_size': int(schedule.group(2)) if schedule else 1
#     }

def extract_features_from_example(example):
    static = example.get('static_analysis', [])

    # Aggregate over all loops
    instruction_count = sum(loop.get('NumInstructions', 0) for loop in static)
    load_count = sum(loop.get('Loads', 0) for loop in static)
    store_count = sum(loop.get('Stores', 0) for loop in static)
    branch_count = sum(loop.get('Branches', 0) for loop in static)

    features = {
        'instruction_count': instruction_count,
        'load_count': load_count,
        'store_count': store_count,
        'branch_count': branch_count,

        'exist': int(example.get('exist', False)),
        'private': int(example.get('private', False)),
        'reduction': int(example.get('reduction', False)),
    }

    return features

def load_dataset(json_path):
    data = []
    with open(json_path, 'r') as f:
        for line in f:
            ex = json.loads(line.strip())
            
            with open(ex['code'], 'r') as code_file:
                ex['code'] = code_file.read()
            
            with open(ex['static_analysis'], 'r') as static_file:
                ex['static_analysis'] = static(static_file)
            
            data.append(ex)

    return data

def process_dataset(json_path):
    dataset = load_dataset(json_path)
    features_list = []
    labels_list = []

    for ex in dataset:
        features = extract_features_from_example(ex)
        label = int(ex.get('exist', False))  # <- this is your target

        features_list.append(features)
        labels_list.append(label)
    
    # Convert to DataFrame
    X = pd.DataFrame(features_list)
    y = pd.DataFrame(labels_list)
    
    return X, y

class Args:
    train_batch_size = 16
    learning_rate = 5e-5
    adam_epsilon = 1e-8
    weight_decay = 0.01
    epochs = 5
    gradient_accumulation_steps = 1
    max_grad_norm = 1.0
    output_dir = './output'
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_gpu = torch.cuda.device_count()


# Define a simple MLP model (example)
class MLP(torch.nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        self.fc1 = torch.nn.Linear(input_size, 128)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(128, output_size)
    
    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

# Simplified train function
def train(args, train_dataset, model):
    train_dataloader = DataLoader(train_dataset, batch_size=args.train_batch_size, shuffle=True)

    args.max_steps = args.epochs * len(train_dataloader)
    args.warmup_steps = args.max_steps // 5
    args.save_steps = len(train_dataloader) // 10

    model.to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, eps=args.adam_epsilon)
    # optimizer = AdamW(model.parameters(), lr=args.learning_rate, eps=args.adam_epsilon)
    scheduler = get_linear_schedule_with_warmup(optimizer, args.warmup_steps, args.max_steps)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    model.train()
    global_step = 0

    for epoch in range(args.epochs):
        total_loss = 0
        for step, (features, labels) in enumerate(tqdm(train_dataloader)):
            features, labels = features.to(args.device), labels.to(args.device)
            labels = labels.float()
            outputs = model(features)
            loss = loss_fn(outputs.squeeze(), labels)


            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()
            global_step += 1

        avg_loss = total_loss / len(train_dataloader)
        logger.info(f"Epoch {epoch+1}, Average Loss: {avg_loss:.4f}")

# Run training

if __name__ == '__main__':
    args = Args()

    # Load your dataset
    dataset_path = 'database.jsonl'
    X, y = process_dataset(dataset_path)

    # Convert y to a flat Series instead of a DataFrame
    if isinstance(y, pd.DataFrame):
        y = y.iloc[:, 0]  # Take the first (and only) column

    # Convert to torch Dataset
    train_dataset = LoopPragmaDataset(X, y)

    # Instantiate model
    model = MLP(input_size=X.shape[1], output_size=1)  # Binary classification
    

    # Set up logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    train(args, train_dataset, model)

    # Save only the model weights (recommended)
    torch.save(model.state_dict(), 'model_weights.pth')

    logger.info("Model saved successfully.")

