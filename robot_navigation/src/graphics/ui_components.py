"""
UI component rendering functions.

All rendering functions are pure - they create and return pygame surfaces
without modifying external state.
"""
import pygame
from typing import Dict, Any, Tuple
from .config import UILayout, RenderConfig
from .colors import ColorScheme


def render_metrics_panel(
    metrics: Dict[str, Any],
    layout: UILayout,
    colors: ColorScheme,
    config: RenderConfig
) -> pygame.Surface:
    """
    Render metrics display panel.

    PURE function - creates surface from metrics data.

    Args:
        metrics: Simulation metrics dictionary
        layout: UI layout configuration
        colors: Color scheme
        config: Render configuration

    Returns:
        Surface with metrics display
    """
    x, y, width, height = layout.metrics_panel
    surface = pygame.Surface((width, height))
    surface.fill(colors.ui_panel)

    # Draw border
    pygame.draw.rect(surface, colors.ui_text, (0, 0, width, height), 2)

    # Setup font
    try:
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 28)
    except:
        font = pygame.font.SysFont('monospace', 20)
        title_font = pygame.font.SysFont('monospace', 24)

    # Title
    title_text = title_font.render("METRICS", True, colors.ui_text)
    surface.blit(title_text, (10, 10))

    # Metrics text
    y_offset = 45
    line_height = 25

    metrics_display = [
        f"Steps: {metrics.get('total_steps', 0)}",
        f"Unique: {metrics.get('unique_positions', 0)}",
        f"Backtracks: {metrics.get('backtrack_count', 0)}",
        f"Collisions: {metrics.get('collisions', 0)}",
    ]

    if metrics.get('completed', False):
        metrics_display.append("Status: COMPLETE!")

    for line in metrics_display:
        text = font.render(line, True, colors.ui_text)
        surface.blit(text, (10, y_offset))
        y_offset += line_height

    return surface


def render_controls_panel(
    layout: UILayout,
    colors: ColorScheme,
    config: RenderConfig,
    paused: bool
) -> pygame.Surface:
    """
    Render controls help panel.

    PURE function - creates surface with control instructions.

    Args:
        layout: UI layout configuration
        colors: Color scheme
        config: Render configuration
        paused: Whether simulation is paused

    Returns:
        Surface with controls display
    """
    x, y, width, height = layout.controls_panel
    surface = pygame.Surface((width, height))
    surface.fill(colors.ui_panel)

    # Draw border
    pygame.draw.rect(surface, colors.ui_text, (0, 0, width, height), 2)

    # Setup font
    try:
        font = pygame.font.Font(None, 20)
    except:
        font = pygame.font.SysFont('monospace', 16)

    # Controls text
    controls = [
        "CONTROLS",
        "SPACE - Play/Pause",
        "ENTER - Step",
        "+/-   - Speed",
        "P/S/G - Toggles",
        "ESC   - Quit"
    ]

    y_offset = 10
    line_height = 20

    for i, line in enumerate(controls):
        color = colors.ui_text if i > 0 else colors.robot
        text = font.render(line, True, color)
        surface.blit(text, (10, y_offset))
        y_offset += line_height

    return surface


def render_status_bar(
    layout: UILayout,
    colors: ColorScheme,
    config: RenderConfig,
    paused: bool,
    step_count: int,
    completed: bool
) -> pygame.Surface:
    """
    Render bottom status bar.

    PURE function - creates surface with status information.

    Args:
        layout: UI layout configuration
        colors: Color scheme
        config: Render configuration
        paused: Whether simulation is paused
        step_count: Current step count
        completed: Whether simulation is complete

    Returns:
        Surface with status bar
    """
    x, y, width, height = layout.status_bar
    surface = pygame.Surface((width, height))
    surface.fill(colors.ui_background)

    # Draw top border
    pygame.draw.line(surface, colors.ui_text, (0, 0), (width, 0), 2)

    # Setup font
    try:
        font = pygame.font.Font(None, 28)
    except:
        font = pygame.font.SysFont('monospace', 22)

    # Status text components
    status_parts = []

    # Step count
    status_parts.append(f"Steps: {step_count}")

    # Speed
    status_parts.append(f"Speed: {config.animation_speed:.1f}x")

    # State
    if completed:
        status_parts.append("[COMPLETE]")
    elif paused:
        status_parts.append("[PAUSED]")
    else:
        status_parts.append("[RUNNING]")

    # Toggles
    toggles = []
    if config.show_path:
        toggles.append("Path")
    if config.show_sensors:
        toggles.append("Sensors")
    if config.show_grid:
        toggles.append("Grid")

    if toggles:
        status_parts.append(f"[{', '.join(toggles)}]")

    # Render status text
    status_text = " | ".join(status_parts)
    text_surface = font.render(status_text, True, colors.ui_text)
    surface.blit(text_surface, (20, (height - text_surface.get_height()) // 2))

    return surface


def render_title_bar(
    config: RenderConfig,
    colors: ColorScheme,
    strategy_name: str = "Unknown"
) -> pygame.Surface:
    """
    Render title bar at top of screen.

    PURE function - creates surface with title.

    Args:
        config: Render configuration
        colors: Color scheme
        strategy_name: Name of navigation strategy

    Returns:
        Surface with title bar
    """
    surface = pygame.Surface((config.screen_width, config.ui_header_height))
    surface.fill(colors.ui_background)

    # Draw bottom border
    pygame.draw.line(
        surface,
        colors.ui_text,
        (0, config.ui_header_height - 1),
        (config.screen_width, config.ui_header_height - 1),
        2
    )

    # Setup font
    try:
        font = pygame.font.Font(None, 36)
    except:
        font = pygame.font.SysFont('monospace', 28)

    # Title
    title = f"Robot Navigation Simulator - {strategy_name} Strategy"
    text = font.render(title, True, colors.ui_text)
    text_x = (config.screen_width - text.get_width()) // 2
    text_y = (config.ui_header_height - text.get_height()) // 2
    surface.blit(text, (text_x, text_y))

    return surface


def render_completion_overlay(
    config: RenderConfig,
    colors: ColorScheme,
    metrics: Dict[str, Any]
) -> pygame.Surface:
    """
    Render completion overlay when simulation finishes.

    PURE function - creates semi-transparent overlay.

    Args:
        config: Render configuration
        colors: Color scheme
        metrics: Final simulation metrics

    Returns:
        Surface with completion overlay
    """
    surface = pygame.Surface((config.screen_width, config.screen_height))
    surface.fill((0, 0, 0))
    surface.set_alpha(200)

    # Create text overlay
    overlay = pygame.Surface((400, 300))
    overlay.fill(colors.ui_panel)
    pygame.draw.rect(overlay, colors.exit, (0, 0, 400, 300), 4)

    # Setup fonts
    try:
        title_font = pygame.font.Font(None, 48)
        font = pygame.font.Font(None, 32)
    except:
        title_font = pygame.font.SysFont('monospace', 36)
        font = pygame.font.SysFont('monospace', 24)

    # Title
    title_text = title_font.render("SIMULATION COMPLETE!", True, colors.exit)
    title_x = (400 - title_text.get_width()) // 2
    overlay.blit(title_text, (title_x, 30))

    # Results
    results = [
        f"Total Steps: {metrics.get('total_steps', 0)}",
        f"Unique Positions: {metrics.get('unique_positions', 0)}",
        f"Efficiency: {metrics.get('efficiency', 0):.2%}",
    ]

    y_offset = 100
    for line in results:
        text = font.render(line, True, colors.ui_text)
        text_x = (400 - text.get_width()) // 2
        overlay.blit(text, (text_x, y_offset))
        y_offset += 40

    # Instructions
    try:
        small_font = pygame.font.Font(None, 24)
    except:
        small_font = pygame.font.SysFont('monospace', 18)

    inst_text = small_font.render("Press R to restart or ESC to quit", True, colors.ui_text)
    inst_x = (400 - inst_text.get_width()) // 2
    overlay.blit(inst_text, (inst_x, 240))

    # Position overlay in center of screen
    overlay_x = (config.screen_width - 400) // 2
    overlay_y = (config.screen_height - 300) // 2

    surface.blit(overlay, (overlay_x, overlay_y))

    return surface
