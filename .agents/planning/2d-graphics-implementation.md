# Implementation Plan: 2D Graphics for Robot Navigation Simulation

## Overview

Add a graphical 2D visualization system to the robot navigation simulator while maintaining functional programming principles. The graphics system will provide real-time visualization of robot movement, path tracking, and sensor data.

## Goals

1. **Visual Maze Rendering**: Display maze walls, paths, start/exit positions
2. **Robot Visualization**: Animated robot with orientation indicators
3. **Path Tracking**: Visual trail of robot's path history
4. **Sensor Visualization**: Display sensor readings graphically
5. **Real-time Animation**: Smooth frame-by-frame simulation playback
6. **Control Interface**: Play/pause, speed control, step-through
7. **Metrics Display**: Real-time statistics overlay
8. **Maintain Functional Purity**: Keep core logic pure, isolate graphics as I/O

## Technology Choice

### Primary Option: Pygame
**Rationale:**
- Excellent for 2D graphics and animation
- Simple API suitable for functional approach
- Good performance for real-time rendering
- Active community and documentation
- Cross-platform support

**Alternatives Considered:**
- **Tkinter**: Too basic for smooth animation, less suitable for games/simulations
- **matplotlib**: Better for static plots, less ideal for real-time interactive graphics
- **PyQt5/PySide**: More complex, heavier dependency, overkill for this use case
- **pyglet**: Good alternative, but Pygame has better documentation/community

### Decision: **Pygame** for optimal balance of simplicity and capability

## Architecture Design

### Functional Programming Considerations

```python
# PURE: Rendering state to surface (returns Surface object)
def render_maze_surface(state: SimulationState, config: RenderConfig) -> pygame.Surface:
    """Pure function - creates surface from state"""
    pass

# PURE: Calculate visual positions from logical positions
def logical_to_screen(pos: Tuple[int, int], config: RenderConfig) -> Tuple[int, int]:
    """Pure coordinate transformation"""
    pass

# IMPURE: Display surface to screen (I/O operation)
def display_surface(screen: pygame.Surface, surface: pygame.Surface, pos: Tuple[int, int]) -> None:
    """Side effect: draws to screen"""
    pass

# IMPURE: Main event loop (I/O boundary)
def run_graphics_simulation(initial_state: SimulationState, strategy: StrategyFunction) -> None:
    """Event loop with I/O side effects"""
    pass
```

### Separation of Concerns

```
┌─────────────────────────────────────────┐
│         I/O Boundary (Impure)           │
│  - Event handling (keyboard, mouse)    │
│  - Screen updates (pygame.display)     │
│  - Main game loop                       │
└──────────────┬──────────────────────────┘
               │
               ↓ (passes pure state)
┌─────────────────────────────────────────┐
│      Rendering Logic (Pure)             │
│  - State → Surface conversion           │
│  - Color calculations                   │
│  - Coordinate transformations           │
│  - Layout calculations                  │
└──────────────┬──────────────────────────┘
               │
               ↓ (uses)
┌─────────────────────────────────────────┐
│      Core Simulation (Pure)             │
│  - Existing simulation engine           │
│  - State transformations                │
│  - Strategy execution                   │
└─────────────────────────────────────────┘
```

## Project Structure Changes

```
robot_navigation/
├── src/
│   ├── graphics/              # NEW: Graphics module
│   │   ├── __init__.py
│   │   ├── config.py         # Rendering configuration
│   │   ├── rendering.py      # Pure rendering functions
│   │   ├── colors.py         # Color schemes and palettes
│   │   ├── animations.py     # Animation helpers (pure)
│   │   └── ui_components.py  # UI element rendering (pure)
│   └── ... (existing modules)
├── examples/
│   ├── run_simulation.py     # Existing CLI
│   └── run_graphical.py      # NEW: Graphical runner
└── requirements.txt          # Add pygame dependency
```

## Component Design

### 1. Rendering Configuration (`config.py`)

```python
@dataclass(frozen=True)
class RenderConfig:
    """Immutable rendering configuration"""
    cell_size: int = 40           # Pixels per maze cell
    screen_width: int = 1024
    screen_height: int = 768
    fps: int = 60
    animation_speed: float = 1.0  # Simulation steps per second
    show_path: bool = True
    show_sensors: bool = True
    show_grid: bool = True
    color_scheme: str = "default"

@dataclass(frozen=True)
class ColorScheme:
    """Color palette for rendering"""
    background: Tuple[int, int, int] = (40, 40, 40)
    wall: Tuple[int, int, int] = (80, 80, 80)
    path: Tuple[int, int, int] = (200, 200, 200)
    robot: Tuple[int, int, int] = (100, 150, 255)
    start: Tuple[int, int, int] = (100, 255, 100)
    exit: Tuple[int, int, int] = (255, 100, 100)
    trail: Tuple[int, int, int] = (150, 150, 200)
    sensor_clear: Tuple[int, int, int] = (100, 255, 100)
    sensor_blocked: Tuple[int, int, int] = (255, 100, 100)
    ui_text: Tuple[int, int, int] = (255, 255, 255)
    ui_background: Tuple[int, int, int] = (30, 30, 30)
```

### 2. Pure Rendering Functions (`rendering.py`)

```python
# PURE: Render entire scene to surface
def render_simulation_state(
    state: SimulationState,
    config: RenderConfig,
    color_scheme: ColorScheme
) -> pygame.Surface:
    """
    PURE function - generates pygame Surface from state.
    No side effects, deterministic output.
    """
    surface = create_blank_surface(config)

    # Layer by layer rendering
    surface = draw_maze_layer(surface, state.maze, config, color_scheme)
    surface = draw_path_layer(surface, state.robot, config, color_scheme)
    surface = draw_robot_layer(surface, state.robot, config, color_scheme)

    return surface

# PURE: Coordinate transformation
def logical_to_screen(
    logical_pos: Tuple[int, int],
    config: RenderConfig,
    maze_dimensions: Tuple[int, int]
) -> Tuple[int, int]:
    """Convert maze coordinates to screen pixels"""
    x, y = logical_pos
    offset_x = (config.screen_width - maze_dimensions[0] * config.cell_size) // 2
    offset_y = 50  # Leave space for UI at top
    return (offset_x + x * config.cell_size, offset_y + y * config.cell_size)

# PURE: Draw maze walls and paths
def draw_maze_layer(
    surface: pygame.Surface,
    maze: Maze,
    config: RenderConfig,
    colors: ColorScheme
) -> pygame.Surface:
    """Draw the maze structure"""
    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            screen_pos = logical_to_screen((x, y), config, maze.dimensions)
            color = get_cell_color(cell, colors)
            draw_cell(surface, screen_pos, config.cell_size, color)
    return surface

# PURE: Draw robot with orientation
def draw_robot_layer(
    surface: pygame.Surface,
    robot: Robot,
    config: RenderConfig,
    colors: ColorScheme
) -> pygame.Surface:
    """Draw robot at current position with orientation indicator"""
    screen_pos = logical_to_screen(robot.position, config, ...)
    surface = draw_robot_body(surface, screen_pos, config, colors)
    surface = draw_orientation_arrow(surface, screen_pos, robot.orientation, config, colors)
    return surface
```

### 3. Sensor Visualization (`rendering.py`)

```python
# PURE: Render sensor readings
def draw_sensor_overlay(
    surface: pygame.Surface,
    robot: Robot,
    sensor_readings: List[SensorReading],
    config: RenderConfig,
    colors: ColorScheme
) -> pygame.Surface:
    """Visualize sensor data around robot"""
    for reading in sensor_readings:
        if reading.sensor_type == 'ultrasound':
            surface = draw_ultrasound_beam(surface, robot, reading, config, colors)
        elif reading.sensor_type == 'infrared':
            surface = draw_infrared_indicator(surface, robot, reading, config, colors)
    return surface

# PURE: Draw ultrasound beam visualization
def draw_ultrasound_beam(
    surface: pygame.Surface,
    robot: Robot,
    reading: SensorReading,
    config: RenderConfig,
    colors: ColorScheme
) -> pygame.Surface:
    """Draw a gradient beam showing ultrasound distance"""
    # Calculate beam start and end points
    # Draw gradient line with alpha based on distance
    return surface
```

### 4. UI Components (`ui_components.py`)

```python
@dataclass(frozen=True)
class UILayout:
    """UI element positions and sizes"""
    metrics_panel: Tuple[int, int, int, int]  # x, y, width, height
    controls_panel: Tuple[int, int, int, int]
    info_panel: Tuple[int, int, int, int]

# PURE: Render metrics panel
def render_metrics_panel(
    metrics: Dict[str, Any],
    layout: UILayout,
    colors: ColorScheme
) -> pygame.Surface:
    """Create surface with metrics display"""
    surface = create_panel_surface(layout.metrics_panel)
    # Render text lines
    return surface

# PURE: Render controls help
def render_controls_panel(
    layout: UILayout,
    colors: ColorScheme,
    paused: bool,
    speed: float
) -> pygame.Surface:
    """Display control instructions and current state"""
    return surface
```

### 5. Animation Helpers (`animations.py`)

```python
# PURE: Calculate interpolation between two positions
def interpolate_position(
    start: Tuple[int, int],
    end: Tuple[int, int],
    progress: float  # 0.0 to 1.0
) -> Tuple[float, float]:
    """Linear interpolation between positions"""
    x1, y1 = start
    x2, y2 = end
    return (
        x1 + (x2 - x1) * progress,
        y1 + (y2 - y1) * progress
    )

# PURE: Calculate rotation interpolation
def interpolate_rotation(
    start_orientation: str,
    end_orientation: str,
    progress: float
) -> float:
    """Calculate intermediate rotation angle"""
    start_angle = orientation_to_angle(start_orientation)
    end_angle = orientation_to_angle(end_orientation)
    return start_angle + (end_angle - start_angle) * progress
```

### 6. Main Graphical Runner (`examples/run_graphical.py`)

```python
# IMPURE: Main event loop
def run_graphical_simulation(
    initial_state: SimulationState,
    strategy: StrategyFunction,
    config: RenderConfig,
    max_steps: int = 1000
) -> None:
    """
    IMPURE: Main graphics loop with event handling.

    Isolates all I/O operations at the boundary.
    """
    pygame.init()
    screen = pygame.display.set_mode((config.screen_width, config.screen_height))
    clock = pygame.time.Clock()

    # Pure state management
    current_state = initial_state
    paused = False
    step_accumulator = 0.0

    running = True
    while running and not is_complete(current_state):
        # Event handling (IMPURE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                paused, config = handle_keypress(event, paused, config)

        # Simulation step (PURE logic)
        if not paused:
            step_accumulator += config.animation_speed / config.fps
            if step_accumulator >= 1.0:
                current_state = step_simulation(current_state, strategy)
                step_accumulator -= 1.0

        # Rendering (PURE functions → IMPURE display)
        sensor_readings = apply_sensors(current_state.robot, current_state.maze, ...)
        surface = render_simulation_state(current_state, config, color_scheme)
        surface = draw_sensor_overlay(surface, current_state.robot, sensor_readings, config, ...)
        ui_surface = render_ui(current_state, paused, config)

        # Display (IMPURE)
        screen.blit(surface, (0, 0))
        screen.blit(ui_surface, (0, 0))
        pygame.display.flip()
        clock.tick(config.fps)

    pygame.quit()
```

## Features Implementation

### Phase 1: Basic Visualization (MVP)
1. ✓ Maze grid rendering with walls/paths
2. ✓ Robot position and orientation
3. ✓ Path trail visualization
4. ✓ Start/exit markers
5. ✓ Basic metrics display

### Phase 2: Enhanced Visualization
1. ✓ Sensor beam visualization (ultrasound)
2. ✓ Sensor indicator lights (infrared)
3. ✓ Smooth animations between steps
4. ✓ Color-coded path (recent vs old)
5. ✓ Grid overlay toggle

### Phase 3: Interactive Controls
1. ✓ Play/Pause (SPACE)
2. ✓ Speed adjustment (+/-)
3. ✓ Single step (ENTER)
4. ✓ Reset simulation (R)
5. ✓ Toggle overlays (G=grid, S=sensors, P=path)
6. ✓ Zoom in/out (mouse wheel)

### Phase 4: Advanced Features
1. ✓ Side-by-side strategy comparison
2. ✓ Replay saved simulation
3. ✓ Export frames as images
4. ✓ Minimap for large mazes
5. ✓ Strategy selection menu

## User Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  Robot Navigation Simulator      [Metrics] [Controls]  │ ← Header (50px)
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    ┌───────────┐                        │
│                    │ # # # # # │                        │
│                    │ #S.·····# │                        │
│      Maze View     │ #·##·###│                        │
│    (Centered)      │ #····^··# │                        │
│                    │ # # # #E# │                        │
│                    └───────────┘                        │
│                                                         │
│   [Sensor beams shown as colored rays]                │
│   [Path shown as dotted trail]                         │
├─────────────────────────────────────────────────────────┤
│ Steps: 42 | Unique: 15 | Speed: 1.0x | [PAUSED]       │ ← Status (30px)
└─────────────────────────────────────────────────────────┘

Controls displayed as overlay when needed:
┌──────────────────────┐
│   CONTROLS           │
│ SPACE - Play/Pause   │
│ ENTER - Step         │
│ +/-   - Speed        │
│ R     - Reset        │
│ G/S/P - Toggles      │
│ ESC   - Quit         │
└──────────────────────┘
```

## Dependencies Update

### requirements.txt additions:
```
PyYAML>=6.0
pygame>=2.5.0
```

### Optional enhancements:
```
pygame-gui>=0.6.0    # For advanced UI widgets (future)
numpy>=1.24.0        # For advanced graphics calculations (future)
```

## Testing Strategy

### Graphics Testing
Since graphics are I/O operations, test the pure functions separately:

```python
def test_coordinate_transformation():
    """Test pure coordinate conversion"""
    config = RenderConfig(cell_size=40, screen_width=800, screen_height=600)
    maze_dims = (10, 10)

    result = logical_to_screen((5, 5), config, maze_dims)
    # Assert expected screen coordinates
    assert result == (expected_x, expected_y)

def test_rendering_determinism():
    """Test that rendering is deterministic"""
    state = create_test_state()
    config = RenderConfig()
    colors = ColorScheme()

    surface1 = render_simulation_state(state, config, colors)
    surface2 = render_simulation_state(state, config, colors)

    # Surfaces should be identical
    assert surfaces_equal(surface1, surface2)
```

### Integration Testing
- Manual testing for visual appearance
- Screenshot comparison tests (optional, advanced)
- Performance benchmarks (FPS, memory usage)

## Performance Considerations

### Optimization Strategies
1. **Dirty Rectangle Updates**: Only redraw changed areas (if needed)
2. **Surface Caching**: Cache static maze background
3. **Lazy Rendering**: Only render visible area for large mazes
4. **Efficient Blitting**: Use pygame's optimized blit operations
5. **Frame Rate Control**: Cap at 60 FPS for smooth experience

### Performance Targets
- **60 FPS** for smooth animation
- **< 100ms** frame time for mazes up to 50x50
- **< 50MB** memory overhead for graphics

## Implementation Timeline

### Week 1: Foundation
- Set up pygame infrastructure
- Implement basic rendering configuration
- Create pure rendering functions for maze
- Basic window and event loop

### Week 2: Core Visualization
- Robot rendering with orientation
- Path trail visualization
- Coordinate transformation system
- Basic UI overlay

### Week 3: Sensors & Animation
- Sensor visualization (beams, indicators)
- Smooth animation between steps
- Color schemes and themes
- Enhanced metrics display

### Week 4: Interactivity
- Keyboard controls (play/pause, speed, step)
- Toggle overlays (grid, sensors, path)
- Reset and replay functionality
- Polish and testing

## Risk Mitigation

### Risks & Solutions

1. **Risk**: Graphics breaks functional purity
   - **Solution**: Strict separation of pure rendering logic from I/O operations
   - **Validation**: Code review, type hints, documentation

2. **Risk**: Performance issues with large mazes
   - **Solution**: Implement lazy rendering, surface caching
   - **Mitigation**: Profile early, optimize hot paths

3. **Risk**: Cross-platform compatibility issues
   - **Solution**: Use pygame's cross-platform features
   - **Testing**: Test on Windows, macOS, Linux

4. **Risk**: Pygame learning curve
   - **Solution**: Start with simple MVP, iterate
   - **Resources**: Extensive pygame documentation and examples

## Success Criteria

### Must Have (MVP)
- ✓ Displays maze visually with walls and paths
- ✓ Shows robot position and orientation
- ✓ Visualizes path history
- ✓ Real-time animation of simulation
- ✓ Basic controls (play/pause, quit)
- ✓ Maintains functional programming principles

### Should Have
- ✓ Sensor visualization
- ✓ Speed control
- ✓ Metrics overlay
- ✓ Smooth animations
- ✓ Multiple color schemes

### Nice to Have
- ✓ Strategy comparison view
- ✓ Replay functionality
- ✓ Export to images/video
- ✓ Minimap for navigation
- ✓ Custom theme editor

## Documentation Updates

### Files to Update
1. **README.md**: Add graphics usage examples
2. **CLAUDE.md**: Document graphics architecture
3. **requirements.txt**: Add pygame dependency
4. **examples/README.md**: Create usage guide for graphical mode

### New Documentation
1. **GRAPHICS.md**: Detailed graphics system documentation
2. **CONTROLS.md**: User control reference
3. **THEMES.md**: Color scheme customization guide

## Conclusion

This implementation plan provides a clear path to adding 2D graphics while preserving the functional programming principles that define the project. The separation of pure rendering logic from I/O operations ensures testability and maintainability. The phased approach allows for incremental development and early validation of design decisions.

**Next Steps:**
1. Review and approve plan
2. Set up pygame development environment
3. Begin Phase 1 implementation (MVP)
4. Iterate based on testing and feedback
