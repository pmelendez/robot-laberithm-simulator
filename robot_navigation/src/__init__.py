"""
Robot Navigation Simulation System

A functional programming-based robot navigation simulator.
"""
from .types import Maze, Robot, SensorReading, SimulationState
from .maze import (
    load_maze_from_yaml,
    load_maze_from_markdown,
    is_valid_position,
    is_exit_position,
    get_cell
)
from .robot import (
    create_robot,
    move_robot,
    rotate_robot,
    add_to_path,
    get_robot_front_position
)
from .sensors import (
    ultrasound_sensor,
    infrared_sensor,
    load_sensor_config,
    apply_sensors
)
from .simulation import (
    create_initial_state,
    step_simulation,
    run_simulation,
    is_complete,
    calculate_metrics
)
from .visualization import (
    render_maze,
    render_sensor_readings,
    render_metrics,
    display_state,
    display_final_results
)

__all__ = [
    # Types
    'Maze', 'Robot', 'SensorReading', 'SimulationState',
    # Maze functions
    'load_maze_from_yaml', 'load_maze_from_markdown',
    'is_valid_position', 'is_exit_position', 'get_cell',
    # Robot functions
    'create_robot', 'move_robot', 'rotate_robot',
    'add_to_path', 'get_robot_front_position',
    # Sensor functions
    'ultrasound_sensor', 'infrared_sensor',
    'load_sensor_config', 'apply_sensors',
    # Simulation functions
    'create_initial_state', 'step_simulation', 'run_simulation',
    'is_complete', 'calculate_metrics',
    # Visualization functions
    'render_maze', 'render_sensor_readings', 'render_metrics',
    'display_state', 'display_final_results',
]
