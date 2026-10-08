import traceback
import torch
from fastapi import UploadFile, HTTPException
from .preprocessing import load_edf, preprocess_signal, create_model_input
from .model import model_loader

async def predict(file: UploadFile) -> dict:
    """
    Main entry point for PyTorch inference.
    Executes EDF loading, signal processing, and robust PyTorch prediction.
    """
    try:
        # 1. Load raw EDF bytes
        file_bytes = await file.read()
        raw_signal = load_edf(file_bytes)
        
        # 2. Preprocess (Normalize)
        processed_signal = preprocess_signal(raw_signal)
        
        # 3. Shape Tensor
        model_input = create_model_input(processed_signal)
        
        # 4. Access Singleton Model
        model = model_loader.get_model()
        
        # 5. Inference
        with torch.no_grad():
            output = model(model_input)
            
            # The model might return a raw logit or softmax probabilities.
            # Handle binary output:
            if output.shape[-1] == 1:
                # Single logit -> Apply Sigmoid
                seizure_prob = torch.sigmoid(output).item()
            else:
                # Softmax case (2 classes)
                seizure_prob = torch.softmax(output, dim=-1)[0][1].item()
                
        # 6. Formatting the Response
        confidence_score = seizure_prob if seizure_prob >= 0.5 else 1.0 - seizure_prob
        
        if seizure_prob >= 0.5:
            prediction_label = "Epileptic"
        else:
            prediction_label = "Non-Epileptic"
            
        return {
            "prediction": prediction_label,
            "confidence_score": round(confidence_score, 4),
            "seizure_probability": round(seizure_prob, 4),
            "status": "Success"
        }
        
    except HTTPException as he:
        # Re-raise known FastApi exceptions to preserve accurate HTTP Status Codes
        raise he
    except Exception as e:
        # Log deep stack trace for internal backend debugging
        print("PyTorch Inference Error:", traceback.format_exc())
        # Return generic 500 so FastAPI doesn't crash
        raise HTTPException(status_code=500, detail=f"Prediction failed internally: {str(e)}")