"""
Pure rendering functions for graphical visualization.

All functions in this module are pure - they create and return surfaces
without modifying external state. This maintains functional programming principles.
"""
import pygame
import math
from typing import Tuple, List
from ..types import Maze, Robot, SimulationState, SensorReading
from .config import RenderConfig, UILayout
from .colors import ColorScheme, get_cell_color


def logical_to_screen(
    logical_pos: Tuple[int, int],
    maze_dimensions: Tuple[int, int],
    config: RenderConfig,
    layout: UILayout
) -> Tuple[int, int]:
    """
    Convert maze coordinates to screen pixels.

    PURE function - deterministic coordinate transformation.

    Args:
        logical_pos: (x, y) position in maze coordinates
        maze_dimensions: (width, height) of maze
        config: Rendering configuration
        layout: UI layout

    Returns:
        (x, y) position in screen coordinates
    """
    x, y = logical_pos
    maze_width, maze_height = maze_dimensions

    # Calculate maze pixel dimensions
    maze_pixel_width = maze_width * config.cell_size
    maze_pixel_height = maze_height * config.cell_size

    # Get viewport area
    viewport_x, viewport_y, viewport_width, viewport_height = layout.maze_viewport

    # Center maze in viewport
    offset_x = viewport_x + (viewport_width - maze_pixel_width) // 2
    offset_y = viewport_y + (viewport_height - maze_pixel_height) // 2

    screen_x = offset_x + x * config.cell_size
    screen_y = offset_y + y * config.cell_size

    return (screen_x, screen_y)


def orientation_to_angle(orientation: str) -> float:
    """
    Convert orientation string to angle in degrees.

    PURE function.

    Args:
        orientation: 'N', 'E', 'S', or 'W'

    Returns:
        Angle in degrees (0 = East, 90 = North, etc.)
    """
    angles = {
        'N': 90.0,
        'E': 0.0,
        'S': 270.0,
        'W': 180.0
    }
    return angles.get(orientation, 0.0)


def draw_maze_background(
    maze: Maze,
    config: RenderConfig,
    colors: ColorScheme,
    layout: UILayout
) -> pygame.Surface:
    """
    Draw the maze background with walls and paths.

    PURE function - creates surface from maze data.

    Args:
        maze: Maze configuration
        config: Rendering configuration
        colors: Color scheme
        layout: UI layout

    Returns:
        Surface with maze background
    """
    surface = pygame.Surface((config.screen_width, config.screen_height))
    surface.fill(colors.background)

    # Draw each cell
    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            screen_pos = logical_to_screen((x, y), maze.dimensions, config, layout)
            cell_color = get_cell_color(cell, colors)

            # Draw cell
            rect = pygame.Rect(
                screen_pos[0],
                screen_pos[1],
                config.cell_size,
                config.cell_size
            )
            pygame.draw.rect(surface, cell_color, rect)

            # Draw grid lines if enabled
            if config.show_grid:
                pygame.draw.rect(surface, colors.grid_line, rect, 1)

    return surface


def draw_path_trail(
    robot: Robot,
    maze: Maze,
    config: RenderConfig,
    colors: ColorScheme,
    layout: UILayout
) -> pygame.Surface:
    """
    Draw the robot's path trail.

    PURE function - creates surface with path visualization.

    Args:
        robot: Robot state with path history
        maze: Maze configuration
        config: Rendering configuration
        colors: Color scheme
        layout: UI layout

    Returns:
        Transparent surface with path trail
    """
    if not config.show_path or len(robot.path_history) < 2:
        return pygame.Surface((config.screen_width, config.screen_height), pygame.SRCALPHA)

    surface = pygame.Surface((config.screen_width, config.screen_height), pygame.SRCALPHA)

    # Draw path as circles and lines
    path_length = len(robot.path_history)

    for i in range(path_length):
        pos = robot.path_history[i]
        screen_pos = logical_to_screen(pos, maze.dimensions, config, layout)

        # Calculate opacity based on age (newer = brighter)
        age_ratio = i / max(1, path_length - 1)
        if i == path_length - 1:
            # Current position - brightest
            color = colors.trail_recent
            opacity = 255
        elif age_ratio > 0.7:
            # Recent positions
            color = colors.trail_recent
            opacity = int(config.trail_opacity * (0.5 + 0.5 * age_ratio))
        else:
            # Older positions
            color = colors.trail
            opacity = int(config.trail_opacity * age_ratio * 0.8)

        # Create color with opacity
        color_with_alpha = (*color, opacity)

        # Draw circle at position
        center = (
            screen_pos[0] + config.cell_size // 2,
            screen_pos[1] + config.cell_size // 2
        )
        radius = max(2, config.cell_size // 8)
        pygame.draw.circle(surface, color_with_alpha, center, radius)

        # Draw line to next position
        if i < path_length - 1:
            next_pos = robot.path_history[i + 1]
            next_screen_pos = logical_to_screen(next_pos, maze.dimensions, config, layout)
            next_center = (
                next_screen_pos[0] + config.cell_size // 2,
                next_screen_pos[1] + config.cell_size // 2
            )
            pygame.draw.line(surface, color_with_alpha, center, next_center, 2)

    return surface


def draw_robot(
    robot: Robot,
    maze: Maze,
    config: RenderConfig,
    colors: ColorScheme,
    layout: UILayout
) -> pygame.Surface:
    """
    Draw the robot with orientation indicator.

    PURE function - creates surface with robot visualization.

    Args:
        robot: Robot state
        maze: Maze configuration
        config: Rendering configuration
        colors: Color scheme
        layout: UI layout

    Returns:
        Transparent surface with robot
    """
    surface = pygame.Surface((config.screen_width, config.screen_height), pygame.SRCALPHA)

    screen_pos = logical_to_screen(robot.position, maze.dimensions, config, layout)
    center = (
        screen_pos[0] + config.cell_size // 2,
        screen_pos[1] + config.cell_size // 2
    )

    # Draw robot body (circle)
    robot_radius = int(config.cell_size * config.robot_size_ratio / 2)
    pygame.draw.circle(surface, colors.robot, center, robot_radius)
    pygame.draw.circle(surface, colors.ui_text, center, robot_radius, 2)

    # Draw orientation indicator (triangle/arrow)
    angle = orientation_to_angle(robot.orientation)
    angle_rad = math.radians(angle)

    # Calculate arrow points
    arrow_length = robot_radius * 0.8
    arrow_width = robot_radius * 0.4

    # Front point
    front_x = center[0] + arrow_length * math.cos(angle_rad)
    front_y = center[1] - arrow_length * math.sin(angle_rad)

    # Side points
    left_angle = angle_rad + math.radians(150)
    right_angle = angle_rad - math.radians(150)

    left_x = center[0] + arrow_width * math.cos(left_angle)
    left_y = center[1] - arrow_width * math.sin(left_angle)

    right_x = center[0] + arrow_width * math.cos(right_angle)
    right_y = center[1] - arrow_width * math.sin(right_angle)

    # Draw triangle
    points = [(front_x, front_y), (left_x, left_y), (right_x, right_y)]
    pygame.draw.polygon(surface, colors.robot_direction, points)
    pygame.draw.polygon(surface, colors.ui_text, points, 2)

    return surface


def draw_sensor_readings(
    robot: Robot,
    sensor_readings: List[SensorReading],
    maze: Maze,
    config: RenderConfig,
    colors: ColorScheme,
    layout: UILayout
) -> pygame.Surface:
    """
    Draw sensor reading visualizations.

    PURE function - creates surface with sensor data visualization.

    Args:
        robot: Robot state
        sensor_readings: List of sensor readings
        maze: Maze configuration
        config: Rendering configuration
        colors: Color scheme
        layout: UI layout

    Returns:
        Transparent surface with sensor visualizations
    """
    if not config.show_sensors:
        return pygame.Surface((config.screen_width, config.screen_height), pygame.SRCALPHA)

    surface = pygame.Surface((config.screen_width, config.screen_height), pygame.SRCALPHA)

    screen_pos = logical_to_screen(robot.position, maze.dimensions, config, layout)
    center = (
        screen_pos[0] + config.cell_size // 2,
        screen_pos[1] + config.cell_size // 2
    )

    # Direction to angle mapping
    direction_angles = {
        'front': orientation_to_angle(robot.orientation),
        'back': orientation_to_angle(robot.orientation) + 180,
        'left': orientation_to_angle(robot.orientation) + 90,
        'right': orientation_to_angle(robot.orientation) - 90,
    }

    for reading in sensor_readings:
        if reading.sensor_type == 'ultrasound':
            # Get direction angle
            angle = direction_angles.get(reading.direction, 0.0)
            angle_rad = math.radians(angle)

            # Calculate beam end point
            distance = reading.value if isinstance(reading.value, (int, float)) else 0
            beam_length = min(distance * config.cell_size, config.cell_size * 10)

            end_x = center[0] + beam_length * math.cos(angle_rad)
            end_y = center[1] - beam_length * math.sin(angle_rad)

            # Color based on distance
            if distance < 2:
                beam_color = colors.sensor_blocked
            else:
                beam_color = colors.sensor_beam

            # Draw beam
            beam_color_alpha = (*beam_color, 150)
            pygame.draw.line(surface, beam_color_alpha, center, (end_x, end_y), config.sensor_beam_width)

            # Draw endpoint circle
            pygame.draw.circle(surface, beam_color_alpha, (int(end_x), int(end_y)), 4)

        elif reading.sensor_type == 'infrared':
            # Draw indicator light
            angle = direction_angles.get(reading.direction, 0.0)
            angle_rad = math.radians(angle)

            indicator_distance = config.cell_size * 0.6
            indicator_x = center[0] + indicator_distance * math.cos(angle_rad)
            indicator_y = center[1] - indicator_distance * math.sin(angle_rad)

            # Color based on reading
            if reading.value:
                indicator_color = colors.sensor_blocked
            else:
                indicator_color = colors.sensor_clear

            indicator_color_alpha = (*indicator_color, 200)
            pygame.draw.circle(surface, indicator_color_alpha, (int(indicator_x), int(indicator_y)), 6)

    return surface


def render_simulation_state(
    state: SimulationState,
    sensor_readings: List[SensorReading],
    config: RenderConfig,
    colors: ColorScheme,
    layout: UILayout
) -> pygame.Surface:
    """
    Render complete simulation state to a surface.

    PURE function - combines all rendering layers.

    Args:
        state: Current simulation state
        sensor_readings: Current sensor readings
        config: Rendering configuration
        colors: Color scheme
        layout: UI layout

    Returns:
        Complete rendered surface
    """
    # Create base surface
    surface = pygame.Surface((config.screen_width, config.screen_height))
    surface.fill(colors.background)

    # Layer 1: Maze background
    maze_surface = draw_maze_background(state.maze, config, colors, layout)
    surface.blit(maze_surface, (0, 0))

    # Layer 2: Path trail
    trail_surface = draw_path_trail(state.robot, state.maze, config, colors, layout)
    surface.blit(trail_surface, (0, 0))

    # Layer 3: Sensor readings
    sensor_surface = draw_sensor_readings(
        state.robot,
        sensor_readings,
        state.maze,
        config,
        colors,
        layout
    )
    surface.blit(sensor_surface, (0, 0))

    # Layer 4: Robot
    robot_surface = draw_robot(state.robot, state.maze, config, colors, layout)
    surface.blit(robot_surface, (0, 0))

    return surface
