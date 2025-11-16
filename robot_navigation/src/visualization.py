"""
Visualization functions for the robot navigation simulation.

Functions that return strings are PURE.
Functions that print to console are IMPURE (I/O side effect).
"""
from typing import List, Dict, Any
from .types import SimulationState, SensorReading


# Robot orientation symbols
ROBOT_SYMBOLS = {
    'N': '^',
    'S': 'v',
    'E': '>',
    'W': '<'
}


def render_maze(state: SimulationState) -> str:
    """
    Render the maze with robot position.

    PURE function - returns string representation.

    Args:
        state: Current simulation state

    Returns:
        String representation of maze with robot
    """
    lines = []
    robot_pos = state.robot.position
    robot_symbol = ROBOT_SYMBOLS[state.robot.orientation]

    for y, row in enumerate(state.maze.grid):
        line_chars = []
        for x, cell in enumerate(row):
            if (x, y) == robot_pos:
                line_chars.append(robot_symbol)
            elif (x, y) in state.robot.path_history[:-1]:
                # Show path with dots (except current position)
                if cell in '.SE':
                    line_chars.append('·')
                else:
                    line_chars.append(cell)
            else:
                line_chars.append(cell)
        lines.append(''.join(line_chars))

    return '\n'.join(lines)


def render_sensor_readings(readings: List[SensorReading]) -> str:
    """
    Render sensor readings as formatted string.

    PURE function.

    Args:
        readings: List of sensor readings

    Returns:
        Formatted string representation
    """
    if not readings:
        return "No sensor readings"

    lines = ["Sensor Readings:"]

    # Group by sensor type
    by_type = {}
    for reading in readings:
        if reading.sensor_type not in by_type:
            by_type[reading.sensor_type] = []
        by_type[reading.sensor_type].append(reading)

    for sensor_type, sensor_readings in by_type.items():
        lines.append(f"  {sensor_type.capitalize()}:")
        for reading in sensor_readings:
            value_str = str(reading.value)
            lines.append(f"    {reading.direction:>5}: {value_str}")

    return '\n'.join(lines)


def render_metrics(metrics: Dict[str, Any]) -> str:
    """
    Render simulation metrics as formatted string.

    PURE function.

    Args:
        metrics: Dictionary of metrics

    Returns:
        Formatted string representation
    """
    lines = ["Simulation Metrics:"]

    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            lines.append(f"  {key}: {value:.2f}")
        else:
            lines.append(f"  {key}: {value}")

    return '\n'.join(lines)


def render_state_summary(state: SimulationState) -> str:
    """
    Render a summary of the current state.

    PURE function.

    Args:
        state: Current simulation state

    Returns:
        Formatted summary string
    """
    lines = [
        f"Step: {state.step_count}",
        f"Position: {state.robot.position}",
        f"Orientation: {state.robot.orientation}",
        f"Path length: {len(state.robot.path_history)}"
    ]
    return '\n'.join(lines)


def render_full_state(state: SimulationState, sensor_readings: List[SensorReading] = None) -> str:
    """
    Render complete state including maze, stats, and sensors.

    PURE function.

    Args:
        state: Current simulation state
        sensor_readings: Optional list of sensor readings to display

    Returns:
        Complete formatted state string
    """
    parts = [
        "=" * 50,
        render_state_summary(state),
        "-" * 50,
        render_maze(state),
        "-" * 50
    ]

    if sensor_readings:
        parts.append(render_sensor_readings(sensor_readings))
        parts.append("-" * 50)

    parts.append(render_metrics(state.metrics))
    parts.append("=" * 50)

    return '\n'.join(parts)


def display_state(state: SimulationState, sensor_readings: List[SensorReading] = None) -> None:
    """
    Display the current state to console.

    IMPURE function - performs I/O.

    Args:
        state: Current simulation state
        sensor_readings: Optional list of sensor readings to display
    """
    output = render_full_state(state, sensor_readings)
    print(output)


def display_final_results(states: List[SimulationState], metrics: Dict[str, Any]) -> None:
    """
    Display final simulation results.

    IMPURE function - performs I/O.

    Args:
        states: All simulation states
        metrics: Final calculated metrics
    """
    if not states:
        print("No simulation states to display")
        return

    final_state = states[-1]

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print()
    print(render_maze(final_state))
    print()
    print(render_metrics(metrics))
    print("=" * 60)


def create_progress_bar(current: int, total: int, width: int = 40) -> str:
    """
    Create a text-based progress bar.

    PURE function.

    Args:
        current: Current progress value
        total: Total value
        width: Width of progress bar in characters

    Returns:
        Progress bar string
    """
    if total == 0:
        progress = 0
    else:
        progress = current / total

    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    percentage = progress * 100

    return f"[{bar}] {percentage:.1f}% ({current}/{total})"


def render_compact_state(state: SimulationState) -> str:
    """
    Render a compact one-line state representation.

    PURE function.

    Args:
        state: Current simulation state

    Returns:
        Compact state string
    """
    return (
        f"Step {state.step_count:4d} | "
        f"Pos: {state.robot.position} | "
        f"Orient: {state.robot.orientation} | "
        f"Path: {len(state.robot.path_history)}"
    )
