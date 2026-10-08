import os
import torch

# Define root directory properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "bonn", "weights", "EEG_Epilepsy_GNN_BiLSTM_BiGRU_30epochs.pth")

# Use CPU for inference by default
DEVICE = torch.device("cpu")

# Bonn dataset standards
SAMPLING_RATE = 173.61
WINDOW_SIZE = 4096

# Normalization constants
NORM_MEAN = 0.0
NORM_STD = 1.0