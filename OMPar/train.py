import torch
from torch.utils.data import DataLoader, Subset
from OMPify.model import OMPify  # Load your model from OMPify/model.py
from OMPify.dataset import OMPifyDataset, group_split_dataset
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import os

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Initialize OMPify model with pretrained weights and set it to training mode.
ompfy = OMPify(model_path="OMPify", device=device, load_weights=True)
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

# Initialize the optimizer and scheduler.
optimizer = torch.optim.AdamW(ompfy.model.parameters(), lr=5e-5, eps=1e-8, weight_decay=0.01)
total_steps = len(train_loader) * 20
scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=0.0, total_iters=total_steps)


best_f1 = 0
num_epochs = 20
# start_epoch = 17


# checkpoint_path = os.path.join("OMPify", "best_model.bin")
# ompfy.model.load_state_dict(torch.load(checkpoint_path))

for epoch in range(num_epochs):
# for epoch in range(start_epoch, num_epochs):
    total_loss = 0.0
    ompfy.model.train()
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
        scheduler.step()
        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch+1}/{num_epochs} - Average Loss: {avg_loss:.4f}")
    log_file.write(f"Epoch {epoch+1}/{num_epochs} - Average Loss: {avg_loss:.4f}\n")

    # Evaluation
    ompfy.model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for features, targets in eval_loader:
            input_ids = features["input_ids"].to(device)
            position_idx = features["position_idx"].to(device)
            attn_mask = features.get("attn_mask", None)
            if attn_mask is not None:
                attn_mask = attn_mask.to(device)
            dyn_feats = features["dynamic_features"].to(device)
            mem_feats = features["memory_features"].to(device)
            targets = targets.to(device)
            probs = ompfy.model(input_ids, position_idx, attn_mask, dynamic_feats=dyn_feats, memory_feats=mem_feats)
            # probs = ompfy.model(input_ids, position_idx, attn_mask, dynamic_feats=dyn_feats)
            y_true.append(targets.cpu())
            y_pred.append((probs > 0.5).float().cpu())

    y_true = torch.cat(y_true, dim=0).numpy()
    y_pred = torch.cat(y_pred, dim=0).numpy()
    f1 = f1_score(y_true, y_pred, average='micro')
    prec = precision_score(y_true, y_pred, average='micro')
    rec = recall_score(y_true, y_pred, average='micro')
    accuracy = accuracy_score(y_true, y_pred)

    print(f"Eval F1: {f1:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | Accuracy: {accuracy:.4f}")
    log_file.write(f"Eval F1: {f1:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | Accuracy: {accuracy:.4f}\n")


    # Save best checkpoint
    if f1 > best_f1:
        best_f1 = f1
        best_path = os.path.join("OMPify", "best_model.bin")
        torch.save(ompfy.model.state_dict(), best_path)
        print(f"Best model saved to {best_path} (f1: {best_f1:.4f})")
        log_file.write(f"Best model saved to {best_path} (f1: {best_f1:.4f})\n")

log_file.close()
