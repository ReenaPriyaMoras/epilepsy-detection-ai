import torch

MODEL_PATH = "ml/epieeg/weights/gnn_bilstm_bigru_split.pt"

ckpt = torch.load(
    MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

print("=" * 60)
print("Adjacency Matrix")
print("=" * 60)

adj = ckpt["adj_matrix"]

print(type(adj))
print("Shape:", adj.shape)

print("\n")

print("=" * 60)
print("Scaler Mean")
print("=" * 60)

print(type(ckpt["scaler_mean"]))

try:
    print(ckpt["scaler_mean"].shape)
except:
    print("No shape")

print("\n")

print("=" * 60)
print("Scaler Scale")
print("=" * 60)

print(type(ckpt["scaler_scale"]))

try:
    print(ckpt["scaler_scale"].shape)
except:
    print("No shape")

print("\n")

print("=" * 60)
print("Threshold")
print("=" * 60)

print(ckpt["threshold"])