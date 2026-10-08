from ml.epieeg.inference import predict_epieeg

with open("Patient_01.edf", "rb") as f:
    result = predict_epieeg(f.read())

print(result)