# PDSA Games Portal

A central hub for educational algorithm visualization games that illustrate key concepts in Problem Solving and Data Structure Algorithms (PDSA).

## Games Included

The portal currently includes five algorithm visualization games:

1. **Eight Queens Puzzle** - Place eight queens on a chessboard so that no queen can attack another queen.
2. **Knight's Tour** - Find a sequence of moves for a knight to visit every square on a chessboard exactly once.
3. **Tic Tac Toe** - Classic game with AI opponents using Minimax and Alpha-Beta pruning algorithms.
4. **Tower of Hanoi** - Move disks from one rod to another following specific rules.
5. **Traveling Salesman** - Find the shortest route to visit all cities and return to the starting point.

## Requirements

The portal dashboard and games require Python 3.7+ and several libraries:

```
PyQt5>=5.15.0
pygame>=2.6.0
pandas>=2.0.0
numpy>=2.0.0
matplotlib>=3.0.0
```

## Installation

### Option 1: Use the provided Virtual Environment (Recommended)

The portal comes with a pre-configured virtual environment that has all the necessary dependencies installed:

```bash
# Activate the virtual environment
# On macOS/Linux:
source pdsa_env/bin/activate

# On Windows:
pdsa_env\Scripts\activate

# Then run the dashboard
python dashboard.py
```

### Option 2: Install dependencies in your system Python

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Portal

To run the PDSA Games Portal:

```bash
# If using the virtual environment (recommended):
source pdsa_env/bin/activate  # On macOS/Linux
python dashboard.py

# Or directly with:
python3 dashboard.py
```

The dashboard will display cards for each available game. Click the "START GAME" button on any card to launch that game.

## Dependency Management

The dashboard automatically uses the common virtual environment when launching games, ensuring all dependencies are available. The portal has been designed to work with a common set of libraries to ensure compatibility across all games.

## Individual Games

Each game can also be run directly from its directory:

```bash
# Examples (using the virtual environment):
python games/traveling_salesman_game/main.py
python games/tic_tac_toe_game/main.py
```

However, we recommend using the central dashboard for better user experience.

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are properly installed in the virtual environment
2. Check the log files (pdsa_games_portal.log) for error messages
3. For game-specific issues, check the individual game directories for additional documentation

## Virtual Environment Details

The project uses a common virtual environment (`pdsa_env`) that contains all dependencies needed for all games. This approach ensures:

- Consistent Python version and package versions across all games
- Simplified dependency management
- Easy installation for users