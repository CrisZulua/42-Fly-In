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
    """Class containing link data:

    Attributes:
        max_link_capacity (int): Link capacity
        occupancy (Link): Drones in link
    """
    max_link_capacity: int
    occupancy: int


class Graph:
    """This class contains data for a Graph. The data is provided as a list
    of hub names.

    Attributes:
        _graph (Dict[str, Dict[str, Link]]): Each node has a dictionary
        containing all of its neighbors and their link state.
    """

    def __init__(self, hubs: List[str]) -> None:
        """Initiate an instance of the Graph class

        This class contains an attribute called _graph which is a dictionary.
        Each keay is a node an its value is a dictionary with each neighbor
        node and a Link object describing state of that connection.

        Args:
            hubs (List[str]): Hub names for all hubs for a graph
        """
        self._graph: Dict[str, Dict[str, Link]] = {}
        for hub in hubs:
            self._graph[hub] = {}

    def add_neighbor(self, from_hub: str, to_hub: str, max_link: int) -> None:
        """Add a neighbor to a hub(Node). The neighbor is mirror as the
        connections are bidirectional.

        Both connections share the same link object so its updated for both
        whenever a connection is updated.

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
        structure: (from, to, max_link_capacity).

        Before calling this function the Graph instance contains all hubs
        names, now is time to connect them.

        Args:
            conex (List[Tuple[str, str, int]]): List of connections
        """
        for con in conex:
            self.add_neighbor(con[0], con[1], con[2])

    def get_neighbors(self, hub: str) -> Dict[str, Link]:
        """Get all neighbors for a hub

        Args:
            hub (str): Check neighbors for this hub

        Returns:
            Dict[str, Link]: Dictionary containing neighbors
            and their respective link information
        """
        return self._graph[hub]

    def update_link(self, from_hub: str, to_hub: str, occupancy_change: int
                    ) -> None:
        """Update the occupancy of a link between two hubs.

        Args:
            from_hub (str): The starting hub of the link.
            to_hub (str): The destination hub of the link.
            occupancy_change (int): The change in occupancy
            (positive or negative).
        """
        if to_hub in self._graph[from_hub]:
            link = self._graph[from_hub][to_hub]
            link.occupancy += occupancy_change
