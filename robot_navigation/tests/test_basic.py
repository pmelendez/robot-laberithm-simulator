"""
Basic tests for robot navigation system.

Tests verify that core functions are pure and work correctly.
"""
import sys
import os
from dataclasses import replace

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.types import Maze, Robot
from src.maze import is_valid_position, is_exit_position, get_cell
from src.robot import (
    create_robot,
    rotate_robot,
    move_robot,
    get_robot_front_position
)
from src.sensors import ultrasound_sensor, infrared_sensor
from src.simulation import create_initial_state, step_simulation, is_complete


def test_maze_functions():
    """Test maze query functions."""
    print("Testing maze functions...")

    # Create a simple test maze
    grid = (
        ('#', '#', '#', '#', '#'),
        ('#', 'S', '.', '.', '#'),
        ('#', '#', '#', 'E', '#'),
        ('#', '#', '#', '#', '#'),
    )

    maze = Maze(
        grid=grid,
        start_pos=(1, 1),
        exit_pos=(3, 2),
        dimensions=(5, 4)
    )

    # Test is_valid_position
    assert is_valid_position(maze, (1, 1)) == True  # Start position
    assert is_valid_position(maze, (2, 1)) == True  # Open space
    assert is_valid_position(maze, (0, 0)) == False  # Wall
    assert is_valid_position(maze, (-1, 0)) == False  # Out of bounds
    assert is_valid_position(maze, (10, 10)) == False  # Out of bounds

    # Test is_exit_position
    assert is_exit_position(maze, (3, 2)) == True
    assert is_exit_position(maze, (1, 1)) == False

    # Test get_cell
    assert get_cell(maze, (1, 1)) == 'S'
    assert get_cell(maze, (3, 2)) == 'E'
    assert get_cell(maze, (0, 0)) == '#'
    assert get_cell(maze, (10, 10)) is None

    print("  ✓ Maze functions work correctly")


def test_robot_immutability():
    """Test that robot operations return new instances."""
    print("Testing robot immutability...")

    robot1 = create_robot(position=(1, 1), orientation='N')

    # Test rotation returns new instance
    robot2 = rotate_robot(robot1, 'right')
    assert robot1.orientation == 'N'  # Original unchanged
    assert robot2.orientation == 'E'  # New instance changed
    assert robot1 is not robot2  # Different objects

    # Test that rotating again doesn't affect previous
    robot3 = rotate_robot(robot2, 'right')
    assert robot2.orientation == 'E'  # Previous unchanged
    assert robot3.orientation == 'S'  # New instance changed

    print("  ✓ Robot operations maintain immutability")


def test_robot_movement():
    """Test robot movement functions."""
    print("Testing robot movement...")

    # Create test maze
    grid = (
        ('#', '#', '#', '#', '#'),
        ('#', '.', '.', '.', '#'),
        ('#', '.', '#', '.', '#'),
        ('#', '.', '.', '.', '#'),
        ('#', '#', '#', '#', '#'),
    )

    maze = Maze(
        grid=grid,
        start_pos=(1, 1),
        exit_pos=(3, 3),
        dimensions=(5, 5)
    )

    robot = create_robot(position=(1, 1), orientation='E')

    # Test get_robot_front_position
    front_pos = get_robot_front_position(robot)
    assert front_pos == (2, 1)

    # Test moving forward
    moved_robot = move_robot(robot, 'forward', maze)
    assert moved_robot.position == (2, 1)
    assert robot.position == (1, 1)  # Original unchanged

    # Test blocked movement (hitting wall)
    blocked_robot = create_robot(position=(1, 2), orientation='S')
    moved_blocked = move_robot(blocked_robot, 'forward', maze)
    # Should try to move to (1, 3) which has a wall at (2,2) nearby but (1,3) is open
    # Actually (1,3) is open, so it should move
    assert moved_blocked.position == (1, 3)

    # Test moving into wall
    wall_robot = create_robot(position=(1, 1), orientation='N')
    moved_wall = move_robot(wall_robot, 'forward', maze)
    assert moved_wall.position == (1, 1)  # Blocked by wall, stays in place

    print("  ✓ Robot movement works correctly")


def test_sensors():
    """Test sensor functions."""
    print("Testing sensors...")

    # Create test maze
    grid = (
        ('#', '#', '#', '#', '#'),
        ('#', '.', '.', '.', '#'),
        ('#', '.', '#', '.', '#'),
        ('#', '.', '.', '.', '#'),
        ('#', '#', '#', '#', '#'),
    )

    maze = Maze(
        grid=grid,
        start_pos=(1, 1),
        exit_pos=(3, 3),
        dimensions=(5, 5)
    )

    robot = create_robot(position=(1, 1), orientation='E')

    # Test infrared sensor (detects immediate obstacles)
    front_reading = infrared_sensor(robot, maze, 'front')
    assert front_reading.sensor_type == 'infrared'
    assert front_reading.direction == 'front'
    assert front_reading.value == False  # No obstacle immediately in front

    # Test ultrasound sensor (measures distance)
    front_distance = ultrasound_sensor(robot, maze, 'front')
    assert front_distance.sensor_type == 'ultrasound'
    assert front_distance.direction == 'front'
    assert front_distance.value > 0  # Some distance to wall

    # Test sensor pointing at wall
    robot_facing_wall = create_robot(position=(1, 1), orientation='W')
    wall_reading = infrared_sensor(robot_facing_wall, maze, 'front')
    assert wall_reading.value == True  # Wall immediately in front

    print("  ✓ Sensors work correctly")


def test_simulation():
    """Test simulation functions."""
    print("Testing simulation...")

    # Create test maze
    grid = (
        ('#', '#', '#', '#', '#'),
        ('#', 'S', '.', 'E', '#'),
        ('#', '#', '#', '#', '#'),
    )

    maze = Maze(
        grid=grid,
        start_pos=(1, 1),
        exit_pos=(3, 1),
        dimensions=(5, 3)
    )

    sensor_config = {
        'sensors': [
            {'type': 'infrared', 'directions': ['front', 'left', 'right']}
        ]
    }

    # Create initial state
    initial_state = create_initial_state(maze, sensor_config)
    assert initial_state.robot.position == (1, 1)
    assert initial_state.step_count == 0

    # Test is_complete
    assert is_complete(initial_state) == False

    # Create state at exit
    at_exit_robot = create_robot(position=(3, 1), orientation='E', sensor_config=sensor_config)
    at_exit_state = replace(initial_state, robot=at_exit_robot)
    assert is_complete(at_exit_state) == True

    print("  ✓ Simulation functions work correctly")


def test_pure_functions():
    """Test that functions are actually pure (same input = same output)."""
    print("Testing function purity...")

    robot = create_robot(position=(5, 5), orientation='N')

    # Call rotate multiple times with same input
    result1 = rotate_robot(robot, 'right')
    result2 = rotate_robot(robot, 'right')

    # Results should be equal (same output for same input)
    assert result1.orientation == result2.orientation
    assert result1.position == result2.position

    # Original should be unchanged
    assert robot.orientation == 'N'

    print("  ✓ Functions are pure (deterministic and immutable)")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Robot Navigation System Tests")
    print("=" * 60 + "\n")

    try:
        test_maze_functions()
        test_robot_immutability()
        test_robot_movement()
        test_sensors()
        test_simulation()
        test_pure_functions()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
