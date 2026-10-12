import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.epieeg.model import EpiEEGModelLoader
from ml.epieeg.explainability import compute_attribution, generate_explanation

def test_explainability_pipeline():
    loader = EpiEEGModelLoader.load()
    assert loader.model is not None
    assert loader.adj_matrix is not None

    # Dummy normalized feature matrix: shape (43 channels, 17 features)
    np.random.seed(42)
    dummy_features = np.random.randn(43, 17).astype(np.float32)

    # 1. Compute attribution
    attribution = compute_attribution(loader, dummy_features)
    assert attribution.shape == (43, 17)
    assert not np.isnan(attribution).any()
    assert np.all(attribution >= 0.0)

    # 2. Generate full clinical explanation
    explanation = generate_explanation(loader, dummy_features, "Epileptic")
    assert explanation is not None
    assert "top_channels" in explanation
    assert len(explanation["top_channels"]) == 5
    assert "top_features" in explanation
    assert len(explanation["top_features"]) == 5
    assert "summary" in explanation
    assert len(explanation["summary"]) > 20
    assert "time_ms" in explanation
