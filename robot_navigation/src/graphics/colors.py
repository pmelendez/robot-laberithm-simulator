"""
Color schemes and palettes for visualization.

All color definitions are immutable to support functional programming principles.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ColorScheme:
    """
    Immutable color palette for rendering.

    All colors are RGB tuples (0-255 for each channel).
    """
    background: Tuple[int, int, int] = (40, 40, 40)
    wall: Tuple[int, int, int] = (80, 80, 80)
    path: Tuple[int, int, int] = (200, 200, 200)
    robot: Tuple[int, int, int] = (100, 150, 255)
    robot_direction: Tuple[int, int, int] = (255, 255, 100)
    start: Tuple[int, int, int] = (100, 255, 100)
    exit: Tuple[int, int, int] = (255, 100, 100)
    trail: Tuple[int, int, int] = (150, 150, 200)
    trail_recent: Tuple[int, int, int] = (180, 180, 220)
    sensor_clear: Tuple[int, int, int] = (100, 255, 100)
    sensor_blocked: Tuple[int, int, int] = (255, 100, 100)
    sensor_beam: Tuple[int, int, int] = (100, 200, 255)
    ui_text: Tuple[int, int, int] = (255, 255, 255)
    ui_background: Tuple[int, int, int] = (30, 30, 30)
    ui_panel: Tuple[int, int, int] = (50, 50, 50)
    grid_line: Tuple[int, int, int] = (60, 60, 60)


@dataclass(frozen=True)
class DarkColorScheme:
    """Dark theme color palette."""
    background: Tuple[int, int, int] = (20, 20, 25)
    wall: Tuple[int, int, int] = (60, 60, 70)
    path: Tuple[int, int, int] = (180, 180, 190)
    robot: Tuple[int, int, int] = (80, 120, 200)
    robot_direction: Tuple[int, int, int] = (220, 220, 80)
    start: Tuple[int, int, int] = (80, 200, 80)
    exit: Tuple[int, int, int] = (200, 80, 80)
    trail: Tuple[int, int, int] = (120, 120, 160)
    trail_recent: Tuple[int, int, int] = (150, 150, 180)
    sensor_clear: Tuple[int, int, int] = (80, 200, 80)
    sensor_blocked: Tuple[int, int, int] = (200, 80, 80)
    sensor_beam: Tuple[int, int, int] = (80, 160, 200)
    ui_text: Tuple[int, int, int] = (220, 220, 220)
    ui_background: Tuple[int, int, int] = (15, 15, 20)
    ui_panel: Tuple[int, int, int] = (35, 35, 40)
    grid_line: Tuple[int, int, int] = (40, 40, 50)


@dataclass(frozen=True)
class LightColorScheme:
    """Light theme color palette."""
    background: Tuple[int, int, int] = (240, 240, 245)
    wall: Tuple[int, int, int] = (100, 100, 110)
    path: Tuple[int, int, int] = (255, 255, 255)
    robot: Tuple[int, int, int] = (50, 100, 200)
    robot_direction: Tuple[int, int, int] = (255, 200, 0)
    start: Tuple[int, int, int] = (50, 180, 50)
    exit: Tuple[int, int, int] = (200, 50, 50)
    trail: Tuple[int, int, int] = (150, 150, 200)
    trail_recent: Tuple[int, int, int] = (120, 120, 180)
    sensor_clear: Tuple[int, int, int] = (50, 200, 50)
    sensor_blocked: Tuple[int, int, int] = (200, 50, 50)
    sensor_beam: Tuple[int, int, int] = (50, 150, 220)
    ui_text: Tuple[int, int, int] = (20, 20, 20)
    ui_background: Tuple[int, int, int] = (220, 220, 225)
    ui_panel: Tuple[int, int, int] = (200, 200, 210)
    grid_line: Tuple[int, int, int] = (180, 180, 190)


# Color scheme registry
COLOR_SCHEMES = {
    'default': ColorScheme(),
    'dark': DarkColorScheme(),
    'light': LightColorScheme(),
}


def get_color_scheme(name: str = 'default') -> ColorScheme:
    """
    Get a color scheme by name.

    PURE function.

    Args:
        name: Color scheme name ('default', 'dark', 'light')

    Returns:
        ColorScheme instance
    """
    return COLOR_SCHEMES.get(name, ColorScheme())


def get_cell_color(cell_char: str, colors: ColorScheme) -> Tuple[int, int, int]:
    """
    Get color for a maze cell character.

    PURE function.

    Args:
        cell_char: Character representing cell type ('#', '.', 'S', 'E')
        colors: Color scheme to use

    Returns:
        RGB tuple for the cell
    """
    if cell_char == '#':
        return colors.wall
    elif cell_char == '.':
        return colors.path
    elif cell_char == 'S':
        return colors.start
    elif cell_char == 'E':
        return colors.exit
    else:
        return colors.path
