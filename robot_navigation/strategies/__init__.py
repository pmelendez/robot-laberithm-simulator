"""
Navigation strategies for the robot.

Each strategy module exports a 'strategy' function with the signature:
    strategy(robot: Robot, sensor_readings: List[SensorReading], maze: Maze) -> str
"""

__all__ = ['wall_follow', 'random_walk', 'greedy']
