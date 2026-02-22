from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Absolute path fix
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "telemetry.json")

with open(file_path) as f:
    data = json.load(f)

@app.post("/api/latency")
async def latency(payload: dict):
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
            "avg_latency": sum(latencies)/len(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": sum(uptimes)/len(uptimes),
            "breaches": len([l for l in latencies if l > threshold])
        }

    return result

# IMPORTANT FOR VERCEL
handler = app
