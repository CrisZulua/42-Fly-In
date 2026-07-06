#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   graph.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/02 10:01:17 by czuluaga            #+#    #+#            #
#   Updated: 2026/07/02 11:38:41 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Link:
    max_link_capacity: int
    occupancy: int


class Graph:
    def __init__(self, hubs: List[str]) -> None:
        self._graph: Dict[str, Dict[str, Link]] = {}
        for hub in hubs:
            self._graph[hub] = {}

    def add_neighbor(self, from_hub: str, to_hub: str, max_link: int) -> None:
        """Add a neighbor to a hub(Node). The neighbor is mirror as the
        connections are bidirectional.

        Args:
            from_hub (str): Connection from hub
            to_hub (str): Connection to hub
            max_link (int): Maximum link capacity. Meaning max drones that can
            travel through the connection simultaneously
        """
        link = Link(max_link_capacity=max_link, occupancy=0)
        self._graph[from_hub][to_hub] = link
        self._graph[to_hub][from_hub] = link

    def init_graph(self, conex: List[Tuple[str, str, int]]) -> None:
        """Initialize a graph from a list of connections following this
        structure: (from, to, max_link_capacity)

        Args:
            conex (List[Tuple[str, str, int]]): List of connections
        """
        for con in conex:
            self.add_neighbor(con[0], con[1], con[2])

    def get_neighbors(self, hub: str) -> Dict[str, Link]:
        """Get neighbors for a hub

        Args:
            hub (str): Check neighbors for this hub

        Returns:
            Dict[str, Link]: Dictionary containing neighbors
            and their respective link information
        """
        return self._graph[hub]
