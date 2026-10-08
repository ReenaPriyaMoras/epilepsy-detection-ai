import os
import tempfile
import numpy as np
import mne
from scipy.stats import skew, kurtosis
from .model import EpiEEGModelLoader

def extract_all_features(eeg: np.ndarray) -> np.ndarray:
    """
    Vectorized extraction of 17 statistical features across all 43 channels simultaneously.
    eeg shape: (43, num_samples)
    Returns shape: (43, 17)
    """
    # Guard against invalid dimensions or empty samples
    if eeg.shape[1] < 2:
        # Minimum padding for 2 samples
        pad = np.zeros((eeg.shape[0], 2 - eeg.shape[1]), dtype=eeg.dtype)
        eeg = np.hstack([eeg, pad])

    eeg = np.nan_to_num(eeg, nan=0.0, posinf=0.0, neginf=0.0)
    eeg_diff = np.diff(eeg, axis=1)
    
    eeg_mean = np.mean(eeg, axis=1)
    eeg_std = np.std(eeg, axis=1)
    eeg_var = np.var(eeg, axis=1)
    eeg_min = np.min(eeg, axis=1)
    eeg_max = np.max(eeg, axis=1)
    eeg_median = np.median(eeg, axis=1)
    eeg_rms = np.sqrt(np.mean(eeg**2, axis=1))
    
    # Skew & Kurtosis with zero-division protection
    try:
        eeg_skew = skew(eeg, axis=1, nan_policy='omit')
    except Exception:
        eeg_skew = np.zeros(eeg.shape[0])
        
    try:
        eeg_kurtosis = kurtosis(eeg, axis=1, nan_policy='omit')
    except Exception:
        eeg_kurtosis = np.zeros(eeg.shape[0])

    eeg_p25 = np.percentile(eeg, 25, axis=1)
    eeg_p75 = np.percentile(eeg, 75, axis=1)
    eeg_mean_abs = np.mean(np.abs(eeg), axis=1)
    eeg_wl = np.sum(np.abs(eeg_diff), axis=1)
    eeg_zc = np.sum(np.diff(np.sign(eeg), axis=1) != 0, axis=1)
    eeg_max_abs = np.max(np.abs(eeg), axis=1)
    eeg_sum_sq = np.sum(eeg**2, axis=1)
    eeg_mean_diff_sq = np.mean(eeg_diff**2, axis=1)

    feature_matrix = np.column_stack([
        eeg_mean, eeg_std, eeg_var, eeg_min, eeg_max, eeg_median, eeg_rms,
        eeg_skew, eeg_kurtosis, eeg_p25, eeg_p75, eeg_mean_abs, eeg_wl,
        eeg_zc, eeg_max_abs, eeg_sum_sq, eeg_mean_diff_sq
    ])
    
    feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=0.0, neginf=0.0)
    return feature_matrix.astype(np.float32)

def preprocess_edf(file_bytes: bytes) -> np.ndarray:
    """
    Complete preprocessing pipeline for EpiEEG EDF files.
    Reads bytes, pads/truncates channels to 43, extracts 17 features per channel,
    and applies standard scaling using the singleton loader parameters.
    """
    if not file_bytes:
        raise ValueError("EDF file buffer is empty.")

    # 1. Parse EDF securely with safe temp file deletion on Windows
    tmp = tempfile.NamedTemporaryFile(suffix=".edf", delete=False)
    try:
        tmp.write(file_bytes)
        tmp.flush()
        tmp.close()
        
        raw = mne.io.read_raw_edf(tmp.name, preload=True, verbose=False)
        eeg = raw.get_data()
        try:
            raw.close()
        except Exception:
            pass
    finally:
        if os.path.exists(tmp.name):
            try:
                os.remove(tmp.name)
            except Exception:
                pass

    if eeg is None or eeg.size == 0:
        raise ValueError("EDF recording contains no signal data.")

    if eeg.ndim == 1:
        eeg = eeg[np.newaxis, :]

    # 2. Adjust spatial dimension (channels) to precisely 43
    NUM_NODES = 43
    num_channels = eeg.shape[0]

    if num_channels < NUM_NODES:
        padding = np.zeros((NUM_NODES - num_channels, eeg.shape[1]), dtype=eeg.dtype)
        eeg = np.vstack([eeg, padding])
    elif num_channels > NUM_NODES:
        eeg = eeg[:NUM_NODES]

    # 3. Extract 17 features across all channels at once
    feature_matrix = extract_all_features(eeg)

    # 4. Scaling
    loader = EpiEEGModelLoader.load()
    scale = np.asarray(loader.scaler_scale, dtype=np.float32).copy()
    mean = np.asarray(loader.scaler_mean, dtype=np.float32)

    # Prevent division by zero or tiny values safely
    scale[np.abs(scale) < 1e-8] = 1.0

    feature_matrix = (feature_matrix - mean) / scale

    # 5. Defensive Post-scaling cleanup
    feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=0.0, neginf=0.0)
    feature_matrix = np.clip(feature_matrix, -10.0, 10.0)

    # Final guarantee of type and shape
    feature_matrix = feature_matrix.astype(np.float32)

    return feature_matrix