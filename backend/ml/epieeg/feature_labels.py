FEATURE_LABELS = [
    "Mean",
    "Standard Deviation",
    "Variance",
    "Skewness",
    "Kurtosis",
    "Entropy",
    "Energy",
    "RMS",
    "Peak-to-Peak",
    "Band Power Delta",
    "Band Power Theta",
    "Band Power Alpha",
    "Band Power Beta",
    "Band Power Gamma",
    "Hjorth Activity",
    "Hjorth Mobility",
    "Hjorth Complexity"
]

def get_feature_label(index: int) -> str:
    if 0 <= index < len(FEATURE_LABELS):
        return FEATURE_LABELS[index]
    return f"Feature {index + 1}"
