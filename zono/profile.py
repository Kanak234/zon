"""Player profile persistence and progression tracking for GUNO ZONO."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class PlayerProfile:
    """Stores user career stats, currency, and unlockable rank."""

    name: str = "PILOT"
    wins: int = 0
    losses: int = 0
    credits: int = 500
    xp: int = 0
    level: int = 1
    games_played: int = 0

    def add_win(self, credit_reward: int = 1000, xp_reward: int = 500) -> None:
        """Record a victory and update progression metrics."""
        self.wins += 1
        self.games_played += 1
        self.credits += credit_reward
        self.xp += xp_reward
        self._check_level_up()

    def add_loss(self, credit_reward: int = 100, xp_reward: int = 50) -> None:
        """Record a defeat and grant consolation progression."""
        self.losses += 1
        self.games_played += 1
        self.credits += credit_reward
        self.xp += xp_reward
        self._check_level_up()

    def _check_level_up(self) -> None:
        """Recalculate level based on cumulative XP (1000 XP per level)."""
        self.level = max(1, (self.xp // 1000) + 1)

    @property
    def win_rate(self) -> float:
        """Calculate career win percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100.0

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlayerProfile:
        """Construct profile instance from stored dictionary data."""
        return cls(
            name=data.get("name", "PILOT"),
            wins=int(data.get("wins", 0)),
            losses=int(data.get("losses", 0)),
            credits=int(data.get("credits", 500)),
            xp=int(data.get("xp", 0)),
            level=int(data.get("level", 1)),
            games_played=int(data.get("games_played", 0)),
        )


class ProfileManager:
    """Manages disk persistence for player profiles."""

    DEFAULT_FILENAME: str = "zono_master_profile.json"

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath: Path = Path(filepath or self.DEFAULT_FILENAME)
        self.profile: PlayerProfile = self.load()

    def load(self) -> PlayerProfile:
        """Load player profile from disk or initialize defaults."""
        if not self.filepath.exists():
            return PlayerProfile()

        try:
            with open(self.filepath, encoding="utf-8") as f:
                data = json.load(f)
                return PlayerProfile.from_dict(data)
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            return PlayerProfile()

    def save(self) -> None:
        """Save current profile to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.profile.to_dict(), f, indent=2)
