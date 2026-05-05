from traffic import congestion_label, get_congestion_score
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── ANSI colour codes ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
ORANGE = "\033[38;5;208m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"


def color_for_congestion(score):
    if score < 25:   return GREEN
    if score < 50:   return YELLOW
    if score < 75:   return ORANGE
    return RED


def congestion_bar(score, width=20):
    filled = int((score / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    c = color_for_congestion(score)
    return f"{c}{bar}{RESET} {score:>3}/100"


def print_header():
    print()
    print(f"{RED}{BOLD}{'═' * 64}{RESET}")
    print(f"{RED}{BOLD}  AMBULANCE ROUTE OPTIMIZER — NOIDA, UP{RESET}")
    print(f"{GRAY}  A* Pathfinding with Real-Time Traffic Simulation (IST){RESET}")
    print(f"{RED}{BOLD}{'═' * 64}{RESET}")
    print()


def print_section(title):
    print()
    print(f"{CYAN}{BOLD}  ▶  {title}{RESET}")
    print(f"{GRAY}  {'─' * 58}{RESET}")


def print_route_steps(result, hour, day_type, label="Optimal Route", is_best=True):
    from graph import NODES

    path = result['path']
    badge = f"{GREEN}[BEST ROUTE]{RESET}" if is_best else f"{GRAY}[ALTERNATIVE]{RESET}"
    print()
    print(f"  {BOLD}{label}{RESET}  {badge}")
    print(f"  {GRAY}{'─' * 58}{RESET}")

    for i, step in enumerate(path, 1):
        from_name = NODES[step['from_id']][0]
        to_name   = NODES[step['to_id']][0]
        score     = step['congestion_score']
        c         = color_for_congestion(score)
        label_c   = congestion_label(score)

        print(f"  {GRAY}{i:>2}.{RESET} {WHITE}{step['road_name']}{RESET}")
        print(f"      {GRAY}From:{RESET} {from_name}")
        print(f"      {GRAY}  To:{RESET} {to_name}")
        print(f"      {GRAY}Dist:{RESET} {step['distance_km']:.1f} km  "
              f"{GRAY}Speed:{RESET} {c}{step['effective_speed']:.0f} km/h{RESET}  "
              f"{GRAY}Traffic:{RESET} {c}{label_c}{RESET}  "
              f"{GRAY}Time:{RESET} {step['time_min']:.1f} min")
        print()


def print_comparison_table(results_list, names, hour, day_type):
    """
    Print a side-by-side comparison table of multiple routes.
    results_list: list of astar result dicts
    names: list of route names
    """
    print_section("ROUTE COMPARISON TABLE")
    print()

    col_w = 20
    header_row = f"  {'Metric':<22}" + "".join(f"{n:<{col_w}}" for n in names)
    print(f"  {BOLD}{WHITE}{header_row}{RESET}")
    print(f"  {GRAY}{'─' * (22 + col_w * len(names))}{RESET}")

    def row(label, values, color_fn=None):
        line = f"  {GRAY}{label:<22}{RESET}"
        for i, v in enumerate(values):
            c = color_fn(i) if color_fn else WHITE
            line += f"{c}{str(v):<{col_w}}{RESET}"
        print(line)

    # Distance
    dists = [f"{r['total_distance_km']:.1f} km" for r in results_list]
    min_d = min(r['total_distance_km'] for r in results_list)
    row("Distance", dists,
        lambda i: GREEN if results_list[i]['total_distance_km'] == min_d else WHITE)

    # Estimated time
    times = [f"{r['total_time_min']:.0f} min" for r in results_list]
    min_t = min(r['total_time_min'] for r in results_list)
    row("Est. Travel Time", times,
        lambda i: GREEN if results_list[i]['total_time_min'] == min_t else WHITE)

    # Free-flow time (no traffic)
    ff_times = [f"{r['free_flow_time_min']:.0f} min" for r in results_list]
    row("Free-Flow Time", ff_times)

    # Delay due to traffic
    delays = [f"+{r['total_time_min'] - r['free_flow_time_min']:.0f} min"
              for r in results_list]
    min_delay = min(r['total_time_min'] - r['free_flow_time_min'] for r in results_list)
    row("Traffic Delay", delays,
        lambda i: GREEN if (results_list[i]['total_time_min']
                            - results_list[i]['free_flow_time_min']) == min_delay
                        else RED)

    # Stops (nodes)
    stops = [f"{len(r['path'])} roads" for r in results_list]
    row("Road Segments", stops)

    print(f"  {GRAY}{'─' * (22 + col_w * len(names))}{RESET}")

    # Winner annotation
    best_i = min(range(len(results_list)), key=lambda i: results_list[i]['total_time_min'])
    best_time = results_list[best_i]['total_time_min']
    others_times = [results_list[i]['total_time_min'] for i in range(len(results_list)) if i != best_i]
    max_saved = max(others_times) - best_time if others_times else 0

    # A* vs Shortest Distance insight
    astar_i = 0
    shortest_i = next((i for i, n in enumerate(names) if "GPS" in n or "Shortest" in n), None)

    print()
    print(f"  {GREEN}{BOLD}DISPATCHING: {names[best_i]}{RESET}")
    if max_saved >= 1:
        print(f"  {GREEN}→ Saves {max_saved:.0f} minute(s) vs the slowest alternative{RESET}")
    if shortest_i is not None and astar_i != shortest_i:
        astar_time    = results_list[astar_i]['total_time_min']
        shortest_time = results_list[shortest_i]['total_time_min']
        astar_dist    = results_list[astar_i]['total_distance_km']
        shortest_dist = results_list[shortest_i]['total_distance_km']
        diff          = shortest_time - astar_time
        if diff >= 1:
            print(f"  {YELLOW}→ A* takes {astar_dist:.1f} km (vs GPS shortest {shortest_dist:.1f} km){RESET}")
            print(f"  {YELLOW}→ Longer road, but {diff:.0f} min FASTER by avoiding congested zones{RESET}")
        elif diff <= -1:
            extra = -diff
            print(f"  {YELLOW}→ Shortest-distance route is {extra:.0f} min faster here (low congestion){RESET}")
    print()


def print_traffic_context(hour, day_type, key_nodes):
    """Show current traffic situation for key zones on the route."""
    print_section(f"TRAFFIC STATUS AT {hour:02d}:00  [{day_type.upper()}]")
    print()
    print(f"  {'Zone':<35} {'Congestion':<12} {'Score'}")
    print(f"  {GRAY}{'─' * 60}{RESET}")
    seen = set()
    for nid in key_nodes:
        if nid in seen:
            continue
        seen.add(nid)
        from graph import NODES
        if nid not in NODES:
            continue
        name = NODES[nid][0]
        score = get_congestion_score(nid, hour, day_type)
        label = congestion_label(score)
        c = color_for_congestion(score)
        bar = congestion_bar(score, 14)
        print(f"  {name:<35} {c}{label:<12}{RESET} {bar}")
    print()


def print_summary_box(best_result, best_name, hour, day_type):
    from traffic import time_label
    import re

    delay = best_result['total_time_min'] - best_result['free_flow_time_min']

    ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')
    def vlen(s): 
        return len(ANSI_ESCAPE.sub('', s))

    BOX_WIDTH = 56  

    def line(content):
        pad = BOX_WIDTH - vlen(content)
        return f"  {RED}│{RESET}{content}{' ' * pad}{RED}│{RESET}"

    title = f"{BOLD}{WHITE}DISPATCH SUMMARY{RESET}"

    route    = f"  Route    : {GREEN}{best_name}{RESET}"
    distance = f"  Distance : {WHITE}{best_result['total_distance_km']:.1f} km{RESET}"
    eta      = f"  ETA      : {YELLOW}{best_result['total_time_min']:.0f} minutes{RESET}"
    delay_l  = f"  Delay    : Traffic adds {delay:.0f} min over free flow"
    time_l   = f"  Time     : {WHITE}{time_label(hour)} [{day_type}]{RESET}"

    print()
    print(f"  {RED}┌{'─' * BOX_WIDTH}┐{RESET}")

    tpad = (BOX_WIDTH - vlen(title)) // 2
    print(f"  {RED}│{RESET}{' ' * tpad}{title}{' ' * (BOX_WIDTH - vlen(title) - tpad)}{RED}│{RESET}")

    print(line(route))
    print(line(distance))
    print(line(eta))
    print(line(delay_l))
    print(line(time_l))

    print(f"  {RED}└{'─' * BOX_WIDTH}┘{RESET}")
    print()
