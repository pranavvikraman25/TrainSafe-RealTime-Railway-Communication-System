# streamlit_app.py
import streamlit as st
import json
import os
from pathlib import Path
import math
import time

st.set_page_config(page_title="TrainSafe — Moving Pin Demo", layout="wide")
st.title("🚆 TrainSafe — Moving Pin Demo (Chennai Central → Perambur)")

# --- Paths ---
BASE = Path(__file__).parent
GEOJSON_PATH = BASE / "frontend" / "chennai_perambur_demo.geojson"
TRACE_PATH = BASE / "replay" / "sample_trace.json"

# --- Load route geojson (if missing show error) ---
if not GEOJSON_PATH.exists():
    st.error(f"Missing route file: {GEOJSON_PATH}. Upload `chennai_perambur_demo.geojson` to frontend/")
    st.stop()

route_data = json.loads(GEOJSON_PATH.read_text())

# --- Load or prepare trace frames ---
if TRACE_PATH.exists():
    try:
        trace_raw = json.loads(TRACE_PATH.read_text())
        frames = trace_raw.get("frames", [])
        if not frames:
            frames = []
    except Exception:
        frames = []
else:
    frames = []

# If no frames, create an auto-sampled trace from the route coordinates (simple)
if not frames:
    # extract coordinates from route_data LineString
    coords = []
    for feat in route_data.get("features", []):
        geom = feat.get("geometry", {})
        if geom.get("type") == "LineString":
            coords.extend(geom.get("coordinates", []))
        elif geom.get("type") == "MultiLineString":
            for line in geom.get("coordinates", []):
                coords.extend(line)
    # coords are [lon, lat] — sample a subset for trace with approx spacing
    sample_coords = coords[0:: max(1, len(coords)//20)]
    # build frames: every 1 second
    frames = []
    t = 0
    for lon, lat in sample_coords:
        frames.append({"t": t, "lat": lat, "lon": lon})
        t += 1

# --- UI controls ---
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("### Playback Controls")
    speed = st.slider("Playback speed (x)", min_value=1.0, max_value=5.0, value=1.5, step=0.1,
                      help="Multiplier for how fast the pin moves through frames")
    loop = st.checkbox("Loop trace", value=True)
    autostart = st.checkbox("Autostart", value=True)
    st.markdown("---")
    st.markdown("### Info")
    if frames:
        st.write(f"Frames: {len(frames)}")
        st.write(f"Duration: {frames[-1]['t']} s (raw)")
    else:
        st.write("No frames available")
    st.write("Route points:", sum(len(f.get("geometry",{}).get("coordinates",[])) if f.get("geometry") else 0 for f in route_data.get("features",[])))

with col2:
    st.markdown("### Map (moving pin will appear)")

# Prepare JSON strings to inject into HTML
route_json = json.dumps(route_data)
trace_json = json.dumps(frames)

# ---- HTML/JS: Leaflet map with animated marker ----
html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>TrainSafe Moving Pin</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  html,body,#map {{ height:100%; margin:0; padding:0; }}
  #map{{ border-radius:8px; box-shadow:0 6px 16px rgba(10,10,10,0.08); }}
  .infoBox {{ position:absolute; top:8px; left:8px; z-index:9999; background:white; padding:8px 10px; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.12); font-family:Arial; font-size:13px; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="infoBox" id="infoBox">Loading...</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const routeData = {route_json};
const frames = {trace_json};
const speedMultiplier = {speed};  // injected
const loopTrace = {"true" if loop else "false"};

const map = L.map('map', {{ preferCanvas:true }}).setView([13.09,80.26], 13);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);

// draw route
let routeCoords = [];
routeData.features.forEach(f => {{
  const geom = f.geometry;
  if (geom.type === 'LineString') {{
    const pts = geom.coordinates.map(c => [c[1], c[0]]);
    routeCoords = routeCoords.concat(pts);
    L.polyline(pts, {{color:'#1976d2', weight:4, opacity:0.85}}).addTo(map);
  }} else if (geom.type === 'MultiLineString') {{
    geom.coordinates.forEach(line => {{
      const pts = line.map(c => [c[1], c[0]]);
      routeCoords = routeCoords.concat(pts);
      L.polyline(pts, {{color:'#1976d2', weight:4, opacity:0.85}}).addTo(map);
    }});
  }}
}});

// initial view bounds to route
if (routeCoords.length) {{
  const bounds = L.latLngBounds(routeCoords);
  map.fitBounds(bounds.pad(0.2));
}}

// create marker (blue circle) and shadow polyline for path covered
const pin = L.circleMarker(frames.length ? [frames[0].lat, frames[0].lon] : [routeCoords[0][0], routeCoords[0][1]], {{
  radius:8, color:'#0b5', fillColor:'#0b5', fillOpacity:1
}}).addTo(map);

let covered = L.polyline([], {{color:'#0b5', weight:3, opacity:0.6}}).addTo(map);

// animation loop
let idx = 0;
let playing = { "true" if autostart else "false" };

function formatTimeSeconds(s) {{
  const mm = Math.floor(s/60).toString().padStart(2,'0');
  const ss = Math.floor(s%60).toString().padStart(2,'0');
  return mm + ":" + ss;
}}

function updateInfo(idx) {{
  const f = frames[idx];
  const info = `Frame: ${idx+1}/${frames.length}  —  time: ${frames[idx].t}s  —  lat: ${frames[idx].lat.toFixed(5)}, lon: ${frames[idx].lon.toFixed(5)}`;
  document.getElementById('infoBox').innerText = info;
}}

function moveTo(from, to, duration_ms, cb) {{
  const steps = Math.max(6, Math.round(duration_ms/40));
  let step = 0;
  const latStep = (to[0] - from[0]) / steps;
  const lonStep = (to[1] - from[1]) / steps;
  const handle = setInterval(() => {{
    step++;
    const lat = from[0] + latStep * step;
    const lon = from[1] + lonStep * step;
    pin.setLatLng([lat, lon]);
    covered.addLatLng([lat, lon]);
    if (step >= steps) {{
      clearInterval(handle);
      if (cb) cb();
    }}
  }}, Math.max(25, duration_ms/steps));
}}

function playOnce(callbackAtEnd) {{
  if (!frames.length) return;
  idx = 0;
  function next() {{
    const cur = frames[idx];
    const nxt = frames[(idx+1) % frames.length];
    updateInfo(idx);
    const from = [cur.lat, cur.lon];
    const to = [nxt.lat, nxt.lon];
    // duration is proportional to time difference (or fallback to 1000ms)
    const dt = (nxt.t - cur.t) || 1;
    const duration_ms = Math.max(250, dt*1000 / speedMultiplier);
    moveTo(from, to, duration_ms, () => {{
      idx++;
      if (idx >= frames.length-1) {{
        updateInfo(idx);
        if (loopTrace === true) {{
          // small pause then loop
          setTimeout(() => {{
            covered.setLatLng([]); // reset covered path optionally
            idx = 0;
            pin.setLatLng([frames[0].lat, frames[0].lon]);
            playOnce(callbackAtEnd);
          }}, 250);
        }} else {{
          if (callbackAtEnd) callbackAtEnd();
        }}
      }} else {{
        next();
      }}
    }});
  }}
  next();
}}

if (playing) {{
  playOnce();
}} else {{
  updateInfo(idx);
}}

// add simple keyboard control: space to toggle
document.addEventListener('keydown', (e) => {{
  if (e.code === 'Space') {{
    e.preventDefault();
    if (playing) {{
      playing = false;
    }} else {{
      playing = true;
      playOnce();
    }}
  }}
}});
</script>
</body>
</html>
"""

# embed widget with full height
st.components.v1.html(html, height=700, scrolling=False)
