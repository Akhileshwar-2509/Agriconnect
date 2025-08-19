import json
import requests

BASE = "http://localhost:8000"

payload = {
  "soil_N": 10, "soil_P": 8, "soil_K": 12, "pH": 6.5, "OM": 2.0, "EC": 0.2,
  "texture": "loam", "region": "Midwest", "season": "Spring", "main_crop": "corn",
  "weather_30d": {"rain": 40, "gdd": 300}, "weather_60d": {"rain": 80, "gdd": 600},
  "N_rate": 90, "P_rate": 40, "K_rate": 60
}

weeds = ["pigweed", "foxtail"]

print("/predict/yield:")
print(requests.post(f"{BASE}/predict/yield", json=payload).json())

print("/classify/weed:")
print(requests.post(f"{BASE}/classify/weed", json={"weeds": weeds, "region": "Midwest", "season": "Spring", "main_crop": "corn"}).json())

print("/recommend/cover:")
print(json.dumps(requests.post(f"{BASE}/recommend/cover", json={"main_crop": "corn", "observed_weeds": weeds, "region": "Midwest", "season": "Spring"}).json(), indent=2))

print("/optimize:")
opt_inp = {**payload, "observed_weeds": weeds, "candidate_covers": ["rye", "clover", "mustard"]}
print(json.dumps(requests.post(f"{BASE}/optimize", json=opt_inp).json(), indent=2))

print("/explain:")
print(json.dumps(requests.post(f"{BASE}/explain", json={"payload": {**payload, "observed_weeds": weeds}}).json(), indent=2))

print("/export/pdf:")
plans = requests.post(f"{BASE}/optimize", json=opt_inp).json()["pareto"]
pdf = requests.post(f"{BASE}/export/pdf", json={"scenario_name": "demo", "inputs": payload, "plans": plans})
print(pdf.status_code, pdf.headers.get('Content-Type'))
