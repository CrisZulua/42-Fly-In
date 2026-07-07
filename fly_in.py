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
from src.parser import parse_map_file, MapConfig
from src.network import Network

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fly_in.py <input_file>")
        sys.exit(1)

    config: MapConfig = parse_map_file(sys.argv[1])
    network: Network = Network(config)
    print(network.dispatch_drones())
