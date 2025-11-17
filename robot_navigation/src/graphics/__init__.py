"""
Graphics module for 2D visualization of robot navigation simulation.

This module provides pure rendering functions and configuration for
graphical display while maintaining functional programming principles.

Core Components:
- config: Immutable rendering configuration
- colors: Color schemes and palettes
- rendering: Pure rendering functions (state → surface)
- ui_components: UI element rendering (pure functions)

Usage:
    from src.graphics import RenderConfig, ColorScheme, render_simulation_state

All rendering functions are pure - they create and return pygame surfaces
without modifying external state. I/O operations (display, events) are
isolated in the graphical runner application.
"""

from .config import RenderConfig, UILayout, calculate_ui_layout, update_config, adjust_speed, toggle_setting
from .colors import ColorScheme, DarkColorScheme, LightColorScheme, get_color_scheme, get_cell_color
from .rendering import (
    render_simulation_state,
    draw_maze_background,
    draw_path_trail,
    draw_robot,
    draw_sensor_readings,
    logical_to_screen,
    orientation_to_angle
)
from .ui_components import (
    render_metrics_panel,
    render_controls_panel,
    render_status_bar,
    render_title_bar,
    render_completion_overlay,
    render_strategy_selector
)

__all__ = [
    # Configuration
    'RenderConfig',
    'UILayout',
    'calculate_ui_layout',
    'update_config',
    'adjust_speed',
    'toggle_setting',

    # Colors
    'ColorScheme',
    'DarkColorScheme',
    'LightColorScheme',
    'get_color_scheme',
    'get_cell_color',

    # Rendering
    'render_simulation_state',
    'draw_maze_background',
    'draw_path_trail',
    'draw_robot',
    'draw_sensor_readings',
    'logical_to_screen',
    'orientation_to_angle',

    # UI Components
    'render_metrics_panel',
    'render_controls_panel',
    'render_status_bar',
    'render_title_bar',
    'render_completion_overlay',
    'render_strategy_selector',
]
