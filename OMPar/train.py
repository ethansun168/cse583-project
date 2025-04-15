import torch
from torch.utils.data import DataLoader, Subset
from OMPify.model import OMPify  # Load your model from OMPify/model.py
from OMPify.dataset import OMPifyDataset, group_split_dataset
import os

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Initialize OMPify model with pretrained weights and set it to training mode.
ompfy = OMPify(model_path="OMPify", device=device)
ompfy.model.train()

# Initialize the dataset using the JSON file from OMPify/database.json.
dataset = OMPifyDataset("OMPify/database.json", tokenizer=None, ompfy=ompfy)

# Use the group_split_dataset function to split the dataset by folder group.
train_idx, val_idx = group_split_dataset(dataset, train_ratio=0.8)
print(f"Grouped Split: {len(train_idx)} training samples, {len(val_idx)} validation samples.")

# Open a log file for appending results.
log_filename = "train_log.txt"

log_file = open(log_filename, "a", encoding="utf-8")
log_file.write(f"Grouped Split: {len(train_idx)} training samples, {len(val_idx)} validation samples.\n")

# Create DataLoaders from the subsets.
train_dataset = Subset(dataset, train_idx)
eval_dataset = Subset(dataset, val_idx)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
eval_loader = DataLoader(eval_dataset, batch_size=8, shuffle=False)

# Initialize the optimizer.
optimizer = torch.optim.Adam(ompfy.model.parameters(), lr=1e-5)

num_epochs = 20
for epoch in range(num_epochs):
    total_loss = 0.0
    # Training loop.
    for features, targets in train_loader:
        input_ids = features["input_ids"].to(device)
        position_idx = features["position_idx"].to(device)
        attn_mask = features.get("attn_mask", None)
        if attn_mask is not None:
            attn_mask = attn_mask.to(device)

        dyn_feats = features["dynamic_features"].to(device)
        mem_feats = features["memory_features"].to(device)
        targets = targets.to(device)
        
        optimizer.zero_grad()
        output = ompfy.model(
            input_ids, position_idx, attn_mask,
            dynamic_feats=dyn_feats,
            memory_feats=mem_feats,
            pragma_labels=targets[:, 0],
            private_labels=targets[:, 1],
            reduction_labels=targets[:, 2]
        )

        loss = output[0]  # assuming the model returns (loss, probabilities)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    avg_loss = total_loss / len(train_loader)
    epoch_log = f"Epoch {epoch+1}/{num_epochs} - Average Loss: {avg_loss:.4f}\n"
    print(epoch_log)
    log_file.write(epoch_log)
    
    # Evaluation phase.
    ompfy.model.eval()
    total_correct = 0
    total_elements = 0
    with torch.no_grad():
        for features, targets in eval_loader:
            input_ids = features["input_ids"].to(device)
            position_idx = features["position_idx"].to(device)
            attn_mask = features.get("attn_mask", None)
            if attn_mask is not None:
                attn_mask = attn_mask.to(device)
            targets = targets.to(device)
            probs = ompfy.model(input_ids, position_idx, attn_mask)
            preds = (probs > 0.5).float()  # threshold at 0.5
            total_correct += (preds == targets).sum().item()
            total_elements += targets.numel()
    accuracy = total_correct / total_elements
    eval_log = f"Evaluation accuracy after epoch {epoch+1}: {accuracy * 100:.2f}%\n"
    print(eval_log)
    log_file.write(eval_log)
    
    ompfy.model.train()
    
    # Save a checkpoint at the end of each epoch.
    checkpoint_path = os.path.join("OMPify", f"checkpoint_epoch_{epoch+1}.bin")
    torch.save(ompfy.model.state_dict(), checkpoint_path)
    checkpoint_log = f"Checkpoint saved to {checkpoint_path}\n"
    print(checkpoint_log)
    log_file.write(checkpoint_log)
    log_file.flush()

# Save the final model weights.
final_model_path = os.path.join("OMPify", "new_model.bin")
torch.save(ompfy.model.state_dict(), final_model_path)
final_log = f"Retrained model saved to {final_model_path}\n"
print(final_log)
log_file.write(final_log)
log_file.close()
