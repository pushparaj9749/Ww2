#!/usr/bin/env python3
"""
ZERO-LINK Phase 2 simulator: fair comparison of 4 architectures.

Architectures:
  A. ZERO-LINK H1 TAM-DTN (greedy + epidemic copy budget + route cache + custody ACK + retry)
  B. Flooding mesh (Meshtastic-like: broadcast, hop limit 7, short TTL, no store)
  C. Star/gateway (LoRaWAN-like: single gateway, duty-cycle enforced, gateway always up)
  D. DTN Spray-and-Wait (binary spray L=4, wait phase, no greedy)

Fairness: identical topology, messages, failures, link loss, and duration per seed.
Realism: probabilistic loss, LoRa airtime, half-duplex, collisions, retries,
battery, storage limits, custody ACKs, realistic ferry speeds.

APPROXIMATIONS (explicitly not a full PHY simulation):
  - Loss is distance+base probabilistic, not a fading/terrain model.
  - Collisions are overlap-based, not a full CSMA/slotted-ALOHA model.
  - No DEM/terrain; range is a scalar parameter.
  - No crypto overhead; no frequency planning beyond one channel.

SOFTWARE SIMULATION ONLY. Results are NOT field-tested performance.
Stdlib only. Usage: python3 simulation/zero_link_sim.py [--seeds 42,7] [--out simulation/results_phase2.csv]
"""

import argparse
import copy
import csv
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------- global config
TICKS = 1800            # 1 tick = 1 s => 30 min simulated
MSG_TMAX = 900          # messages generated in first 15 min
N_MESSAGES = 30
TICK_S = 1.0

# LoRa airtime approximations (seconds) for ~100 B bundle at BW125
AIRTIME = {"SF7": 0.4, "SF9": 0.9, "SF12": 2.0}
ACK_AIRTIME = 0.3
P_TX_W = 0.10           # 20 dBm ~ 100 mW
P_RX_W = 0.02
BATTERY_J = 36000.0     # 10 Wh Li-ion
STORE_MAX = 50          # bundles per node
SEEN_MAX = 500
MAX_RETRIES = 2
FLOOD_HOP_LIMIT = 7
FLOOD_TTL_S = 60
DTN_TTL_S = 1500
MAX_COPIES = 6
SPRAY_L = 4
CONNECTED_LAT_S = 60    # latency <= 60 s counts as connected delivery
DUTY_CYCLE = 0.01       # 1% airtime (star enforcement)
DUTY_BUDGET_S = DUTY_CYCLE * 3600.0   # 36 s of TX per simulated hour

# ---------------------------------------------------------------- data types
@dataclass
class Bundle:
    bid: int
    src: int
    dst: int
    born: int
    copies: int = 1
    hops: int = 0
    retries: int = 0

@dataclass
class Node:
    nid: int
    x: float
    y: float
    kind: str = "endpoint"   # endpoint | relay | ferry | gateway
    vx: float = 0.0
    vy: float = 0.0
    alive: bool = True
    battery: float = BATTERY_J
    store: dict = field(default_factory=dict)
    seen: set = field(default_factory=set)
    route_cache: dict = field(default_factory=dict)  # dst -> (next_hop, expiry)
    hopmap: dict = field(default_factory=dict)       # bid -> forwarding steps to reach this node
    busy_until: int = 0      # half-duplex: cannot TX/RX while busy
    backoff_until: int = 0   # CSMA backoff after failed TX
    airtime_used: float = 0.0  # for duty cycle (star)
    tx_count: int = 0
    rx_count: int = 0
    collided: int = 0
    store_drops: int = 0

def dist(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def neighbours(node, nodes, rng_km):
    return [n for n in nodes if n.alive and n.nid != node.nid and dist(node, n) <= rng_km]

# ---------------------------------------------------------------- scenario generation (shared per seed)
def gen_topology(scenario, rng):
    """Return (nodes, rng_km, width_km, height_km). Positions in km."""
    if scenario == "T1":  # dense connected
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 3 == 0 else "endpoint") for i in range(40)]
        return nodes, 5.0, 20.0, 20.0
    if scenario == "T2":  # sparse
        nodes = [Node(i, rng.uniform(0, 50), rng.uniform(0, 50),
                      "relay" if i % 4 == 0 else "endpoint") for i in range(25)]
        return nodes, 5.0, 50.0, 50.0
    if scenario == "T3":  # disconnected (no ferries)
        nodes = []
        for i in range(15):
            nodes.append(Node(i, rng.uniform(0, 10), rng.uniform(0, 20), "endpoint"))
        for i in range(15, 30):
            nodes.append(Node(i, rng.uniform(90, 100), rng.uniform(0, 20), "endpoint"))
        return nodes, 5.0, 100.0, 20.0
    if scenario == "T4":  # ferry corridor (gap 20 km, ferry 15 m/s => ~1330 s crossing)
        nodes = []
        for i in range(15):
            nodes.append(Node(i, rng.uniform(0, 10), rng.uniform(0, 20), "endpoint"))
        for i in range(15, 30):
            nodes.append(Node(i, rng.uniform(30, 40), rng.uniform(0, 20), "endpoint"))
        for i in range(30, 35):
            nodes.append(Node(i, rng.uniform(10, 30), rng.uniform(0, 20), "ferry",
                              vx=rng.choice([-1, 1]) * 0.015, vy=0.0))
        return nodes, 5.0, 40.0, 20.0
    if scenario == "T5":  # 100 km chain
        nodes = [Node(i, i * (100.0 / 11), 10.0,
                      "relay" if 0 < i < 11 else "endpoint") for i in range(12)]
        return nodes, 10.0, 100.0, 20.0
    if scenario == "T6":  # dense + failures (failures generated separately, shared)
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 3 == 0 else "endpoint") for i in range(40)]
        return nodes, 5.0, 20.0, 20.0
    if scenario == "T7":  # congestion (high density)
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 4 == 0 else "endpoint") for i in range(80)]
        return nodes, 5.0, 20.0, 20.0
    if scenario == "T8":  # dense + high loss (loss set by caller)
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 3 == 0 else "endpoint") for i in range(40)]
        return nodes, 5.0, 20.0, 20.0
    raise ValueError(scenario)

def gen_messages(nodes, rng):
    endpoints = [n.nid for n in nodes if n.kind == "endpoint"]
    msgs = []
    for _ in range(N_MESSAGES):
        t = rng.randint(0, MSG_TMAX)
        s = rng.choice(endpoints)
        d = rng.choice([e for e in endpoints if e != s])
        msgs.append((t, s, d))
    msgs.sort()
    return msgs

def gen_failures(nodes, rng, scenario):
    """Shared failure schedule: list of (tick, nid). Empty except T6."""
    if scenario != "T6":
        return []
    relays = [n.nid for n in nodes if n.kind == "relay"]
    k = max(1, int(len(relays) * 0.4))  # 40% of relays fail (documented)
    victims = rng.sample(relays, k)
    return [(rng.randint(300, 600), v) for v in victims]

# ---------------------------------------------------------------- link / radio model
def link_success(d_km, rng_km, loss_rate, rng):
    """Probabilistic success. Approximation: base loss + distance-edge effect."""
    if d_km > rng_km:
        return False
    edge = 0.30 * (d_km / rng_km) ** 4   # extra loss near range edge
    p = (1.0 - loss_rate) * (1.0 - edge)
    return rng.random() < p

def can_tx(node, tick):
    return node.alive and node.battery > 0 and tick >= node.busy_until and tick >= node.backoff_until

# Per-tick TX log for collision approximation: list of (tx_nid, rx_nid).
# Approximation: if a receiver already has an incoming TX this tick, the new
# TX collides (fails). Real collisions kill both packets; sequential order
# here kills only the later one. Documented as an approximation.
TX_LOG = []

def do_tx(tx_node, rx_node, airtime_s, tick, rng, loss_rate, rng_km):
    """Attempt one unicast transmission. Returns True if received."""
    if not can_tx(tx_node, tick):
        return False
    if not rx_node.alive or rx_node.battery <= 0:
        return False
    tx_node.busy_until = tick + math.ceil(airtime_s)
    tx_node.airtime_used += airtime_s
    tx_node.tx_count += 1
    tx_node.battery -= P_TX_W * airtime_s
    TX_LOG.append((tx_node.nid, rx_node.nid))
    # collision: receiver already targeted this tick
    if any(rx == rx_node.nid for (_, rx) in TX_LOG[:-1]):
        tx_node.collided += 1
        tx_node.backoff_until = tick + rng.randint(1, 5)
        return False
    d = dist(tx_node, rx_node)
    if not link_success(d, rng_km, loss_rate, rng):
        tx_node.backoff_until = tick + rng.randint(1, 5)
        return False
    if tick < rx_node.busy_until:
        tx_node.backoff_until = tick + rng.randint(1, 5)
        return False
    rx_node.busy_until = tick + math.ceil(airtime_s)
    rx_node.rx_count += 1
    rx_node.battery -= P_RX_W * airtime_s
    return True

def do_broadcast(tx_node, rx_list, airtime_s, tick, rng, loss_rate, rng_km):
    """One broadcast TX received by all in-range neighbours (per-link loss).
    Returns list of receivers that got it. Counts as ONE transmission."""
    if not can_tx(tx_node, tick):
        return []
    tx_node.busy_until = tick + math.ceil(airtime_s)
    tx_node.airtime_used += airtime_s
    tx_node.tx_count += 1
    tx_node.battery -= P_TX_W * airtime_s
    got = []
    for rx_node in rx_list:
        if not rx_node.alive or rx_node.battery <= 0:
            continue
        TX_LOG.append((tx_node.nid, rx_node.nid))
        if any(rx == rx_node.nid for (_, rx) in TX_LOG[:-1]):
            tx_node.collided += 1
            continue
        d = dist(tx_node, rx_node)
        if not link_success(d, rng_km, loss_rate, rng):
            continue
        if tick < rx_node.busy_until:
            continue
        rx_node.busy_until = tick + math.ceil(airtime_s)
        rx_node.rx_count += 1
        rx_node.battery -= P_RX_W * airtime_s
        got.append(rx_node)
    if not got:
        tx_node.backoff_until = tick + rng.randint(1, 5)
    return got

def store_bundle(node, bundle):
    if bundle.bid in node.store:
        return True
    if len(node.store) >= STORE_MAX:
        # drop oldest
        oldest = min(node.store.values(), key=lambda b: b.born)
        del node.store[oldest.bid]
        node.store_drops += 1
    node.store[bundle.bid] = bundle
    node.hopmap.setdefault(bundle.bid, 0)
    if len(node.seen) < SEEN_MAX:
        node.seen.add(bundle.bid)
    return True

# ---------------------------------------------------------------- architectures
def run_zero_link(nodes, rng_km, msgs, failures, loss_rate, rng):
    """H1 TAM-DTN: greedy + epidemic + route cache + custody ACK + retry."""
    by_id = {n.nid: n for n in nodes}
    delivered = {}
    fail_map = {}
    for (t, v) in failures:
        fail_map.setdefault(t, []).append(v)
    bid_counter = 0
    sent = 0
    # pending retries: (tick, bundle, from_nid, to_nid)
    retries = []
    for tick in range(TICKS):
        TX_LOG.clear()
        for v in fail_map.get(tick, []):
            by_id[v].alive = False
        for n in nodes:
            if n.alive and n.kind == "ferry":
                n.x += n.vx
                if n.x < 0 or n.x > 40.0:
                    n.vx *= -1
                    n.x = max(0.0, min(40.0, n.x))
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick)
                bid_counter += 1
                store_bundle(by_id[s], b)
                sent += 1
        # retries due
        due = [r for r in retries if r[0] <= tick]
        retries = [r for r in retries if r[0] > tick]
        for (_, b, frm, to) in due:
            tx_node = by_id[frm]; rx_node = by_id[to]
            if do_tx(tx_node, rx_node, AIRTIME["SF9"], tick, rng, loss_rate, rng_km):
                store_bundle(rx_node, b)
                rx_node.hopmap[b.bid] = tx_node.hopmap.get(b.bid, 0) + 1
                # custody ACK (counts as TX)
                if do_tx(rx_node, tx_node, ACK_AIRTIME, tick, rng, loss_rate, rng_km):
                    if b.bid in tx_node.store:
                        del tx_node.store[b.bid]
        # forwarding
        for n in nodes:
            if not n.alive or n.battery <= 0:
                continue
            for bid in list(n.store):
                b = n.store[bid]
                if tick - b.born > DTN_TTL_S:
                    del n.store[bid]
                elif b.dst == n.nid:
                    # relay count = forwarders before the destination
                    delivered[bid] = (tick - b.born, max(0, n.hopmap.get(bid, 1) - 1))
                    del n.store[bid]
            nbrs = neighbours(n, nodes, rng_km)
            for bid, b in list(n.store.items()):
                if b.dst == n.nid:
                    continue
                # direct route
                route = n.route_cache.get(b.dst)
                if route and route[1] > tick:
                    nxt = by_id.get(route[0])
                    if nxt and nxt.alive and dist(n, nxt) <= rng_km and b.bid not in nxt.seen:
                        if do_tx(n, nxt, AIRTIME["SF9"], tick, rng, loss_rate, rng_km):
                            store_bundle(nxt, b)
                            nxt.hopmap[b.bid] = n.hopmap.get(b.bid, 0) + 1
                            del n.store[bid]
                        elif b.retries < MAX_RETRIES:
                            b.retries += 1
                            retries.append((tick + 2, b, n.nid, nxt.nid))
                        continue
                dst_node = by_id.get(b.dst)
                my_d = dist(n, dst_node) if dst_node else 0.0
                forwarded = 0
                for nb in nbrs:
                    if forwarded >= 3:
                        break
                    if b.bid in nb.seen:
                        continue
                    greedy = dst_node is not None and dist(nb, dst_node) < my_d
                    if greedy or b.copies < MAX_COPIES:
                        if do_tx(n, nb, AIRTIME["SF9"], tick, rng, loss_rate, rng_km):
                            store_bundle(nb, b)
                            nb.hopmap[b.bid] = n.hopmap.get(b.bid, 0) + 1
                            nb.route_cache[n.nid] = (n.nid, tick + 300)
                            if not greedy:
                                b.copies += 1
                            forwarded += 1
                            if n.kind == "ferry" and b.copies >= MAX_COPIES:
                                del n.store[bid]
                                break
                        elif b.retries < MAX_RETRIES:
                            b.retries += 1
                            retries.append((tick + 2, b, n.nid, nb.nid))
    return summarise(nodes, delivered, sent)

def run_flooding(nodes, rng_km, msgs, failures, loss_rate, rng):
    """Flooding: broadcast to all neighbours, hop limit, short TTL, no store."""
    by_id = {n.nid: n for n in nodes}
    delivered = {}
    fail_map = {}
    for (t, v) in failures:
        fail_map.setdefault(t, []).append(v)
    queue = []  # (bundle, hops, holder)
    bid_counter = 0
    sent = 0
    for tick in range(TICKS):
        TX_LOG.clear()
        for v in fail_map.get(tick, []):
            by_id[v].alive = False
        for n in nodes:
            if n.alive and n.kind == "ferry":
                n.x += n.vx
                if n.x < 0 or n.x > 40.0:
                    n.vx *= -1
                    n.x = max(0.0, min(40.0, n.x))
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick)
                bid_counter += 1
                queue.append((b, 0, s))
                sent += 1
        new_queue = []
        for (b, hops, holder) in queue:
            if tick - b.born > FLOOD_TTL_S:
                continue
            h = by_id[holder]
            if not h.alive or h.battery <= 0:
                continue
            if b.dst == holder:
                delivered[b.bid] = (tick - b.born, max(0, hops - 1))
                continue
            if hops >= FLOOD_HOP_LIMIT:
                continue
            if not can_tx(h, tick):
                new_queue.append((b, hops, holder))  # busy/backoff: retry next tick
                continue
            targets = [nb for nb in neighbours(h, nodes, rng_km) if b.bid not in nb.seen]
            got = do_broadcast(h, targets, AIRTIME["SF12"], tick, rng, loss_rate, rng_km)
            for nb in got:
                nb.seen.add(b.bid)
                new_queue.append((b, hops + 1, nb.nid))
            if not got and targets:
                new_queue.append((b, hops, holder))  # all lost: retry next tick
        queue = new_queue
    return summarise(nodes, delivered, sent)

def run_star(nodes, rng_km, msgs, failures, loss_rate, rng):
    """Star: 4 gateways (grid), duty-cycle enforced per gateway, gateways always up.
    Fair deployment: LoRaWAN operators deploy multiple gateways. Uplink to nearest
    gateway in range; downlink from same gateway (simplification, documented)."""
    by_id = {n.nid: n for n in nodes}
    xs = [n.x for n in nodes]; ys = [n.y for n in nodes]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    gateways = []
    for i, (fx, fy) in enumerate([(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)]):
        g = Node(-1 - i, x0 + fx * (x1 - x0), y0 + fy * (y1 - y0), "gateway")
        g.battery = float("inf")
        gateways.append(g)
    delivered = {}
    sent = 0
    bid_counter = 0
    pending = []  # (tick, bundle, stage, gw_nid)
    for tick in range(TICKS):
        TX_LOG.clear()
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick)
                bid_counter += 1
                pending.append((tick, b, 0, None))
                sent += 1
        still = []
        for (t, b, stage, gw_nid) in pending:
            if t > tick:
                still.append((t, b, stage, gw_nid))  # not yet due
                continue
            src = by_id[b.src]; dst = by_id[b.dst]
            if stage == 0:
                # nearest gateway in range
                gw = None; best = 1e9
                for g in gateways:
                    d = math.hypot(src.x - g.x, src.y - g.y)
                    if d <= rng_km and d < best:
                        best = d; gw = g
                if gw is None:
                    continue  # no gateway in range: lost
                if gw.airtime_used > DUTY_BUDGET_S:  # 1% duty cycle
                    still.append((t, b, stage, gw_nid))
                    continue
                if do_tx(src, gw, AIRTIME["SF12"], tick, rng, loss_rate, rng_km):
                    # downlink after uplink airtime (2 s) + processing (2 s): gateway half-duplex
                    still.append((tick + 4, b, 1, gw.nid))
            else:
                # downlink from nearest gateway to dst in range (real LoRaWAN: any gateway)
                gw = None; best = 1e9
                for g in gateways:
                    d = math.hypot(dst.x - g.x, dst.y - g.y)
                    if d <= rng_km and d < best:
                        best = d; gw = g
                if gw is None:
                    continue  # dst out of gateway coverage: lost
                if gw.airtime_used > DUTY_BUDGET_S:
                    still.append((t, b, stage, gw_nid))
                    continue
                if do_tx(gw, dst, AIRTIME["SF12"], tick, rng, loss_rate, rng_km):
                    delivered[b.bid] = (tick - b.born, 1)
        pending = still
    nodes.extend(gateways)
    return summarise(nodes, delivered, sent)

def run_spray(nodes, rng_km, msgs, failures, loss_rate, rng):
    """Spray-and-Wait: binary spray L=4, then wait (only dst holder forwards)."""
    by_id = {n.nid: n for n in nodes}
    delivered = {}
    fail_map = {}
    for (t, v) in failures:
        fail_map.setdefault(t, []).append(v)
    bid_counter = 0
    sent = 0
    for tick in range(TICKS):
        TX_LOG.clear()
        for v in fail_map.get(tick, []):
            by_id[v].alive = False
        for n in nodes:
            if n.alive and n.kind == "ferry":
                n.x += n.vx
                if n.x < 0 or n.x > 40.0:
                    n.vx *= -1
                    n.x = max(0.0, min(40.0, n.x))
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick, copies=SPRAY_L)
                bid_counter += 1
                store_bundle(by_id[s], b)
                sent += 1
        for n in nodes:
            if not n.alive or n.battery <= 0:
                continue
            for bid in list(n.store):
                b = n.store[bid]
                if tick - b.born > DTN_TTL_S:
                    del n.store[bid]
                elif b.dst == n.nid:
                    delivered[bid] = (tick - b.born, b.hops)
                    del n.store[bid]
            nbrs = neighbours(n, nodes, rng_km)
            for bid, b in list(n.store.items()):
                if b.dst == n.nid:
                    continue
                if b.copies > 1:
                    # spray: hand half copies to one unseen neighbour
                    for nb in nbrs:
                        if b.bid not in nb.seen:
                            if do_tx(n, nb, AIRTIME["SF12"], tick, rng, loss_rate, rng_km):
                                nb_bundle = Bundle(b.bid, b.src, b.dst, b.born,
                                                   copies=b.copies // 2, hops=b.hops + 1)
                                store_bundle(nb, nb_bundle)
                                b.copies -= b.copies // 2
                            break
                elif b.copies == 1:
                    # wait: only forward directly to destination
                    dst = by_id.get(b.dst)
                    if dst and dst.alive and dist(n, dst) <= rng_km and b.bid not in dst.seen:
                        if do_tx(n, dst, AIRTIME["SF12"], tick, rng, loss_rate, rng_km):
                            store_bundle(dst, b)
                            del n.store[bid]
    return summarise(nodes, delivered, sent)

# ---------------------------------------------------------------- metrics
def summarise(nodes, delivered, sent):
    tx = sum(n.tx_count for n in nodes)
    rx = sum(n.rx_count for n in nodes)
    collided = sum(n.collided for n in nodes)
    # energy from actual battery drain (TX/RX per airtime), not a fixed per-packet cost
    batt_used = sum(BATTERY_J - n.battery for n in nodes if n.battery != float("inf"))
    lat = sorted(v[0] for v in delivered.values())
    hops = [v[1] for v in delivered.values()]
    # relay dependency: share of deliveries that needed >=1 intermediate node
    # >=1 intermediate node between source and destination
    relay_dep = (sum(1 for h in hops if h >= 1) / len(hops)) if hops else float("nan")
    mean_hops = statistics.mean(hops) if hops else float("nan")
    conn = [l for l in lat if l <= CONNECTED_LAT_S]
    dtn = [l for l in lat if l > CONNECTED_LAT_S]
    store_peak = sum(len(n.store) for n in nodes)
    store_drops = sum(n.store_drops for n in nodes)
    total_airtime = sum(n.airtime_used for n in nodes)
    chan_util = total_airtime / (TICKS * max(1, len(nodes))) if nodes else 0.0
    return {
        "sent": sent,
        "delivered": len(delivered),
        "pdr": len(delivered) / sent if sent else 0.0,
        "median_lat_s": statistics.median(lat) if lat else float("nan"),
        "p95_lat_s": lat[min(len(lat) - 1, int(0.95 * len(lat)))] if lat else float("nan"),
        "mean_lat_s": statistics.mean(lat) if lat else float("nan"),
        "connected_delivered": len(conn),
        "dtn_delivered": len(dtn),
        "tx": tx,
        "rx": rx,
        "energy_j": batt_used,
        "energy_per_delivered_j": batt_used / len(delivered) if delivered else float("nan"),
        "tx_per_delivered": tx / len(delivered) if delivered else float("nan"),
        "collisions": collided,
        "collision_rate": collided / tx if tx else 0.0,
        "store_peak": store_peak,
        "relay_dependency": relay_dep,
        "mean_hops": mean_hops,
        "store_drops": store_drops,
        "chan_util": chan_util,
    }


# ---------------------------------------------------------------- 100 km study
def build_chain(spacing_km, total_km=100.0):
    """Evenly spaced chain; radio range == spacing (worst case: links at range edge)."""
    n_links = int(round(total_km / spacing_km))
    xs = [i * spacing_km for i in range(n_links + 1)]
    nodes = []
    for i, x in enumerate(xs):
        kind = "endpoint" if i in (0, len(xs) - 1) else "relay"
        nodes.append(Node(i, x, 10.0, kind))
    return nodes, spacing_km, total_km, 20.0

def run_hop_sensitivity(seeds, hop_limits=(7, 10, 12)):
    """Fairness check: is the 100 km chain result just flooding's hop limit?"""
    global FLOOD_HOP_LIMIT, FLOOD_TTL_S
    rows = []
    for hl in hop_limits:
        for ttl in (60, 600):
            for seed in seeds:
                g = random.Random(seed)
                nodes, rng_km, w, h = gen_topology("T5", g)
                msgs = gen_messages(nodes, g)
                fails = gen_failures(nodes, g, "T5")
                old_hl, old_ttl = FLOOD_HOP_LIMIT, FLOOD_TTL_S
                FLOOD_HOP_LIMIT, FLOOD_TTL_S = hl, ttl
                r = run_flooding(copy.deepcopy(nodes), rng_km, msgs, fails, 0.02,
                                 random.Random(seed * 1000 + 1))
                FLOOD_HOP_LIMIT, FLOOD_TTL_S = old_hl, old_ttl
                r.update({"arch": "Flooding", "hop_limit": hl, "ttl_s": ttl,
                          "seed": seed})
                rows.append(r)
                rz = run_zero_link(copy.deepcopy(nodes), rng_km, msgs, fails, 0.02,
                                   random.Random(seed * 1000))
                rz.update({"arch": "ZERO-LINK", "hop_limit": "", "ttl_s": "",
                           "seed": seed})
                rows.append(rz)
    return rows

def run_100km_sweep(seeds, total_km=100.0):
    """Relay spacing x relay availability sweep for the 100 km multi-hop claim."""
    rows = []
    for spacing in (5.0, 7.5, 10.0, 15.0, 20.0):
        for avail in (1.0, 0.95, 0.9, 0.8, 0.7):
            for seed in seeds:
                rng_gen = random.Random(seed)
                base_nodes, rng_km, w, h = build_chain(spacing, total_km)
                msgs = gen_messages(base_nodes, rng_gen)
                relays = [n.nid for n in base_nodes if n.kind == "relay"]
                down = [r for r in relays if rng_gen.random() > avail]
                failures = [(0, r) for r in down]
                rng = random.Random(seed * 1000 + 77)
                r = run_zero_link(copy.deepcopy(base_nodes), rng_km, msgs,
                                  failures, 0.02, rng)
                r.update({"spacing_km": spacing, "avail": avail, "seed": seed,
                          "n_relays": len(relays), "n_links": len(relays) + 1,
                          "rng_km": rng_km, "loss_rate": 0.02})
                rows.append(r)
    return rows

def aggregate_100km(rows):
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        g[(r["spacing_km"], r["avail"])].append(r)
    out = []
    for (sp, av), rs in sorted(g.items()):
        pdrs = [r["pdr"] for r in rs]
        lats = [r["median_lat_s"] for r in rs if r["median_lat_s"] == r["median_lat_s"]]
        p95 = [r["p95_lat_s"] for r in rs if r["p95_lat_s"] == r["p95_lat_s"]]
        def ci(vals):
            if len(vals) < 2:
                return (statistics.mean(vals) if vals else float("nan"), float("nan"))
            return (statistics.mean(vals),
                    1.96 * statistics.stdev(vals) / math.sqrt(len(vals)))
        pm, pc = ci(pdrs)
        lm, _ = ci(lats)
        p9, _ = ci(p95)
        out.append({"spacing_km": sp, "avail": av,
                    "n_relays": rs[0]["n_relays"], "n_links": rs[0]["n_links"],
                    "pdr_mean": pm, "pdr_ci95": pc,
                    "median_lat_mean": lm, "p95_lat_mean": p9,
                    "tx_mean": statistics.mean([r["tx"] for r in rs]),
                    "n_seeds": len(rs)})
    return out

# ---------------------------------------------------------------- driver
SCENARIOS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]
LOSS = {"T1": 0.02, "T2": 0.02, "T3": 0.02, "T4": 0.02, "T5": 0.02,
        "T6": 0.02, "T7": 0.02, "T8": 0.15}
ARCHS = [("ZERO-LINK", run_zero_link), ("Flooding", run_flooding),
         ("Star", run_star), ("SprayWait", run_spray)]

def run_all(seeds):
    rows = []
    for scenario in SCENARIOS:
        for seed in seeds:
            rng_gen = random.Random(seed)
            base_nodes, rng_km, w, h = gen_topology(scenario, rng_gen)
            msgs = gen_messages(base_nodes, rng_gen)
            failures = gen_failures(base_nodes, rng_gen, scenario)
            loss_rate = LOSS[scenario]
            for arch_idx, (arch_name, fn) in enumerate(ARCHS):
                rng = random.Random(seed * 1000 + arch_idx)
                nodes = copy.deepcopy(base_nodes)
                r = fn(nodes, rng_km, msgs, failures, loss_rate, rng)
                r.update({"scenario": scenario, "arch": arch_name, "seed": seed,
                          "rng_km": rng_km, "loss_rate": loss_rate})
                rows.append(r)
    return rows

def aggregate(rows):
    """Mean, median, stdev, 95% CI per (scenario, arch)."""
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[(r["scenario"], r["arch"])].append(r)
    out = []
    for (sc, arch), rs in sorted(groups.items()):
        pdrs = [r["pdr"] for r in rs]
        meds = [r["median_lat_s"] for r in rs if r["median_lat_s"] == r["median_lat_s"]]
        p95s = [r["p95_lat_s"] for r in rs if r["p95_lat_s"] == r["p95_lat_s"]]
        epd = [r["energy_per_delivered_j"] for r in rs if r["energy_per_delivered_j"] == r["energy_per_delivered_j"]]
        def ci(vals):
            if len(vals) < 2:
                return (statistics.mean(vals) if vals else float("nan"), float("nan"))
            m = statistics.mean(vals)
            s = statistics.stdev(vals)
            return (m, 1.96 * s / math.sqrt(len(vals)))
        pm, pci = ci(pdrs)
        mm, mci = ci(meds)
        p9m, p9ci = ci(p95s)
        em, eci = ci(epd)
        out.append({"scenario": sc, "arch": arch, "n_seeds": len(rs),
                    "pdr_mean": pm, "pdr_ci95": pci,
                    "median_lat_mean": mm, "median_lat_ci95": mci,
                    "p95_lat_mean": p9m, "p95_lat_ci95": p9ci,
                    "energy_per_delivered_mean": em, "energy_per_delivered_ci95": eci,
                    "tx_mean": statistics.mean([r["tx"] for r in rs]),
                    "conn_mean": statistics.mean([r["connected_delivered"] for r in rs]),
                    "dtn_mean": statistics.mean([r["dtn_delivered"] for r in rs]),
                    "chan_util_mean": statistics.mean([r["chan_util"] for r in rs]),
                    "relay_dep_mean": statistics.mean([r["relay_dependency"] for r in rs
                                                       if r["relay_dependency"] == r["relay_dependency"]] or [0.0]),
                    "mean_hops_mean": statistics.mean([r["mean_hops"] for r in rs
                                                       if r["mean_hops"] == r["mean_hops"]] or [0.0]),
                    "store_drops_mean": statistics.mean([r["store_drops"] for r in rs])})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="42,7,123,2024,99")
    ap.add_argument("--out", default="simulation/results_phase2.csv")
    ap.add_argument("--json", default="simulation/results_phase2.json")
    ap.add_argument("--sweep-100km", action="store_true",
                    help="run the 100 km relay-spacing x availability study instead")
    ap.add_argument("--sweep-out", default="simulation/results_phase2_100km_sweep.csv")
    ap.add_argument("--hop-sensitivity", action="store_true",
                    help="T5 chain: does flooding only lose because of its hop limit?")
    ap.add_argument("--hop-out", default="simulation/results_phase2_hop_sensitivity.csv")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    if args.hop_sensitivity:
        print("ZERO-LINK hop-limit fairness check on the 100 km chain (SOFTWARE ONLY)")
        print(f"Seeds={seeds}  Ticks={TICKS}  Messages={N_MESSAGES}  Loss=0.02")
        print()
        rows = run_hop_sensitivity(seeds)
        keys = ["arch", "hop_limit", "ttl_s", "seed", "sent", "delivered", "pdr",
                "median_lat_s", "p95_lat_s", "tx", "relay_dependency", "mean_hops"]
        with open(args.hop_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in keys})
        from collections import defaultdict
        grp = defaultdict(list)
        for r in rows:
            grp[(r["arch"], r["hop_limit"], r["ttl_s"])].append(r["pdr"])
        print(f"{'Arch':<10} {'HopLimit':>8} {'TTL':>5} {'PDR(mean)':>10} {'N':>3}")
        print("-" * 40)
        for (arch, hl, ttl), v in sorted(grp.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]), str(kv[0][2]))):
            print(f"{arch:<10} {str(hl):>8} {str(ttl):>5} {statistics.mean(v):>10.2f} {len(v):>3}")
        print()
        print(f"Wrote {args.hop_out} ({len(rows)} rows)")
        return
    if args.sweep_100km:
        print("ZERO-LINK 100 km multi-hop study (SOFTWARE ONLY)")
        print(f"Seeds={seeds}  Ticks={TICKS}  Messages={N_MESSAGES}  Loss=0.02")
        print("Chain: source at 0 km, destination at 100 km, range == relay spacing")
        print()
        rows = run_100km_sweep(seeds)
        agg = aggregate_100km(rows)
        keys = ["spacing_km", "avail", "seed", "n_relays", "n_links", "sent",
                "delivered", "pdr", "median_lat_s", "p95_lat_s", "mean_lat_s",
                "dtn_delivered", "tx", "relay_dependency", "mean_hops",
                "energy_per_delivered_j"]
        with open(args.sweep_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in keys})
        with open(args.sweep_out.replace(".csv", ".json"), "w") as f:
            json.dump({"raw": rows, "aggregate": agg}, f, indent=2)
        print(f"{'Spacing':>8} {'Relays':>7} {'Avail':>6} {'PDR(mean±CI)':>16} "
              f"{'MedLat':>7} {'p95Lat':>7} {'TX':>5}")
        print("-" * 64)
        for a in agg:
            print(f"{a['spacing_km']:>8.1f} {a['n_relays']:>7} {a['avail']:>6.2f} "
                  f"{a['pdr_mean']:>6.2f}±{a['pdr_ci95']:<6.2f} "
                  f"{a['median_lat_mean']:>7.1f} {a['p95_lat_mean']:>7.1f} "
                  f"{a['tx_mean']:>5.0f}")
        print()
        print(f"Wrote {args.sweep_out} ({len(rows)} rows)")
        return
    print(f"ZERO-LINK Phase 2 simulation (SOFTWARE ONLY)")
    print(f"Seeds={seeds}  Ticks={TICKS} ({TICKS}s)  Messages={N_MESSAGES}")
    print(f"Architectures: {[a for a, _ in ARCHS]}")
    print()
    rows = run_all(seeds)
    agg = aggregate(rows)
    # CSV: raw per-seed rows
    keys = ["scenario", "arch", "seed", "sent", "delivered", "pdr", "median_lat_s",
            "p95_lat_s", "mean_lat_s", "connected_delivered", "dtn_delivered", "tx", "rx",
            "energy_j", "energy_per_delivered_j", "tx_per_delivered", "collisions",
            "collision_rate", "store_peak", "store_drops", "chan_util",
            "relay_dependency", "mean_hops"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    with open(args.json, "w") as f:
        json.dump({"raw": rows, "aggregate": agg}, f, indent=2)
    # console table
    hdr = f"{'Scenario':<9} {'Arch':<10} {'PDR(mean±CI)':>16} {'MedLat':>8} {'p95Lat':>8} {'E/deliv':>8} {'TX':>6} {'Conn':>5} {'DTN':>4} {'RD':>5} {'Hops':>6}"
    print(hdr)
    print("-" * len(hdr))
    for a in agg:
        print(f"{a['scenario']:<9} {a['arch']:<10} {a['pdr_mean']:>6.2f}±{a['pdr_ci95']:<6.2f} "
              f"{a['median_lat_mean']:>8.1f} {a['p95_lat_mean']:>8.1f} "
              f"{a['energy_per_delivered_mean']:>8.2f} {a['tx_mean']:>6.0f} "
              f"{a['conn_mean']:>5.1f} {a['dtn_mean']:>4.1f} "
              f"{a['relay_dep_mean']:>5.2f} {a['mean_hops_mean']:>6.2f}")
    print()
    print(f"Wrote {args.out} ({len(rows)} rows) and {args.json}")

if __name__ == "__main__":
    main()
