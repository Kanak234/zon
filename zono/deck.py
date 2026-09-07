"""Deck construction and discard pile recycling for GUNO ZONO."""
from __future__ import annotations

import random

from zono.card import COLORS, Card


class Deck:
    """Manages the draw deck and discard pile with automated recycling."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._draw_pile: list[Card] = []
        self._discard_pile: list[Card] = []
        self.reset()

    def _create_standard_cards(self) -> list[Card]:
        """Construct full 76-card inventory."""
        cards: list[Card] = []
        for color in COLORS:
            for num in range(10):
                cards.append(Card(color=color, value=num))
            for action in ["Skip", "Reverse", "Draw3"]:
                cards.append(Card(color=color, value=action))
                cards.append(Card(color=color, value=action))

        for _ in range(6):
            cards.append(Card(color="Wild", value="Wild"))
            cards.append(Card(color="Wild", value="WildDraw5"))
        return cards

    def reset(self) -> None:
        """Reconstruct full 76-card deck and clear discard pile."""
        self._draw_pile = self._create_standard_cards()
        self._discard_pile = []
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the current draw pile."""
        self._rng.shuffle(self._draw_pile)

    def draw(self) -> Card:
        """Draw a single card from the deck, recycling discard pile or replenishing if empty."""
        if not self._draw_pile:
            self._recycle_discards()

        if not self._draw_pile:
            self._draw_pile = self._create_standard_cards()
            self.shuffle()

        return self._draw_pile.pop()

    def draw_multiple(self, count: int) -> list[Card]:
        """Draw `count` cards from the deck."""
        return [self.draw() for _ in range(count)]

    def discard(self, card: Card) -> None:
        """Add a card to the discard pile."""
        self._discard_pile.append(card)

    def _recycle_discards(self) -> None:
        """Recycle all discard pile cards (except the most recent top card) into draw pile."""
        if len(self._discard_pile) <= 1:
            return

        top_card = self._discard_pile.pop()
        self._draw_pile = self._discard_pile
        self._discard_pile = [top_card]
        self.shuffle()

    def get_initial_top_card(self) -> Card:
        """Draw the opening top card, reshuffling until a non-Wild card is selected."""
        card = self.draw()
        while card.is_wild:
            self._draw_pile.insert(0, card)
            self.shuffle()
            card = self.draw()
        self.discard(card)
        return card

    @property
    def draw_pile_size(self) -> int:
        """Count of cards remaining in draw pile."""
        return len(self._draw_pile)

    @property
    def discard_pile_size(self) -> int:
        """Count of cards in discard pile."""
        return len(self._discard_pile)

    @property
    def total_cards(self) -> int:
        """Total cards across both piles."""
        return self.draw_pile_size + self.discard_pile_size
