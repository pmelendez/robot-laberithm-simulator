"""
Random walk navigation strategy.

Randomly explores the maze, avoiding walls.
Note: Uses deterministic pseudo-random based on robot state to maintain purity.
"""
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.types import Robot, Maze, SensorReading


def get_sensor_value(readings: List[SensorReading], direction: str, sensor_type: str = 'infrared'):
    """
    Helper function to extract sensor value for a specific direction.

    PURE function.

    Args:
        readings: List of sensor readings
        direction: Direction to look for
        sensor_type: Type of sensor to use

    Returns:
        Sensor value or None if not found
    """
    for reading in readings:
        if reading.direction == direction and reading.sensor_type == sensor_type:
            return reading.value
    return None


def deterministic_choice(robot: Robot, options: List[str]) -> str:
    """
    Make a deterministic "random" choice based on robot state.

    PURE function - uses robot position as seed for determinism.

    Args:
        robot: Current robot state
        options: List of possible choices

    Returns:
        Selected option
    """
    if not options:
        return 'forward'

    # Use position and path length as pseudo-random seed
    x, y = robot.position
    path_len = len(robot.path_history)
    seed = (x * 31 + y * 17 + path_len * 13) % len(options)

    return options[seed]


def strategy(robot: Robot, sensor_readings: List[SensorReading], maze: Maze) -> str:
    """
    Random walk strategy with obstacle avoidance.

    PURE function - uses deterministic pseudo-randomness based on state.

    Algorithm:
    1. Collect all non-blocked directions
    2. Choose one pseudo-randomly (deterministically based on state)
    3. If all blocked, try backward

    Args:
        robot: Current robot state
        sensor_readings: List of current sensor readings
        maze: Maze configuration

    Returns:
        Next action: 'forward', 'left', 'right', 'backward'
    """
    # Get infrared sensor readings (True = obstacle, False = clear)
    front_blocked = get_sensor_value(sensor_readings, 'front', 'infrared')
    left_blocked = get_sensor_value(sensor_readings, 'left', 'infrared')
    right_blocked = get_sensor_value(sensor_readings, 'right', 'infrared')

    # Default values if sensors not available
    if front_blocked is None:
        front_blocked = False
    if left_blocked is None:
        left_blocked = False
    if right_blocked is None:
        right_blocked = False

    # Collect available directions
    available_directions = []

    if not front_blocked:
        available_directions.append('forward')
    if not left_blocked:
        available_directions.append('left')
    if not right_blocked:
        available_directions.append('right')

    # If no directions available, go backward
    if not available_directions:
        return 'backward'

    # Choose pseudo-randomly from available directions
    return deterministic_choice(robot, available_directions)


# Export for dynamic loading
__all__ = ['strategy']
