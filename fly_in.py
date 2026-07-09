#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   fly_in.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/02 09:41:14 by czuluaga            #+#    #+#            #
#   Updated: 2026/07/02 16:14:06 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from src.map_parser import parse_map_file, MapConfig
from src.network import Network
from src.visuals import visuals

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fly_in.py <input_file>")
        sys.exit(1)

    config: MapConfig = parse_map_file(sys.argv[1])
    # config: MapConfig = parse_map_file("maps/easy/01_linear_path.txt")
    # Execute Dijkstra to find best possible paths
    network: Network = Network(config)
    network.find_shortest_paths()

    # Execute drone dispatcher
    schedule: str = network.dispatch_drones()

    # Get dispatcher network statistics after dispatcher execution
    statistics = network.get_statistics()

    # Print results
    print("\033[34mNetwork Schedule\033[0m")
    print(schedule)
    print("\033[34mNetwork Statistics\033[0m")
    for k, v in statistics.items():
        print(f"{k}: {v}")

    # Display simulation
    visuals(network)
