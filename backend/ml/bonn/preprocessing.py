import numpy as np
import mne
import os
import tempfile
import torch
from fastapi import HTTPException
from .config import SAMPLING_RATE, WINDOW_SIZE, NORM_MEAN, NORM_STD, DEVICE

def load_edf(file_bytes: bytes) -> np.ndarray:
    """
    Load an EDF file securely from bytes using MNE, extracting raw EEG signal.
    Automatically handles resampling if the EDF's frequency doesn't match Bonn Dataset standard.
    """
    try:
        # MNE requires a path on disk, we use a secure temporary file
        fd, tmp_path = tempfile.mkstemp(suffix=".edf")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(file_bytes)
            
            # Read the EDF silently
            raw = mne.io.read_raw_edf(tmp_path, preload=True, verbose=False)
            
            # Default to the first channel for simplicity. 
            data, times = raw[:]
            channel_data = data[0]
            
            # Resample if frequency mismatches standard (173.61 Hz)
            if raw.info['sfreq'] != SAMPLING_RATE:
                raw.resample(SAMPLING_RATE)
                data, times = raw[:]
                channel_data = data[0]
                
            return channel_data
            
        finally:
            # Ensure the temporary file is deleted regardless of success or failure
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted EDF file: {str(e)}")

def preprocess_signal(signal: np.ndarray) -> np.ndarray:
    """
    Apply standard Z-score normalization as expected by the trained model.
    """
    mean = np.mean(signal) if NORM_MEAN == 0.0 else NORM_MEAN
    std = np.std(signal) if NORM_STD == 1.0 else NORM_STD
    
    # Avoid division by zero
    if std == 0:
        std = 1e-8
        
    normalized = (signal - mean) / std
    return normalized

def create_model_input(signal: np.ndarray) -> torch.Tensor:
    """
    Convert the raw signal into a structured PyTorch Tensor ready for model input.
    Ensures length matches WINDOW_SIZE by padding or truncating.
    """
    # Truncate or zero-pad the signal to strictly match the trained WINDOW_SIZE
    if len(signal) >= WINDOW_SIZE:
        segment = signal[:WINDOW_SIZE]
    else:
        pad_width = WINDOW_SIZE - len(signal)
        segment = np.pad(signal, (0, pad_width), 'constant')
        
    # Shape suitable for BiLSTM: (Batch Size, Sequence Length, Features)
    # Output: (1, 4097, 1)
    tensor = torch.tensor(segment, dtype=torch.float32).view(1, WINDOW_SIZE, 1)
    
    # Move tensor to Target Device (CPU)
    return tensor.to(DEVICE)