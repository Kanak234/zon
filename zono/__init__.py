"""GUNO ZONO: Horizon Protocol - Cyberpunk card game engine and interfaces."""
from __future__ import annotations

from zono.card import COLOR_HEX, COLORS, Card
from zono.cli import ZonoCLI
from zono.deck import Deck
from zono.engine import GameEngine
from zono.events import WorldEventManager, WorldEventType
from zono.player import Player
from zono.profile import PlayerProfile, ProfileManager

__version__ = "1.0.0"
__all__ = [
    "COLORS",
    "COLOR_HEX",
    "Card",
    "Deck",
    "GameEngine",
    "Player",
    "PlayerProfile",
    "ProfileManager",
    "WorldEventManager",
    "WorldEventType",
    "ZonoCLI",
]
