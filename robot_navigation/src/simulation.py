"""
Simulation engine for robot navigation.

This module provides pure functions for running simulations as a series
of state transformations.
"""
from typing import List, Callable, Dict, Any
from .types import Maze, Robot, SimulationState, SensorReading
from .robot import create_robot, move_robot
from .sensors import apply_sensors
from .maze import is_exit_position


# Type alias for strategy functions
StrategyFunction = Callable[[Robot, List[SensorReading], Maze], str]


def create_initial_state(
    maze: Maze,
    sensor_config: Dict[str, Any],
    start_orientation: str = 'N'
) -> SimulationState:
    """
    Create the initial simulation state.

    PURE function.

    Args:
        maze: Maze configuration
        sensor_config: Sensor configuration dictionary
        start_orientation: Initial robot orientation

    Returns:
        Initial SimulationState
    """
    robot = create_robot(
        position=maze.start_pos,
        orientation=start_orientation,
        sensor_config=sensor_config
    )

    return SimulationState(
        maze=maze,
        robot=robot,
        step_count=0,
        metrics={
            'total_steps': 0,
            'unique_positions': 1,
            'backtrack_count': 0,
            'collisions': 0
        }
    )


def is_complete(state: SimulationState) -> bool:
    """
    Check if simulation is complete (robot reached exit).

    PURE function.

    Args:
        state: Current simulation state

    Returns:
        True if robot is at exit position
    """
    return is_exit_position(state.maze, state.robot.position)


def update_metrics(
    old_state: SimulationState,
    new_robot: Robot
) -> Dict[str, Any]:
    """
    Update simulation metrics.

    PURE function.

    Args:
        old_state: Previous simulation state
        new_robot: New robot state

    Returns:
        Updated metrics dictionary
    """
    metrics = old_state.metrics.copy()

    # Update step count
    metrics['total_steps'] = old_state.step_count + 1

    # Count unique positions visited
    unique_positions = set(new_robot.path_history)
    metrics['unique_positions'] = len(unique_positions)

    # Detect backtracking (visiting previously visited position)
    if new_robot.position in old_state.robot.path_history[:-1]:
        metrics['backtrack_count'] = metrics.get('backtrack_count', 0) + 1

    # Detect collision (position didn't change despite move command)
    if new_robot.position == old_state.robot.position:
        metrics['collisions'] = metrics.get('collisions', 0) + 1

    return metrics


def step_simulation(
    state: SimulationState,
    strategy: StrategyFunction
) -> SimulationState:
    """
    Execute one step of the simulation.

    PURE function - returns new state.

    Args:
        state: Current simulation state
        strategy: Strategy function to determine next action

    Returns:
        New simulation state after one step
    """
    # Get sensor readings
    sensor_readings = apply_sensors(
        state.robot,
        state.maze,
        state.robot.sensor_config
    )

    # Determine next action using strategy
    action = strategy(state.robot, sensor_readings, state.maze)

    # Execute action (move robot)
    new_robot = move_robot(state.robot, action, state.maze)

    # Update metrics
    new_metrics = update_metrics(state, new_robot)

    # Return new state
    return SimulationState(
        maze=state.maze,
        robot=new_robot,
        step_count=state.step_count + 1,
        metrics=new_metrics
    )


def run_simulation(
    initial_state: SimulationState,
    strategy: StrategyFunction,
    max_steps: int = 1000
) -> List[SimulationState]:
    """
    Run a complete simulation until completion or max steps.

    PURE function - generates sequence of states.

    Args:
        initial_state: Starting simulation state
        strategy: Strategy function to use
        max_steps: Maximum number of steps to run

    Returns:
        List of all simulation states (including initial state)
    """
    states = [initial_state]
    current_state = initial_state

    for _ in range(max_steps):
        if is_complete(current_state):
            break

        current_state = step_simulation(current_state, strategy)
        states.append(current_state)

    return states


def calculate_metrics(states: List[SimulationState]) -> Dict[str, Any]:
    """
    Calculate final metrics from simulation states.

    PURE function.

    Args:
        states: List of all simulation states

    Returns:
        Dictionary of calculated metrics
    """
    if not states:
        return {}

    final_state = states[-1]
    final_metrics = final_state.metrics.copy()

    # Add additional calculated metrics
    final_metrics['total_states'] = len(states)
    final_metrics['completed'] = is_complete(final_state)
    final_metrics['efficiency'] = (
        final_metrics['unique_positions'] / final_metrics['total_steps']
        if final_metrics['total_steps'] > 0 else 0
    )

    # Path length
    final_metrics['path_length'] = len(final_state.robot.path_history)

    return final_metrics


def run_simulation_generator(
    initial_state: SimulationState,
    strategy: StrategyFunction,
    max_steps: int = 1000
):
    """
    Run simulation as a generator for step-by-step execution.

    PURE function (generator).

    Args:
        initial_state: Starting simulation state
        strategy: Strategy function to use
        max_steps: Maximum number of steps to run

    Yields:
        SimulationState for each step
    """
    current_state = initial_state
    yield current_state

    for _ in range(max_steps):
        if is_complete(current_state):
            break

        current_state = step_simulation(current_state, strategy)
        yield current_state
