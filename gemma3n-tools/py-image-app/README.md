# Text Pattern Generator

This project contains a simple command-line application written in Python that can generate a variety of text-based patterns such as triangles, pyramids, squares, and diamonds. It can be used either by providing command-line arguments or interactively prompting the user.

## Features

- Generate four types of patterns:
  - **Triangle** – Left‑justified growing block of characters.
  - **Pyramid** – Centered, odd‑length characters growing symmetrically.
  - **Square** – A block of equal‑length rows.
  - **Diamond** – Centered, symmetrical pattern; size must be an odd number, or the program will adjust it.
- Supports custom characters for drawing the pattern.
- If no arguments are supplied, the program asks for input interactively.

## Installation

The script requires only the Python 3 standard library. No external dependencies are needed.

```bash
python3 -m venv venv   # Optional: create a virtual environment
source venv/bin/activate
python main.py        # Run the script
```

## Usage

```bash
python main.py --type triangle --size 5 --char #
```

You can also use it interactively:

```bash
python main.py
# Follow the prompts
```

## Contribution

Feel free to submit pull requests or issues. The repository follows standard Python conventions.
