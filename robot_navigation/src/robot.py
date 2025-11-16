"""
Pure functions for robot state transformations.

All functions in this module are pure - they take a robot state and return
a new robot state without modifying the original.
"""
from typing import Tuple
from .types import Robot, Maze
from .maze import is_valid_position


# Orientation mappings
ORIENTATIONS = ['N', 'E', 'S', 'W']  # Clockwise order

DIRECTION_DELTAS = {
    'N': (0, -1),
    'S': (0, 1),
    'E': (1, 0),
    'W': (-1, 0)
}

OPPOSITE_DIRECTIONS = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}


def rotate_robot(robot: Robot, rotation: str) -> Robot:
    """
    Rotate the robot left or right.

    PURE function - returns new Robot instance.

    Args:
        robot: Current robot state
        rotation: 'left' or 'right'

    Returns:
        New robot state with updated orientation
    """
    current_idx = ORIENTATIONS.index(robot.orientation)

    if rotation == 'left':
        new_idx = (current_idx - 1) % 4
    elif rotation == 'right':
        new_idx = (current_idx + 1) % 4
    else:
        raise ValueError(f"Invalid rotation: {rotation}")

    new_orientation = ORIENTATIONS[new_idx]

    return Robot(
        position=robot.position,
        orientation=new_orientation,
        sensor_config=robot.sensor_config,
        path_history=robot.path_history
    )


def get_robot_front_position(robot: Robot) -> Tuple[int, int]:
    """
    Get the position in front of the robot based on its orientation.

    PURE function.

    Args:
        robot: Current robot state

    Returns:
        Position tuple (x, y) in front of robot
    """
    x, y = robot.position
    dx, dy = DIRECTION_DELTAS[robot.orientation]
    return (x + dx, y + dy)


def get_position_in_direction(position: Tuple[int, int], direction: str) -> Tuple[int, int]:
    """
    Get a position in a given direction from current position.

    PURE function.

    Args:
        position: Current position (x, y)
        direction: Direction ('N', 'S', 'E', 'W')

    Returns:
        New position tuple (x, y)
    """
    x, y = position
    dx, dy = DIRECTION_DELTAS[direction]
    return (x + dx, y + dy)


def get_relative_direction(robot: Robot, relative: str) -> str:
    """
    Get absolute direction from relative direction.

    PURE function.

    Args:
        robot: Current robot state
        relative: Relative direction ('front', 'left', 'right', 'back')

    Returns:
        Absolute direction ('N', 'S', 'E', 'W')
    """
    current_idx = ORIENTATIONS.index(robot.orientation)

    if relative == 'front':
        return robot.orientation
    elif relative == 'left':
        return ORIENTATIONS[(current_idx - 1) % 4]
    elif relative == 'right':
        return ORIENTATIONS[(current_idx + 1) % 4]
    elif relative == 'back':
        return ORIENTATIONS[(current_idx + 2) % 4]
    else:
        raise ValueError(f"Invalid relative direction: {relative}")


def move_robot(robot: Robot, direction: str, maze: Maze) -> Robot:
    """
    Move the robot in a specified direction if possible.

    PURE function - returns new Robot instance.

    Args:
        robot: Current robot state
        direction: Movement direction ('forward', 'backward', 'left', 'right')
        maze: Maze configuration

    Returns:
        New robot state (position updated if move is valid)
    """
    if direction == 'forward':
        new_position = get_robot_front_position(robot)
    elif direction == 'backward':
        # Move opposite to orientation
        back_direction = OPPOSITE_DIRECTIONS[robot.orientation]
        new_position = get_position_in_direction(robot.position, back_direction)
    elif direction == 'left':
        # Rotate left and move forward
        rotated = rotate_robot(robot, 'left')
        new_position = get_robot_front_position(rotated)
        # Update orientation
        robot = rotated
    elif direction == 'right':
        # Rotate right and move forward
        rotated = rotate_robot(robot, 'right')
        new_position = get_robot_front_position(rotated)
        # Update orientation
        robot = rotated
    else:
        raise ValueError(f"Invalid direction: {direction}")

    # Check if new position is valid
    if is_valid_position(maze, new_position):
        return add_to_path(
            Robot(
                position=new_position,
                orientation=robot.orientation,
                sensor_config=robot.sensor_config,
                path_history=robot.path_history
            ),
            new_position
        )
    else:
        # Return robot unchanged if move is invalid
        return robot


def add_to_path(robot: Robot, position: Tuple[int, int]) -> Robot:
    """
    Add a position to the robot's path history.

    PURE function - returns new Robot instance.

    Args:
        robot: Current robot state
        position: Position to add

    Returns:
        New robot state with updated path history
    """
    return Robot(
        position=robot.position,
        orientation=robot.orientation,
        sensor_config=robot.sensor_config,
        path_history=robot.path_history + (position,)
    )


def create_robot(
    position: Tuple[int, int],
    orientation: str = 'N',
    sensor_config: dict = None
) -> Robot:
    """
    Create a new robot instance.

    PURE function.

    Args:
        position: Starting position (x, y)
        orientation: Starting orientation ('N', 'S', 'E', 'W')
        sensor_config: Sensor configuration dictionary

    Returns:
        New Robot instance
    """
    if sensor_config is None:
        sensor_config = {}

    return Robot(
        position=position,
        orientation=orientation,
        sensor_config=sensor_config,
        path_history=(position,)
    )
