import time
import os
import psutil
from fastapi.testclient import TestClient

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import app

client = TestClient(app)
url = "/api/v1/inference/epieeg"
edf_path = "F001.edf"

print("Starting Validation...")
if not os.path.exists(edf_path):
    print("F001.edf not found!")
    exit(1)

total_times = []
xai_times = []
memory_usages = []

process = psutil.Process(os.getpid())

with open(edf_path, "rb") as f:
    file_bytes = f.read()

for i in range(50):
    start = time.time()
    res = client.post(url, files={"file": ("F001.edf", file_bytes, "application/octet-stream")})
    end = time.time()
    
    if res.status_code != 200:
        print(f"Failed at {i}. Status: {res.status_code}, Body: {res.text}")
        break
        
    total_time = end - start
    total_times.append(total_time)
    
    data = res.json()
    if data.get("explainability"):
        xai_times.append(data["explainability"]["time_ms"])
        
    memory_usages.append(process.memory_info().rss / 1024 / 1024)
    
    if (i+1) % 10 == 0:
        print(f"Completed {i+1}/50 requests.")

print(f"Average Total Time: {sum(total_times)/len(total_times):.3f}s")
print(f"Average XAI Time: {sum(xai_times)/len(xai_times):.2f}ms")
print(f"Peak Memory: {max(memory_usages):.2f}MB")
print(f"Start Memory: {memory_usages[0]:.2f}MB, End Memory: {memory_usages[-1]:.2f}MB")
print(f"Prediction: {data.get('prediction')}, Confidence: {data.get('confidence_score')}")
