import os
import time
import tempfile
import psutil
import logging
import numpy as np
import mne
from scipy.stats import skew, kurtosis
from .model import EpiEEGModelLoader

logger = logging.getLogger("inference_logger")

def _get_process_rss_mb() -> float:
    """Returns current process RSS memory in MB."""
    try:
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0

def extract_all_features(eeg: np.ndarray) -> np.ndarray:
    """
    Vectorized extraction of 17 statistical features across all 43 channels simultaneously.
    eeg shape: (43, num_samples)
    Returns shape: (43, 17)
    """
    # Guard against invalid dimensions or empty samples
    if eeg.shape[1] < 2:
        pad = np.zeros((eeg.shape[0], 2 - eeg.shape[1]), dtype=eeg.dtype)
        eeg = np.hstack([eeg, pad])

    eeg = np.nan_to_num(eeg, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    if eeg.dtype != np.float32:
        eeg = eeg.astype(np.float32)

    eeg_diff = np.diff(eeg, axis=1)
    
    eeg_mean = np.mean(eeg, axis=1)
    eeg_std = np.std(eeg, axis=1)
    eeg_var = np.var(eeg, axis=1)
    eeg_min = np.min(eeg, axis=1)
    eeg_max = np.max(eeg, axis=1)
    eeg_median = np.median(eeg, axis=1)
    
    # Avoid duplicate allocations by computing square once
    eeg_sq = np.square(eeg)
    eeg_sum_sq = np.sum(eeg_sq, axis=1)
    eeg_rms = np.sqrt(eeg_sum_sq / eeg.shape[1])
    
    # Skew & Kurtosis with zero-division protection
    try:
        eeg_skew = skew(eeg, axis=1)
    except Exception:
        eeg_skew = np.zeros(eeg.shape[0], dtype=np.float32)
        
    try:
        eeg_kurtosis = kurtosis(eeg, axis=1)
    except Exception:
        eeg_kurtosis = np.zeros(eeg.shape[0], dtype=np.float32)

    eeg_p25 = np.percentile(eeg, 25, axis=1)
    eeg_p75 = np.percentile(eeg, 75, axis=1)
    
    abs_eeg = np.abs(eeg)
    eeg_mean_abs = np.mean(abs_eeg, axis=1)
    eeg_max_abs = np.max(abs_eeg, axis=1)
    
    abs_diff = np.abs(eeg_diff)
    eeg_wl = np.sum(abs_diff, axis=1)
    eeg_zc = np.sum(np.diff(np.sign(eeg), axis=1) != 0, axis=1)
    eeg_mean_diff_sq = np.mean(np.square(eeg_diff), axis=1)

    feature_matrix = np.column_stack([
        eeg_mean, eeg_std, eeg_var, eeg_min, eeg_max, eeg_median, eeg_rms,
        eeg_skew, eeg_kurtosis, eeg_p25, eeg_p75, eeg_mean_abs, eeg_wl,
        eeg_zc, eeg_max_abs, eeg_sum_sq, eeg_mean_diff_sq
    ])
    
    feature_matrix = np.nan_to_num(feature_matrix, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return feature_matrix.astype(np.float32)

from core.telemetry import log_stage_telemetry

def preprocess_edf(file_bytes: bytes, max_window_seconds: float = 30.0, req_id: str = "N/A") -> np.ndarray:
    """
    Optimized clinical preprocessing pipeline for EpiEEG EDF files with stage telemetry.
    - Inspects EDF header via preload=False
    - Determines sampling frequency and bounds analysis to clinical window (30s)
    - Loads ONLY the required channels (up to 43) and samples
    - Vectorized extraction of 17 statistical features in float32
    - Applies standard scaling using singleton loader parameters
    - Avoids multi-gigabyte memory spikes
    """
    if not file_bytes:
        raise ValueError("EDF file buffer is empty.")

    NUM_NODES = 43
    tmp_path = None
    eeg = None

    t_pipe_start = time.perf_counter()

    # 1. Parse EDF securely with safe temp file cleanup
    try:
        t0 = time.perf_counter()
        fd, tmp_path = tempfile.mkstemp(suffix=".edf")
        with os.fdopen(fd, 'wb') as f:
            f.write(file_bytes)
        t_tmp = (time.perf_counter() - t0) * 1000
        log_stage_telemetry(
            "Temporary file created",
            req_id=req_id,
            duration_ms=t_tmp,
            extra=f"Path: {tmp_path} | Size: {len(file_bytes)}B"
        )
        
        # Read header only without loading signal into RAM
        try:
            t0 = time.perf_counter()
            raw = mne.io.read_raw_edf(tmp_path, preload=False, verbose=False)
            t_open = (time.perf_counter() - t0) * 1000
            log_stage_telemetry(
                "EDF opened",
                req_id=req_id,
                duration_ms=t_open,
                extra=f"Preload=False"
            )

            t0 = time.perf_counter()
            total_channels = len(raw.ch_names)
            sfreq = float(raw.info.get('sfreq', 256.0))
            n_times = raw.n_times
            total_duration_sec = n_times / sfreq if sfreq > 0 else 0.0
            
            # Determine analysis sample window
            if max_window_seconds and max_window_seconds > 0:
                max_samples = int(sfreq * max_window_seconds)
                stop_sample = min(n_times, max_samples) if max_samples > 0 else n_times
            else:
                stop_sample = n_times
            
            window_duration_sec = stop_sample / sfreq if sfreq > 0 else 0.0
            t_header = (time.perf_counter() - t0) * 1000
            log_stage_telemetry(
                "Header parsed",
                req_id=req_id,
                duration_ms=t_header,
                extra=(
                    f"Sfreq={sfreq}Hz | TotalChannels={total_channels} | "
                    f"TotalSamples={n_times} ({total_duration_sec:.1f}s) | "
                    f"WindowSamples=0..{stop_sample} ({window_duration_sec:.1f}s)"
                )
            )

            # Load ONLY required window & channels
            t0 = time.perf_counter()
            picks = list(range(min(total_channels, NUM_NODES)))
            eeg = raw.get_data(picks=picks, start=0, stop=stop_sample)
            t_load = (time.perf_counter() - t0) * 1000
            log_stage_telemetry(
                "Signal loaded",
                req_id=req_id,
                duration_ms=t_load,
                extra=f"Shape={eeg.shape} | Dtype={eeg.dtype} | Buffer={eeg.nbytes / (1024*1024):.2f}MB"
            )
            
            try:
                raw.close()
            except Exception:
                pass
            del raw
        except (Exception, AssertionError) as pe:
            log_stage_telemetry("EDF header parse error", req_id=req_id, error=pe)
            raise ValueError(f"Corrupted or invalid EDF recording structure: {str(pe)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    if eeg is None or eeg.size == 0:
        raise ValueError("EDF recording contains no signal data.")

    if eeg.ndim == 1:
        eeg = eeg[np.newaxis, :]

    # Ensure float32 contiguous array immediately
    if eeg.dtype != np.float32:
        eeg = np.ascontiguousarray(eeg, dtype=np.float32)

    # 2. Adjust spatial dimension (channels) to precisely 43
    num_channels = eeg.shape[0]
    if num_channels < NUM_NODES:
        padding = np.zeros((NUM_NODES - num_channels, eeg.shape[1]), dtype=np.float32)
        eeg = np.vstack([eeg, padding])
    elif num_channels > NUM_NODES:
        eeg = eeg[:NUM_NODES]

    # 3. Extract 17 features across all channels at once
    t0 = time.perf_counter()
    feature_matrix = extract_all_features(eeg)
    del eeg
    t_feat = (time.perf_counter() - t0) * 1000
    log_stage_telemetry(
        "Feature extraction",
        req_id=req_id,
        duration_ms=t_feat,
        extra=f"Shape={feature_matrix.shape} | Dtype={feature_matrix.dtype}"
    )

    # 4. Scaling & Dimension Validation
    t0 = time.perf_counter()
    loader = EpiEEGModelLoader.load()
    scale = np.asarray(loader.scaler_scale, dtype=np.float32).copy()
    mean = np.asarray(loader.scaler_mean, dtype=np.float32)

    if len(mean) != feature_matrix.shape[1] or len(scale) != feature_matrix.shape[1]:
        raise ValueError(
            f"Scaler dimension mismatch: features have {feature_matrix.shape[1]} dims, "
            f"but scaler expected mean={len(mean)}, scale={len(scale)}"
        )

    # Prevent division by zero or tiny values safely
    scale[np.abs(scale) < 1e-8] = 1.0

    feature_matrix = (feature_matrix - mean) / scale

    # 5. Defensive Post-scaling cleanup & validation
    feature_matrix = np.nan_to_num(feature_matrix, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    feature_matrix = np.clip(feature_matrix, -10.0, 10.0)
    feature_matrix = feature_matrix.astype(np.float32)

    t_scale = (time.perf_counter() - t0) * 1000
    min_val = float(np.min(feature_matrix))
    max_val = float(np.max(feature_matrix))
    log_stage_telemetry(
        "Scaling",
        req_id=req_id,
        duration_ms=t_scale,
        extra=f"Shape={feature_matrix.shape} | Min={min_val:.2f} | Max={max_val:.2f}"
    )

    return feature_matrix