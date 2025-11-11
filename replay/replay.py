# replay/replay.py
"""
Replay simulator that posts train positions to the backend /update endpoint.
Usage:
    python replay.py --host http://localhost:5000 --file sample_trace.json --loop 0 --interval 1.0

Options:
  --host      backend base URL (default http://localhost:5000)
  --file      sample trace JSON path (default sample_trace.json)
  --interval  seconds between frames (default 1.0)
  --loop      number of times to loop the trace (0 = infinite)
"""

import argparse
import json
import time
import requests
import sys

def load_trace(path):
    with open(path, "r") as f:
        return json.load(f).get("trace", [])

def post_update(host, trains_payload):
    url = host.rstrip("/") + "/update"
    try:
        r = requests.post(url, json={"trains": trains_payload}, timeout=5)
        if r.status_code != 200:
            print("POST error", r.status_code, r.text)
        else:
            print("Posted update:", [t["id"] for t in trains_payload])
    except Exception as e:
        print("Request failed:", e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="http://localhost:5000")
    p.add_argument("--file", default="sample_trace.json")
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--loop", type=int, default=1)
    args = p.parse_args()

    trace = load_trace(args.file)
    if not trace:
        print("No trace frames found in", args.file)
        sys.exit(1)

    loops = args.loop
    loop_count = 0
    try:
        while True:
            for frame in trace:
                trains = frame.get("trains", [])
                post_update(args.host, trains)
                time.sleep(args.interval)
            loop_count += 1
            if loops > 0 and loop_count >= loops:
                break
    except KeyboardInterrupt:
        print("Replay stopped by user")

if __name__ == "__main__":
    main()
