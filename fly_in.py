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
    print(config.hubs)
    print(config.connections)
    network: Network = Network(config)

    schedule: str = network.dispatch_drones()
    statistics = network.get_statistics()

    print("\033[34mNetwork Schedule\033[0m")
    print(schedule)
    print("\033[34mNetwork Statistics\033[0m")
    for k, v in statistics.items():
        print(f"{k}: {v}")

    visuals(network)
