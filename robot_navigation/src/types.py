"""
Immutable data structures for the robot navigation simulation.

All types defined here are immutable to support functional programming principles.
"""
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any


@dataclass(frozen=True)
class Maze:
    """
    Represents an immutable maze configuration.

    Attributes:
        grid: 2D list representing the maze layout
        start_pos: Starting position (x, y)
        exit_pos: Exit position (x, y)
        dimensions: Tuple of (width, height)
    """
    grid: Tuple[Tuple[str, ...], ...]  # Immutable 2D grid
    start_pos: Tuple[int, int]
    exit_pos: Tuple[int, int]
    dimensions: Tuple[int, int]


@dataclass(frozen=True)
class Robot:
    """
    Represents an immutable robot state.

    Attributes:
        position: Current position (x, y)
        orientation: Current orientation ('N', 'S', 'E', 'W')
        sensor_config: Dictionary of sensor configurations
        path_history: Tuple of positions visited
    """
    position: Tuple[int, int]
    orientation: str
    sensor_config: Dict[str, Any]
    path_history: Tuple[Tuple[int, int], ...]


@dataclass(frozen=True)
class SensorReading:
    """
    Represents an immutable sensor reading.

    Attributes:
        sensor_type: Type of sensor ('ultrasound', 'infrared', etc.)
        value: Reading value (distance, boolean, etc.)
        direction: Direction of the reading ('front', 'left', 'right', 'back')
    """
    sensor_type: str
    value: Any
    direction: str


@dataclass(frozen=True)
class SimulationState:
    """
    Represents an immutable simulation state at a given step.

    Attributes:
        maze: The maze configuration
        robot: Current robot state
        step_count: Number of steps taken
        metrics: Dictionary of simulation metrics
    """
    maze: Maze
    robot: Robot
    step_count: int
    metrics: Dict[str, Any]
