# 🚆 TrainSafe — Real-Time Railway Communication & Collision Prevention System

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-SocketIO-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-Map-green?logo=leaflet)](https://leafletjs.com/)
[![Stream Data](https://img.shields.io/badge/Data%20Feed-Live-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🧭 Overview

**TrainSafe** is a real-time **Train-to-Train Communication and Collision Avoidance Dashboard** that visualizes live GPS data of multiple trains on shared or merging railway tracks.

It helps train operators and signal centers identify possible collisions earlier than conventional signalling delays — giving them real-time visibility and alerts.

Built using **Flask + Socket.IO** (backend) and **Leaflet + JavaScript** (frontend), the system fits directly into **Indian Railways modernization initiatives (2025 and beyond)**. It also supports **Arduino GPS integration** for hardware prototypes.

---



JSON Train Data Stream



---

## ⚙️ Features

✅ Real-time **GPS streaming** from multiple trains  
✅ **WebSocket** live updates (no refresh)  
✅ **Leaflet map dashboard** with animated train movement  
✅ **Collision detection** when trains share a track  
✅ **ETA / distance / signal status** display  
✅ **Offline simulator** for demo without hardware  
✅ Ready for **Arduino + GPS** expansion  

---

## 🧩 Tech Stack

| Layer | Technology | Purpose |
|:------|:------------|:---------|
| **Frontend** | Leaflet + Socket.IO + HTML + JS | Live map dashboard |
| **Backend** | Flask + Flask-SocketIO | Real-time API and broadcasting |
| **Feed Source** | JSON / Arduino GPS | Train coordinate input |
| **Simulator** | Python Replay Script | Offline GPS replay for testing |

---



