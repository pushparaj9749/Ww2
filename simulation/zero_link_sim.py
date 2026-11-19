#!/usr/bin/env python3
"""
ZERO-LINK simulation: H1 TAM-DTN vs Flooding mesh vs Star (LoRaWAN-like).

Tick-based simulation. Stdlib only. Fixed seed for reproducibility.
Units: positions in km, range in km. 1 tick = 10 s.

Models: nodes, range-limited links, multi-hop forwarding, DTN store-carry-forward,
node failures, partitions, message expiry, delivery rate, latency, energy.

This is a SOFTWARE simulation. Results are NOT real-world hardware performance.
"""

import math
import random
import statistics
from dataclasses import dataclass, field

# ---------------------------------------------------------------- config
SEED = 42
TICKS = 600            # 600 ticks * 10 s = 100 min
TICK_SECONDS = 10
BUNDLE_TTL = 300       # ticks a DTN bundle lives in store (50 min)
FLOOD_TTL = 30         # ticks a flooding packet lives (no long-term store)
MAX_COPIES = 6         # DTN copy budget
FLOOD_HOP_LIMIT = 7    # Meshtastic-like baseline
TX_ENERGY_J = 0.3      # energy per transmission (SF12-ish, radio only)
RX_ENERGY_J = 0.05     # energy per reception

@dataclass
class Bundle:
    bid: int
    src: int
    dst: int
    born: int
    copies: int = 1
    hops: int = 0

@dataclass
class Node:
    nid: int
    x: float
    y: float
    kind: str = "endpoint"   # endpoint | relay | ferry
    vx: float = 0.0
    vy: float = 0.0
    alive: bool = True
    store: dict = field(default_factory=dict)   # bid -> Bundle
    seen: set = field(default_factory=set)
    route_cache: dict = field(default_factory=dict)  # dst -> (next_hop, expiry_tick)
    tx_count: int = 0
    rx_count: int = 0

def dist(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

def neighbours(node: Node, nodes: list, rng_km: float) -> list:
    return [n for n in nodes if n.alive and n.nid != node.nid and dist(node, n) <= rng_km]

def move_ferries(nodes, width_km):
    for n in nodes:
        if n.alive and n.kind == "ferry":
            n.x += n.vx
            if n.x < 0 or n.x > width_km:
                n.vx *= -1
                n.x = max(0.0, min(width_km, n.x))

def make_messages(n_messages, nodes, rng, t_max=400):
    endpoints = [n.nid for n in nodes if n.kind == "endpoint"]
    msgs = []
    for _ in range(n_messages):
        t = rng.randint(0, t_max)
        s = rng.choice(endpoints)
        d = rng.choice([e for e in endpoints if e != s])
        msgs.append((t, s, d))
    msgs.sort()
    return msgs

def fail_relays(nodes, rng, frac=0.4):
    relays = [n for n in nodes if n.kind == "relay" and n.alive]
    for n in rng.sample(relays, max(1, int(len(relays) * frac))):
        n.alive = False

# ---------------------------------------------------------------- scenarios
def scenario_nodes(kind: str, rng: random.Random):
    """Return (nodes, rng_km, width_km, n_messages)."""
    if kind == "S1":  # dense connected
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 3 == 0 else "endpoint") for i in range(40)]
        return nodes, 5.0, 20.0, 30
    if kind == "S2":  # sparse (likely partitioned at 5 km)
        nodes = [Node(i, rng.uniform(0, 50), rng.uniform(0, 50),
                      "relay" if i % 4 == 0 else "endpoint") for i in range(25)]
        return nodes, 5.0, 50.0, 30
    if kind == "S3":  # partitioned corridor + ferries
        nodes = []
        for i in range(15):
            nodes.append(Node(i, rng.uniform(0, 10), rng.uniform(0, 20), "endpoint"))
        for i in range(15, 30):
            nodes.append(Node(i, rng.uniform(90, 100), rng.uniform(0, 20), "endpoint"))
        for i in range(30, 35):
            nodes.append(Node(i, rng.uniform(10, 90), rng.uniform(0, 20), "ferry",
                              vx=rng.choice([-1, 1]) * 0.5, vy=0.0))
        return nodes, 5.0, 100.0, 20
    if kind == "S4":  # 100 km line chain (11 hops, spacing ~9.1 km)
        nodes = [Node(i, i * (100.0 / 11), 10.0,
                      "relay" if 0 < i < 11 else "endpoint") for i in range(12)]
        return nodes, 10.0, 100.0, 20
    if kind == "S5":  # S1 + relay failures mid-run
        nodes = [Node(i, rng.uniform(0, 20), rng.uniform(0, 20),
                      "relay" if i % 3 == 0 else "endpoint") for i in range(40)]
        return nodes, 5.0, 20.0, 30
    raise ValueError(kind)

# ---------------------------------------------------------------- architectures
def run_zero_link(nodes, rng_km, n_messages, rng, fail_at=None):
    """H1 TAM-DTN: flood-once-then-direct (route cache) + DTN store-carry-forward."""
    msgs = make_messages(n_messages, nodes, rng)
    by_id = {n.nid: n for n in nodes}
    delivered = {}
    bid_counter = 0
    sent = 0
    for tick in range(TICKS):
        if fail_at is not None and tick == fail_at:
            fail_relays(nodes, rng)
        move_ferries(nodes, 100.0)
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick)
                bid_counter += 1
                by_id[s].store[b.bid] = b
                by_id[s].seen.add(b.bid)
                sent += 1
        for n in nodes:
            if not n.alive:
                continue
            # expire + deliver
            for bid in list(n.store):
                b = n.store[bid]
                if tick - b.born > BUNDLE_TTL:
                    del n.store[bid]
                elif b.dst == n.nid:
                    delivered[bid] = tick - b.born
                    # learn route back to source via sender is implicit; cache dst->self
                    del n.store[bid]
            nbrs = neighbours(n, nodes, rng_km)
            for bid, b in list(n.store.items()):
                # 1) direct route if fresh and next hop in range
                route = n.route_cache.get(b.dst)
                if route and route[1] > tick:
                    nxt = by_id.get(route[0])
                    if nxt and nxt.alive and dist(n, nxt) <= rng_km and b.bid not in nxt.seen:
                        nxt.store[b.bid] = b
                        nxt.seen.add(b.bid)
                        n.tx_count += 1; nxt.rx_count += 1
                        del n.store[bid]
                        continue
                # 2) DTN forward: greedy (neighbour closer to dst, free) or
                #    epidemic (copy budget). Up to 3 neighbours per tick.
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
                        nb.store[b.bid] = b
                        nb.seen.add(b.bid)
                        nb.route_cache[n.nid] = (n.nid, tick + 100)  # reverse route to sender
                        n.tx_count += 1; nb.rx_count += 1
                        if not greedy:
                            b.copies += 1
                        forwarded += 1
                        if n.kind == "ferry" and b.copies >= MAX_COPIES:
                            del n.store[bid]
                            break
    tx = sum(n.tx_count for n in nodes)
    rx = sum(n.rx_count for n in nodes)
    energy = tx * TX_ENERGY_J + rx * RX_ENERGY_J
    lat = sorted(delivered.values())
    return {
        "sent": sent, "delivered": len(delivered),
        "pdr": len(delivered) / sent if sent else 0,
        "mean_lat_s": (statistics.mean(lat) * TICK_SECONDS) if lat else float("nan"),
        "p95_lat_s": (lat[int(0.95 * len(lat))] * TICK_SECONDS) if lat else float("nan"),
        "tx": tx, "energy_j": energy,
        "tx_per_delivered": tx / len(delivered) if delivered else float("nan"),
    }

def run_flooding(nodes, rng_km, n_messages, rng, fail_at=None):
    """Baseline A: blind flooding, hop limit + short TTL, no long-term store."""
    msgs = make_messages(n_messages, nodes, rng)
    by_id = {n.nid: n for n in nodes}
    delivered = {}
    queue = []  # (bundle, hops, holder)
    bid_counter = 0
    sent = 0
    for tick in range(TICKS):
        if fail_at is not None and tick == fail_at:
            fail_relays(nodes, rng)
        move_ferries(nodes, 100.0)
        for (t, s, d) in msgs:
            if t == tick:
                b = Bundle(bid_counter, s, d, tick)
                bid_counter += 1
                queue.append((b, 0, s))
                sent += 1
        new_queue = []
        for (b, hops, holder) in queue:
            if tick - b.born > FLOOD_TTL:
                continue  # expired, no store
            h = by_id[holder]
            if not h.alive:
                continue
            if b.dst == holder:
                delivered[b.bid] = tick - b.born
                continue
            if hops >= FLOOD_HOP_LIMIT:
                continue
            for nb in neighbours(h, nodes, rng_km):
                if b.bid not in nb.seen:
                    nb.seen.add(b.bid)
                    h.tx_count += 1; nb.rx_count += 1
                    new_queue.append((b, hops + 1, nb.nid))
        queue = new_queue
    tx = sum(n.tx_count for n in nodes)
    rx = sum(n.rx_count for n in nodes)
    energy = tx * TX_ENERGY_J + rx * RX_ENERGY_J
    lat = sorted(delivered.values())
    return {
        "sent": sent, "delivered": len(delivered),
        "pdr": len(delivered) / sent if sent else 0,
        "mean_lat_s": (statistics.mean(lat) * TICK_SECONDS) if lat else float("nan"),
        "p95_lat_s": (lat[int(0.95 * len(lat))] * TICK_SECONDS) if lat else float("nan"),
        "tx": tx, "energy_j": energy,
        "tx_per_delivered": tx / len(delivered) if delivered else float("nan"),
    }

def run_star(nodes, rng_km, n_messages, rng, fail_at=None):
    """Baseline B: LoRaWAN-like star via gateway at bounding-box centre."""
    xs = [n.x for n in nodes]; ys = [n.y for n in nodes]
    gx, gy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    endpoints = [n for n in nodes if n.kind == "endpoint"]
    sent = 0
    delivered = 0
    lat = []
    tx = 0
    for _ in range(n_messages):
        s = rng.choice(endpoints)
        d = rng.choice([e for e in endpoints if e.nid != s.nid])
        sent += 1
        if math.hypot(s.x - gx, s.y - gy) <= rng_km and math.hypot(d.x - gx, d.y - gy) <= rng_km:
            delivered += 1
            tx += 2
            lat.append(2 * TICK_SECONDS)
        else:
            tx += 1
    lat.sort()
    energy = tx * TX_ENERGY_J
    return {
        "sent": sent, "delivered": delivered,
        "pdr": delivered / sent if sent else 0,
        "mean_lat_s": statistics.mean(lat) if lat else float("nan"),
        "p95_lat_s": lat[int(0.95 * len(lat))] if lat else float("nan"),
        "tx": tx, "energy_j": energy,
        "tx_per_delivered": tx / delivered if delivered else float("nan"),
    }

# ---------------------------------------------------------------- main
def main():
    print("ZERO-LINK simulation (SOFTWARE ONLY — not hardware performance)")
    print(f"Seed={SEED}  Ticks={TICKS} ({TICKS*TICK_SECONDS}s)  DTN_TTL={BUNDLE_TTL}  FLOOD_TTL={FLOOD_TTL}  MAX_COPIES={MAX_COPIES}")
    print()
    hdr = f"{'Scenario':<10} {'Arch':<10} {'PDR':>6} {'MeanLat':>9} {'p95Lat':>9} {'TX':>6} {'EnergyJ':>8} {'TX/deliv':>8}"
    print(hdr)
    print("-" * len(hdr))
    results = {}
    for sc in ["S1", "S2", "S3", "S4", "S5"]:
        fail = 200 if sc == "S5" else None
        for name, fn in [("ZERO-LINK", run_zero_link), ("Flooding", run_flooding), ("Star", run_star)]:
            rng = random.Random(SEED)
            nodes, rng_km, w, nmsg = scenario_nodes(sc, rng)
            r = fn(nodes, rng_km, nmsg, rng, fail_at=fail)
            results[(sc, name)] = r
            print(f"{sc:<10} {name:<10} {r['pdr']:>6.2f} {r['mean_lat_s']:>9.1f} {r['p95_lat_s']:>9.1f} "
                  f"{r['tx']:>6} {r['energy_j']:>8.1f} {r['tx_per_delivered']:>8.1f}")
        print()
    print("Verdict (simulation only):")
    for sc in ["S1", "S2", "S3", "S4", "S5"]:
        z = results[(sc, "ZERO-LINK")]; f = results[(sc, "Flooding")]; s = results[(sc, "Star")]
        print(f"  {sc}: ZERO-LINK PDR={z['pdr']:.2f} vs Flooding {f['pdr']:.2f} vs Star {s['pdr']:.2f}")

if __name__ == "__main__":
    main()
