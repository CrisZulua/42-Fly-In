import pygame
from src.network import Network
from src.hubs import Hub
from typing import Dict, List, Tuple
from collections.abc import Callable
import sys


def create_coordinate_converter(
        nodes: List[Hub],
        width: int,
        height: int,
        margin: int = 100
        ) -> Callable[[Tuple[int, int]], Tuple[int, int]]:
    """
    Creates a function that converts graph coordinates to pygame coordinates.

    Args:
        nodes: iterable of objects with .coords -> (x, y)
        width: pygame screen width
        height: pygame screen height
        margin: empty border around graph

    Returns:
        function converting (x, y) -> (screen_x, screen_y)
    """

    xs = [node.coords[0] for node in nodes]
    ys = [node.coords[1] for node in nodes]

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    graph_width = max_x - min_x
    graph_height = max_y - min_y

    if graph_width == 0:
        graph_width = 1

    if graph_height == 0:
        graph_height = 1

    # Scale graph to fit screen
    scale_x = (width - 2 * margin) / graph_width
    scale_y = (height - 2 * margin) / graph_height
    scale = min(scale_x, scale_y)

    # Graph center
    graph_center_x = (min_x + max_x) / 2
    graph_center_y = (min_y + max_y) / 2

    # Screen center
    screen_center_x = width / 2
    screen_center_y = height / 2

    def convert(coords: Tuple[int, int]) -> Tuple[int, int]:
        x, y = coords

        # Move graph center to screen center
        pygame_x = (
            screen_center_x +
            (x - graph_center_x) * scale
        )

        # Flip Y axis and center vertically
        pygame_y = (
            screen_center_y -
            (y - graph_center_y) * scale
        )

        return int(pygame_x), int(pygame_y)

    return convert


def color_from_string(color_name: str) -> Tuple[int, int, int]:
    """
    Converts a color name into an RGB tuple for pygame.
    """

    colors = {
        "blue":   (70, 130, 180),   # Steel blue
        "green":  (80, 200, 120),   # Soft green
        "red":    (220, 80, 80),    # Warm red
        "yellow": (240, 200, 70),   # Golden yellow
        "orange": (240, 140, 50),   # Orange
        "cyan":   (70, 210, 210),   # Aqua cyan
        "purple": (160, 100, 220),  # Soft purple
        "lime":    (150, 240, 80),  # Bright lime green
        "magenta": (220, 80, 200),  # Pink-purple
        "brown": (150, 100, 70),    # Brown
        "gold": (220, 180, 60)      # Gold
    }

    return colors.get(color_name.lower(), (180, 180, 180))


def draw_hubs(
        hubs: Dict[str, Hub],
        screen: pygame.Surface,
        font: pygame.font.Font,
        coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
        ) -> None:

    for name, hub in hubs.items():
        coords = coord_converter(hub.coords)
        color = color_from_string(hub.color)
        radius: float = 30
        if name not in ('start', 'goal'):
            radius *= (1 + hub.max_drones / 10)
        pygame.draw.circle(
            screen,
            color,
            coords,
            radius
        )

        text = font.render(
            name,
            True,
            (225, 225, 225)
        )

        screen.blit(
            text,
            (coords[0] - (radius / 2), coords[1] - 5)
        )


def draw_links(
        network: Network,
        screen: pygame.Surface,
        coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
        ) -> None:
    for name, hub in network.hubs.items():
        curr_coord = coord_converter(hub.coords)
        for neighbor, link in network.graph.get_neighbors(name).items():
            neighbor_coord = coord_converter(network.hubs[neighbor].coords)
            pygame.draw.line(
                screen,
                (180, 180, 180),
                curr_coord,
                neighbor_coord,
                4 * link.max_link_capacity
            )


def draw_drones(drones: Dict[str, str],
                hubs: Dict[str, Hub],
                screen: pygame.Surface,
                font: pygame.font.Font,
                coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
                ) -> None:
    for drone, node in drones.items():
        coord = coord_converter(hubs[node].coords)
        pygame.draw.circle(
            screen,
            (50, 50, 125),
            coord,
            10
        )

        text = font.render(
            drone,
            True,
            (255, 255, 255)
        )

        screen.blit(
            text,
            (coord[0] - 5, coord[1] - 2)
        )
    return


def visuals(network: Network) -> None:
    # Initialize pygame
    pygame.init()

    font = pygame.font.Font(None, 20)
    font.set_bold(True)
    drone_font = pygame.font.Font(None, 14)
    drone_font.set_bold(True)
    turn_font = pygame.font.Font(None, 36)
    turn_font.set_bold(True)

    # Create window
    WIDTH = 1920
    HEIGHT = 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Network for map "
                               f"{sys.argv[1].split('/', 1)[-1]}")

    # Define colors (RGB)
    BACKGROUND = (25, 30, 45)

    # Game loop
    running = True
    clock = pygame.time.Clock()

    # States Set-up
    # Create coordinate converter
    coord_converter = create_coordinate_converter(
        [hub for hub in network.hubs.values()],
        WIDTH,
        HEIGHT
    )

    # Drone states set-up
    drones: Dict[str, str] = {drone.id: 'start' for drone in network.drones}

    turn: int = 0

    while running:

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # update drones states
                    for drone, state in network.turns_moves[turn].items():
                        drones[drone] = state
                    turn += 1
                    if turn > network.total_turns:
                        for drone in drones:
                            drones[drone] = "start"
                            turn = 0
                if event.key == pygame.K_q:
                    running = False

        # Draw
        screen.fill(BACKGROUND)
        # Draw Objects
        draw_links(network, screen, coord_converter)
        draw_hubs(network.hubs, screen, font, coord_converter)
        draw_drones(drones, network.hubs, screen, drone_font, coord_converter)
        turn_text = turn_font.render(
            f"Turn: {turn}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            turn_text,
            (20, 20)
        )
        # Update display
        pygame.display.flip()

        # Limit to 60 FPS
        clock.tick(60)

    # Cleanup
    pygame.quit()
    return
