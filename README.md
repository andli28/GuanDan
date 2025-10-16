# Guan Dan Game Engine

This repository contains a Python implementation of the card game "Guan Dan" (Throwing Eggs). It includes a game engine that handles the rules and logic of the game, along with a simple AI agent capable of playing a basic game.

## About Guan Dan

Guan Dan is a popular Chinese card game played by four players in two fixed partnerships. It uses a double deck of 108 cards (two standard 52-card decks plus four jokers). The primary objective is for your team to be the first to play all of your cards. The game involves strategy, teamwork, and understanding a unique hierarchy of card combinations.

For a detailed explanation of the game's rules, please see the [rules.md](rules.md) file.

## Getting Started

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:andli28/GuanDan.git
    cd GuanDan
    ```

2.  **Create and activate a virtual environment:**
    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate
    ```
    Using `venv`:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the project in editable mode:**
    This allows you to run the game and tests directly from the source code.
    Using `uv`:
    ```bash
    uv pip install -e .
    ```
    Using `pip`:
    ```bash
    pip install -e .
    ```

## How to Run

### Running the Game Simulation

To see the game in action, you can run the main simulation script. This will pit four `SimpleAgent` AI players against each other and print the results of each hand to the console.

```bash
python src/engine.py
```

### Running the Tests

The project includes a suite of unit tests to ensure the game logic is correct. To run the tests, use the following command from the root of the repository:

Using `uv`:
```bash
uv run python -m unittest discover tests
```

Using `python`:
```bash
python -m unittest discover tests
```

## Project Structure

-   `src/engine.py`: Contains the core game logic, including the `GuanDanGame` class, `Player` and `Card` representations, and the `SimpleAgent` AI.
-   `tests/test_engine.py`: Unit tests for the game engine.
-   `rules.md`: A document detailing the rules of Guan Dan.
-   `pyproject.toml`: Project configuration and dependencies.