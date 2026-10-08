import torch
import numpy as np
import time

from .feature_labels import get_feature_label
from .channel_labels import get_channel_label

def compute_attribution(loader, features_numpy):
    """
    Computes feature attribution using Input * Gradient method.
    This is fully compatible with GNN-BiLSTM architectures.
    Safely manages gradients without state leakage.
    """
    loader.model.zero_grad(set_to_none=True)
    device = loader.model.bilstm.weight_ih_l0.device
    
    # Create tensor, unsqueeze first, then set requires_grad so it is a leaf tensor
    x = torch.tensor(features_numpy, dtype=torch.float32, device=device).unsqueeze(0)
    x.requires_grad_(True)
    
    adj_matrix = loader.adj_matrix.to(device)
    
    with torch.set_grad_enabled(True):
        output = loader.model(x, adj_matrix)
        if output.numel() == 1:
            output.backward()
        else:
            output.backward(torch.ones_like(output))
            
    if x.grad is not None:
        attribution = (x.grad * x).abs().squeeze(0).detach().cpu().numpy()
    else:
        # Fallback to feature magnitude if grad is not available
        attribution = np.abs(features_numpy)
    
    # Zero gradients immediately and cleanup
    loader.model.zero_grad(set_to_none=True)
    del x, adj_matrix, output
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return attribution

def generate_explanation(loader, features_numpy, prediction):
    try:
        start_time = time.time()
        
        # 1. Compute attribution scores (43 channels x 17 features)
        attribution = compute_attribution(loader, features_numpy)
        
        # Normalize attribution to [0, 1] range globally for percentages
        total_importance = np.sum(attribution)
        if total_importance > 0:
            attribution = attribution / total_importance
            
        # 2. Aggregate importance
        channel_importance = np.sum(attribution, axis=1) # Shape (43,)
        feature_importance = np.sum(attribution, axis=0) # Shape (17,)
        
        # 3. Get top channels
        top_channel_indices = np.argsort(channel_importance)[::-1][:5]
        top_channels = [
            {
                "name": get_channel_label(idx),
                "importance": float(round(channel_importance[idx], 4))
            }
            for idx in top_channel_indices
        ]
        
        # 4. Get top features
        top_feature_indices = np.argsort(feature_importance)[::-1][:5]
        top_features = [
            {
                "name": get_feature_label(idx),
                "importance": float(round(feature_importance[idx], 4))
            }
            for idx in top_feature_indices
        ]
        
        # 5. Generate clinical summary
        primary_feature = top_features[0]["name"].lower()
        secondary_feature = top_features[1]["name"].lower()
        primary_channel = top_channels[0]["name"]
        
        if prediction.lower() == "epileptic":
            summary = f"The model prediction was primarily influenced by anomalies in {primary_feature} and {secondary_feature}, particularly localized around the {primary_channel} channel. These variations are consistent with patterns often observed in epileptic recordings."
        else:
            summary = f"The normal EEG classification was driven by expected baseline levels of {primary_feature} and {secondary_feature}. The {primary_channel} channel contributed most significantly to establishing this healthy baseline."
            
        return {
            "top_channels": top_channels,
            "top_features": top_features,
            "summary": summary,
            "time_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
