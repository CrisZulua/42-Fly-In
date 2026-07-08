import pygame
from src.network import Network
from src.hubs import Hub
from typing import Dict, List, Tuple
from collections.abc import Callable


def create_coordinate_converter(
        nodes: List[Hub],
        width: int,
        height: int,
        margin: int = 100
        ) -> Callable:
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
        coord_converter: Callable
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
            (255, 255, 255)
        )

        screen.blit(
            text,
            coords
        )


def visuals(network: Network) -> None:
    # Initialize pygame
    pygame.init()

    font = pygame.font.Font(None, 24)

    # Create window
    WIDTH = 1920
    HEIGHT = 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Blue Screen")

    # Create coordinate converter
    coord_converter = create_coordinate_converter(
        [hub for hub in network.hubs.values()],
        WIDTH,
        HEIGHT
    )

    # Define colors (RGB)
    BACKGROUND = (25, 30, 45)

    # Game loop
    running = True
    clock = pygame.time.Clock()

    while running:

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw
        screen.fill(BACKGROUND)
        # Draw Objects
        draw_hubs(network.hubs, screen, font, coord_converter)
        # Update display
        pygame.display.flip()

        # Limit to 60 FPS
        clock.tick(60)

    # Cleanup
    pygame.quit()
    return
