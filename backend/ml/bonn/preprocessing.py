import numpy as np
import mne
import os
import tempfile
import torch
from fastapi import HTTPException
from .config import SAMPLING_RATE, WINDOW_SIZE, NORM_MEAN, NORM_STD, DEVICE

import scipy.signal

def load_edf(file_bytes: bytes) -> np.ndarray:
    """
    Load an EDF file securely from bytes using MNE, extracting raw EEG signal from channel 0.
    Optimized for high-performance memory-efficient streaming.
    Automatically handles resampling if the EDF's frequency doesn't match Bonn standard (173.61 Hz).
    """
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".edf")
        with os.fdopen(fd, 'wb') as f:
            f.write(file_bytes)
        
        # Read header only first (preload=False) to avoid multi-hundred megabyte memory spikes
        raw = mne.io.read_raw_edf(tmp_path, preload=False, verbose=False)
        
        orig_sfreq = float(raw.info['sfreq'])
        target_sfreq = float(SAMPLING_RATE)
        
        # We only need WINDOW_SIZE samples at target sampling rate (~23.6 seconds)
        # Load a small buffer (e.g. 35 seconds or total recording duration if shorter)
        needed_seconds = (WINDOW_SIZE / target_sfreq) + 5.0
        total_seconds = raw.n_times / orig_sfreq if orig_sfreq > 0 else 0
        load_seconds = min(total_seconds, max(needed_seconds, 30.0))
        
        # Read data for channel 0 only
        channel_data = raw.get_data(picks=[0], tmin=0, tmax=load_seconds)[0]
        
        try:
            raw.close()
        except Exception:
            pass
            
        # Resample only channel 0 if frequency differs
        if abs(orig_sfreq - target_sfreq) > 0.01 and len(channel_data) > 0:
            target_num_samples = int(round(len(channel_data) * target_sfreq / orig_sfreq))
            if target_num_samples > 1:
                channel_data = scipy.signal.resample(channel_data, target_num_samples)
            
        return channel_data.astype(np.float32)
        
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid or corrupted EDF file: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

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