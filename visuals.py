from network import Network
from hubs import Hub
from typing import Dict, List, Tuple
from collections.abc import Callable
import sys
import os
try:
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
except ImportError as e:
    print(f"{e.__class__.__name__}: {e}")
    print(" Please install the modules needed via 'make install'\n"
          " Use of virtual environment is recommended")
    exit(1)


def create_coordinate_converter(
        nodes: List[Hub],
        width: int,
        height: int,
        margin: int = 100
        ) -> Callable[[Tuple[int, int]], Tuple[int, int]]:
    """
    Creates a function that converts graph coordinates to pygame coordinates.

    Args:
        nodes (List[Hub]): iterable of Hub objects with .coords -> (x, y)
        width (int): pygame screen width
        height (int): pygame screen height
        margin (int): empty border around graph. Default value is 100

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
    """Converts a color name into an RGB tuple for pygame.

    Args:
        color_name (str): Color name

    Returns:
        Tuple[int, int, int]: RGB values.
    """

    colors = {
        "blue":    (60, 120, 200),    # Clean dashboard blue
        "green":   (70, 190, 110),    # Balanced green
        "red":     (210, 70, 80),     # Alert red
        "yellow":  (230, 190, 50),    # Warm yellow
        "orange":  (235, 125, 40),    # Strong orange
        "cyan":    (50, 190, 200),    # Technical cyan
        "purple":  (145, 85, 210),    # Deep purple
        "lime":    (140, 220, 70),    # Bright lime
        "magenta": (210, 70, 190),    # Strong magenta
        "brown":   (150, 95, 60),     # Earth brown
        "gold":    (220, 170, 40),    # Metallic gold
        "black":   (35, 35, 45),      # Soft black
        "maroon":  (150, 45, 70),     # Deep red-purple
        "darkred": (160, 45, 55),     # Dark restricted-zone red
        "violet":  (120, 80, 200),    # Rich violet
        "crimson": (190, 50, 90),     # Strong crimson
        "rainbow": (255, 120, 220),   # Special goal color
    }

    return colors.get(color_name.lower(), (180, 180, 180))


def draw_hubs(
        hubs: Dict[str, Hub],
        screen: pygame.surface.Surface,
        font: pygame.font.Font,
        coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
        ) -> None:
    """Draw hubs on canvas. Size and color varies depending on hub data.

    Args:
        hubs (Dict[str, Hub]): All hubs in the graph
        screen (pygame.Surface): Surface object on which to draw
        font (pygame.font.Font): Font object for hub names
        coord_converter (Callable[[Tuple[int, int]], Tuple[int, int]]):
            Function to convert original hub coordinates into pygame
            valid coordinates.
    """
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
            (245, 245, 245)
        )

        screen.blit(
            text,
            (coords[0] - (radius / 2), coords[1] - 5)
        )


def draw_links(
        network: Network,
        screen: pygame.surface.Surface,
        coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
        ) -> None:
    """Draw links between hubs.

    Args:
        network (Network): Network object
        screen (pygame.Surface): Surface object on which to paint
        coord_converter (Callable[[Tuple[int, int]], Tuple[int, int]]):
            Function to convert original hub coordinates into pygame
            valid coordinates.
    """
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
                screen: pygame.surface.Surface,
                font: pygame.font.Font,
                coord_converter: Callable[[Tuple[int, int]], Tuple[int, int]]
                ) -> None:
    """Draw drones on canvas.

    Args:
        drones (Dict[str, str]): Drone and its location.
        hubs (Dict[str, Hub]): Hubs in the graph
        screen (pygame.Surface): Surface object on which to paint
        font (pygame.font.Font): Font object for drone data
        coord_converter (Callable[[Tuple[int, int]], Tuple[int, int]]):
            Function to convert original hub coordinates into pygame
            valid coordinates.
    """
    x_offset_positions: Dict[str, int] = {}
    y_offset_positions: Dict[str, int] = {}

    for drone, node in drones.items():

        if node not in x_offset_positions:
            x_offset_positions[node] = 0
        if node not in y_offset_positions:
            y_offset_positions[node] = 0

        if x_offset_positions[node] < -2:
            y_offset_positions[node] -= 1
            x_offset_positions[node] = 0

        offset = (x_offset_positions[node],
                  y_offset_positions[node])

        coord = (0, 0)
        # Check if drone goes in link
        if '-' in node:
            link = node.split('-', 1)
            from_node = coord_converter(hubs[link[0]].coords)
            to_node = coord_converter(hubs[link[1]].coords)
            # Get middle point
            coord = ((to_node[0] + from_node[0]) // 2,
                     (to_node[1] + from_node[1]) // 2)
        else:
            coord = coord_converter(hubs[node].coords)

        pygame.draw.circle(
            screen,
            (55, 65, 90),
            (coord[0] + offset[0] * 20,
             coord[1] + offset[1] * 20),
            10
        )

        text = font.render(
            drone,
            True,
            (230, 230, 230)
        )

        screen.blit(
            text,
            (coord[0] - 5 + offset[0] * 20,
             coord[1] - 2 + offset[1] * 20)
        )

        x_offset_positions[node] -= 1
    return


def visuals(network: Network) -> None:
    """Main loop for pygame.

    Args:
        network (Network): Network object
    """
    # Initialize pygame
    pygame.init()

    font = pygame.font.Font(None, 20)
    font.set_bold(True)
    drone_font = pygame.font.Font(None, 14)
    drone_font.set_bold(True)
    turn_font = pygame.font.Font(None, 36)
    turn_font.set_bold(True)
    info_font = pygame.font.Font(None, 24)

    # Create window
    WIDTH = 1920
    HEIGHT = 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Network for map "
                               f"{sys.argv[1].split('/', 1)[-1]}")

    # Define colors (RGB)
    BACKGROUND = (18, 24, 38)

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
            (210, 220, 235)
        )

        screen.blit(
            turn_text,
            (20, 20)
        )

        info_text = info_font.render(
            "Space bar -> Next turn",
            True,
            (110, 120, 135)
        )

        screen.blit(
            info_text,
            (20, 60)
        )

        info_text = info_font.render(
            "q -> Quit simulation",
            True,
            (110, 120, 135)
        )

        screen.blit(
            info_text,
            (20, 80)
        )
        # Update display
        pygame.display.flip()

        # Limit to 60 FPS
        clock.tick(60)

    # Cleanup
    pygame.quit()
    return
