import streamlit as st
import json
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="TrainSafe — Indian Railways", layout="wide")

st.title("🚄 TrainSafe — Real-Time Railway Collision Prevention System")
st.markdown("### Chennai – Bangalore Line | Real Railway Route Demo")

# Load real route GeoJSON
with open("frontend/chennai_bengaluru.geojson", "r") as f:
    route_data = json.load(f)

# Create Folium map
m = folium.Map(location=[12.9, 78.8], zoom_start=7, tiles="cartodb positron")
folium.GeoJson(route_data, name="Chennai–Bangalore Route", tooltip="Railway Route").add_to(m)

# Example two trains (static now — later connected via socket)
train_a = [13.05, 80.27]  # Chennai side
train_b = [12.97, 77.59]  # Bangalore side
folium.Marker(train_a, tooltip="Train A — Chennai Express", icon=folium.Icon(color="green", icon="train", prefix="fa")).add_to(m)
folium.Marker(train_b, tooltip="Train B — Bengaluru Mail", icon=folium.Icon(color="red", icon="train", prefix="fa")).add_to(m)

st_folium(m, width=1200, height=600)

st.markdown("""
---
### 🔧 Project Info
**Live GPS Visualization** using OpenStreetMap and Folium.  
Backend: Flask-SocketIO (for future expansion)  
Frontend: Leaflet/Streamlit hybrid  
Data: Real OSM railway tracks
""")
