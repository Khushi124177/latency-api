from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import numpy as np

app = FastAPI()

# ✅ CORS enable karna (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Sabko allow karega
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# telemetry.json load karna
file_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open("telemetry.json") as f:
    data = json.load(f)

@app.post("/api/latency")
async def latency_metrics(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": len([l for l in latencies if l > threshold])
        }

    return result
