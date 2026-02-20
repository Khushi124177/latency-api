import json
import os
from http.server import BaseHTTPRequestHandler
import statistics

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            regions = data.get("regions", [])
            threshold = data.get("threshold_ms", 180)

            # Correct file path for Vercel
            base_path = os.path.dirname(__file__)
            file_path = os.path.join(base_path, "../telemetry.json")

            with open(file_path) as f:
                telemetry = json.load(f)

            result = {}

            for region in regions:
                region_data = [r for r in telemetry if r["region"] == region]

                if not region_data:
                    continue

                latencies = [r["latency_ms"] for r in region_data]
                uptimes = [r["uptime"] for r in region_data]

                avg_latency = statistics.mean(latencies)
                p95_latency = sorted(latencies)[int(len(latencies) * 0.95) - 1]
                avg_uptime = statistics.mean(uptimes)
                breaches = len([l for l in latencies if l > threshold])

                result[region] = {
                    "avg_latency": avg_latency,
                    "p95_latency": p95_latency,
                    "avg_uptime": avg_uptime,
                    "breaches": breaches
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
