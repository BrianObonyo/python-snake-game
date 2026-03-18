
"""
snake_game.py
=============
A Snake game built with Python's tkinter library.

Author  : Brian Otieno Obonyo
Email   : brianprofocus@gmail.com
GitHub  : https://github.com/BrianObonyo
Portfolio: https://brianobonyo.dev

Features
--------
- Arrow keys + WASD controls
- Progressive speed increase as score grows
- Persistent high score for the session
- Pause / Resume with P or Space
- Restart without closing the window (Enter / R after Game Over)
- Proper OOP — Snake, Food, and Game are distinct classes
- No global canvas/window variables leaking out of the game class
"""

import random
import tkinter as tk
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────
#  CONFIGURATION
#  Change these values to adjust look and feel.
# ─────────────────────────────────────────────────────────────

@dataclass
class Config:
    """All tuneable game settings in one place."""

    width:        int = 500          # Canvas width  (pixels)
    height:       int = 500          # Canvas height (pixels)
    cell:         int = 20           # Size of each grid cell (pixels)
    initial_speed: int = 180         # Starting delay between turns (ms)
    min_speed:    int = 60           # Fastest the snake can get (ms)
    speed_step:   int = 5            # How many ms to drop per food eaten
    initial_length: int = 3          # How many cells the snake starts with

    # Colours
    bg:           str = "#0d0d0d"    # Canvas background
    snake_head:   str = "#00ff99"    # Head cell colour
    snake_body:   str = "#007a47"    # Body cell colour
    food:         str = "#ff4757"    # Food colour
    grid:         str = "#1a1a1a"    # Subtle grid lines
    text_primary: str = "#ffffff"    # HUD text
    text_accent:  str = "#00ff99"    # Score highlight colour
    text_danger:  str = "#ff4757"    # Game-over text


# ─────────────────────────────────────────────────────────────
#  SNAKE
# ─────────────────────────────────────────────────────────────

class Snake:
    """
    Manages the snake's position, drawing, and growth.

    Attributes
    ----------
    coords : list[list[int, int]]
        Ordered list of [x, y] cell coordinates, head first.
    squares : list[int]
        Canvas item IDs for each body rectangle.
    """

    def __init__(self, canvas: tk.Canvas, config: Config) -> None:
        self.canvas = canvas
        self.cfg    = config
        self.coords: list[list[int, int]] = []
        self.squares: list[int]           = []

        # Start at the centre of the grid, horizontal
        start_x = (config.width  // 2 // config.cell) * config.cell
        start_y = (config.height // 2 // config.cell) * config.cell

        for i in range(config.initial_length):
            self.coords.append([start_x - i * config.cell, start_y])

        for idx, (x, y) in enumerate(self.coords):
            colour = config.snake_head if idx == 0 else config.snake_body
            sq = canvas.create_rectangle(
                x, y,
                x + config.cell, y + config.cell,
                fill=colour, outline=config.bg, width=2,
                tags="snake",
            )
            self.squares.append(sq)

    def move(self, nx: int, ny: int) -> None:
        """
        Advance the snake by one cell.

        Parameters
        ----------
        nx, ny : int
            New head position in pixels.
        """
        # Insert new head
        self.coords.insert(0, [nx, ny])
        sq = self.canvas.create_rectangle(
            nx, ny,
            nx + self.cfg.cell, ny + self.cfg.cell,
            fill=self.cfg.snake_head, outline=self.cfg.bg, width=2,
            tags="snake",
        )
        self.squares.insert(0, sq)

        # Recolour the old head to body colour
        if len(self.squares) > 1:
            self.canvas.itemconfig(self.squares[1], fill=self.cfg.snake_body)

    def shrink(self) -> None:
        """Remove the tail cell (called when no food was eaten)."""
        del self.coords[-1]
        self.canvas.delete(self.squares[-1])
        del self.squares[-1]

    @property
    def head(self) -> list[int, int]:
        """Current head position."""
        return self.coords[0]


# ─────────────────────────────────────────────────────────────
#  FOOD
# ─────────────────────────────────────────────────────────────

class Food:
    """
    Places a food item on a random empty cell.

    Attributes
    ----------
    coords : list[int, int]
        [x, y] pixel coordinates of the food item.
    """

    def __init__(
        self,
        canvas:       tk.Canvas,
        config:       Config,
        occupied:     list[list[int, int]],
    ) -> None:
        self.canvas = canvas
        self.cfg    = config
        self.coords = self._random_position(occupied)

        x, y = self.coords
        # Draw as a slightly inset oval to look different from snake squares
        pad = config.cell // 5
        canvas.create_oval(
            x + pad, y + pad,
            x + config.cell - pad, y + config.cell - pad,
            fill=config.food, outline="", tags="food",
        )

    def _random_position(
        self,
        occupied: list[list[int, int]],
    ) -> list[int, int]:
        """Pick a grid cell that the snake does not currently occupy."""
        cols = self.cfg.width  // self.cfg.cell
        rows = self.cfg.height // self.cfg.cell
        all_cells = [
            [c * self.cfg.cell, r * self.cfg.cell]
            for c in range(cols)
            for r in range(rows)
        ]
        free = [cell for cell in all_cells if cell not in occupied]
        return random.choice(free) if free else [0, 0]


# ─────────────────────────────────────────────────────────────
#  GAME
#  Contains all game state and orchestrates everything.
# ─────────────────────────────────────────────────────────────

class Game:
    """
    Main game controller.

    Responsibilities
    ----------------
    - Owns the Tk window, canvas, and HUD labels
    - Manages game state (running / paused / over)
    - Drives the game loop via window.after()
    - Tracks current score and session high score
    """

    def __init__(self) -> None:
        self.cfg = Config()

        # ── Window ──────────────────────────────────────────
        self.window = tk.Tk()
        self.window.title("Snake — Brian Otieno")
        self.window.resizable(False, False)
        self.window.configure(bg="#111111")

        # ── HUD ─────────────────────────────────────────────
        hud = tk.Frame(self.window, bg="#111111")
        hud.pack(fill=tk.X, padx=10, pady=(8, 4))

        self.score_label = tk.Label(
            hud, text="Score: 0",
            font=("Consolas", 14, "bold"),
            fg=self.cfg.text_accent, bg="#111111",
        )
        self.score_label.pack(side=tk.LEFT)

        self.hi_label = tk.Label(
            hud, text="Best: 0",
            font=("Consolas", 14),
            fg=self.cfg.text_primary, bg="#111111",
        )
        self.hi_label.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            hud, text="",
            font=("Consolas", 11),
            fg="#888888", bg="#111111",
        )
        self.status_label.pack(side=tk.LEFT, padx=16)

        # ── Canvas ──────────────────────────────────────────
        self.canvas = tk.Canvas(
            self.window,
            bg=self.cfg.bg,
            width=self.cfg.width,
            height=self.cfg.height,
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        # ── Controls hint ───────────────────────────────────
        hint = tk.Label(
            self.window,
            text="Arrow keys / WASD  ·  P or Space = Pause  ·  R or Enter = Restart",
            font=("Consolas", 9),
            fg="#555555", bg="#111111",
        )
        hint.pack(pady=(0, 8))

        # ── Centre window ───────────────────────────────────
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        sw, sh = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.window.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        # ── Key bindings ─────────────────────────────────────
        for key, fn in (
            ("<Left>",   lambda e: self.change_direction("left")),
            ("<Right>",  lambda e: self.change_direction("right")),
            ("<Up>",     lambda e: self.change_direction("up")),
            ("<Down>",   lambda e: self.change_direction("down")),
            ("a",        lambda e: self.change_direction("left")),
            ("d",        lambda e: self.change_direction("right")),
            ("w",        lambda e: self.change_direction("up")),
            ("s",        lambda e: self.change_direction("down")),
            ("p",        lambda e: self.toggle_pause()),
            ("<space>",  lambda e: self.toggle_pause()),
            ("r",        lambda e: self.restart()),
            ("<Return>", lambda e: self.restart()),
        ):
            self.window.bind(key, fn)

        # ── State ────────────────────────────────────────────
        self.high_score:  int  = 0
        self._after_id:   str  = ""   # handle to cancel scheduled turns

        # ── Start ─────────────────────────────────────────────
        self._draw_grid()
        self._new_game()
        self.window.mainloop()

    # ────────────────────────────────────────────────────────
    #  Setup helpers
    # ────────────────────────────────────────────────────────

    def _draw_grid(self) -> None:
        """Draw subtle grid lines once onto the canvas background."""
        cfg = self.cfg
        for x in range(0, cfg.width + 1, cfg.cell):
            self.canvas.create_line(x, 0, x, cfg.height, fill=cfg.grid, tags="grid")
        for y in range(0, cfg.height + 1, cfg.cell):
            self.canvas.create_line(0, y, cfg.width, y, fill=cfg.grid, tags="grid")

    def _new_game(self) -> None:
        """Initialise (or reset) all game state and begin the loop."""
        # Cancel any in-flight turn
        if self._after_id:
            self.window.after_cancel(self._after_id)
            self._after_id = ""

        # Clear everything except the grid
        self.canvas.delete("snake", "food", "overlay")

        self.score:     int  = 0
        self.direction: str  = "right"
        self._next_dir: str  = "right"   # buffered direction
        self.paused:    bool = False
        self.speed:     int  = self.cfg.initial_speed
        self.alive:     bool = True

        self._update_hud()
        self.status_label.config(text="")

        self.snake = Snake(self.canvas, self.cfg)
        self.food  = Food(self.canvas, self.cfg, self.snake.coords)

        self._after_id = self.window.after(self.speed, self._tick)

    # ────────────────────────────────────────────────────────
    #  Game loop
    # ────────────────────────────────────────────────────────

    def _tick(self) -> None:
        """One game step — move, check, schedule next."""
        if not self.alive or self.paused:
            return

        # Commit the buffered direction
        self.direction = self._next_dir

        hx, hy = self.snake.head

        offsets = {
            "up":    (0,               -self.cfg.cell),
            "down":  (0,               +self.cfg.cell),
            "left":  (-self.cfg.cell,  0),
            "right": (+self.cfg.cell,  0),
        }
        dx, dy = offsets[self.direction]
        nx, ny = hx + dx, hy + dy

        # Move the snake
        self.snake.move(nx, ny)

        # Ate food?
        if [nx, ny] == self.food.coords:
            self.score += 1
            self._update_hud()
            self.canvas.delete("food")
            self.food = Food(self.canvas, self.cfg, self.snake.coords)

            # Speed up (lower delay = faster), capped at min_speed
            self.speed = max(self.cfg.min_speed, self.speed - self.cfg.speed_step)
        else:
            self.snake.shrink()

        # Collision?
        if self._collision():
            self._end_game()
            return

        self._after_id = self.window.after(self.speed, self._tick)

    def _collision(self) -> bool:
        """Return True if the head is out of bounds or touching the body."""
        x, y = self.snake.head

        out_of_bounds = (
            x < 0 or x >= self.cfg.width or
            y < 0 or y >= self.cfg.height
        )
        self_collision = [x, y] in self.snake.coords[1:]

        return out_of_bounds or self_collision

    # ────────────────────────────────────────────────────────
    #  Controls
    # ────────────────────────────────────────────────────────

    def change_direction(self, new_dir: str) -> None:
        """
        Buffer a direction change.

        Prevents the snake from reversing on itself by
        disallowing direct 180° turns.
        """
        if not self.alive or self.paused:
            return

        opposites = {"left": "right", "right": "left", "up": "down", "down": "up"}
        if new_dir != opposites.get(self.direction):
            self._next_dir = new_dir

    def toggle_pause(self) -> None:
        """Pause or resume the game."""
        if not self.alive:
            return

        self.paused = not self.paused

        if self.paused:
            self.status_label.config(text="PAUSED")
            self._show_overlay("PAUSED", "#ffffff", size=36)
        else:
            self.status_label.config(text="")
            self.canvas.delete("overlay")
            self._after_id = self.window.after(self.speed, self._tick)

    def restart(self) -> None:
        """Start a new game at any time."""
        self._new_game()

    # ────────────────────────────────────────────────────────
    #  Game over
    # ────────────────────────────────────────────────────────

    def _end_game(self) -> None:
        """Handle end-of-game state."""
        self.alive = False

        if self.score > self.high_score:
            self.high_score = self.score
            self._update_hud()

        # Full-screen overlay
        self.canvas.create_rectangle(
            0, 0, self.cfg.width, self.cfg.height,
            fill="#000000", stipple="gray50", tags="overlay",
        )
        self.canvas.create_text(
            self.cfg.width // 2, self.cfg.height // 2 - 40,
            text="GAME OVER",
            font=("Consolas", 42, "bold"),
            fill=self.cfg.text_danger,
            tags="overlay",
        )
        self.canvas.create_text(
            self.cfg.width // 2, self.cfg.height // 2 + 10,
            text=f"Score: {self.score}",
            font=("Consolas", 22),
            fill=self.cfg.text_primary,
            tags="overlay",
        )
        if self.score == self.high_score and self.score > 0:
            self.canvas.create_text(
                self.cfg.width // 2, self.cfg.height // 2 + 45,
                text="★  New Best!",
                font=("Consolas", 16, "bold"),
                fill=self.cfg.text_accent,
                tags="overlay",
            )
        self.canvas.create_text(
            self.cfg.width // 2, self.cfg.height // 2 + 90,
            text="Press R or Enter to play again",
            font=("Consolas", 13),
            fill="#888888",
            tags="overlay",
        )

        self.status_label.config(text="Game Over")

    # ────────────────────────────────────────────────────────
    #  HUD helpers
    # ────────────────────────────────────────────────────────

    def _update_hud(self) -> None:
        self.score_label.config(text=f"Score: {self.score}")
        self.hi_label.config(text=f"Best: {self.high_score}")

    def _show_overlay(self, text: str, colour: str, size: int = 40) -> None:
        """Display a centred text overlay (used for pause)."""
        self.canvas.create_rectangle(
            0, 0, self.cfg.width, self.cfg.height,
            fill="#000000", stipple="gray50", tags="overlay",
        )
        self.canvas.create_text(
            self.cfg.width // 2, self.cfg.height // 2,
            text=text,
            font=("Consolas", size, "bold"),
            fill=colour,
            tags="overlay",
        )


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    Game()