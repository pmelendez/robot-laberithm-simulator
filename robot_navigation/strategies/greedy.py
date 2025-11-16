"""
Greedy navigation strategy.

Attempts to move toward the exit position using Manhattan distance.
"""
from typing import List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.types import Robot, Maze, SensorReading
from src.robot import get_relative_direction, get_position_in_direction


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


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two positions.

    PURE function.

    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)

    Returns:
        Manhattan distance
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_best_direction(robot: Robot, maze: Maze, sensor_readings: List[SensorReading]) -> str:
    """
    Determine the best direction to move toward the exit.

    PURE function.

    Args:
        robot: Current robot state
        maze: Maze configuration
        sensor_readings: List of sensor readings

    Returns:
        Best direction to move
    """
    current_pos = robot.position
    exit_pos = maze.exit_pos
    current_distance = manhattan_distance(current_pos, exit_pos)

    # Get sensor readings for blocking
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

    # Evaluate each possible direction
    options = []

    # Front
    if not front_blocked:
        front_abs_dir = get_relative_direction(robot, 'front')
        front_pos = get_position_in_direction(current_pos, front_abs_dir)
        front_dist = manhattan_distance(front_pos, exit_pos)
        options.append(('forward', front_dist))

    # Left
    if not left_blocked:
        left_abs_dir = get_relative_direction(robot, 'left')
        left_pos = get_position_in_direction(current_pos, left_abs_dir)
        left_dist = manhattan_distance(left_pos, exit_pos)
        options.append(('left', left_dist))

    # Right
    if not right_blocked:
        right_abs_dir = get_relative_direction(robot, 'right')
        right_pos = get_position_in_direction(current_pos, right_abs_dir)
        right_dist = manhattan_distance(right_pos, exit_pos)
        options.append(('right', right_dist))

    # If no options available, go backward
    if not options:
        return 'backward'

    # Choose direction with minimum distance to exit
    best_direction = min(options, key=lambda x: x[1])
    return best_direction[0]


def strategy(robot: Robot, sensor_readings: List[SensorReading], maze: Maze) -> str:
    """
    Greedy strategy - always move toward exit if possible.

    PURE function - no side effects.

    Algorithm:
    1. Calculate Manhattan distance to exit for each available direction
    2. Choose the direction that minimizes distance
    3. If all blocked, go backward

    Args:
        robot: Current robot state
        sensor_readings: List of current sensor readings
        maze: Maze configuration

    Returns:
        Next action: 'forward', 'left', 'right', 'backward'
    """
    return get_best_direction(robot, maze, sensor_readings)


# Export for dynamic loading
__all__ = ['strategy']
