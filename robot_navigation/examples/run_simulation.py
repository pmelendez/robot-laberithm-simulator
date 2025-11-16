#!/usr/bin/env python3
"""
Robot Navigation Simulation - Main CLI

This script demonstrates the functional programming approach to robot navigation.
All logic uses pure functions with state transformations.
"""
import argparse
import sys
import os
import time
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.maze import load_maze_from_yaml, load_maze_from_markdown
from src.sensors import load_sensor_config
from src.simulation import (
    create_initial_state,
    run_simulation,
    run_simulation_generator,
    calculate_metrics,
    is_complete
)
from src.visualization import (
    display_state,
    display_final_results,
    render_compact_state,
    render_full_state
)
from src.sensors import apply_sensors


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


def run_fast(args):
    """
    Run simulation to completion and show final results.

    IMPURE: Performs I/O operations.
    """
    # Load configuration (I/O operations)
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

    # Create initial state (pure function)
    print("\nInitializing simulation...")
    initial_state = create_initial_state(maze, sensor_config)

    # Run simulation (pure function - generates state sequence)
    print(f"Running simulation (max {args.max_steps} steps)...")
    states = run_simulation(initial_state, strategy, args.max_steps)

    # Calculate metrics (pure function)
    metrics = calculate_metrics(states)

    # Display results (I/O operation)
    display_final_results(states, metrics)

    if metrics.get('completed'):
        print("\nSUCCESS: Robot reached the exit!")
    else:
        print("\nFAILURE: Robot did not reach the exit within max steps.")


def run_step_mode(args):
    """
    Run simulation step-by-step with user interaction.

    IMPURE: Performs I/O operations.
    """
    # Load configuration
    print(f"Loading maze from: {args.maze}")
    if args.maze.endswith('.yaml') or args.maze.endswith('.yml'):
        maze = load_maze_from_yaml(args.maze)
    elif args.maze.endswith('.md'):
        maze = load_maze_from_markdown(args.maze)
    else:
        print("Error: Maze file must be .yaml or .md")
        sys.exit(1)

    sensor_config = load_sensor_config(args.sensors)
    strategy = load_strategy_from_module(args.strategy)

    # Create initial state
    initial_state = create_initial_state(maze, sensor_config)

    # Run simulation as generator
    print("\nStep-by-step mode. Press Enter to advance, 'q' to quit.\n")

    for state in run_simulation_generator(initial_state, strategy, args.max_steps):
        # Get sensor readings for display
        sensor_readings = apply_sensors(state.robot, state.maze, state.robot.sensor_config)

        # Display state
        display_state(state, sensor_readings)

        if is_complete(state):
            print("\nSUCCESS: Robot reached the exit!")
            break

        # Wait for user input
        user_input = input("\nPress Enter for next step (or 'q' to quit): ")
        if user_input.lower() == 'q':
            print("Simulation terminated by user.")
            break

    # Final metrics
    metrics = calculate_metrics([state])
    print("\nFinal Metrics:")
    print(f"  Total steps: {metrics.get('total_steps', 0)}")
    print(f"  Unique positions: {metrics.get('unique_positions', 0)}")
    print(f"  Efficiency: {metrics.get('efficiency', 0):.2%}")


def run_animated(args):
    """
    Run simulation with animation.

    IMPURE: Performs I/O operations.
    """
    # Load configuration
    if args.maze.endswith('.yaml') or args.maze.endswith('.yml'):
        maze = load_maze_from_yaml(args.maze)
    elif args.maze.endswith('.md'):
        maze = load_maze_from_markdown(args.maze)
    else:
        print("Error: Maze file must be .yaml or .md")
        sys.exit(1)

    sensor_config = load_sensor_config(args.sensors)
    strategy = load_strategy_from_module(args.strategy)

    # Create initial state
    initial_state = create_initial_state(maze, sensor_config)

    print(f"\nRunning animated simulation (speed: {args.speed}s per step)...")
    print("Press Ctrl+C to stop.\n")

    try:
        for state in run_simulation_generator(initial_state, strategy, args.max_steps):
            # Clear screen (simple version)
            print("\033[2J\033[H")  # ANSI escape codes

            # Get sensor readings
            sensor_readings = apply_sensors(state.robot, state.maze, state.robot.sensor_config)

            # Display state
            print(render_full_state(state, sensor_readings))

            if is_complete(state):
                print("\nSUCCESS: Robot reached the exit!")
                break

            time.sleep(args.speed)

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

    # Final metrics
    metrics = calculate_metrics([state])
    print(f"\nFinal Metrics:")
    print(f"  Total steps: {metrics.get('total_steps', 0)}")
    print(f"  Unique positions: {metrics.get('unique_positions', 0)}")
    print(f"  Efficiency: {metrics.get('efficiency', 0):.2%}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Robot Navigation Simulation (Functional Programming)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults
  python run_simulation.py

  # Use specific maze and strategy
  python run_simulation.py --maze ../config/mazes/complex.md --strategy ../strategies/greedy.py

  # Step-by-step mode
  python run_simulation.py --step-mode

  # Animated mode
  python run_simulation.py --animated --speed 0.2
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
        '--step-mode',
        action='store_true',
        help='Run in step-by-step mode with user interaction'
    )

    parser.add_argument(
        '--animated',
        action='store_true',
        help='Run with animation'
    )

    parser.add_argument(
        '--speed',
        type=float,
        default=0.5,
        help='Animation speed in seconds per step (default: 0.5)'
    )

    args = parser.parse_args()

    # Execute appropriate mode
    if args.step_mode:
        run_step_mode(args)
    elif args.animated:
        run_animated(args)
    else:
        run_fast(args)


if __name__ == '__main__':
    main()
