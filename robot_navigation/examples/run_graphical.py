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
    T     - Toggle strategy selector
    1-5   - Select strategy (when selector is open)
    ESC   - Quit (or close strategy selector)
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
    render_strategy_selector,
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


def load_all_strategies(strategies_dir: str):
    """
    Load all available strategy modules from the strategies directory.

    IMPURE: Loads modules from file system.

    Args:
        strategies_dir: Path to strategies directory

    Returns:
        Dictionary of {name: (path, function)} for all strategies
    """
    strategies = {}

    if not os.path.exists(strategies_dir):
        return strategies

    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(strategies_dir, filename)
            name = get_strategy_name(filepath)

            try:
                strategy_func = load_strategy_from_module(filepath)
                strategies[name] = (filepath, strategy_func)
            except Exception as e:
                print(f"Warning: Could not load strategy {filename}: {e}")

    return strategies


def handle_events(paused: bool, config: RenderConfig, show_selector: bool = False):
    """
    Handle pygame events and return updated state.

    IMPURE: Reads from event queue.

    Args:
        paused: Current pause state
        config: Current render configuration
        show_selector: Whether strategy selector is currently shown

    Returns:
        Tuple of (running, paused, config, should_step, should_reset, toggle_selector, selected_strategy_num)
    """
    running = True
    should_step = False
    should_reset = False
    toggle_selector = False
    selected_strategy_num = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_selector:
                    toggle_selector = True  # Close selector
                else:
                    running = False

            elif event.key == pygame.K_SPACE and not show_selector:
                paused = not paused

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if paused and not show_selector:
                    should_step = True

            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                if not show_selector:
                    config = adjust_speed(config, 1.5)

            elif event.key == pygame.K_MINUS:
                if not show_selector:
                    config = adjust_speed(config, 0.67)

            elif event.key == pygame.K_p:
                if not show_selector:
                    config = toggle_setting(config, 'path')

            elif event.key == pygame.K_s and not show_selector:
                config = toggle_setting(config, 'sensors')

            elif event.key == pygame.K_g:
                if not show_selector:
                    config = toggle_setting(config, 'grid')

            elif event.key == pygame.K_r:
                if not show_selector:
                    should_reset = True

            elif event.key == pygame.K_t:
                toggle_selector = True  # Show/hide strategy selector

            # Number keys for strategy selection
            elif show_selector:
                if event.key == pygame.K_1:
                    selected_strategy_num = 1
                elif event.key == pygame.K_2:
                    selected_strategy_num = 2
                elif event.key == pygame.K_3:
                    selected_strategy_num = 3
                elif event.key == pygame.K_4:
                    selected_strategy_num = 4
                elif event.key == pygame.K_5:
                    selected_strategy_num = 5

    return running, paused, config, should_step, should_reset, toggle_selector, selected_strategy_num


def run_graphical_simulation(
    initial_state,
    strategy,
    config: RenderConfig,
    color_scheme: ColorScheme,
    strategy_name: str = "Unknown",
    max_steps: int = 1000,
    all_strategies: dict = None
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
        all_strategies: Dictionary of all available strategies
    """
    if all_strategies is None:
        all_strategies = {strategy_name: (None, strategy)}
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
    show_strategy_selector = False
    current_strategy = strategy
    current_strategy_name = strategy_name

    running = True

    while running:
        # Event handling (IMPURE)
        running, paused, config, should_step, should_reset, toggle_selector, selected_strategy_num = handle_events(
            paused, config, show_strategy_selector
        )

        # Toggle strategy selector
        if toggle_selector:
            show_strategy_selector = not show_strategy_selector
            if show_strategy_selector:
                paused = True  # Auto-pause when opening selector

        # Handle strategy selection
        if selected_strategy_num is not None and show_strategy_selector:
            strategy_names = sorted(all_strategies.keys())
            if 1 <= selected_strategy_num <= len(strategy_names):
                selected_name = strategy_names[selected_strategy_num - 1]
                _, new_strategy = all_strategies[selected_name]

                # Switch strategy and reset simulation
                current_strategy = new_strategy
                current_strategy_name = selected_name
                current_state = initial_state
                all_states = [initial_state]
                step_accumulator = 0.0
                paused = True
                show_strategy_selector = False  # Close selector after selection

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
            # Step simulation (PURE) - use current_strategy
            current_state = step_simulation(current_state, current_strategy)
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

        # Title bar - use current_strategy_name
        title_surface = render_title_bar(config, color_scheme, current_strategy_name)

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

        # Show strategy selector if active
        if show_strategy_selector:
            selector_surface = render_strategy_selector(
                screen.copy(),
                all_strategies,
                current_strategy_name,
                config,
                color_scheme
            )
            screen.blit(selector_surface, (0, 0))

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
  T     - Toggle strategy selector
  1-5   - Select strategy (when selector is open)
  ESC   - Quit (or close strategy selector)

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

    # Load all available strategies for toggling
    print("Loading available strategies...")
    strategies_dir = os.path.join(os.path.dirname(args.strategy), '..')
    strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
    all_strategies = load_all_strategies(strategies_dir)
    print(f"Found {len(all_strategies)} strategies: {', '.join(sorted(all_strategies.keys()))}")

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
        args.max_steps,
        all_strategies
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
