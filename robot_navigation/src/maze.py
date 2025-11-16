"""
Pure functions for loading and querying mazes.

All functions in this module are pure except for I/O operations
(load_maze_from_yaml, load_maze_from_markdown) which are clearly marked.
"""
from typing import Tuple, Optional
import yaml
from .types import Maze


def load_maze_from_yaml(filepath: str) -> Maze:
    """
    Load a maze from a YAML file.

    IMPURE: Performs I/O operation (file reading).

    Args:
        filepath: Path to the YAML file

    Returns:
        Maze object

    YAML Format:
        dimensions: [width, height]
        start: [x, y]
        exit: [x, y]
        grid:
          - "######"
          - "#S...#"
          - "#.##.#"
          - "#...E#"
          - "######"
    """
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)

    # Convert list of strings to immutable tuple of tuples
    grid_rows = data['grid']
    grid = tuple(tuple(row) for row in grid_rows)

    dimensions = tuple(data['dimensions'])
    start_pos = tuple(data['start'])
    exit_pos = tuple(data['exit'])

    return Maze(
        grid=grid,
        start_pos=start_pos,
        exit_pos=exit_pos,
        dimensions=dimensions
    )


def load_maze_from_markdown(filepath: str) -> Maze:
    """
    Load a maze from a Markdown file with ASCII art.

    IMPURE: Performs I/O operation (file reading).

    Args:
        filepath: Path to the Markdown file

    Returns:
        Maze object

    Format:
        # walls, . paths, S start, E exit

    Example:
        ######
        #S...#
        #.##.#
        #...E#
        ######
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Extract maze lines (skip markdown formatting)
    maze_lines = []
    for line in lines:
        stripped = line.rstrip()
        # Only include lines that look like maze rows
        if stripped and all(c in '#.SE ' for c in stripped):
            maze_lines.append(stripped)

    if not maze_lines:
        raise ValueError("No valid maze lines found in file")

    # Convert to immutable grid
    grid = tuple(tuple(row) for row in maze_lines)

    # Find start and exit positions
    start_pos = None
    exit_pos = None
    height = len(grid)
    width = max(len(row) for row in grid) if grid else 0

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == 'S':
                start_pos = (x, y)
            elif cell == 'E':
                exit_pos = (x, y)

    if start_pos is None:
        raise ValueError("No start position 'S' found in maze")
    if exit_pos is None:
        raise ValueError("No exit position 'E' found in maze")

    return Maze(
        grid=grid,
        start_pos=start_pos,
        exit_pos=exit_pos,
        dimensions=(width, height)
    )


def is_valid_position(maze: Maze, position: Tuple[int, int]) -> bool:
    """
    Check if a position is valid (within bounds and not a wall).

    PURE function.

    Args:
        maze: Maze object
        position: Position tuple (x, y)

    Returns:
        True if position is valid, False otherwise
    """
    x, y = position
    width, height = maze.dimensions

    # Check bounds
    if x < 0 or y < 0 or y >= height:
        return False

    # Check if row exists and x is within row bounds
    if y >= len(maze.grid):
        return False

    row = maze.grid[y]
    if x >= len(row):
        return False

    # Check if it's not a wall
    cell = row[x]
    return cell != '#'


def is_exit_position(maze: Maze, position: Tuple[int, int]) -> bool:
    """
    Check if a position is the exit.

    PURE function.

    Args:
        maze: Maze object
        position: Position tuple (x, y)

    Returns:
        True if position is the exit, False otherwise
    """
    return position == maze.exit_pos


def get_cell(maze: Maze, position: Tuple[int, int]) -> Optional[str]:
    """
    Get the cell content at a position.

    PURE function.

    Args:
        maze: Maze object
        position: Position tuple (x, y)

    Returns:
        Cell character or None if out of bounds
    """
    x, y = position

    if y < 0 or y >= len(maze.grid):
        return None

    row = maze.grid[y]
    if x < 0 or x >= len(row):
        return None

    return row[x]


def get_neighbors(maze: Maze, position: Tuple[int, int]) -> Tuple[Tuple[int, int], ...]:
    """
    Get valid neighboring positions (up, down, left, right).

    PURE function.

    Args:
        maze: Maze object
        position: Position tuple (x, y)

    Returns:
        Tuple of valid neighbor positions
    """
    x, y = position
    potential_neighbors = [
        (x, y - 1),  # North
        (x, y + 1),  # South
        (x - 1, y),  # West
        (x + 1, y),  # East
    ]

    return tuple(
        pos for pos in potential_neighbors
        if is_valid_position(maze, pos)
    )
