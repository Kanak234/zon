# GUNO ZONO : Horizon Protocol (zon)

A production-ready cyberpunk sci-fi card game featuring dynamic world anomalies, boss encounters, persistent career progression, cross-platform audio cues, desktop Tkinter interface, and headless terminal CLI mode.

## Overview

`zon` is the flat-root distribution of the Horizon Protocol card engine:

- **Modular Architecture**: Complete separation of game rules (`zono.engine`), deck recycling (`zono.deck`), player & bot AI heuristics (`zono.player`), world events (`zono.events`), career progression (`zono.profile`), terminal CLI (`zono.cli`), and Tkinter GUI (`zono.gui`).
- **World Anomalies**:
  - `STABLE`: Standard sub-space transmission protocol.
  - `GLITCH`: Hand buffer memory corruption; random cards in hand are scrambled with the draw deck.
  - `GRAVITY SWAP`: Gravitational polarity reversal; direction of play flips immediately.
  - `BLACKOUT`: Sensory blackout; card faces and colors are blinded.
  - `DOUBLE DATA`: Bandwidth surge; all draw penalties (`Draw3`, `WildDraw5`) are doubled!
- **AI Archetypes & Boss Battles**:
  - `BETA-7`: Tactical combatant balancing suit matching with action card conservation.
  - `DELTA-2`: Defensive bot prioritizing hand thinning.
  - `GAMMA-9`: Standard AI pilot.
  - `ZERO-X (BOSS)`: High-threat boss unlocked when career wins reach 10+. Ruthlessly prioritizes offensive draw assaults.
- **Dual Interface Modes**:
  - **Desktop GUI**: Dark-mode cyberpunk dashboard with active Draw Card button, Wild color picker dialog, audio cues, and live status displays.
  - **Terminal CLI**: Full interactive text-mode gameplay (`--cli`), enabling execution in headless environments, Docker containers, and SSH sessions.
- **Career Progression**: Tracks career wins, losses, win rates, XP, credits, and pilot levels persisted across sessions in JSON.

## Directory Structure

```text
├── guno_zono_master.py       # Root entrypoint (GUI + CLI fallback)
├── zono/
│   ├── __init__.py           # Public API exports
│   ├── __main__.py           # CLI / GUI auto-detecting entrypoint
│   ├── audio.py              # Cross-platform sound cues
│   ├── card.py               # Card model, validation, and play rules
│   ├── cli.py                # Interactive terminal CLI mode
│   ├── deck.py               # 76-card deck with automated recycling
│   ├── engine.py             # Pure Python headless game engine
│   ├── events.py             # World event anomalies simulator
│   ├── gui.py                # Cyberpunk Tkinter desktop GUI
│   ├── player.py             # Player and Bot AI decision strategies
│   └── profile.py            # Career statistics and level progression
├── tests/
│   ├── test_card.py
│   ├── test_cli.py
│   ├── test_deck.py
│   ├── test_engine.py
│   ├── test_events.py
│   ├── test_player.py
│   └── test_profile.py
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── .github/workflows/ci.yml
```

## Installation & Setup

### Requirements

- Python 3.10+
- Optional: Tkinter (for Desktop GUI mode; CLI mode runs on all systems without Tkinter)

```bash
# Install locally in editable mode
pip install -e ".[dev]"
```

## Running the Game

### Direct Script Execution

```bash
# Launch GUI (or auto-fallback to CLI in headless environments)
python3 guno_zono_master.py

# Explicit terminal CLI mode
python3 guno_zono_master.py --cli
```

### Module / Console Script Launch

```bash
# Via Python module
python3 -m zono

# Via installed commands
zon
# or
guno-zono
```

## Running Tests

```bash
# Run 29 comprehensive unit and simulation tests
pytest tests/ -v

# Run code style and lint validation
ruff check .
```

## License

MIT
