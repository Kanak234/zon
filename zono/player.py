"""Player and Bot AI decision strategies for GUNO ZONO."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from zono.card import COLORS, Card


@dataclass
class Player:
    """Represents a human or AI player in the game."""

    name: str
    is_human: bool = False
    ai_strategy: str | None = "normal"  # "normal", "aggressive", "boss"
    hand: list[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        """Add a single card to hand."""
        self.hand.append(card)

    def add_cards(self, cards: list[Card]) -> None:
        """Add multiple cards to hand."""
        self.hand.extend(cards)

    def remove_card_at(self, index: int) -> Card:
        """Remove and return card at index."""
        return self.hand.pop(index)

    @property
    def hand_size(self) -> int:
        """Count of cards currently held."""
        return len(self.hand)

    def playable_cards(self, top_card: Card, active_color: str | None = None) -> list[tuple[int, Card]]:
        """Return list of (index, card) tuples for all legally playable cards in hand."""
        playable: list[tuple[int, Card]] = []
        for idx, card in enumerate(self.hand):
            if card.playable_on(top_card, active_color):
                playable.append((idx, card))
        return playable

    def best_wild_color(self) -> str:
        """Determine optimal color choice for Wild cards based on hand distribution."""
        color_counts = Counter(c.color for c in self.hand if c.color in COLORS)
        if not color_counts:
            return COLORS[0]
        most_common = color_counts.most_common(1)
        return most_common[0][0]

    def choose_ai_move(
        self,
        top_card: Card,
        active_color: str | None = None,
        draw_stack: int = 0,
    ) -> tuple[int | None, str | None]:
        """Compute the best move for this AI player.

        Returns:
            (card_index, chosen_wild_color) if playing a card, or (None, None) to draw.
        """
        playable = self.playable_cards(top_card, active_color)
        if not playable:
            return None, None

        # If there is a draw stack penalty pending, can we stack another draw card?
        if draw_stack > 0:
            draw_cards = [(idx, c) for idx, c in playable if c.is_draw]
            if draw_cards:
                playable = draw_cards
            else:
                # Cannot stack draw card, must draw the penalty stack
                return None, None

        # Select card according to AI personality
        if self.ai_strategy == "boss":
            # Boss prioritizes Draw cards, Wilds, and Skip/Reverse
            def boss_score(item: tuple[int, Card]) -> int:
                _, c = item
                if c.value == "WildDraw5":
                    return 100
                if c.value == "Draw3":
                    return 80
                if c.value in {"Skip", "Reverse"}:
                    return 50
                if c.is_wild:
                    return 40
                return 10

            playable.sort(key=boss_score, reverse=True)

        elif self.ai_strategy == "aggressive":
            # Aggressive prioritizes high disruption action cards
            def aggro_score(item: tuple[int, Card]) -> int:
                _, c = item
                if c.is_draw:
                    return 90
                if c.is_action:
                    return 60
                return 20

            playable.sort(key=aggro_score, reverse=True)

        else:
            # Normal AI prioritizes matching color, then matching number, keeping Wild as last resort
            def normal_score(item: tuple[int, Card]) -> int:
                _, c = item
                if not c.is_wild and c.color == (active_color or top_card.color):
                    return 50
                if not c.is_wild and str(c.value) == str(top_card.value):
                    return 40
                if c.is_action:
                    return 30
                return 10

            playable.sort(key=normal_score, reverse=True)

        chosen_idx, chosen_card = playable[0]
        chosen_color = self.best_wild_color() if chosen_card.is_wild else None
        return chosen_idx, chosen_color
