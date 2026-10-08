from ml.epieeg.model import EpiEEGModelLoader
import torch

loader = EpiEEGModelLoader.load()

adj = loader.adj_matrix

print("Shape:", adj.shape)
print("dtype:", adj.dtype)
print("Min:", torch.min(adj))
print("Max:", torch.max(adj))
print("Contains NaN:", torch.isnan(adj).any())
print("Contains Inf:", torch.isinf(adj).any())