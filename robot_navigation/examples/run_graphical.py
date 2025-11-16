#!/usr/bin/env python3
"""
Robot Navigation Simulation - Graphical Interface

This script provides a graphical 2D visualization of the robot navigation
simulation using pygame. All rendering logic is kept pure while I/O operations
are isolated at the boundary.

Controls:
    SPACE - Play/Pause simulation
    ENTER - Step forward one step (when paused)
    +/=   - Increase speed
    -     - Decrease speed
    P     - Toggle path trail
    S     - Toggle sensor visualization
    G     - Toggle grid overlay
    R     - Reset simulation
    ESC   - Quit
"""
import argparse
import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pygame
except ImportError:
    print("Error: pygame not found. Please install it:")
    print("  pip install pygame>=2.5.0")
    sys.exit(1)

from src.maze import load_maze_from_yaml, load_maze_from_markdown
from src.sensors import load_sensor_config, apply_sensors
from src.simulation import (
    create_initial_state,
    step_simulation,
    is_complete,
    calculate_metrics
)
from src.graphics import (
    RenderConfig,
    ColorScheme,
    get_color_scheme,
    calculate_ui_layout,
    render_simulation_state,
    render_metrics_panel,
    render_controls_panel,
    render_status_bar,
    render_title_bar,
    render_completion_overlay,
    adjust_speed,
    toggle_setting
)


def load_strategy_from_module(strategy_path: str):
    """
    Dynamically load a strategy function from a Python file.

    IMPURE: Loads code from file system.

    Args:
        strategy_path: Path to strategy Python file

    Returns:
        Strategy function
    """
    spec = importlib.util.spec_from_file_location("custom_strategy", strategy_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.strategy


def get_strategy_name(strategy_path: str) -> str:
    """
    Extract strategy name from file path.

    PURE function.

    Args:
        strategy_path: Path to strategy file

    Returns:
        Strategy name
    """
    basename = os.path.basename(strategy_path)
    name = os.path.splitext(basename)[0]
    return name.replace('_', ' ').title()


def handle_events(paused: bool, config: RenderConfig):
    """
    Handle pygame events and return updated state.

    IMPURE: Reads from event queue.

    Args:
        paused: Current pause state
        config: Current render configuration

    Returns:
        Tuple of (running, paused, config, should_step, should_reset)
    """
    running = True
    should_step = False
    should_reset = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if paused:
                    should_step = True

            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                config = adjust_speed(config, 1.5)

            elif event.key == pygame.K_MINUS:
                config = adjust_speed(config, 0.67)

            elif event.key == pygame.K_p:
                config = toggle_setting(config, 'path')

            elif event.key == pygame.K_s:
                config = toggle_setting(config, 'sensors')

            elif event.key == pygame.K_g:
                config = toggle_setting(config, 'grid')

            elif event.key == pygame.K_r:
                should_reset = True

    return running, paused, config, should_step, should_reset


def run_graphical_simulation(
    initial_state,
    strategy,
    config: RenderConfig,
    color_scheme: ColorScheme,
    strategy_name: str = "Unknown",
    max_steps: int = 1000
):
    """
    Run the graphical simulation with pygame.

    IMPURE: Main event loop with I/O operations.

    Args:
        initial_state: Initial simulation state
        strategy: Strategy function
        config: Rendering configuration
        color_scheme: Color scheme to use
        strategy_name: Name of strategy for display
        max_steps: Maximum simulation steps
    """
    # Initialize pygame (IMPURE)
    pygame.init()
    screen = pygame.display.set_mode((config.screen_width, config.screen_height))
    pygame.display.set_caption("Robot Navigation Simulator")
    clock = pygame.time.Clock()

    # Calculate UI layout (PURE)
    layout = calculate_ui_layout(config)

    # Simulation state
    current_state = initial_state
    paused = True  # Start paused
    step_accumulator = 0.0
    all_states = [initial_state]

    running = True

    while running:
        # Event handling (IMPURE)
        running, paused, config, should_step, should_reset = handle_events(paused, config)

        # Reset simulation if requested
        if should_reset:
            current_state = initial_state
            all_states = [initial_state]
            step_accumulator = 0.0
            paused = True

        # Update layout if config changed
        layout = calculate_ui_layout(config)

        # Simulation stepping (PURE logic)
        should_advance = False

        if should_step:
            should_advance = True
        elif not paused and not is_complete(current_state):
            # Accumulate time for smooth speed control
            step_accumulator += config.animation_speed / config.fps
            if step_accumulator >= 1.0:
                should_advance = True
                step_accumulator -= 1.0

        if should_advance and not is_complete(current_state) and len(all_states) < max_steps:
            # Step simulation (PURE)
            current_state = step_simulation(current_state, strategy)
            all_states.append(current_state)

        # Get sensor readings (PURE)
        sensor_readings = apply_sensors(
            current_state.robot,
            current_state.maze,
            current_state.robot.sensor_config
        )

        # Rendering (PURE functions)
        # Main simulation view
        main_surface = render_simulation_state(
            current_state,
            sensor_readings,
            config,
            color_scheme,
            layout
        )

        # Title bar
        title_surface = render_title_bar(config, color_scheme, strategy_name)

        # Status bar
        status_surface = render_status_bar(
            layout,
            color_scheme,
            config,
            paused,
            current_state.step_count,
            is_complete(current_state)
        )

        # Metrics panel
        if config.show_metrics:
            metrics_surface = render_metrics_panel(
                current_state.metrics,
                layout,
                color_scheme,
                config
            )

        # Controls panel
        if config.show_controls:
            controls_surface = render_controls_panel(
                layout,
                color_scheme,
                config,
                paused
            )

        # Display (IMPURE - blitting to screen)
        screen.blit(main_surface, (0, 0))
        screen.blit(title_surface, (0, 0))
        screen.blit(status_surface, (0, layout.status_bar[1]))

        if config.show_metrics:
            screen.blit(metrics_surface, (layout.metrics_panel[0], layout.metrics_panel[1]))

        if config.show_controls:
            screen.blit(controls_surface, (layout.controls_panel[0], layout.controls_panel[1]))

        # Show completion overlay if done
        if is_complete(current_state):
            final_metrics = calculate_metrics(all_states)
            completion_surface = render_completion_overlay(config, color_scheme, final_metrics)
            screen.blit(completion_surface, (0, 0))

        # Update display (IMPURE)
        pygame.display.flip()
        clock.tick(config.fps)

    # Cleanup (IMPURE)
    pygame.quit()

    # Return final metrics for reporting
    return calculate_metrics(all_states)


def main():
    """Main entry point for graphical simulation."""
    parser = argparse.ArgumentParser(
        description='Robot Navigation Simulation - Graphical Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  SPACE - Play/Pause simulation
  ENTER - Step forward one step (when paused)
  +/=   - Increase speed
  -     - Decrease speed
  P     - Toggle path trail
  S     - Toggle sensor visualization
  G     - Toggle grid overlay
  R     - Reset simulation
  ESC   - Quit

Examples:
  # Run with defaults
  python run_graphical.py

  # Use specific maze and strategy
  python run_graphical.py --maze ../config/mazes/medium.yaml --strategy ../strategies/greedy.py

  # Start with different settings
  python run_graphical.py --speed 5.0 --no-grid --theme dark
        """
    )

    parser.add_argument(
        '--maze',
        default='../config/mazes/simple.yaml',
        help='Path to maze configuration file (.yaml or .md)'
    )

    parser.add_argument(
        '--sensors',
        default='../config/sensors/default_sensors.yaml',
        help='Path to sensor configuration file'
    )

    parser.add_argument(
        '--strategy',
        default='../strategies/wall_follow.py',
        help='Path to strategy module'
    )

    parser.add_argument(
        '--max-steps',
        type=int,
        default=1000,
        help='Maximum number of simulation steps'
    )

    parser.add_argument(
        '--speed',
        type=float,
        default=2.0,
        help='Initial animation speed (steps per second)'
    )

    parser.add_argument(
        '--theme',
        choices=['default', 'dark', 'light'],
        default='default',
        help='Color theme'
    )

    parser.add_argument(
        '--cell-size',
        type=int,
        default=40,
        help='Size of maze cells in pixels'
    )

    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='Window width in pixels'
    )

    parser.add_argument(
        '--height',
        type=int,
        default=768,
        help='Window height in pixels'
    )

    parser.add_argument(
        '--no-grid',
        action='store_true',
        help='Disable grid overlay'
    )

    parser.add_argument(
        '--no-sensors',
        action='store_true',
        help='Disable sensor visualization'
    )

    parser.add_argument(
        '--no-path',
        action='store_true',
        help='Disable path trail'
    )

    args = parser.parse_args()

    # Load configuration (IMPURE I/O)
    print(f"Loading maze from: {args.maze}")
    if args.maze.endswith('.yaml') or args.maze.endswith('.yml'):
        maze = load_maze_from_yaml(args.maze)
    elif args.maze.endswith('.md'):
        maze = load_maze_from_markdown(args.maze)
    else:
        print("Error: Maze file must be .yaml or .md")
        sys.exit(1)

    print(f"Loading sensor config from: {args.sensors}")
    sensor_config = load_sensor_config(args.sensors)

    print(f"Loading strategy from: {args.strategy}")
    strategy = load_strategy_from_module(args.strategy)
    strategy_name = get_strategy_name(args.strategy)

    # Create configuration (PURE)
    config = RenderConfig(
        cell_size=args.cell_size,
        screen_width=args.width,
        screen_height=args.height,
        animation_speed=args.speed,
        show_grid=not args.no_grid,
        show_sensors=not args.no_sensors,
        show_path=not args.no_path,
        color_scheme=args.theme
    )

    color_scheme = get_color_scheme(args.theme)

    # Create initial state (PURE)
    print("Initializing simulation...")
    initial_state = create_initial_state(maze, sensor_config)

    # Run graphical simulation (IMPURE)
    print(f"Starting graphical simulation...")
    print(f"Theme: {args.theme}")
    print(f"Initial speed: {args.speed}x")
    print("\nStarting paused. Press SPACE to begin, or ENTER to step.\n")

    final_metrics = run_graphical_simulation(
        initial_state,
        strategy,
        config,
        color_scheme,
        strategy_name,
        args.max_steps
    )

    # Print final summary
    print("\n" + "="*50)
    print("SIMULATION SUMMARY")
    print("="*50)
    print(f"Strategy: {strategy_name}")
    print(f"Total Steps: {final_metrics.get('total_steps', 0)}")
    print(f"Unique Positions: {final_metrics.get('unique_positions', 0)}")
    print(f"Efficiency: {final_metrics.get('efficiency', 0):.2%}")
    print(f"Backtracks: {final_metrics.get('backtrack_count', 0)}")
    print(f"Collisions: {final_metrics.get('collisions', 0)}")

    if final_metrics.get('completed'):
        print("\nSTATUS: SUCCESS - Robot reached the exit!")
    else:
        print("\nSTATUS: INCOMPLETE - Robot did not reach the exit.")

    print("="*50)


if __name__ == '__main__':
    main()
