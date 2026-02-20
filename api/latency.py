import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            regions = data.get("regions", [])
            threshold = data.get("threshold_ms", 180)

            root_dir = os.path.dirname(os.path.dirname(__file__))
            file_path = os.path.join(root_dir, "telemetry.json")

            with open(file_path, "r") as f:
                telemetry = json.load(f)

            result = {}

            for region in regions:
                region_data = [r for r in telemetry if r["region"] == region]
                if not region_data:
                    continue

                latencies = [r["latency_ms"] for r in region_data]
                uptimes = [r["uptime"] for r in region_data]

                avg_latency = sum(latencies) / len(latencies)
                p95_latency = sorted(latencies)[int(0.95 * len(latencies)) - 1]
                avg_uptime = sum(uptimes) / len(uptimes)
                breaches = len([l for l in latencies if l > threshold])

                result[region] = {
                    "avg_latency": avg_latency,
                    "p95_latency": p95_latency,
                    "avg_uptime": avg_uptime,
                    "breaches": breaches
                }

            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
