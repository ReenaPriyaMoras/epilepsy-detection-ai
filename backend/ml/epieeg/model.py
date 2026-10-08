import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import (
    MODEL_PATH,
    DEVICE,
    NUM_NODES,
    NODE_FEATURES,
    HIDDEN_DIM,
)


# ---------------------------------------------------
# Graph Convolution Block
# ---------------------------------------------------

class GraphConvBlock(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()

        self.fc = nn.Linear(in_features, out_features)

    def forward(self, x, adj):
        # Set to True for verbose tensor debugging
        DEBUG = False
        
        if DEBUG:
            print("\n========== GRAPH DEBUG ==========")
            print("Input shape:", x.shape)
            print("Adj shape:", adj.shape)
            print("Input min:", torch.min(x))
            print("Input max:", torch.max(x))
            print("Input NaN:", torch.isnan(x).any())

        h = self.fc(x)

        if DEBUG:
            print("Linear output shape:", h.shape)
            print("Linear NaN:", torch.isnan(h).any())

        out = torch.matmul(adj, h)

        if DEBUG:
            print("Matmul output shape:", out.shape)
            print("Matmul NaN:", torch.isnan(out).any())
            print("=================================\n")

        return F.leaky_relu(out, negative_slope=0.1)


# ---------------------------------------------------
# Hybrid GNN + BiLSTM + BiGRU
# ---------------------------------------------------

class GNN_BiLSTM_BiGRU(nn.Module):

    def __init__(
        self,
        num_nodes=NUM_NODES,
        node_in_feats=NODE_FEATURES,
        hidden_dim=HIDDEN_DIM,
    ):
        super().__init__()

        self.gnn = GraphConvBlock(
            node_in_feats,
            hidden_dim,
        )

        self.gnn_norm = nn.LayerNorm(hidden_dim)

        self.bilstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )

        self.lstm_norm = nn.LayerNorm(hidden_dim * 2)

        self.bigru = nn.GRU(
            input_size=hidden_dim * 2,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )

        self.gru_norm = nn.LayerNorm(hidden_dim * 2)

        self.classifier = nn.Sequential(

            nn.Linear(hidden_dim * 2, 64),

            nn.BatchNorm1d(64),

            nn.ReLU(),

            nn.Dropout(0.3),

            nn.Linear(64, 1)

        )

    def forward(self, x, adj):
        gnn_out = self.gnn(x, adj)
        gnn_out = self.gnn_norm(gnn_out)
        
        lstm_out, _ = self.bilstm(gnn_out)
        lstm_out = self.lstm_norm(lstm_out)
        
        gru_out, _ = self.bigru(lstm_out)
        gru_out = self.gru_norm(gru_out + lstm_out)
        
        pooled = torch.mean(gru_out, dim=1)
        logits = self.classifier(pooled)
        
        return torch.sigmoid(logits)


import threading

_model_lock = threading.Lock()

# ---------------------------------------------------
# Singleton Loader
# ---------------------------------------------------

class EpiEEGModelLoader:

    _instance = None
    _loaded = False

    model = None
    adj_matrix = None
    scaler_mean = None
    scaler_scale = None
    threshold = 0.5

    @classmethod
    def load(cls):
        if not cls._loaded:
            with _model_lock:
                if not cls._loaded:
                    checkpoint = torch.load(
                        MODEL_PATH,
                        map_location=DEVICE,
                        weights_only=False,
                    )

                    model = GNN_BiLSTM_BiGRU()
                    model.load_state_dict(checkpoint["model_state_dict"])
                    model.eval()

                    cls.model = model
                    cls.adj_matrix = checkpoint["adj_matrix"].float()
                    cls.scaler_mean = checkpoint["scaler_mean"]
                    cls.scaler_scale = checkpoint["scaler_scale"]
                    cls.threshold = checkpoint.get("threshold", 0.5)

                    cls._loaded = True

        return cls