import logging
import traceback
import torch
import numpy as np
from fastapi import HTTPException

from .model import EpiEEGModelLoader
from .preprocessing import preprocess_edf

logger = logging.getLogger("inference_logger")

def predict_epieeg(file_bytes: bytes) -> dict:
    """
    Handles EDF bytes, processes them, 
    and returns a prediction payload.
    Stateless, leak-free, robust.
    """
    try:
        loader = EpiEEGModelLoader.load()
        
        # Preprocessing pipeline
        features = preprocess_edf(file_bytes)
        
        if features.shape != (43, 17):
            raise ValueError(f"Feature matrix shape mismatch: Expected (43, 17), got {features.shape}")
            
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        device = loader.model.bilstm.weight_ih_l0.device
        x = x.to(device)
        adj_matrix = loader.adj_matrix.to(device)
        
        with torch.inference_mode():
            output = loader.model(x, adj_matrix)
            # loader.model already includes sigmoid in forward() -> output is probability in [0, 1]
            raw_prob = output.item() if output.numel() == 1 else output[0].item()
            probability = float(np.clip(raw_prob, 0.0, 1.0))
            
        prediction = "Epileptic" if probability >= loader.threshold else "Non-Epileptic"
        confidence = probability if prediction == "Epileptic" else 1.0 - probability
        confidence = float(np.clip(confidence, 0.0, 1.0))
        
        # Explicit cleanup of tensors
        del x, adj_matrix, output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Explainability layer (failsafe)
        try:
            from .explainability import generate_explanation
            explainability_data = generate_explanation(loader, features, prediction)
        except Exception as e:
            logger.warning(f"Explainability generation notice: {str(e)}")
            explainability_data = None
            
        return {
            "status": "Success",
            "prediction": prediction,
            "confidence_score": float(round(confidence, 4)),
            "seizure_probability": float(round(probability, 4)),
            "dataset": "EpiEEG",
            "explainability": explainability_data
        }
    except ValueError as ve:
        logger.error(f"EpiEEG Validation Error: {str(ve)}")
        raise HTTPException(status_code=422, detail="Invalid EEG signal format or channel topology.")
    except Exception as e:
        logger.error(f"EpiEEG Inference Internal Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="EEG analysis inference failed due to an internal processing error.")