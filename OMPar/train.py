import os
import torch
from torch.utils.data import DataLoader, Subset
from transformers import AdamW, get_linear_schedule_with_warmup  # scheduler helper
from OMPify.model import OMPify  # Load your model from OMPify/model.py
from OMPify.dataset import OMPifyDataset, group_split_dataset
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

# Device setup
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Hyperparameters
num_epochs = 10
batch_size = 10
learning_rate = 5e-5
weight_decay = 0.01
max_grad_norm = 1.0  # for gradient clipping
warmup_ratio = 0.1   # 10% of total steps

# Initialize model and set to training mode
ompfy = OMPify(model_path="OMPify", device=device, load_weights=True)
ompfy.model.train()

# Load dataset and split into train/validation groups
dataset = OMPifyDataset("OMPify/database.json", tokenizer=None, ompfy=ompfy)
train_idx, val_idx = group_split_dataset(dataset, train_ratio=0.8)
print(f"Grouped Split: {len(train_idx)} training samples, {len(val_idx)} validation samples.")

# Prepare DataLoaders
train_dataset = Subset(dataset, train_idx)
eval_dataset  = Subset(dataset, val_idx)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
eval_loader  = DataLoader(eval_dataset, batch_size=batch_size, shuffle=False)

# Optimizer and learning rate scheduler
optimizer = AdamW(
    ompfy.model.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay
)
# Compute total steps and warmup
total_steps = len(train_loader) * num_epochs
warmup_steps = int(warmup_ratio * total_steps)

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps
)

# Logging setup
log_file = open("train_log.txt", "a", encoding="utf-8")
log_file.write(f"Grouped Split: {len(train_idx)} training samples, {len(val_idx)} validation samples.\n")

best_f1 = 0.0

# Training loop
for epoch in range(1, num_epochs + 1):
    ompfy.model.train()
    total_loss = 0.0

    for features, targets in train_loader:
        input_ids   = features["input_ids"].to(device)
        position_idx= features["position_idx"].to(device)
        attn_mask   = features.get("attn_mask", None)
        if attn_mask is not None:
            attn_mask = attn_mask.to(device)
        dyn_feats   = features["dynamic_features"].to(device)
        mem_feats   = features["memory_features"].to(device)
        targets     = targets.to(device)

        optimizer.zero_grad()
        loss, _ = ompfy.model(
            input_ids, position_idx, attn_mask,
            dynamic_feats=dyn_feats,
            memory_feats=m
            em_feats,
            pragma_labels=targets[:, 0],
            private_labels=targets[:, 1],
            reduction_labels=targets[:, 2]
        )
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(ompfy.model.parameters(), max_grad_norm)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()

    avg_train_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch}/{num_epochs} - Train Loss: {avg_train_loss:.4f}")
    log_file.write(f"Epoch {epoch}/{num_epochs} - Train Loss: {avg_train_loss:.4f}\n")

    # Validation
    ompfy.model.eval()
    val_loss = 0.0
    y_true, y_pred = [], []
    with torch.no_grad():
        for features, targets in eval_loader:
            input_ids    = features["input_ids"].to(device)
            position_idx = features["position_idx"].to(device)
            attn_mask    = features.get("attn_mask", None)
            if attn_mask is not None:
                attn_mask = attn_mask.to(device)
            dyn_feats = features["dynamic_features"].to(device)
            mem_feats = features["memory_features"].to(device)
            targets   = targets.to(device)

            # Get loss and probabilities
            loss, probs = ompfy.model(
                input_ids, position_idx, attn_mask,
                dynamic_feats=dyn_feats,
                memory_feats=mem_feats,
                pragma_labels=targets[:, 0],
                private_labels=targets[:, 1],
                reduction_labels=targets[:, 2]
            )
            val_loss += loss.item()

            # Binarize predictions at 0.5
            y_true.append(targets.cpu())
            y_pred.append((probs > 0.5).float().cpu())

    avg_val_loss = val_loss / len(eval_loader)
    y_true = torch.cat(y_true, dim=0).numpy()
    y_pred = torch.cat(y_pred, dim=0).numpy()
    f1    = f1_score(y_true, y_pred, average='micro')
    prec  = precision_score(y_true, y_pred, average='micro')
    rec   = recall_score(y_true, y_pred, average='micro')
    # acc   = accuracy_score(y_true, y_pred)

    flat_true = y_true.flatten()
    flat_pred = y_pred.flatten()
    element_correct = (flat_true == flat_pred).sum()
    total_elements = flat_true.shape[0]
    acc = element_correct / total_elements

    print(f"Val Loss: {avg_val_loss:.4f} | F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | Acc: {acc:.4f}")
    log_file.write(
        f"Epoch {epoch} - Val Loss: {avg_val_loss:.4f} | "
        f"F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | Acc: {acc:.4f}\n"
    )

    # Save best model by F1
    if f1 > best_f1:
        best_f1 = f1
        best_path = os.path.join("OMPify", "best_model.bin")
        torch.save(ompfy.model.state_dict(), best_path)
        print(f"Best model saved to {best_path} (F1: {best_f1:.4f})")
        log_file.write(f"Saved best model (F1: {best_f1:.4f}) to {best_path}\n")

log_file.close()

