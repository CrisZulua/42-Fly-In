## Flow Network Problem
A flow network is a directed graph where each edge has a capacity and each edge receives a flow.


# First Idea Layout
- Check for min cost path to end goal(is it part of and already). And check max-flow through this path.
- If the current node has another neighbor, check if any possible path to end goal exist, get its cost and max flow. This is made to maximize throuhgput. Repeat this for every current node neighbor.
- After finished schedule every movement and execute. Update the network status, link usage in case link travel takes 2 turns. Node occupancie(in-flow, out-flow).
- Go to first sentence.

# Drone routing algorithm — design summary

## Goal

Route N drones from start to goal through a shared network, respecting per-link and
per-node capacity limits and multi-turn travel times, while minimizing the total number
of simulation turns needed to get every drone to the goal.

No time-expanded graph, no pre-built copies of the map. Just two small pieces of live
state, checked fresh every turn.

---

## 1. Data you need to track

**Static** (from the map, fixed for the whole run):
- `nodes`: each with `max_drones` — how many can occupy it at once
- `edges`: each with `max_link_capacity` — how many can be in transit at once — and
  `travel_time` — turns to cross

**Dynamic** (changes every turn):
- `node_occupancy[node]` — drones currently sitting at that node
- `edge_in_transit[edge]` — list of `(drone_id, arrival_turn)` for drones currently
  crossing that edge
- `drone_state[drone]` — one of: `waiting_at(node)`, `in_transit(edge, arrival_turn)`,
  `arrived`

---

## 2. Main loop

```
turn = 0
initialize all drones as waiting_at(start)

WHILE not all drones have arrived:
    turn += 1

    # Step A — process arrivals first
    FOR each edge with drones scheduled to arrive this turn:
        FOR each (drone, arrival_turn) in edge_in_transit[edge] where arrival_turn == turn:
            remove drone from edge_in_transit[edge]      # frees one edge slot
            node_occupancy[destination] += 1
            IF destination == goal:
                drone_state[drone] = arrived
            ELSE:
                drone_state[drone] = waiting_at(destination)

    # Step B — try to move every waiting drone
    FOR each drone currently waiting_at(node), in dispatch order (see section 4):
        path = find_path(node, goal)          # see section 3 — always recomputed live
        IF path exists AND first edge of path has room right now:
            next_node = path[1]
            edge = (node, next_node)
            node_occupancy[node] -= 1
            edge_in_transit[edge].add( (drone, turn + edge.travel_time) )
            drone_state[drone] = in_transit(edge, turn + edge.travel_time)
        ELSE:
            # no room anywhere right now — drone just waits this turn
            leave drone_state unchanged

END WHILE
report turn as total turns taken
```

---

## 3. Pathfinding subroutine — `find_path(from_node, goal)`

Run this **fresh every time it's called** — using this turn's live occupancy and
transit numbers. Never reuse a path computed on an earlier turn; capacity changes
turn to turn as drones move and free up slots.

```
FUNCTION find_path(from_node, goal):
    # Dijkstra, weighted by travel_time — the objective is turns, so time IS the cost.
    # If every edge has the same travel_time, plain BFS by hop count works too.
    frontier = priority queue ordered by cumulative travel time, start = (from_node, 0)
    visited = {}

    WHILE frontier not empty:
        (node, time_so_far) = frontier.pop_lowest()
        IF node == goal:
            RETURN reconstructed path
        IF node in visited:
            CONTINUE
        visited.add(node)

        FOR each neighbor reachable via edge(node, neighbor):
            IF len(edge_in_transit[edge]) < edge.max_link_capacity
               AND node_occupancy[neighbor] < neighbor.max_drones:
                frontier.push(neighbor, time_so_far + edge.travel_time)

    RETURN no_path_found
```

This only checks *current* capacity, not what might free up a turn from now — that's
the right amount of lookahead for a live, per-turn planner. It also naturally skips
dead ends: a node with no viable route onward simply never gets added to the frontier,
with no special-casing needed.

---

## 4. Dispatch order — who gets first pick each turn

When several drones are waiting at once, the order you evaluate them in matters —
whichever drone claims a path first can take a slot a different drone needed more.

- **FIFO** (whoever's been waiting longest) — simplest, fair, gets you a working loop
  fast, but not throughput-optimal.
- **Longest-remaining-path first** — prioritize drones with the longer trip, so
  short-hop drones (which have more slack/flexibility) don't grab scarce capacity that
  a long-haul drone specifically needed.

Start with FIFO to get the loop working end-to-end. Switch to longest-path-first
later as a tuning pass once the basic version runs correctly — it's a one-line change
to the sort order in Step B, not a redesign.

---

## 5. Termination and edge cases to watch for

- **Deadlock protection**: if the network genuinely can't route everyone (or two
  drones are stuck waiting on each other), the `WHILE` loop could spin forever. Cap
  the turn count (e.g. `nb_drones * longest_possible_single_path * 2`) and report
  "no full schedule found" if you hit it. Treat that as a signal about the test map,
  not necessarily a bug in the loop.
- **Dead-end nodes** are already handled — `find_path` never routes into them, since
  nothing from there leads to the goal.
- **Drones that never move**: worth logging. If one drone keeps losing out to others
  turn after turn, that's a useful signal while testing dispatch order.

---

## 6. Why this stays simple

Nothing about the map is duplicated across time. You keep exactly two small, mutable
structures — `node_occupancy` and `edge_in_transit` — and a standard Dijkstra/BFS that
reads live capacity off them. Everything else is the bookkeeping you already sketched
in your first draft; this version just makes sure that bookkeeping gets consulted
fresh at every single decision point, instead of reused from a stale check.

---

## 7. Optional — only if the greedy version isn't good enough later

The loop above is a solid, buildable starting point, but it's a greedy heuristic — not
guaranteed to find the mathematically fewest possible total turns for the whole batch.
Getting the provably optimal schedule is a separate, harder problem (multi-agent
pathfinding with shared, capacity-limited resources). Not something to reach for now —
just worth knowing it's there if the greedy version turns out to leave throughput on
the table once you're testing against real levels.