<<<<<<< HEAD
#  Snake Game — Python / tkinter

A classic Snake game built with Python's built-in `tkinter` GUI library.  
No third-party dependencies — just Python.

**Author:** Brian Otieno Obonyo  
**Portfolio:** [brianobonyo.dev](https://brianobonyo.dev)  
**Email:** brianprofocus@gmail.com

---

## What It Demonstrates

This project is intentionally kept to pure Python stdlib to show:

- **Object-oriented design** — `Snake`, `Food`, and `Game` are separate classes with clear responsibilities
- **Game loop logic** — tick-based loop driven by `tkinter.after()` with cancellable scheduling
- **Event handling** — keyboard bindings, direction buffering to prevent 180° reversals
- **Collision detection** — boundary and self-collision checks
- **State management** — running / paused / game-over states without a framework
- **Progressive difficulty** — speed increases as score grows, capped at a minimum delay

---

## Features

| Feature | Detail |
|---|---|
| Controls | Arrow keys **and** WASD |
| Pause / Resume | `P` or `Space` |
| Restart | `R` or `Enter` after game over |
| Progressive speed | Gets faster every time you eat |
| Session high score | Tracked without a database |
| New best indicator | ★ shown on game over if you beat your high score |
| Grid overlay | Subtle visual grid so you can count cells |
| No external dependencies | Pure Python stdlib only |

---

## Screenshots

> The snake starts green (`#00ff99`) with a darker body (`#007a47`).  
> Food is red (`#ff4757`). Background is near-black (`#0d0d0d`).

---

## Requirements

- Python 3.8 or later
- `tkinter` — included with Python on Windows and macOS

**Linux** — if tkinter is missing:
```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter
```

---

## Running the Game

```bash
# Clone
git clone https://github.com/Brian-Otieno-dev/snake-game-python.git
cd snake-game-python

# Run — no install needed
python snake_game.py
```

---

## Configuration

All game settings are in the `Config` dataclass at the top of `snake_game.py`:

```python
@dataclass
class Config:
    width:          int = 500    # Canvas width in pixels
    height:         int = 500    # Canvas height in pixels
    cell:           int = 20     # Grid cell size in pixels
    initial_speed:  int = 180    # Starting turn delay (ms) — lower = faster
    min_speed:      int = 60     # Fastest the snake can reach (ms)
    speed_step:     int = 5      # How much faster each food makes the snake (ms)
    initial_length: int = 3      # Starting snake length in cells
```

Change any of these values to adjust the feel of the game.

---

## How It Works

```
Game.__init__()
  │
  ├── draws grid onto canvas
  ├── creates Snake and Food
  └── schedules first _tick() via window.after()

_tick()  (called every `speed` ms)
  │
  ├── commits buffered direction
  ├── calculates new head position
  ├── calls snake.move(nx, ny)
  ├── checks if food was eaten
  │     ├── YES → increment score, spawn new Food, increase speed
  │     └── NO  → call snake.shrink() to remove tail
  ├── checks for collision
  │     ├── YES → _end_game()
  │     └── NO  → schedule next _tick()
  └── repeats
```

Direction changes are **buffered** into `_next_dir` and committed at the start of each tick. This prevents the snake from reversing into itself if two keys are pressed in the same frame.

---

## Project Structure

```
snake-game-python/
├── snake_game.py   # All game logic — single file, no modules needed
└── README.md
```

---

## What I'd Add Next

- [ ] Persistent high score saved to a local file
- [ ] Levels with walls or obstacles
- [ ] Sound effects using `pygame` (would add as an optional dependency)
- [ ] A proper menu screen before the game starts
- [ ] Multiplayer on the same keyboard

---

## Licence

MIT — use it however you like.

---

*Part of my Python projects collection — [brianobonyo.dev](https://brianobonyo.dev)*
=======
# python-snake-game
A classic Snake game built with Python and pygame.
>>>>>>> aa66ecc2553e3f245c47833276046f622bd737ea
