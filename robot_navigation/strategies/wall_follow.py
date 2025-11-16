"""
Wall-following navigation strategy.

Implements the "right-hand rule" - keep the right hand touching the wall.
This strategy is guaranteed to find the exit in simply-connected mazes.
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


def strategy(robot: Robot, sensor_readings: List[SensorReading], maze: Maze) -> str:
    """
    Wall-following strategy using right-hand rule.

    PURE function - no side effects.

    Algorithm:
    1. If right side is open, turn right and move forward
    2. Else if front is open, move forward
    3. Else if left side is open, turn left and move forward
    4. Else turn around (rotate left twice)

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

    # Right-hand rule logic
    if not right_blocked:
        # Right side is open - turn right (which also moves forward)
        return 'right'
    elif not front_blocked:
        # Front is open - move forward
        return 'forward'
    elif not left_blocked:
        # Left side is open - turn left (which also moves forward)
        return 'left'
    else:
        # All sides blocked - turn around
        return 'backward'


# Export for dynamic loading
__all__ = ['strategy']
