"""Cross-platform audio and sound cue dispatcher for GUNO ZONO."""
from __future__ import annotations

import sys


def play_sound(kind: str = "play") -> None:
    """Trigger an audio cue without throwing exceptions on any platform.

    Supports Windows Beep frequencies, terminal bell on Unix, and silent fallback.
    """
    try:
        if sys.platform.startswith("win"):
            import winsound  # type: ignore

            tones = {
                "play": (800, 120),
                "draw": (500, 200),
                "win": (1000, 400),
                "lose": (300, 400),
                "event": (900, 250),
                "wild": (850, 150),
            }
            freq, dur = tones.get(kind, (700, 150))
            winsound.Beep(freq, dur)
        else:
            # Unix / macOS fallback: write audible bell character if interactive
            if kind in {"win", "event"} and sys.stdout.isatty():
                sys.stdout.write("\a")
                sys.stdout.flush()
    except (ImportError, OSError):
        # Audio failure should never impede gameplay
        pass
