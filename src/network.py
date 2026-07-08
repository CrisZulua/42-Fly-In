#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   network.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/02 11:59:52 by czuluaga            #+#    #+#            #
#   Updated: 2026/07/06 12:59:33 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from src.parser import MapConfig
from src.graph import Graph
from src.hubs import Hub
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from functools import reduce
import heapq


@dataclass
class Drone:
    """This class holds status data for a drone travelling through the network.
    """
    id: str
    status: str = "waiting"  # waiting, traveling, arrived
    waiting_at: str = "start"
    traveling_to: str = "goal"
    arrival_time: int = 1
    total_path_cost: float = 0
    # How deep is the drone in the network (number of hops taken)
    deepness: float = 0
    path: list = field(default_factory=list)


class Network:
    def __init__(self, config: MapConfig) -> None:
        # Init number of drones
        self.drones: List[Drone] = [
           Drone(id=f"D{i}", path=["start"])
           for i in range(1, config.nb_drones + 1)
        ]

        # Init graph structure
        self.graph: Graph = Graph([hub.name for hub in config.hubs])
        self.graph.init_graph(config.connections)

        # Init hubs data-holder
        self.hubs: Dict[str, Hub] = {hub.name: hub for hub in config.hubs}

        self.total_turns: int = 0

        self.turns_moves: List[Dict[str, str]] = []

    @staticmethod
    def get_weight(zone: str) -> int:
        """Gets the weight of the link (Turns cost for this link)

        Args:
            zone (str): Type of zone linked

        Returns:
            int: 1 for normal and priority
            2 for restricted
            0 for blocked or unknown type
        """
        match zone:
            case 'normal' | 'priority':
                return 1
            case 'restricted':
                return 2
            case _:
                return 0

    def calculate_next_step(
            self, from_hub: str, to_hub: str
            ) -> Tuple[str | None, float]:
        """This function executes Dijkstra's algorithm to get the next
        step of the shortest path possible to the goal hub.

        Args:
            from_hub (str): Starting hub
            to_hub (str): End goal hub

        Returns:
            Tuple[str, float] | None: Returns (hub_name, cost_to_end_goal)
            or None if there is no possible way to get to the end goal
        """
        # Check if start and destination are the same hub
        if from_hub == to_hub:
            return from_hub, 0

        # Keep track of the shortest path and distance to each hub
        parent: Dict[str, List[str]] = {}
        # Initialize distances to infinity, except for the starting hub
        dist: Dict[str, float] = {hub: float('inf') for hub in self.hubs}
        dist[from_hub] = 0

        visited: set[str] = set()

        # Use a priority queue to explore the graph
        # based on the shortest distance
        heap: List[Tuple[int, str]] = [(0, from_hub)]
        parent[from_hub] = []

        while heap:
            curr_dist, curr = heapq.heappop(heap)

            if curr in visited:
                continue

            if curr == to_hub:
                # Goal has been reached, return the next step in the path and
                # the total distance to the destination
                next_steps: List[str] = []
                frontier: List[str] = [curr]
                # Find the next available step in the path
                while frontier:
                    node = frontier.pop()

                    for p in parent[node]:
                        if p == from_hub:
                            next_steps.append(node)
                        else:
                            if p in frontier:
                                continue
                            frontier.append(p)

                for step in next_steps:
                    # Now we check link capacity and hub capacity
                    # for the next step
                    links = self.graph.get_neighbors(from_hub)
                    # Check if the neighbor link is at max flow
                    link_cap = links[step].max_link_capacity
                    link_occ = links[step].occupancy
                    if link_occ >= link_cap:
                        continue
                    # Check if neighbor hub has available capacity
                    nstep_hub = self.hubs[step]
                    nstep_occ = nstep_hub.current_drones
                    nstep_cap = nstep_hub.max_drones
                    if nstep_occ >= nstep_cap:
                        continue
                    return step, float(curr_dist)
                return (None, 0)

            visited.add(curr)

            for neighbor in self.graph.get_neighbors(curr):
                weight = self.get_weight(self.hubs[neighbor].zone)
                # Protect against blocked zones
                if weight < 1:
                    continue
                if neighbor in visited:
                    continue

                new_dist = curr_dist + weight
                if new_dist <= dist[neighbor]:
                    dist[neighbor] = new_dist
                    if parent.get(neighbor) is None:
                        parent[neighbor] = []
                    parent[neighbor].append(curr)
                    heapq.heappush(heap, (new_dist, neighbor))

        return (None, 0.0)

    def dispatch_drones(self) -> str:
        turn: int = 0
        schedule: str = ""
        moves_per_turn: int = 0
        first: bool = True
        self.turns_moves.append({})

        # Iterate while there is at least one drone that has not arrived
        # at its destination
        while any(drone.status != "arrived" for drone in self.drones):

            # 1 - Process drones traveling and arriving this turn
            for drone in self.drones:
                if drone.status == "traveling" and drone.arrival_time == turn:
                    moves_per_turn += 1
                    schedule += f"{drone.id}-{drone.traveling_to} "
                    # Drone has arrived at its destination
                    self.graph.update_link(
                        drone.waiting_at, drone.traveling_to, -1
                    )
                    drone.path.append(drone.traveling_to)
                    drone.waiting_at = drone.traveling_to
                    drone.traveling_to = ""
                    drone.deepness += 1
                    self.turns_moves[turn - 1][drone.id] = drone.waiting_at
                    if drone.waiting_at == "goal":
                        drone.status = "arrived"
                    else:
                        drone.status = "waiting"
            if first is True:
                first = False
            else:
                schedule += f"\033[32m<>\033[0m Moves: {moves_per_turn}\n"
            if all(drone.status == "arrived" for drone in self.drones):
                break
            moves_per_turn = 0
            # ideally this drones should be the ones that are deepest in
            # the network
            # Priotiry goes: Most deep in the network
            self.drones.sort(key=lambda d: d.deepness, reverse=True)

            # 2 - Start scheduling next turn arrivals
            # Process drones waiting at hubs and dispatch them
            for drone in self.drones:
                if drone.status == "waiting":
                    next_step, _ = self.calculate_next_step(
                        drone.waiting_at, "goal"
                    )
                    if next_step is None:
                        continue
                    # Next step is available, send the drone
                    step_cost = self.get_weight(self.hubs[next_step].zone)
                    self.hubs[drone.waiting_at].current_drones -= 1
                    # Update drone status and path cost
                    drone.status = "traveling"
                    drone.traveling_to = next_step
                    drone.total_path_cost += step_cost
                    drone.arrival_time = turn + step_cost
                    # Reserve link capacity and hub capacity
                    self.graph.update_link(
                            drone.waiting_at, next_step, 1
                        )
                    self.hubs[next_step].current_drones += 1
                    # Check link travel time equal to 2 turns
                    if step_cost > 1:
                        schedule += (
                            f"{drone.id}-{drone.waiting_at}-{next_step} "
                            )
                        self.turns_moves[turn][
                            drone.id] = f"{drone.waiting_at}-{next_step}"
                        drone.path.append(f"{drone.waiting_at}-{next_step}")
                        moves_per_turn += 1
                        drone.deepness += 1
            turn += 1
            self.turns_moves.append({})
        self.total_turns = turn
        return schedule

    def get_statistics(self) -> Dict[str, float]:
        stats: Dict[str, float] = {}
        # Total turns
        stats["total_turns"] = self.total_turns
        # Total path cost
        total_path_cost = reduce(
            lambda x, y: x + y,
            [d.total_path_cost for d in self.drones]
        )
        stats['total_path_cost'] = total_path_cost
        # Average turn cost per drone
        stats['avg_cost'] = total_path_cost / len(self.drones)

        return stats
