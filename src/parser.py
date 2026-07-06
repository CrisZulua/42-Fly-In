#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/01 10:21:20 by czuluaga            #+#    #+#            #
#   Updated: 2026/07/02 15:58:05 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import List, Tuple, Dict
from dataclasses import dataclass
from src.hubs import Hub


@dataclass
class MapConfig:
    """Class containing all data related to a Map
    """
    nb_drones: int
    hubs: List[Hub]
    connections: List[Tuple[str, str, int]]


def load_map(file: str) -> List[Tuple[int, str]]:
    """Reads the 'file', ignores the comments and saves the file inside a list
    line by line.

    Args:
        file (str): Map file path

    Returns:
        List[Tuple[int, str]]: List of tuples containing the line number and
        the line content
    """
    map: List[Tuple[int, str]] = []

    try:
        with open(file, 'r') as f:
            for num, line in enumerate(f, 1):
                clean_line = line.split('#', 1)[0].strip()

                if not clean_line:
                    continue

                map.append((num, clean_line))
        return map
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")
        exit(1)


def get_nb_drones(line: str) -> int:
    """Gets the nb_drones value from line

    Args:
        line (str): Expected first line in map configuration file

    Raises:
        ValueError: If there is no nb_drones in the line

    Returns:
        int: nb_drones value
    """
    data = [ln.strip() for ln in line.split(':', 1)]
    if data[0] != 'nb_drones':
        raise ValueError("Line 1: First line is not properly set!")
    try:
        value = int(data[1])
        if value < 1:
            raise ValueError("nb_drones must be >= 1")
    except ValueError as e:
        raise Exception(f"Line 1: {e}")
    return value


def get_metadata(metadata: str) -> Dict[str, str]:
    """Gets the metadata for the correponding hub

    Args:
        metadata (str): metadata string: [zone=...]

    Raises:
        ValueError: If the argument for metadata its unknown

    Returns:
        dict[str, str]: Key, value pairs containing metadata
    """
    result: Dict[str, str] = {}

    metadata_tokens = metadata.split(' ', 3)

    for item in metadata_tokens:
        token = item.split('=')
        match token[0]:
            case 'zone':
                match token[1]:
                    case 'normal' | 'blocked' | 'restricted' | 'priority':
                        result['zone'] = token[1]
                    case _:
                        raise ValueError(f"Unknown zone argument: {token[1]}")
            case 'color':
                result['color'] = token[1]
            case 'max_drones':
                result['max_drones'] = token[1]
            case 'max_link_capacity':
                result['max_link_capacity'] = token[1]
            case _:
                raise ValueError(f"Unknown metadata argument: {token[0]}")
    return result


def validate_hubs(hubs: List[Hub]) -> None:
    """Extra validation for hubs. No repeated start or end
    or repeated coordinates.

    Args:
        hubs (List[Hub]): List of hubs

    Raises:
        ValueError: In case any invalid hub is encounteredº
    """
    # Check for only one entry start and end
    start_hubs = [hub for hub in hubs if hub.name == "start"]
    end_hubs = [hub
                for hub in hubs if hub.name in ("goal", "impossible_goal")]
    if len(start_hubs) != 1:
        raise ValueError("Invalid number of start hubs")
    if len(end_hubs) != 1:
        raise ValueError("Invalid number of end hubs")

    # Check for repeated coordinates
    coords_set: set[Tuple[int, int]] = set()
    for hub in hubs:
        if hub.coords in coords_set:
            raise ValueError(f"Duplicate coordinates found for hub {hub.name}")
        coords_set.add(hub.coords)
    return


def get_hubs_data(map: List[Tuple[int, str]]) -> List[Hub]:
    """Get hubs data. Name, coords and metadata from
    map configuration lines

    Args:
        map (List[Tuple[int, str]]): Map configuration file line by
        line with line numbers.

    Raises:
        ValueError: Whenever there is a format error with the line
        being read.

    Returns:
        List[Hub]: Returns a list of every hub in the Map congifuration
    """
    hubs: List[Hub] = []

    for num, line in map:
        if line.startswith(('start_hub', 'hub', 'end_hub')):
            line_data = line.split(':', 1)[1].strip()

            if not line_data:
                raise ValueError(f"Line {num}: "
                                 "Hub not properly configured!")

            data = line_data.split(" ", 3)
            if not data or (len(data) < 3):
                raise ValueError(f"Line {num}: "
                                 "Hub not properly configured!")

            name = data[0]
            if name.find('/') != -1 or name.find(' ') != -1:
                raise ValueError(f"Line {num}: "
                                 "Hub not properly configured! "
                                 "Name cannot contain '/' or ' '")
            try:
                coords = (int(data[1]), int(data[2]))
            except ValueError as e:
                raise ValueError(f"Line {num}: "
                                 f"Hub not properly configured! -> {e}")
            metadata_dict = {}
            if data[3] and len(data) > 3:
                if not data[3].endswith("]"):
                    raise ValueError(f"Line {num}: "
                                     "Hub not properly configured!")
                metadata = data[3].strip('[]')
                try:
                    metadata_dict = get_metadata(metadata)
                except ValueError as e:
                    raise ValueError(f"Line {num}: "
                                     f"Hub not properly configured! -> {e}")
            zone = str(metadata_dict.get('zone', 'normal'))
            color = str(metadata_dict.get('color', 'none'))
            try:
                max_drones = int(metadata_dict.get('max_drones', 1))
                if max_drones < 1:
                    raise ValueError("max_drones must be >= 1")
            except ValueError as e:
                raise ValueError(f"Line {num}: "
                                 f"Hub not properly configured! -> {e}")
            new_hub = Hub(
                name=name,
                coords=coords,
                zone=zone,
                color=color,
                max_drones=max_drones,
            )
            if new_hub in hubs:
                raise ValueError(f"Line {num}: "
                                 "Hub not properly configured! "
                                 "Hub already exists")
            hubs.append(new_hub)
    try:

        validate_hubs(hubs)
    except Exception as e:
        raise ValueError(f"Invalid hubs configuration: {e}")
    return hubs


def get_connections_data(
        map: List[Tuple[int, str]],
        hubs: List[Hub]
        ) -> List[Tuple[str, str, int]]:
    """Gets connections data from a Map configuration file previously read

    Args:
        map (List[Tuple[int, str]]): List of (num_line, line_content) tuples
        hubs (List[Hub]): List of hubs

    Raises:
        ValueError: Whenever there is a format error with the line being read.

    Returns:
        _type_: List of tuples containing the connection
        data (from_hub, to_hub, max_link_capacity)
    """
    conex_list: List[Tuple[str, str, int]] = []
    hub_names = [hub.name for hub in hubs]

    for num, line in map:
        if line.startswith("connection"):
            line_data = line.split(':', 1)[1].strip()

            if not line_data:
                raise ValueError(f"Line {num}: "
                                 "Connection not properly configured!")

            data = line_data.split(" ", 1)
            if not data or (len(data) < 1):
                raise ValueError(f"Line {num}: "
                                 "Connection not properly configured!")

            conx = data[0].split('-', 1)
            if not conx[0] in hub_names or not conx[0] in hub_names:
                raise ValueError(f"Line {num}: "
                                 "Connection from/to unknown hub"
                                 f" -> {data[0]}")

            metadata_dict = {}
            if len(data) > 1 and data[1]:
                if not data[1].endswith("]"):
                    raise ValueError(f"Line {num}: "
                                     "Connection not properly configured!")
                metadata = data[1].strip('[]')
                try:
                    metadata_dict = get_metadata(metadata)
                except ValueError as e:
                    raise ValueError(f"Line {num}: "
                                     f"Hub not properly configured! -> {e}")

            try:
                max_link_capacity = int(metadata_dict.get('max_link_capacity',
                                                          1))
                if max_link_capacity < 1:
                    raise ValueError("max_link_capacity must be >= 1")
            except ValueError as e:
                raise ValueError(f"Line {num}: "
                                 f"Connection not properly configured! -> {e}")
            new_conex = (
                conx[0],
                conx[1],
                max_link_capacity
                )

            if new_conex in conex_list:
                raise ValueError(f"Line {num}: "
                                 "Connection already exist!")
            # All connections are bidirectional,
            # if conex a-b exist we cannot register b-a as its the same
            # Check if the connection already exists in the list
            for conex in conex_list:
                if (conex[0] == new_conex[1] and conex[1] == new_conex[0]):
                    raise ValueError(f"Line {num}: "
                                     "Connection already exist!"
                                     f" - {new_conex[0]} <-> {new_conex[1]}")
            conex_list.append(new_conex)

    return conex_list


def parse_map_file(file: str) -> MapConfig:
    """Parses the Map configuration file given as argument

    Args:
        file (str): Path to Map configuration file

    Returns:
        MapConfig: Dataclass with three attributes: nb_drones,
        hubs, connections.
    """
    try:
        map = load_map(file)

        nb_drones = get_nb_drones(map[0][1])
        hubs = get_hubs_data(map)
        connections = get_connections_data(map, hubs)

        return MapConfig(
            nb_drones,
            hubs,
            connections
        )
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")
        exit(1)
