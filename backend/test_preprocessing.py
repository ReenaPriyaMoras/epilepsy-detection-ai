from ml.epieeg.preprocessing import extract_channel_features
import numpy as np

x = np.random.randn(4096)

f = extract_channel_features(x)

print(f.shape)
print(f)