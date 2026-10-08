from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "weights" / "gnn_bilstm_bigru_split.pt"

DEVICE = torch.device("cpu")

NUM_NODES = 43
NODE_FEATURES = 17

HIDDEN_DIM = 64

THRESHOLD = 0.5