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
        match zone:
            case 'normal' | 'priority':
                return 1
            case 'restricted':
                return 2
            case _:
                return 0

    def calculate_costs(
            self, from_hub: str, to_hub: str
            ) -> Dict[str, float]:

        dist: Dict[str, float] = {hub: float('inf') for hub in self.hubs}
        dist[from_hub] = 0

        visited: set[str] = set()

        heap: List[Tuple[int, str]] = [(0, from_hub)]

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
                new_dist = curr_dist + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))

        return dist

    def dispatch_drones(self) -> None:

        return
