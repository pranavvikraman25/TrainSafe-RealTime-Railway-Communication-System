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




## 🚀 Quick Start (Full Demo)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/TrainSafe-RealTime-Railway-Communication-System.git
cd TrainSafe-RealTime-Railway-Communication-System
2️⃣ Setup and run backend
bash
Copy code
cd backend
pip install -r requirements.txt
python app.py
Backend starts at http://localhost:5000

3️⃣ Run frontend dashboard
bash
Copy code
cd ../frontend
python -m http.server 8000
Open http://localhost:8000 in your browser.

4️⃣ Start the GPS simulator
bash
Copy code
cd ../replay
python replay.py --host http://localhost:5000 --file sample_trace.json --interval 1.0
You’ll now see Train A and Train B move live on the map.
If both trains enter the same track within 10 km, an alert banner appears instantly.

🧠 Project Modules
Module	Description
Backend	Receives GPS coordinates, computes distance, detects collisions, and broadcasts via WebSocket.
Frontend	Leaflet dashboard showing train positions, speed, and alerts.
Replay Simulator	Sends prerecorded GPS traces to backend for demo.
Hardware (Planned)	Arduino + GPS sending live coordinates to /update endpoint.

📊 Example Output
View	Description
🌍 Map View	Trains moving along Chennai-Bangalore route.
⚠️ Alert Panel	“🚨 Train A and Train B within 9.8 km on Track 2 — Hold Train B.”
📈 Operator Metrics	Speed, distance, ETA, signal status updating live.

🧰 Repository Structure
pgsql
Copy code
TrainSafe-RealTime-Railway-Communication-System/
│
├── backend/
│   ├── app.py
│   ├── data/
│   │   └── trains_initial.json
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   └── chennai_bengaluru.geojson   # optional route map
│
├── replay/
│   ├── replay.py
│   └── sample_trace.json
│
├── LICENSE
├── README.md
└── .gitignore
🌐 Deployment Options
Railway.app / Render / Heroku → Host Flask backend

GitHub Pages / Vercel / Netlify → Host frontend dashboard

Or deploy both together using Docker Compose

bash
Copy code
docker compose up
🧪 Testing
Run the simulator:

bash
Copy code
python replay/replay.py --interval 1
Observe real-time updates on the dashboard and verify that alerts trigger correctly.

🗺️ Future Roadmap
 Real-time GPS streaming

 Collision detection (same track & distance)

 Map-matching with real OSM railway data

 Dynamic ETA calculation

 Firebase / MQTT cloud integration

 Rotating train icons based on direction

 Dockerized one-click deployment

🛡️ License
Licensed under the MIT License — free for academic & personal use.
See LICENSE for details.

👨‍💻 Contributors
Name	Role	Contribution
PV	Lead Engineer & Creator	Concept · Architecture · Full Stack Dev
ChatGPT (Co-Dev)	Technical Assistant	Backend · Frontend · Documentation

❤️ Inspiration
“A one-minute signalling delay can cost countless lives.
TrainSafe eliminates that delay — bringing trains closer to intelligence.”

🏁 Project Links
📂 Repository: TrainSafe-RealTime-Railway-Communication-System

🎥 Demo Video: December 1st week
📄 Documentation: (Will Upload Later)/docs 

🔧 Contact
Maintainer: PV
📧 Email: pranav.vikraman.25@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/pranav-vikraman-322020242
🌐 Portfolio: Pranavvikraman.me
