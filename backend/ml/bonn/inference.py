import logging
import traceback
import torch
import numpy as np
from fastapi import UploadFile, HTTPException
from .preprocessing import load_edf, preprocess_signal, create_model_input
from .model import model_loader

logger = logging.getLogger("inference_logger")

def predict_bonn(file_bytes: bytes) -> dict:
    """
    Synchronous CPU-bound inference for Bonn dataset model.
    Designed to run safely inside a worker thread pool.
    """
    if not file_bytes:
        raise ValueError("Uploaded EDF byte buffer is empty.")

    try:
        # 1. Load raw EDF bytes & resample channel 0
        raw_signal = load_edf(file_bytes)
        
        # 2. Preprocess (Normalize)
        processed_signal = preprocess_signal(raw_signal)
        
        # 3. Shape Tensor
        model_input = create_model_input(processed_signal)
        
        # 4. Access Singleton Model
        model = model_loader.get_model()
        
        # 5. Inference
        with torch.inference_mode():
            output = model(model_input)
            
            # Handle binary output / 2 classes
            if output.shape[-1] == 1:
                seizure_prob = float(torch.sigmoid(output).item())
            else:
                seizure_prob = float(torch.softmax(output, dim=-1)[0][1].item())
                
        seizure_prob = float(np.clip(seizure_prob, 0.0, 1.0))
        
        # 6. Formatting the Response
        confidence_score = seizure_prob if seizure_prob >= 0.5 else 1.0 - seizure_prob
        confidence_score = float(np.clip(confidence_score, 0.0, 1.0))
        prediction_label = "Epileptic" if seizure_prob >= 0.5 else "Non-Epileptic"
        
        # Explicit tensor cleanup
        del model_input, output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return {
            "prediction": prediction_label,
            "confidence_score": float(round(confidence_score, 4)),
            "seizure_probability": float(round(seizure_prob, 4)),
            "dataset": "Bonn",
            "status": "Success"
        }
        
    except HTTPException as he:
        raise he
    except ValueError as ve:
        logger.error(f"Bonn Validation Error: {str(ve)}")
        raise HTTPException(status_code=422, detail="Invalid EEG signal format or channel topology.")
    except Exception as e:
        logger.error(f"PyTorch Bonn Inference Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed internally: {str(e)}")

async def predict(file: UploadFile) -> dict:
    """Async wrapper around predict_bonn."""
    file_bytes = await file.read()
    return predict_bonn(file_bytes)