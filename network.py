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

from map_parser import MapConfig
from graph import Graph
from hubs import Hub
from typing import Dict, List, Tuple
from dataclasses import dataclass
from functools import reduce
import heapq


@dataclass
class Drone:
    """This class holds status data for a drone travelling
    through the network.
    """
    id: str
    status: str = "waiting"  # waiting, traveling, arrived
    waiting_at: str = "start"
    traveling_to: str = "goal"
    arrival_time: int = 1
    total_path_cost: float = 0
    # How deep is the drone in the network (number of hops taken)
    deepness: float = 0


class Network:
    """Manage data regarding a network.

    Attributes:
        drones (List[Drone]): List of Drone objects.
        graph (Graph): Graph structure (hubs names and connections).
        hubs (Dict[str, Hub]): Hub data for every hub in the graph.
        total_turns (int): Total number of turns until all drones arrive
            at goal.
        tuns_moves (List[Dict[str, str]]): Moves turn by turn.
        node parents (Dict[str, List[str]]): Relation of hubs from best
            paths.
    """
    def __init__(self, config: MapConfig) -> None:
        """Initiate an instance of Network object.

        Args:
            config (MapConfig): Configuration for the network.
        """
        # Init number of drones
        self.drones: List[Drone] = [
           Drone(id=f"D{i}")
           for i in range(1, config.nb_drones + 1)
        ]

        # Init graph structure
        self.graph: Graph = Graph([hub.name for hub in config.hubs])
        self.graph.init_graph(config.connections)

        # Init hubs data-holder
        self.hubs: Dict[str, Hub] = {hub.name: hub for hub in config.hubs}

        self.total_turns: int = 0

        self.turns_moves: List[Dict[str, str]] = []

        self.node_parents: Dict[str, List[str]] = {}

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

    def find_shortest_paths(self) -> None:
        """Executes Dijkstra's algorithm to find the best sorthest paths
        and populates node_parents attribute from the class.
        """
        from_hub = "start"
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
        self.node_parents = parent

    def calculate_next_step(
            self, from_hub: str
            ) -> str | None:
        """Calculates next step from_hub to the neighbors available.
        It uses node_parents to backtrack the path from end goal to
        the from_hub node.

        Then checks for its neighbors wich one has link capacity and node
        capacity.
        Args:
            from_hub (str): Node to travel from.

        Returns:
            str | None: Return the name of the next node if travel is
            available. None in case no travel available between nodes.
        """
        to_hub = "goal"
        # Check if start and destination are the same hub
        if from_hub == to_hub:
            return from_hub

        # Goal has been reached, return the next step in the path and
        # the total distance to the destination
        next_steps: List[str] = []
        frontier: List[str] = [to_hub]
        # Find the next available step in the path
        while frontier:
            node = frontier.pop()

            for parent in self.node_parents[node]:
                if parent == from_hub:
                    next_steps.append(node)
                else:
                    if parent in frontier:
                        continue
                    frontier.append(parent)

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
            return step
        return None

    def dispatch_drones(self) -> str:
        """Dispatch drones through the network calculating the best path
        each turn.

        It follows a discrete loop that stops when every drone arrives
        at end goal.

        Returns:
            str: All moves by turn. Each line corresponds to a turn.
        """
        turn: int = 0
        schedule: str = ""
        moves_per_turn: int = 0
        first: bool = True
        self.turns_moves.append({})
        self.find_shortest_paths()
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
                    next_step = self.calculate_next_step(
                        drone.waiting_at
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
                        moves_per_turn += 1
                        drone.deepness += 1
            turn += 1
            self.turns_moves.append({})
        self.total_turns = turn
        return schedule

    def get_statistics(self) -> Dict[str, float]:
        """Gets statistics from the simulation.

        It returns:
        - total_turns: Total of turns the simulation took to finish.
        - total_path_cost_: cost per drone summed.
        - avg_cost: average cost per drone

        Returns:
            Dict[str, float]: Stat name and its value.
        """
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
