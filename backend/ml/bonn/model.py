import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastapi import HTTPException
from .config import MODEL_PATH, DEVICE

class GNNLayer(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.self_transform = nn.Linear(input_dim, hidden_dim)
        self.neighbor_transform = nn.Linear(input_dim, hidden_dim)
        self.update = nn.Linear(hidden_dim * 2, hidden_dim)

    def forward(self, x, edge_index):
        num_nodes = x.size(0)
        source = edge_index[0]
        target = edge_index[1]
        
        self_features = self.self_transform(x)
        neighbor_features = self.neighbor_transform(x)
        
        aggregated = torch.zeros(num_nodes, neighbor_features.size(1), device=x.device)
        aggregated.index_add_(0, target, neighbor_features[source])
        
        degree = torch.zeros(num_nodes, device=x.device)
        degree.index_add_(0, target, torch.ones(source.size(0), device=x.device))
        degree = degree.clamp(min=1).unsqueeze(1)
        
        aggregated = aggregated / degree
        
        h = torch.cat([self_features, aggregated], dim=1)
        h = F.relu(self.update(h))
        return h

class GNNBiLSTMBiGRU(nn.Module):
    def __init__(self, n_nodes=64, node_len=64, hidden=64, classes=2):
        super().__init__()
        self.n_nodes = n_nodes
        self.node_len = node_len
        
        self.gnn1 = GNNLayer(node_len, 64)
        self.gnn2 = GNNLayer(64, 64)
        
        self.bilstm = nn.LSTM(input_size=64, hidden_size=hidden, batch_first=True, bidirectional=True)
        self.bigru = nn.GRU(input_size=hidden * 2, hidden_size=hidden, batch_first=True, bidirectional=True)
        
        self.dropout = nn.Dropout(0.35)
        self.classifier = nn.Linear(hidden * 2, classes)
        
        edges = []
        for i in range(n_nodes - 1):
            edges.append((i, i + 1))
            edges.append((i + 1, i))
        for i in range(n_nodes):
            edges.append((i, i))
            
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        self.register_buffer("edge_index", edge_index)

    def forward(self, x):
        batch_size = x.size(0)
        
        if x.dim() == 3 and x.size(-1) == 1:
            x = x.squeeze(-1)
            
        x = x.view(batch_size, self.n_nodes, self.node_len)
        
        graph_outputs = []
        for b in range(batch_size):
            h = self.gnn1(x[b], self.edge_index)
            h = self.gnn2(h, self.edge_index)
            graph_outputs.append(h)
            
        h = torch.stack(graph_outputs, dim=0)
        
        h, _ = self.bilstm(h)
        h, _ = self.bigru(h)
        
        h = h[:, -1, :]
        h = self.dropout(h)
        return self.classifier(h)

class BonnModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        """Implement Singleton Pattern."""
        if cls._instance is None:
            cls._instance = super(BonnModelLoader, cls).__new__(cls)
        return cls._instance

    def get_model(self) -> nn.Module:
        """
        Loads the PyTorch model strictly once.
        Automatically detects whether the file is a full model or a state_dict.
        """
        if self._model is None:
            if not os.path.exists(MODEL_PATH):
                raise HTTPException(status_code=500, detail=f"Model file not found at {MODEL_PATH}")
            try:
                # Load PyTorch file directly to the preferred device (CPU) safely
                loaded_data = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
                
                # Check if the loaded data is a state_dict or a full model
                if isinstance(loaded_data, dict) or isinstance(loaded_data, list):
                    # It's likely a state_dict. Instantiate the correct architecture.
                    self._model = GNNBiLSTMBiGRU(classes=2)
                    
                    # Some checkpoints wrap the state dict in another dict
                    if isinstance(loaded_data, dict) and 'model_state_dict' in loaded_data:
                        self._model.load_state_dict(loaded_data['model_state_dict'])
                    elif isinstance(loaded_data, dict) and 'state_dict' in loaded_data:
                        self._model.load_state_dict(loaded_data['state_dict'])
                    else:
                        self._model.load_state_dict(loaded_data)
                        
                elif isinstance(loaded_data, nn.Module):
                    # The file contains the full model architecture and weights
                    self._model = loaded_data
                else:
                    raise ValueError("Unknown format inside the PyTorch .pt file")
                    
                # Move model to CPU (or target device) and set to evaluation mode
                self._model.to(DEVICE)
                self._model.eval()
                
            except Exception as e:
                # Catch architecture mismatches or loading failures and return a 500
                raise HTTPException(status_code=500, detail=f"Failed to load PyTorch model: {str(e)}")
                
        return self._model

# Create Singleton instance to be imported
model_loader = BonnModelLoader()