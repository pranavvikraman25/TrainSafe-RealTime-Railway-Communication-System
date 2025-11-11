# backend/app.py
"""
Flask + Flask-SocketIO backend for TrainSafe demo.

Routes:
  GET  /status            -> returns current state JSON
  POST /update            -> accept a single train update (JSON) and broadcast
  GET  / (optional)       -> small health page

Socket.IO:
  emits 'train_update' to all connected clients whenever state changes.
"""

import os
import time
import json
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from geopy.distance import geodesic

# ---------- Configuration ----------
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "trains_initial.json")
BROADCAST_ON_UPDATE = True  # broadcast immediately when update received
DEFAULT_PORT = 5000

# ---------- App setup ----------
app = Flask(__name__, static_folder=None)  # we are not serving frontend from here by default
CORS(app, resources={r"/*": {"origins": "*"}})

# Use eventlet for production-like behavior with SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ---------- Shared state ----------
state_lock = threading.Lock()
# state structure: {"timestamp": <float>, "trains": [ {train dict}, ... ] }
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        initial_state = json.load(f)
else:
    # fallback minimal state
    initial_state = {
        "timestamp": time.time(),
        "trains": [
            {"id": "T001", "name": "Train_A", "route": "Chennai-Bangalore",
             "lat": 13.0827, "lon": 80.2707, "speed_kmh": 80, "signal": 1, "track_id": 2},
            {"id": "T002", "name": "Train_B", "route": "Kovai-Madurai",
             "lat": 12.9827, "lon": 80.0707, "speed_kmh": 70, "signal": 1, "track_id": 2}
        ]
    }

state = initial_state

# ---------- Helper utilities ----------
def find_train(idx_or_id):
    """Return (index, train_dict) for given id or index (int)."""
    with state_lock:
        if isinstance(idx_or_id, int):
            if 0 <= idx_or_id < len(state["trains"]):
                return idx_or_id, state["trains"][idx_or_id]
            return None, None
        # id string
        for i, t in enumerate(state["trains"]):
            if t.get("id") == idx_or_id:
                return i, t
        return None, None

def update_state_timestamp():
    state["timestamp"] = time.time()

def compute_distance_km(a_lat, a_lon, b_lat, b_lon):
    try:
        return geodesic((a_lat, a_lon), (b_lat, b_lon)).km
    except Exception:
        return None

def broadcast_state():
    """Emit the full state to all connected socketio clients."""
    try:
        socketio.emit("train_update", state)
    except Exception as e:
        app.logger.exception("SocketIO broadcast failed: %s", e)

# ---------- Flask endpoints ----------
@app.route("/")
def index():
    return jsonify({
        "service": "TrainSafe Backend",
        "status": "ok",
        "timestamp": time.time()
    })

@app.route("/status", methods=["GET"])
def get_status():
    """Return current state JSON."""
    with state_lock:
        return jsonify(state)

@app.route("/update", methods=["POST"])
def post_update():
    """
    Accept a JSON payload with either:
       - full train object: {"id": "...", "lat": ..., "lon": ..., "speed_kmh": ..., "signal": ..., "track_id": ...}
       - or list: {"trains": [ {...}, {...} ] }

    On success: returns {'ok': True, 'state': state}
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"ok": False, "error": "Invalid or missing JSON"}), 400

    updates = []
    # normalize updates to list of train dicts
    if isinstance(payload, dict) and "trains" in payload and isinstance(payload["trains"], list):
        updates = payload["trains"]
    elif isinstance(payload, dict):
        updates = [payload]
    elif isinstance(payload, list):
        updates = payload
    else:
        return jsonify({"ok": False, "error": "Unsupported payload format"}), 400

    changed = False
    with state_lock:
        for up in updates:
            # require id
            tid = up.get("id")
            if not tid:
                continue
            idx, t = find_train(tid)
            if t is None:
                # new train: add to state (accept basic shape)
                new_train = {
                    "id": tid,
                    "name": up.get("name", tid),
                    "route": up.get("route", ""),
                    "lat": float(up.get("lat", 0)) if up.get("lat") is not None else 0.0,
                    "lon": float(up.get("lon", 0)) if up.get("lon") is not None else 0.0,
                    "speed_kmh": float(up.get("speed_kmh", 0)),
                    "signal": int(up.get("signal", 1)),
                    "track_id": int(up.get("track_id", 1))
                }
                state["trains"].append(new_train)
                changed = True
                continue
            # update fields of existing train
            # only update the provided keys; keep previous keys intact
            mutable = False
            for k in ("lat", "lon", "speed_kmh", "signal", "track_id", "name", "route"):
                if k in up:
                    # safe type casting
                    try:
                        if k in ("lat", "lon", "speed_kmh"):
                            t[k] = float(up[k])
                        elif k in ("signal", "track_id"):
                            t[k] = int(up[k])
                        else:
                            t[k] = up[k]
                        mutable = True
                    except Exception:
                        app.logger.debug("Skipping field %s value %s (bad type)", k, up.get(k))
            if mutable:
                changed = True
        if changed:
            update_state_timestamp()

    if changed and BROADCAST_ON_UPDATE:
        broadcast_state()

    return jsonify({"ok": True, "changed": changed, "timestamp": state["timestamp"], "trains_count": len(state["trains"])})

# ---------- SocketIO events ----------
@socketio.on("connect")
def on_connect():
    app.logger.info("Client connected")
    # send initial state immediately
    with state_lock:
        emit("train_update", state)

@socketio.on("disconnect")
def on_disconnect():
    app.logger.info("Client disconnected")

# ---------- Optional helper: simple server-side loop for demo (not started by default) ----------
def _server_demo_loop(interval_seconds=2.0):
    """
    Optionally you can start this in a background thread for automated demo updates.
    It will move each train a small step toward a pre-defined target in its dict if present.
    Not used by default. This is an example to run manually if you want.
    """
    app.logger.info("Demo loop started")
    while True:
        time.sleep(interval_seconds)
        with state_lock:
            changed = False
            for t in state["trains"]:
                # if target exists, step toward it
                target = t.get("target")
                if not target:
                    continue
                try:
                    lat, lon = float(t["lat"]), float(t["lon"])
                    tlat, tlon = float(target["lat"]), float(target["lon"])
                    dist_km = compute_distance_km(lat, lon, tlat, tlon)
                    if dist_km is None:
                        continue
                    # small step proportional to speed
                    step_km = max(0.01, float(t.get("speed_kmh", 10)) * (interval_seconds/3600.0))
                    if step_km >= dist_km:
                        t["lat"], t["lon"] = tlat, tlon
                    else:
                        # linear interpolation (short steps only)
                        frac = step_km / dist_km
                        t["lat"] = lat + (tlat - lat) * frac
                        t["lon"] = lon + (tlon - lon) * frac
                    changed = True
                except Exception:
                    continue
            if changed:
                update_state_timestamp()
        broadcast_state()

# ---------- Run server ----------
if __name__ == "__main__":
    # If you want the demo loop to run inside backend uncomment the lines below:
    # demo_thread = threading.Thread(target=_server_demo_loop, kwargs={"interval_seconds": 1.0}, daemon=True)
    # demo_thread.start()

    port = int(os.environ.get("PORT", DEFAULT_PORT))
    # Use eventlet (installed via requirements) for production-like socket behavior
    socketio.run(app, host="0.0.0.0", port=port)
