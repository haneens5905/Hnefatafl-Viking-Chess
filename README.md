# Hnefatafl — Viking Chess

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-3776AB?style=flat-square&logo=python&logoColor=white" alt="Tkinter" />
  <img src="https://img.shields.io/badge/AI-Alpha--Beta%20Pruning-2E8B57?style=flat-square" alt="Alpha-Beta" />
  <img src="https://img.shields.io/badge/Game-Strategy-8B0000?style=flat-square" alt="Strategy Game" />
</p>

A fully playable implementation of **Hnefatafl** (Viking Chess), an asymmetric two-player strategy board game, featuring an AI opponent powered by the **alpha-beta pruning** algorithm with three difficulty levels.

---

## Project Overview

- Two-player asymmetric game on an **11×11 board** — attackers vs defenders
- The **King** (defender side) must reach any corner to escape; the **attackers** must surround and capture the King
- All pieces move like a **Rook in chess** — any number of squares horizontally or vertically
- Pieces are captured by **custodial capture** — sandwiching an opponent between two of your pieces, or between your piece and a special square (throne, corner, or wall)
- The **King is unarmed** — he cannot assist in capturing opponent pieces
- AI opponent uses **alpha-beta pruning** to search the game tree and select the best move
- Three difficulty levels control how many moves ahead the AI looks — Easy (depth 1), Medium (depth 3), Hard (depth 5)
- Built with a **Tkinter GUI** featuring a Norse-themed dark aesthetic, move log, captured piece tracker, and splash screen

---

## Repository Structure

```
Hnefatafl-Viking-Chess/
├── README.md               ← project documentation
├── .gitignore              ← excludes cache and OS files
└── src/
    ├── board.py            ← board representation, constants, king capture/escape logic
    ├── moves.py            ← move generation, capture rules, sandwich prevention
    ├── game.py             ← game controller, player switching, input validation
    ├── utility.py          ← AI evaluation function and scoring heuristics
    ├── alpha_beta.py       ← alpha-beta pruning algorithm and difficulty levels
    ├── gui.py              ← Tkinter graphical interface
    └── tests.py            ← 227 unit and integration tests across all modules
```

---

## Architecture

The project is split into five independent modules that build on each other:

| Module | Responsibility |
|--------|---------------|
| `board.py` | Defines the board as an 11×11 2D list. Handles piece constants, special squares (throne, corners), deep board copying, and king capture/escape detection |
| `moves.py` | Generates all legal moves for a player. Enforces rook movement, restricted squares, sandwich prevention, and all four capture types |
| `game.py` | Runs the game loop. Handles turn switching, human input validation, AI move retrieval, board updates, and end-game detection |
| `utility.py` | Evaluates any board state with a score. Considers king distance to corners, escape paths, king mobility, king encirclement, and piece count |
| `alpha_beta.py` | Implements the alpha-beta pruning search. Explores the game tree to a given depth, prunes irrelevant branches, and returns the best move |

---

## Capture Rules

| Type | Description |
|------|-------------|
| Custodial | Piece sandwiched between two opponents horizontally or vertically |
| Throne | Piece sandwiched between an opponent and the empty throne |
| Corner | Piece sandwiched between an opponent and a corner square |
| Wall | Piece sandwiched between an opponent and the board edge |
| King capture | King surrounded on all 4 sides (3 if against a wall, 2 if against a corner) |

---

## How to Run

**Requirements:** Python 3.8 or higher — no additional libraries needed (Tkinter is built into Python)

**Run the GUI:**
```bash
cd src
python gui.py
```

**Run the terminal version:**
```bash
cd src
python game.py
```

**Run all tests:**
```bash
cd src
python tests.py
```

Expected test output:
```
TOTAL: 227 passed, 0 failed out of 227 tests
```

---

## AI — How It Works

The AI uses **alpha-beta pruning**, an optimisation of the minimax algorithm that skips branches of the game tree that cannot affect the final decision.

- **Alpha (α)** — the best score the maximising player is guaranteed so far
- **Beta (β)** — the best score the minimising player is guaranteed so far
- When **α ≥ β**, the remaining branches are pruned — they will never be chosen

The **utility function** scores any board state from a given player's perspective using five weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| King distance to corner | 6 | Closer king = higher defender score |
| King escape paths | 30 | Clear straight-line paths to corners |
| King mobility | 6 | Number of squares the king can move to |
| King encirclement | 12 | Number of king's sides blocked by attackers |
| Piece count | 4 | Remaining defenders vs attackers |

Move ordering is applied before each search level — moves are sorted by their immediate score so better moves are explored first, allowing the pruning to eliminate more branches.

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core implementation language |
| Tkinter | Graphical user interface |
| threading | Non-blocking AI move computation |
| math | Infinity values for alpha-beta terminal states |
