"""
ASCII map renderer for Noida road network.
Projects real GPS coordinates onto a terminal grid and draws the route.
"""

from graph import NODES
from traffic import get_congestion_score, congestion_label
from display import (
    GREEN, RED, YELLOW, ORANGE, CYAN, GRAY, BOLD, RESET, WHITE, DIM,
    color_for_congestion,
)

# ── Grid dimensions ────────────────────────────────────────────────────────────
COLS = 72
ROWS = 26

# Noida bounding box (real GPS)
LAT_MAX = 28.640
LAT_MIN = 28.505
LNG_MIN = 77.295
LNG_MAX = 77.400


def _project(lat, lng):
    """Map a GPS coordinate to (row, col) on the terminal grid."""
    col = int((lng - LNG_MIN) / (LNG_MAX - LNG_MIN) * (COLS - 1))
    row = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (ROWS - 1))
    col = max(0, min(COLS - 1, col))
    row = max(0, min(ROWS - 1, row))
    return row, col


def _bresenham(r0, c0, r1, c1):
    """Return all (row, col) cells between two grid points (Bresenham's line)."""
    points = []
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r1 > r0 else -1
    sc = 1 if c1 > c0 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        points.append((r, c))
        if r == r1 and c == c1:
            break
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc
    return points


def _line_char(r0, c0, r1, c1, pr, pc, nr, nc):
    """
    Choose the ASCII character for a line segment cell based on direction.
    (pr,pc) = previous cell, (nr,nc) = next cell — used for bends.
    """
    dr = r1 - r0
    dc = c1 - c0
    if dr == 0:
        return '─'
    if dc == 0:
        return '│'
    if (dr > 0 and dc > 0) or (dr < 0 and dc < 0):
        return '\\'
    return '/'


def render_map(route_path, start_id, goal_id, hour, day_type, all_node_ids=None):
    """
    Draw the ASCII map showing the ambulance route.

    route_path : list of step dicts from astar result
    start_id   : origin node id
    goal_id    : destination node id
    hour, day_type : for traffic colouring
    all_node_ids   : if provided, draw background dots for all graph nodes
    """

    # ── 1. Build empty grid ──────────────────────────────────────────────────
    # Each cell: (char, color_str)
    grid = [[((' ', GRAY)) for _ in range(COLS)] for _ in range(ROWS)]

    # ── 2. Draw faint background node dots ───────────────────────────────────
    if all_node_ids:
        for nid in all_node_ids:
            _, lat, lng = NODES[nid]
            r, c = _project(lat, lng)
            grid[r][c] = ('·', GRAY + DIM)

    # ── 3. Draw route segments coloured by congestion ────────────────────────
    for step in route_path:
        from_id = step['from_id']
        to_id   = step['to_id']
        score   = step['congestion_score']
        color   = color_for_congestion(score)

        _, lat0, lng0 = NODES[from_id]
        _, lat1, lng1 = NODES[to_id]
        r0, c0 = _project(lat0, lng0)
        r1, c1 = _project(lat1, lng1)

        cells = _bresenham(r0, c0, r1, c1)
        for i, (r, c) in enumerate(cells):
            # Pick line character based on overall direction
            dr = r1 - r0
            dc = c1 - c0
            if dr == 0:
                ch = '━'
            elif dc == 0:
                ch = '┃'
            elif (dr > 0 and dc > 0) or (dr < 0 and dc < 0):
                ch = '\\'
            else:
                ch = '/'
            grid[r][c] = (ch, color + BOLD)

    # ── 4. Draw waypoint nodes along route ───────────────────────────────────
    route_node_ids = []
    for step in route_path:
        if step['from_id'] not in route_node_ids:
            route_node_ids.append(step['from_id'])
    route_node_ids.append(route_path[-1]['to_id'] if route_path else goal_id)

    for nid in route_node_ids:
        if nid == start_id or nid == goal_id:
            continue
        _, lat, lng = NODES[nid]
        r, c = _project(lat, lng)
        score = get_congestion_score(nid, hour, day_type)
        color = color_for_congestion(score)
        grid[r][c] = ('◆', color + BOLD)

    # ── 5. Mark start (ambulance) and goal (hospital) ────────────────────────
    _, slat, slng = NODES[start_id]
    sr, sc = _project(slat, slng)
    grid[sr][sc] = ('A', GREEN + BOLD)

    _, glat, glng = NODES[goal_id]
    gr, gc = _project(glat, glng)
    grid[gr][gc] = ('H', RED + BOLD)

    # ── 6. Add short labels near start and end ────────────────────────────────
    def place_label(r, c, text, color):
        for i, ch in enumerate(text):
            tc = c + i + 1
            if 0 <= tc < COLS and 0 <= r < ROWS:
                grid[r][tc] = (ch, color)

    start_short = NODES[start_id][0].split()[0][:8]
    goal_short  = NODES[goal_id][0].split()[0][:8]
    place_label(sr, sc, start_short, GREEN)
    place_label(gr, gc, goal_short, RED)

    # ── 7. Render ─────────────────────────────────────────────────────────────
    border_h = f"  {GRAY}┌{'─' * COLS}┐{RESET}"
    border_b = f"  {GRAY}└{'─' * COLS}┘{RESET}"

    print()
    print(f"  {BOLD}{WHITE}NOIDA ROAD MAP  —  AMBULANCE ROUTE{RESET}")
    print()
    print(f"  {GREEN}{BOLD}A{RESET} = Ambulance start   "
          f"{RED}{BOLD}H{RESET} = Hospital   "
          f"{GREEN}◆{RESET} = Low traffic   "
          f"{YELLOW}◆{RESET} = Moderate   "
          f"{ORANGE}◆{RESET} = High   "
          f"{RED}◆{RESET} = Severe")
    print()
    print(border_h)

    for r in range(ROWS):
        line = f"  {GRAY}│{RESET}"
        for c in range(COLS):
            ch, color = grid[r][c]
            line += f"{color}{ch}{RESET}"
        line += f"{GRAY}│{RESET}"
        print(line)

    print(border_b)

    # ── 8. Compass ────────────────────────────────────────────────────────────
    print(f"  {GRAY}W {'─' * (COLS // 2 - 2)} E{RESET}")
    print()

    # ── 9. Route segment legend below map ────────────────────────────────────
    print(f"  {BOLD}Route Segments:{RESET}")
    for i, step in enumerate(route_path, 1):
        score = step['congestion_score']
        c     = color_for_congestion(score)
        label = congestion_label(score)
        from_name = NODES[step['from_id']][0]
        to_name   = NODES[step['to_id']][0]
        print(f"  {GRAY}{i}.{RESET} {from_name} {GRAY}→{RESET} {to_name}  "
              f"{c}[{label} — {step['effective_speed']:.0f} km/h]{RESET}")
    print()
