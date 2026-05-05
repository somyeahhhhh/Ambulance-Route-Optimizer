import math

# ─────────────────────────────────────────────
#  Noida Road Graph  (real GPS coordinates)
# ─────────────────────────────────────────────
#  Each NODE is a major intersection in Noida.
#  Each EDGE is a road segment connecting two nodes.

NODES = {
    "DND_ENTRY":        ("DND Flyway Noida Entry",         28.5716, 77.3004),
    "MAHAMAYA":         ("Mahamaya Flyover",                28.5683, 77.3113),
    "SECTOR_15_METRO":  ("Sector 15 Metro",                 28.5872, 77.3210),
    "SECTOR_18":        ("Sector 18 Market",                28.5698, 77.3220),
    "SECTOR_22":        ("Sector 22 Chowk",                 28.5740, 77.3100),
    "SECTOR_25":        ("Sector 25A Chowk",                28.5840, 77.3150),
    "KAILASH_HOSP":     ("Kailash Hospital Sector 27",      28.5784, 77.3240),
    "SECTOR_29":        ("Sector 29 Chowk",                 28.5808, 77.3375),
    "SECTOR_34":        ("Sector 34 Chowk",                 28.5713, 77.3297),
    "SECTOR_37":        ("Sector 37 Chowk",                 28.5730, 77.3389),
    "BOTANICAL":        ("Botanical Garden Metro",          28.5590, 77.3394),
    "SECTOR_44":        ("Sector 44 Chowk",                 28.5680, 77.3438),
    "SECTOR_50":        ("Sector 50 Chowk",                 28.5944, 77.3541),
    "FILM_CITY":        ("Film City Crossing",              28.5957, 77.3397),
    "SECTOR_62_METRO":  ("Sector 62 Metro Station",         28.6274, 77.3752),
    "FORTIS_HOSP":      ("Fortis Hospital Sector 62",       28.6251, 77.3746),
    "SECTOR_63":        ("Sector 63 Chowk",                 28.6200, 77.3700),
    "SECTOR_76":        ("Sector 76 Chowk",                 28.6126, 77.3720),
    "EXPRESSWAY_N":     ("Noida Expressway (North)",        28.5470, 77.3250),
    "KALINDI_KUNJ":     ("Kalindi Kunj Bridge",             28.5378, 77.3025),
    "SECTOR_12":        ("Sector 12 Chowk",                 28.5776, 77.3063),
    "CITY_CENTER":      ("Noida City Center Metro",         28.5645, 77.3282),
    "SECTOR_33":        ("Sector 33/34 Roundabout",         28.5730, 77.3250),
    "APOLLO_HOSP":      ("Apollo Hospital Sector 26",       28.5742, 77.3320),
    "SECTOR_41":        ("Sector 41 Chowk",                 28.5615, 77.3340),
    "SECTOR_46":        ("Sector 46 Chowk",                 28.5650, 77.3530),
    "MAX_HOSP":         ("Max Hospital Sector 19",          28.5803, 77.3259),
    "SECTOR_1":         ("Sector 1 Chowk",                  28.5956, 77.3090),
    "SECTOR_2":         ("Sector 2 Chowk",                  28.5930, 77.3190),
    "SECTOR_53":        ("Sector 53 Metro",                  28.6100, 77.3500),
    "SECTOR_58":        ("Sector 58 Chowk",                  28.6200, 77.3550),
    "JAYPEE_HOSP":      ("Jaypee Hospital Sector 128",      28.5098, 77.3890),
    "AMITY":            ("Amity University Crossing",        28.5440, 77.3330),
    "SECTOR_104":       ("Sector 104 Chowk",                 28.5200, 77.3500),
    "DISTRICT_HOSP":    ("District Hospital Sector 30",     28.5780, 77.3380),
}

# (node_a, node_b, road_name, distance_km, speed_limit_kmh, has_toll)
EDGES = [
    ("DND_ENTRY",       "MAHAMAYA",       "DND Flyway / Dadri Road Link",      1.40, 50, False),
    ("DND_ENTRY",       "KALINDI_KUNJ",   "DND Flyway",                         4.10, 80, True),
    ("MAHAMAYA",        "SECTOR_18",      "Dadri Road",                         1.30, 40, False),
    ("MAHAMAYA",        "SECTOR_12",      "Sector 22 Link Road",                1.60, 40, False),
    ("MAHAMAYA",        "CITY_CENTER",    "Vipin Khand Marg",                   2.10, 40, False),
    ("SECTOR_15_METRO", "SECTOR_25",      "Sector 25A Road",                    0.90, 40, False),
    ("SECTOR_15_METRO", "SECTOR_2",       "Sector 15/2 Link",                   1.10, 40, False),
    ("SECTOR_15_METRO", "SECTOR_1",       "Sector 16A Road",                    1.30, 40, False),
    ("SECTOR_18",       "SECTOR_33",      "Atta Market Road",                   0.70, 30, False),
    ("SECTOR_18",       "CITY_CENTER",    "Vipin Khand to Sector 18",           0.80, 40, False),
    ("SECTOR_22",       "SECTOR_12",      "Sector 22 Main Road",                0.85, 40, False),
    ("SECTOR_22",       "SECTOR_25",      "Sector 22-25 Road",                  1.20, 40, False),
    ("SECTOR_25",       "KAILASH_HOSP",   "Sector 25A-27 Link",                 0.80, 40, False),
    ("SECTOR_25",       "SECTOR_33",      "Sector 25-33 Road",                  1.10, 40, False),
    ("KAILASH_HOSP",    "MAX_HOSP",       "Hospital Zone Road",                 0.25, 30, False),
    ("KAILASH_HOSP",    "DISTRICT_HOSP",  "Sector 27-30 Road",                  0.60, 30, False),
    ("SECTOR_29",       "DISTRICT_HOSP",  "Sector 29 Road",                     0.50, 30, False),
    ("SECTOR_29",       "SECTOR_50",      "Sector 29-50 Link",                  1.80, 50, False),
    ("SECTOR_34",       "SECTOR_33",      "Sector 34 Road",                     0.75, 40, False),
    ("SECTOR_34",       "APOLLO_HOSP",    "Sector 34-26 Road",                  0.40, 30, False),
    ("SECTOR_37",       "SECTOR_44",      "Sector 37-44 Connector",             1.00, 40, False),
    ("SECTOR_37",       "BOTANICAL",      "Sector 37-Botanical Road",           2.40, 50, False),
    ("BOTANICAL",       "SECTOR_41",      "Botanical Garden Road",              1.20, 40, False),
    ("BOTANICAL",       "EXPRESSWAY_N",   "Noida-GN Expressway (via Botanical)",1.60, 80, False),
    ("SECTOR_44",       "SECTOR_46",      "Sector 44-46 Link",                  0.75, 40, False),
    ("SECTOR_44",       "SECTOR_41",      "Sector 41-44 Marg",                  0.90, 40, False),
    ("SECTOR_50",       "FILM_CITY",      "Sector 50-Film City Road",           1.00, 50, False),
    ("FILM_CITY",       "SECTOR_2",       "Film City Main Road",                0.65, 50, False),
    ("FILM_CITY",       "SECTOR_63",      "Sector 62 Link Road",                2.20, 60, False),
    ("SECTOR_62_METRO", "FORTIS_HOSP",    "Fortis Hospital Approach",           0.20, 30, False),
    ("SECTOR_62_METRO", "SECTOR_63",      "Sector 62-63 Road",                  0.85, 40, False),
    ("SECTOR_62_METRO", "SECTOR_53",      "Sector 62 Metro Road",               1.50, 50, False),
    ("SECTOR_63",       "SECTOR_76",      "Sector 63-76 Link",                  0.85, 40, False),
    ("SECTOR_63",       "SECTOR_58",      "Sector 63-58 Road",                  1.30, 40, False),
    ("SECTOR_76",       "SECTOR_53",      "Sector 76-53 Link",                  1.40, 40, False),
    ("EXPRESSWAY_N",    "AMITY",          "Noida Expressway South",             0.60, 80, False),
    ("EXPRESSWAY_N",    "CITY_CENTER",    "Noida Expressway North",             2.40, 80, False),
    ("EXPRESSWAY_N",    "SECTOR_41",      "Sector 41 Expressway Exit",          1.30, 60, False),
    ("CITY_CENTER",     "SECTOR_33",      "City Center-Sector 33 Road",         0.85, 40, False),
    ("SECTOR_12",       "SECTOR_22",      "Sector 12-22 Marg",                  0.85, 40, False),
    ("SECTOR_33",       "APOLLO_HOSP",    "Sector 33-26 Connector",             0.35, 30, False),
    ("SECTOR_33",       "CITY_CENTER",    "Sector 33-City Center",              0.85, 40, False),
    ("APOLLO_HOSP",     "MAX_HOSP",       "Apollo-Max Hospital Link",           0.30, 30, False),
    ("SECTOR_53",       "SECTOR_58",      "Sector 53-58 Metro Road",            0.95, 50, False),
    ("SECTOR_1",        "SECTOR_2",       "Sector 1-2 Road",                    0.35, 40, False),
    ("AMITY",           "SECTOR_104",     "Amity-Sector 104 Road",              0.90, 60, False),
    ("AMITY",           "EXPRESSWAY_N",   "Sector Amity-Expressway",            0.60, 60, False),
    ("SECTOR_104",      "JAYPEE_HOSP",    "Sector 104-128 Expressway",          3.20, 80, False),
    ("SECTOR_2",        "SECTOR_1",       "Sector 2-1 Link",                    0.35, 40, False),
    ("MAX_HOSP",        "KAILASH_HOSP",   "Max-Kailash Hospital Link",          0.25, 30, False),

    # ── Bypass / alternative roads (create real alternative paths) ─────────────
    # Sector 25 Bypass: longer distance (2.8km) but 60 km/h expressway style.
    # At peak hours A* prefers this over the congested Sector-18 route (4.3km, slower).
    ("MAHAMAYA",        "SECTOR_25",      "Sector 25 Bypass Road",              2.80, 60, False),

    # Sector 50 → Sector 53 direct link avoids Film City congestion
    ("SECTOR_50",       "SECTOR_53",      "Sector 50-53 Expressway Link",       2.50, 60, False),

    # North Noida connector: lets Sector 1/2 traffic reach Sector 12 faster
    ("SECTOR_1",        "SECTOR_12",      "Sector 1-12 Road",                   1.80, 50, False),

    # City Center direct to Sector 25 — useful mid-day shortcut
    ("CITY_CENTER",     "SECTOR_25",      "City Center-Sector 25 Link",         1.50, 50, False),

    # Sector 29 → Sector 37: useful east-west connector
    ("SECTOR_29",       "SECTOR_37",      "Sector 29-37 Cross Road",            2.10, 40, False),
]

# Hospitals available as destinations
HOSPITALS = {
    "1": ("KAILASH_HOSP",    "Kailash Hospital",      "Sector 27",  "Emergency | Cardiology | Neurology"),
    "2": ("FORTIS_HOSP",     "Fortis Hospital",       "Sector 62",  "Emergency | Cardiac Surgery | Oncology"),
    "3": ("APOLLO_HOSP",     "Apollo Hospital",       "Sector 26",  "Emergency | Cardiology | Transplant"),
    "4": ("JAYPEE_HOSP",     "Jaypee Hospital",       "Sector 128", "Emergency | Neurology | Orthopaedics"),
    "5": ("MAX_HOSP",        "Max Super Speciality",  "Sector 19",  "Emergency | Cancer | Paediatrics"),
    "6": ("DISTRICT_HOSP",   "District Hospital",     "Sector 30",  "Emergency | General Medicine"),
}

# Pickup locations (ambulance starting points)
PICKUP_LOCATIONS = {
    "1": ("DND_ENTRY",       "DND Flyway Area"),
    "2": ("SECTOR_18",       "Sector 18 Market Area"),
    "3": ("SECTOR_50",       "Sector 50 Residential"),
    "4": ("SECTOR_62_METRO", "Sector 62 Tech Zone"),
    "5": ("SECTOR_15_METRO", "Sector 15 Metro Area"),
    "6": ("BOTANICAL",       "Botanical Garden Area"),
    "7": ("SECTOR_1",        "Sector 1 North Noida"),
    "8": ("FILM_CITY",       "Film City Area"),
}


def haversine_km(lat1, lng1, lat2, lng2):
    """Calculate straight-line distance between two GPS points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_adjacency():
    """Build adjacency list from edge list (bidirectional)."""
    adj = {n: [] for n in NODES}
    for (a, b, road, dist, speed, toll) in EDGES:
        adj[a].append((b, road, dist, speed, toll))
        adj[b].append((a, road, dist, speed, toll))
    return adj
