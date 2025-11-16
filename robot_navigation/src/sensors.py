"""
Sensor functions for the robot navigation system.

All sensor functions follow the signature:
    SensorFunction = Callable[[Robot, Maze, str], SensorReading]

They are pure functions that return sensor readings based on robot state and maze.
"""
from typing import List, Callable, Dict, Any
import yaml
from .types import Robot, Maze, SensorReading
from .robot import get_relative_direction, get_position_in_direction
from .maze import is_valid_position


# Type alias for sensor functions
SensorFunction = Callable[[Robot, Maze, str], SensorReading]


def ultrasound_sensor(robot: Robot, maze: Maze, direction: str) -> SensorReading:
    """
    Ultrasound sensor - measures distance to nearest wall.

    PURE function.

    Args:
        robot: Current robot state
        maze: Maze configuration
        direction: Relative direction ('front', 'left', 'right', 'back')

    Returns:
        SensorReading with distance (1-5 units, 5 if no wall in range)
    """
    abs_direction = get_relative_direction(robot, direction)
    current_pos = robot.position
    distance = 0
    max_distance = 5

    # Cast ray in direction until we hit a wall or max distance
    for i in range(1, max_distance + 1):
        next_pos = get_position_in_direction(current_pos, abs_direction)
        if not is_valid_position(maze, next_pos):
            distance = i
            break
        current_pos = next_pos
    else:
        # No wall found within range
        distance = max_distance

    return SensorReading(
        sensor_type='ultrasound',
        value=distance,
        direction=direction
    )


def infrared_sensor(robot: Robot, maze: Maze, direction: str) -> SensorReading:
    """
    Infrared sensor - detects immediate obstacles.

    PURE function.

    Args:
        robot: Current robot state
        maze: Maze configuration
        direction: Relative direction ('front', 'left', 'right', 'back')

    Returns:
        SensorReading with boolean value (True if obstacle adjacent)
    """
    abs_direction = get_relative_direction(robot, direction)
    next_pos = get_position_in_direction(robot.position, abs_direction)

    # Check if next position is blocked
    has_obstacle = not is_valid_position(maze, next_pos)

    return SensorReading(
        sensor_type='infrared',
        value=has_obstacle,
        direction=direction
    )


def load_sensor_config(filepath: str) -> Dict[str, Any]:
    """
    Load sensor configuration from YAML file.

    IMPURE: Performs I/O operation.

    Args:
        filepath: Path to sensor config file

    Returns:
        Dictionary with sensor configuration

    Expected format:
        sensors:
          - type: ultrasound
            directions: [front, left, right]
          - type: infrared
            directions: [front, left, right, back]
    """
    with open(filepath, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_sensor_function(sensor_type: str) -> SensorFunction:
    """
    Get sensor function by type name.

    PURE function (returns a function reference).

    Args:
        sensor_type: Name of sensor type

    Returns:
        Sensor function

    Raises:
        ValueError: If sensor type is unknown
    """
    sensors = {
        'ultrasound': ultrasound_sensor,
        'infrared': infrared_sensor,
    }

    if sensor_type not in sensors:
        raise ValueError(f"Unknown sensor type: {sensor_type}")

    return sensors[sensor_type]


def apply_sensors(
    robot: Robot,
    maze: Maze,
    sensor_config: Dict[str, Any]
) -> List[SensorReading]:
    """
    Apply all configured sensors to get readings.

    PURE function.

    Args:
        robot: Current robot state
        maze: Maze configuration
        sensor_config: Sensor configuration dictionary

    Returns:
        List of sensor readings
    """
    readings = []

    for sensor_spec in sensor_config.get('sensors', []):
        sensor_type = sensor_spec['type']
        directions = sensor_spec.get('directions', ['front'])

        sensor_func = get_sensor_function(sensor_type)

        for direction in directions:
            reading = sensor_func(robot, maze, direction)
            readings.append(reading)

    return readings


def create_default_sensor_config() -> Dict[str, Any]:
    """
    Create a default sensor configuration.

    PURE function.

    Returns:
        Default sensor configuration dictionary
    """
    return {
        'sensors': [
            {
                'type': 'ultrasound',
                'directions': ['front', 'left', 'right']
            },
            {
                'type': 'infrared',
                'directions': ['front', 'left', 'right', 'back']
            }
        ]
    }
