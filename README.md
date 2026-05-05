# 🚑 Smart Ambulance Route Optimizer — Noida, UP

A terminal-based pathfinding tool that finds the **fastest ambulance route** across Noida's real road network using **A\* algorithm** with time-aware traffic simulation.



## ✨ Features

- **A\* Pathfinding** with real-time traffic cost weighting
- **Time-based traffic simulation** — morning rush, evening peak, night hours
- **Weekday vs Weekend** congestion profiles for 35+ Noida zones
- **Three route comparison** — A\* optimal, toll-free, and shortest distance (GPS)
- **ASCII map renderer** — visualises the route on a terminal grid using real GPS coordinates
- **Colour-coded output** — green/yellow/orange/red congestion indicators
- **6 hospitals** and **8 pickup locations** across Noida

---

## 📁 Project Structure

```
.
├── main.py          # Entry point — interactive CLI
├── astar.py         # A* and Dijkstra pathfinding algorithms
├── graph.py         # Road network: nodes (GPS), edges, hospitals, pickup points
├── traffic.py       # Hourly congestion scores and speed multipliers
├── display.py       # ANSI colour helpers and formatted output functions
└── ascii_map.py     # ASCII map renderer using Bresenham's line algorithm
```

---

## 🚀 Getting Started

**Requirements:** Python 3.8+ — no external libraries needed.

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ambulance-route-optimizer.git
cd ambulance-route-optimizer

# Run
python3 main.py
```

The program will prompt you to choose:
1. Ambulance pickup location (8 options)
2. Destination hospital (6 options)
3. Current hour (0–23)
4. Weekday or weekend

---

## 🗺️ How It Works

### A\* Algorithm
Each edge cost is weighted by a **traffic multiplier** derived from the congestion score of the origin node at the given hour:

```
multiplier = 1.0 + (congestion_score / 100) × 2.5
effective_speed = speed_limit / multiplier
edge_cost = (distance / effective_speed) × 60  # minutes
```

A congestion score of 0 means full speed; 100 means the road is at ~28% of its speed limit.

### Traffic Model
35+ Noida zones each have a 24-value hourly pattern (0–100) based on real congestion behaviour — DND Flyway peaks at 95 during 8–9 AM, hospital zones stay moderate through the day, and expressways drop to 10 at night.

### Route Comparison
| Route | Strategy |
|-------|----------|
| **A\* Optimal** | Minimises travel time accounting for congestion |
| **Toll-Free** | Same as A\*, but avoids toll roads |
| **Shortest Distance** | Minimises km (like a basic GPS) — then real traffic is applied to show true ETA |

---

## 📍 Road Network

- **35 nodes** — real Noida intersections with GPS coordinates
- **55+ edges** — roads with speed limits and toll flags
- Bounding box: `28.505°N – 28.640°N`, `77.295°E – 77.400°E`

---

## 🏥 Hospitals Covered

| Hospital | Sector | Specialties |
|----------|--------|-------------|
| Kailash Hospital | 27 | Emergency, Cardiology, Neurology |
| Fortis Hospital | 62 | Emergency, Cardiac Surgery, Oncology |
| Apollo Hospital | 26 | Emergency, Cardiology, Transplant |
| Jaypee Hospital | 128 | Emergency, Neurology, Orthopaedics |
| Max Super Speciality | 19 | Emergency, Cancer, Paediatrics |
| District Hospital | 30 | Emergency, General Medicine |

---

## 🖥️ Sample Output

```
  NOIDA ROAD MAP  —  AMBULANCE ROUTE

  A = Ambulance start   H = Hospital   ◆ = Low   ◆ = Moderate   ◆ = High   ◆ = Severe

  ┌────────────────────────────────────────────────────────────────────────┐
  │                        ·   ·  ·                                        │
  │         A Sector18  ━━━━◆━━━◆━━━◆━━━━H Kailash                        │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Pull requests welcome. To add new nodes/edges, edit `graph.py`. To adjust traffic patterns, edit `ZONE_PATTERNS` in `traffic.py`.

---

## 📄 License

MIT License — free to use and modify.# Ambulance-Route-Optimizer
A terminal-based pathfinding tool that finds the fastest ambulance route across Noida's real road network using A* algorithm with time-aware traffic simulation.
