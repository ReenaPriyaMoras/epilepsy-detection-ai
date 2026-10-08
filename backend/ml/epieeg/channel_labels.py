# List of standard 10-20 system EEG channels
STANDARD_CHANNELS = [
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2",
    "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz", "A1",
    "A2", "T1", "T2", "Sp1", "Sp2", "C1", "C2", "C5", "C6", "F1",
    "F2", "F5", "F6", "P1", "P2", "P5", "P6", "O3", "O4", "O5",
    "O6", "PO3", "PO4"
]

def get_channel_label(index: int) -> str:
    if 0 <= index < len(STANDARD_CHANNELS):
        return STANDARD_CHANNELS[index]
    return f"Channel {index + 1}"
