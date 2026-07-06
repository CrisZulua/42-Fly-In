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
import heapq


class Network:
    def __init__(self, config: MapConfig) -> None:
        # Init number of drones
        self.nb_drones: int = config.nb_drones

        # Init graph structure
        self.graph: Graph = Graph([hub.name for hub in config.hubs])
        self.graph.init_graph(config.connections)

        # Init hubs data-holder
        self.hubs: Dict[str, Hub] = {hub.name: hub for hub in config.hubs}

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
            ) -> Tuple[str, float] | None:
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
        parent: Dict[str, str | None] = {}
        # Initialize distances to infinity, except for the starting hub
        dist: Dict[str, float] = {hub: float('inf') for hub in self.hubs}
        dist[from_hub] = 0

        visited: set[str] = set()

        # Use a priority queue to explore the graph
        # based on the shortest distance
        heap: List[Tuple[int, str]] = [(0, from_hub)]
        parent[from_hub] = None

        while heap:
            curr_dist, curr = heapq.heappop(heap)

            if curr in visited:
                continue

            if curr == to_hub:
                # Goal has been reached, return the next step in the path and
                # the total distance to the destination
                path: List[str] = []
                aux: str | None = curr
                # Backtrack to find the next step in the path
                while aux is not None:
                    path.append(aux)
                    aux = parent[aux]
                path.reverse()
                next_step = path[1]
                print(path)
                return next_step, float(curr_dist)

            visited.add(curr)
            curr_neighbors = self.graph.get_neighbors(curr)

            for neighbor in self.graph.get_neighbors(curr):
                weight = self.get_weight(self.hubs[neighbor].zone)
                # Protect against blocked zones
                if weight < 1:
                    continue
                # Check if the neighbor link is at max flow
                link_cap = curr_neighbors[neighbor].max_link_capacity
                link_occ = curr_neighbors[neighbor].occupancy
                if link_occ >= link_cap:
                    continue
                # Check if neighbor hub has available capacity
                nbor_hub = self.hubs[neighbor]
                nbor_occ = nbor_hub.current_drones
                nbor_cap = nbor_hub.max_drones
                if nbor_occ >= nbor_cap:
                    continue

                new_dist = curr_dist + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    parent[neighbor] = curr
                    heapq.heappush(heap, (new_dist, neighbor))

        return None

    def dispatch_drones(self) -> None:

        return
