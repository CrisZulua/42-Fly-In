#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   hubs.py                                              :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/02 10:07:08 by czuluaga            #+#    #+#            #
#   Updated: 2026/07/02 11:32:41 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Hub:
    """Class that holds information for a hub
    name: str
    coords: Tuple[int, int]
    zone: str = 'normal'
    color: str = 'none'
    max_drones: int = 1
    current_drones: int = 0
    """
    name: str
    coords: Tuple[int, int]  # (x, y)
    zone: str = 'normal'
    color: str = 'none'
    max_drones: int = 1
    current_drones: int = 0
