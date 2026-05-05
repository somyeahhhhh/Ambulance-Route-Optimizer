"""
Smart Ambulance Route Optimizer — Noida, UP
==========================================
A* Pathfinding with Time-Based Traffic Simulation

Run:  python3 main.py
"""

import sys
from graph import NODES, HOSPITALS, PICKUP_LOCATIONS
from astar import run_astar, run_shortest_distance
from traffic import time_label
from display import (
    print_header, print_section, print_route_steps,
    print_comparison_table, print_traffic_context, print_summary_box,
    GREEN, RED, CYAN, GRAY, BOLD, RESET, WHITE,
)
from ascii_map import render_map


def pick(prompt, options_dict, label_fn):
    print()
    for k, v in options_dict.items():
        print(f"    {CYAN}{k}{RESET}. {label_fn(v)}")
    print()
    while True:
        choice = input(f"  {prompt}: ").strip()
        if choice in options_dict:
            return choice
        print(f"  {RED}Invalid choice. Enter a number from the list.{RESET}")


def get_hour():
    print()
    print(f"  {GRAY}Examples: 8 = 8:00 AM  |  14 = 2:00 PM  |  18 = 6:00 PM{RESET}")
    while True:
        raw = input("  Enter hour (0–23): ").strip()
        try:
            h = int(raw)
            if 0 <= h <= 23:
                return h
        except ValueError:
            pass
        print(f"  {RED}Please enter a number between 0 and 23.{RESET}")


def get_day_type():
    print()
    print(f"    {CYAN}1{RESET}. Weekday  (Mon–Fri)")
    print(f"    {CYAN}2{RESET}. Weekend  (Sat–Sun)")
    print()
    while True:
        choice = input("  Day type: ").strip()
        if choice == "1":
            return "weekday"
        if choice == "2":
            return "weekend"
        print(f"  {RED}Enter 1 or 2.{RESET}")


def main():
    print_header()

    # ── Step 1: Pickup location ───────────────────────────────────────────────
    print_section("STEP 1 — Select Ambulance Pickup Location")
    pickup_key = pick(
        "Enter pickup number",
        PICKUP_LOCATIONS,
        lambda v: v[1]
    )
    start_id, start_name = PICKUP_LOCATIONS[pickup_key]

    # ── Step 2: Hospital destination ──────────────────────────────────────────
    print_section("STEP 2 — Select Destination Hospital")
    for k, (_, name, sector, specs) in HOSPITALS.items():
        print(f"    {CYAN}{k}{RESET}. {BOLD}{name}{RESET}  ({sector})")
        print(f"       {GRAY}{specs}{RESET}")
    print()
    while True:
        hosp_key = input("  Enter hospital number: ").strip()
        if hosp_key in HOSPITALS:
            break
        print(f"  {RED}Invalid. Choose from 1–{len(HOSPITALS)}.{RESET}")
    goal_id, hosp_name, hosp_sector, hosp_specs = HOSPITALS[hosp_key]

    # ── Step 3: Time ──────────────────────────────────────────────────────────
    print_section("STEP 3 — Current Time")
    hour = get_hour()

    # ── Step 4: Day type ──────────────────────────────────────────────────────
    print_section("STEP 4 — Weekday or Weekend?")
    day_type = get_day_type()

    # ── Compute all 3 routes ──────────────────────────────────────────────────
    print()
    print(f"  {GRAY}Computing routes using A* algorithm...{RESET}")

    route_astar     = run_astar(start_id, goal_id, hour, day_type, avoid_tolls=False)
    route_toll_free = run_astar(start_id, goal_id, hour, day_type, avoid_tolls=True)
    route_shortest  = run_shortest_distance(start_id, goal_id, hour, day_type)

    if not route_astar['found']:
        print(f"  {RED}No route found. Try different locations.{RESET}")
        sys.exit(1)

    name_astar     = "A* Optimal (Traffic-Aware)"
    name_toll_free = "Toll-Free Route"
    name_shortest  = "Shortest Distance (GPS)"

    # ── Traffic context along the best route ──────────────────────────────────
    key_nodes = [step['from_id'] for step in route_astar['path']] + [goal_id]
    print_traffic_context(hour, day_type, key_nodes)

    # ── Comparison table ──────────────────────────────────────────────────────
    all_routes = [route_astar]
    all_names  = [name_astar]

    # Only add toll-free if it found a different path
    if route_toll_free['found']:
        all_routes.append(route_toll_free)
        all_names.append(name_toll_free)

    if route_shortest['found']:
        all_routes.append(route_shortest)
        all_names.append(name_shortest)

    print_comparison_table(all_routes, all_names, hour, day_type)

    # ── ASCII map ─────────────────────────────────────────────────────────────
    print_section("NOIDA MAP  —  A* Optimal Route")
    render_map(
        route_path   = route_astar['path'],
        start_id     = start_id,
        goal_id      = goal_id,
        hour         = hour,
        day_type     = day_type,
        all_node_ids = list(NODES.keys()),
    )

    # ── Step-by-step for A* route (always the dispatch choice) ───────────────
    print_section("STEP-BY-STEP DIRECTIONS  —  A* Optimal Route")
    print_route_steps(route_astar, hour, day_type, label=name_astar, is_best=True)

    # ── Dispatch summary ──────────────────────────────────────────────────────
    print_summary_box(route_astar, name_astar, hour, day_type)

    print(f"  {GRAY}Destination : {BOLD}{hosp_name}{RESET}  {GRAY}({hosp_sector}){RESET}")
    print(f"  {GRAY}Specialties : {hosp_specs}{RESET}")
    print()
    print(f"  {RED}{BOLD}{'═' * 64}{RESET}")
    print()


if __name__ == "__main__":
    main()
