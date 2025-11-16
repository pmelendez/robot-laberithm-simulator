"""
Rendering configuration for graphical visualization.

All configuration classes are immutable to support functional programming principles.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class RenderConfig:
    """
    Immutable rendering configuration.

    Controls all aspects of graphical rendering including screen dimensions,
    cell sizes, animation speeds, and display toggles.
    """
    cell_size: int = 40                # Pixels per maze cell
    screen_width: int = 1024           # Screen width in pixels
    screen_height: int = 768           # Screen height in pixels
    fps: int = 60                      # Target frames per second
    animation_speed: float = 2.0       # Simulation steps per second
    show_path: bool = True             # Display path trail
    show_sensors: bool = True          # Display sensor readings
    show_grid: bool = True             # Display grid overlay
    show_metrics: bool = True          # Display metrics panel
    show_controls: bool = True         # Display controls help
    color_scheme: str = "default"      # Color scheme name
    ui_header_height: int = 50         # Height of top UI panel
    ui_footer_height: int = 40         # Height of bottom status bar
    robot_size_ratio: float = 0.7      # Robot size relative to cell
    trail_opacity: int = 150           # Path trail opacity (0-255)
    sensor_beam_width: int = 2         # Width of sensor beam lines


@dataclass(frozen=True)
class UILayout:
    """
    Immutable UI layout configuration.

    Defines positions and sizes of UI elements.
    """
    metrics_panel: Tuple[int, int, int, int]    # (x, y, width, height)
    controls_panel: Tuple[int, int, int, int]
    status_bar: Tuple[int, int, int, int]
    maze_viewport: Tuple[int, int, int, int]


def calculate_ui_layout(config: RenderConfig) -> UILayout:
    """
    Calculate UI layout from render configuration.

    PURE function.

    Args:
        config: Rendering configuration

    Returns:
        UILayout with calculated positions and sizes
    """
    # Status bar at bottom
    status_bar = (
        0,
        config.screen_height - config.ui_footer_height,
        config.screen_width,
        config.ui_footer_height
    )

    # Metrics panel in top-right corner
    metrics_width = 250
    metrics_height = config.ui_header_height + 100
    metrics_panel = (
        config.screen_width - metrics_width - 10,
        10,
        metrics_width,
        metrics_height
    )

    # Controls panel in top-left corner
    controls_width = 200
    controls_height = 150
    controls_panel = (
        10,
        10,
        controls_width,
        controls_height
    )

    # Maze viewport (central area)
    maze_viewport = (
        0,
        config.ui_header_height,
        config.screen_width,
        config.screen_height - config.ui_header_height - config.ui_footer_height
    )

    return UILayout(
        metrics_panel=metrics_panel,
        controls_panel=controls_panel,
        status_bar=status_bar,
        maze_viewport=maze_viewport
    )


def update_config(config: RenderConfig, **kwargs) -> RenderConfig:
    """
    Create a new configuration with updated values.

    PURE function - returns new instance.

    Args:
        config: Original configuration
        **kwargs: Values to update

    Returns:
        New RenderConfig with updated values
    """
    config_dict = {
        'cell_size': config.cell_size,
        'screen_width': config.screen_width,
        'screen_height': config.screen_height,
        'fps': config.fps,
        'animation_speed': config.animation_speed,
        'show_path': config.show_path,
        'show_sensors': config.show_sensors,
        'show_grid': config.show_grid,
        'show_metrics': config.show_metrics,
        'show_controls': config.show_controls,
        'color_scheme': config.color_scheme,
        'ui_header_height': config.ui_header_height,
        'ui_footer_height': config.ui_footer_height,
        'robot_size_ratio': config.robot_size_ratio,
        'trail_opacity': config.trail_opacity,
        'sensor_beam_width': config.sensor_beam_width,
    }
    config_dict.update(kwargs)
    return RenderConfig(**config_dict)


def adjust_speed(config: RenderConfig, factor: float) -> RenderConfig:
    """
    Adjust animation speed by a factor.

    PURE function.

    Args:
        config: Current configuration
        factor: Multiplier for speed (e.g., 2.0 doubles speed)

    Returns:
        New configuration with adjusted speed
    """
    new_speed = max(0.1, min(10.0, config.animation_speed * factor))
    return update_config(config, animation_speed=new_speed)


def toggle_setting(config: RenderConfig, setting: str) -> RenderConfig:
    """
    Toggle a boolean setting in the configuration.

    PURE function.

    Args:
        config: Current configuration
        setting: Name of boolean setting to toggle

    Returns:
        New configuration with toggled setting
    """
    if setting == 'path':
        return update_config(config, show_path=not config.show_path)
    elif setting == 'sensors':
        return update_config(config, show_sensors=not config.show_sensors)
    elif setting == 'grid':
        return update_config(config, show_grid=not config.show_grid)
    elif setting == 'metrics':
        return update_config(config, show_metrics=not config.show_metrics)
    elif setting == 'controls':
        return update_config(config, show_controls=not config.show_controls)
    else:
        return config
