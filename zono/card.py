"""Card model and validation logic for GUNO ZONO: Horizon Protocol."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

COLORS: list[str] = ["Red", "Green", "Blue", "Yellow"]

COLOR_HEX: dict[str, str] = {
    "Red": "#ff4b2b",
    "Green": "#16a085",
    "Blue": "#00c6ff",
    "Yellow": "#f1c40f",
    "Wild": "#2c3e50",
}

ACTION_VALUES: set[str] = {"Skip", "Reverse", "Draw3", "Wild", "WildDraw5"}


@dataclass(frozen=True)
class Card:
    """Represents an individual playing card."""

    color: str
    value: int | str

    VALID_COLORS: ClassVar[set[str]] = {"Red", "Green", "Blue", "Yellow", "Wild"}

    def __post_init__(self) -> None:
        if self.color not in self.VALID_COLORS:
            raise ValueError(f"Invalid card color: '{self.color}'")
        if self.is_wild and self.value not in {"Wild", "WildDraw5"}:
            raise ValueError(f"Invalid wild card value: '{self.value}'")

    @property
    def is_wild(self) -> bool:
        """Return True if card is a Wild or WildDraw5 card."""
        return self.color == "Wild" or self.value in {"Wild", "WildDraw5"}

    @property
    def is_draw(self) -> bool:
        """Return True if card forces a draw penalty."""
        return self.value in {"Draw3", "WildDraw5"}

    @property
    def draw_amount(self) -> int:
        """Return base draw penalty count."""
        if self.value == "Draw3":
            return 3
        if self.value == "WildDraw5":
            return 5
        return 0

    @property
    def is_action(self) -> bool:
        """Return True if card is an action or wild card."""
        return str(self.value) in ACTION_VALUES

    def playable_on(self, top_card: Card, active_color: str | None = None) -> bool:
        """Determine if this card can be legally played on top of the given card."""
        if self.is_wild:
            return True

        target_color = active_color if (top_card.is_wild and active_color) else top_card.color
        return self.color == target_color or str(self.value) == str(top_card.value)

    def to_dict(self) -> dict[str, Any]:
        """Serialize card to a dictionary representation."""
        return {"color": self.color, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Card:
        """Deserialize card from a dictionary."""
        return cls(color=str(data["color"]), value=data["value"])

    def __str__(self) -> str:
        return f"[{self.color} {self.value}]"
