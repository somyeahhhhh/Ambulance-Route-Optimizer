import heapq
from graph import NODES, build_adjacency, haversine_km
from traffic import get_traffic_multiplier, get_congestion_score


def _reconstruct(came_from, start_id, goal_id, hour, day_type, use_traffic):
    path = []
    cur = goal_id
    while cur != start_id:
        prev_id, road, dist, speed = came_from[cur]
        if use_traffic:
            multiplier = get_traffic_multiplier(prev_id, hour, day_type)
            effective_speed = speed / multiplier
        else:
            effective_speed = speed
        score = get_congestion_score(prev_id, hour, day_type)
        path.insert(0, {
            'from_id':          prev_id,
            'to_id':            cur,
            'road_name':        road,
            'distance_km':      dist,
            'speed_limit':      speed,
            'congestion_score': score,
            'effective_speed':  round(effective_speed, 1),
            'time_min':         round((dist / effective_speed) * 60, 1),
            'free_time_min':    round((dist / speed) * 60, 1),
        })
        cur = prev_id

    total_distance    = sum(s['distance_km'] for s in path)
    total_time        = sum(s['time_min'] for s in path)
    free_flow_time    = sum(s['free_time_min'] for s in path)

    return {
        'found':              True,
        'path':               path,
        'total_distance_km':  round(total_distance, 2),
        'total_time_min':     round(total_time, 1),
        'free_flow_time_min': round(free_flow_time, 1),
    }


def run_astar(start_id, goal_id, hour, day_type="weekday", avoid_tolls=False):
    """
    A* with traffic-weighted edge costs.
    This is the core algorithm — finds the fastest real-world route.
    """
    adjacency = build_adjacency()

    def heuristic(node_id):
        _, lat1, lng1 = NODES[node_id]
        _, lat2, lng2 = NODES[goal_id]
        return (haversine_km(lat1, lng1, lat2, lng2) / 60) * 60

    def edge_cost(from_id, dist_km, speed_kmh):
        multiplier = get_traffic_multiplier(from_id, hour, day_type)
        effective_speed = speed_kmh / multiplier
        return (dist_km / effective_speed) * 60

    g_score  = {n: float('inf') for n in NODES}
    came_from = {}
    g_score[start_id] = 0
    open_heap = [(heuristic(start_id), start_id)]
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)
        if current == goal_id:
            break
        for (neighbor, road, dist, speed, toll) in adjacency[current]:
            if neighbor in visited:
                continue
            if avoid_tolls and toll:
                continue
            cost = edge_cost(current, dist, speed)
            tentative_g = g_score[current] + cost
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = (current, road, dist, speed)
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor)
                heapq.heappush(open_heap, (f, neighbor))

    if goal_id not in came_from and start_id != goal_id:
        return {'found': False}

    return _reconstruct(came_from, start_id, goal_id, hour, day_type, use_traffic=True)


def run_shortest_distance(start_id, goal_id, hour, day_type="weekday"):
    """
    Dijkstra on raw distance (ignores traffic).
    Finds the shortest km path — the naive GPS route.
    We then measure its actual travel time WITH traffic applied,
    so we can show how much slower it really is vs A*.
    """
    adjacency = build_adjacency()

    g_score  = {n: float('inf') for n in NODES}
    came_from = {}
    g_score[start_id] = 0
    open_heap = [(0, start_id)]
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)
        if current == goal_id:
            break
        for (neighbor, road, dist, speed, toll) in adjacency[current]:
            if neighbor in visited:
                continue
            tentative_g = g_score[current] + dist
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = (current, road, dist, speed)
                g_score[neighbor] = tentative_g
                heapq.heappush(open_heap, (tentative_g, neighbor))

    if goal_id not in came_from and start_id != goal_id:
        return {'found': False}

    # Reconstruct and apply real traffic times so comparison is honest
    return _reconstruct(came_from, start_id, goal_id, hour, day_type, use_traffic=True)
