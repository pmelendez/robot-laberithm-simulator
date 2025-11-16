# Robot Navigation Simulation System

A Python-based robot navigation simulation system built using **functional programming principles**. This system simulates a robot navigating through a maze using various sensors and navigation strategies.

## Overview

This project demonstrates pure functional programming in Python with:
- **Immutable data structures** (frozen dataclasses)
- **Pure functions** (no side effects except at I/O boundaries)
- **Higher-order functions** (strategies as function parameters)
- **Composability** (small, focused functions)
- **Type hints** throughout

## Features

- **Multiple Maze Formats**: Load mazes from YAML or Markdown files
- **Configurable Sensors**: Ultrasound and infrared sensors with flexible configuration
- **Pluggable Strategies**: Wall-following, random walk, and greedy navigation strategies
- **Pure Functional Design**: All core logic uses immutable data and pure functions
- **Visualization**: ASCII-based maze rendering with path tracking
- **CLI Interface**: Multiple execution modes (fast, step-by-step, animated)

## Project Structure

```
robot_navigation/
├── README.md
├── requirements.txt
├── config/
│   ├── mazes/
│   │   ├── simple.yaml          # Simple maze configuration
│   │   ├── medium.yaml          # Medium complexity maze
│   │   ├── complex.md           # Complex maze (Markdown)
│   │   └── tiny.md              # Tiny test maze
│   └── sensors/
│       ├── default_sensors.yaml # Full sensor configuration
│       └── minimal_sensors.yaml # Minimal sensors
├── src/
│   ├── __init__.py
│   ├── types.py                 # Immutable data structures
│   ├── maze.py                  # Maze loading and query functions
│   ├── robot.py                 # Robot state transformation functions
│   ├── sensors.py               # Sensor functions
│   ├── simulation.py            # Simulation engine
│   └── visualization.py         # Display functions
├── strategies/
│   ├── __init__.py
│   ├── wall_follow.py           # Wall-following strategy
│   ├── random_walk.py           # Random walk strategy
│   └── greedy.py                # Greedy (distance-based) strategy
├── examples/
│   └── run_simulation.py        # Main CLI script
└── tests/
    └── test_basic.py            # Basic functionality tests
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Run with defaults (simple maze, wall-follow strategy):

```bash
cd examples
python run_simulation.py
```

### Specify a maze and strategy:

```bash
python run_simulation.py \
  --maze ../config/mazes/complex.md \
  --strategy ../strategies/greedy.py
```

### Step-by-step mode (interactive):

```bash
python run_simulation.py --step-mode
```

### Animated mode:

```bash
python run_simulation.py --animated --speed 0.2
```

## Usage Examples

### Basic Usage

```python
from src import (
    load_maze_from_yaml,
    load_sensor_config,
    create_initial_state,
    run_simulation,
    calculate_metrics
)
from strategies.wall_follow import strategy

# Load configuration (I/O operations)
maze = load_maze_from_yaml('config/mazes/simple.yaml')
sensor_config = load_sensor_config('config/sensors/default_sensors.yaml')

# Create initial state (pure function)
initial_state = create_initial_state(maze, sensor_config)

# Run simulation (pure function)
states = run_simulation(initial_state, strategy, max_steps=1000)

# Calculate metrics (pure function)
metrics = calculate_metrics(states)

print(f"Completed: {metrics['completed']}")
print(f"Total steps: {metrics['total_steps']}")
print(f"Efficiency: {metrics['efficiency']:.2%}")
```

### Functional Pipeline Style

```python
from functools import partial

# Create a configured simulation runner
run_with_wall_follow = partial(
    run_simulation,
    strategy=wall_follow_strategy,
    max_steps=1000
)

# Run multiple simulations
mazes = [load_maze_from_yaml(f) for f in maze_files]
results = [
    run_with_wall_follow(create_initial_state(m, sensor_config))
    for m in mazes
]
```

## Core Concepts

### Immutable Data Structures

All data structures are immutable (frozen dataclasses):

```python
@dataclass(frozen=True)
class Robot:
    position: Tuple[int, int]
    orientation: str
    sensor_config: Dict[str, Any]
    path_history: Tuple[Tuple[int, int], ...]
```

### Pure Functions

Functions that transform state without side effects:

```python
def rotate_robot(robot: Robot, rotation: str) -> Robot:
    """Returns NEW robot with updated orientation."""
    # ... pure transformation
    return Robot(position=robot.position, orientation=new_orientation, ...)
```

### Strategy Functions

Strategies are pure functions with a common signature:

```python
def strategy(robot: Robot,
             sensor_readings: List[SensorReading],
             maze: Maze) -> str:
    """
    Returns next action: 'forward', 'left', 'right', 'backward'
    Pure function - deterministic, no side effects
    """
    # ... strategy logic
    return action
```

### Sensor Functions

Sensors as pure functions:

```python
def ultrasound_sensor(robot: Robot, maze: Maze, direction: str) -> SensorReading:
    """Returns distance to nearest wall (1-5 units)."""
    # ... pure calculation
    return SensorReading(sensor_type='ultrasound', value=distance, direction=direction)
```

## Maze File Formats

### YAML Format

```yaml
dimensions: [10, 7]
start: [1, 1]
exit: [8, 5]
grid:
  - "##########"
  - "#S.......#"
  - "#.####...#"
  - "#........E#"
  - "##########"
```

### Markdown Format

```markdown
# My Maze

\`\`\`
#######
#S....#
#.##..#
#....E#
#######
\`\`\`
```

- `#` = wall
- `.` = open path
- `S` = start position
- `E` = exit position

## Sensor Configuration

```yaml
sensors:
  - type: ultrasound
    directions:
      - front
      - left
      - right
  - type: infrared
    directions:
      - front
      - left
      - right
      - back
```

## Creating Custom Strategies

Create a new Python file with a `strategy` function:

```python
# my_strategy.py
from typing import List
from src.types import Robot, Maze, SensorReading

def strategy(robot: Robot,
             sensor_readings: List[SensorReading],
             maze: Maze) -> str:
    """
    Your custom strategy logic.

    Must return one of: 'forward', 'left', 'right', 'backward'
    """
    # Your logic here
    return 'forward'
```

Then use it:

```bash
python run_simulation.py --strategy my_strategy.py
```

## Built-in Strategies

### Wall Follow Strategy
Implements the "right-hand rule" - guaranteed to find the exit in simply-connected mazes.

### Random Walk Strategy
Randomly explores the maze while avoiding walls (uses deterministic pseudo-random for purity).

### Greedy Strategy
Always moves toward the exit using Manhattan distance (may get stuck in dead ends).

## Testing

Run the test suite:

```bash
cd tests
python test_basic.py
```

Tests verify:
- Maze query functions work correctly
- Robot operations maintain immutability
- Movement functions handle walls properly
- Sensors return correct readings
- Simulation state transitions work
- Functions are pure (deterministic)

## Functional Programming Principles

This project demonstrates:

1. **Immutability**: All data structures are immutable
2. **Pure Functions**: Core logic has no side effects
3. **Higher-Order Functions**: Strategies passed as function parameters
4. **Composability**: Small, focused functions that compose well
5. **Type Safety**: Comprehensive type hints
6. **Separation of Concerns**: Pure logic separated from I/O
7. **Determinism**: Same inputs always produce same outputs

### Pure vs. Impure Functions

**Pure Functions** (most of the codebase):
- `rotate_robot()` - transforms robot state
- `move_robot()` - computes new position
- `ultrasound_sensor()` - calculates distance
- `step_simulation()` - computes next state
- `render_maze()` - generates string representation

**Impure Functions** (I/O boundary only):
- `load_maze_from_yaml()` - reads file
- `load_sensor_config()` - reads file
- `display_state()` - prints to console

## Extensibility

The system is designed for easy extension:

### Add a New Sensor

```python
def my_sensor(robot: Robot, maze: Maze, direction: str) -> SensorReading:
    """Your sensor logic."""
    return SensorReading(
        sensor_type='my_sensor',
        value=computed_value,
        direction=direction
    )
```

Register it in `sensors.py`:

```python
sensors = {
    'ultrasound': ultrasound_sensor,
    'infrared': infrared_sensor,
    'my_sensor': my_sensor,  # Add here
}
```

### Add a New Maze Loader

```python
def load_maze_from_json(filepath: str) -> Maze:
    """Load maze from JSON format."""
    # Your loading logic
    return Maze(grid=..., start_pos=..., exit_pos=..., dimensions=...)
```

### Add a New Visualization

```python
def render_maze_html(state: SimulationState) -> str:
    """Render maze as HTML."""
    # Your rendering logic
    return html_string
```

## CLI Options

```
usage: run_simulation.py [-h] [--maze MAZE] [--sensors SENSORS]
                        [--strategy STRATEGY] [--max-steps MAX_STEPS]
                        [--step-mode] [--animated] [--speed SPEED]

optional arguments:
  --maze MAZE           Path to maze configuration file (.yaml or .md)
  --sensors SENSORS     Path to sensor configuration file
  --strategy STRATEGY   Path to strategy module
  --max-steps MAX_STEPS Maximum number of simulation steps
  --step-mode          Run in step-by-step mode with user interaction
  --animated           Run with animation
  --speed SPEED        Animation speed in seconds per step
```

## Examples

### Compare Strategies

```bash
# Test wall-follow
python run_simulation.py --maze ../config/mazes/complex.md --strategy ../strategies/wall_follow.py

# Test greedy
python run_simulation.py --maze ../config/mazes/complex.md --strategy ../strategies/greedy.py

# Test random walk
python run_simulation.py --maze ../config/mazes/complex.md --strategy ../strategies/random_walk.py
```

### Different Mazes

```bash
# Tiny maze (quick test)
python run_simulation.py --maze ../config/mazes/tiny.md

# Medium maze
python run_simulation.py --maze ../config/mazes/medium.yaml

# Complex maze
python run_simulation.py --maze ../config/mazes/complex.md
```

## Performance Characteristics

- **Time Complexity**: O(steps × sensors × maze_query)
- **Space Complexity**: O(steps) for storing state history
- **Immutability Overhead**: Minimal due to structural sharing in Python

## Contributing

To add features:
1. Keep functions pure wherever possible
2. Use immutable data structures
3. Add type hints
4. Document pure vs. impure functions
5. Write tests for new functionality

## License

This is an educational project demonstrating functional programming principles.

## Future Enhancements

Potential extensions:
- A* pathfinding strategy
- More sensor types (camera, compass, etc.)
- 3D maze support
- Multi-robot simulation
- Graphical visualization
- Performance profiling tools
- Parallel simulation execution

## Acknowledgments

This project demonstrates functional programming principles applied to robotics simulation, emphasizing immutability, pure functions, and composability.
