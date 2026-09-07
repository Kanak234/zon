"""Unit tests for Deck generation, shuffling, and discard recycling."""
from zono.card import Card
from zono.deck import Deck


def test_deck_composition():
    deck = Deck(seed=42)
    # Total cards should be 76
    assert deck.total_cards == 76
    assert deck.draw_pile_size == 76
    assert deck.discard_pile_size == 0


def test_draw_and_discard():
    deck = Deck(seed=123)
    c1 = deck.draw()
    assert isinstance(c1, Card)
    assert deck.draw_pile_size == 75

    cards = deck.draw_multiple(5)
    assert len(cards) == 5
    assert deck.draw_pile_size == 70

    deck.discard(c1)
    for c in cards:
        deck.discard(c)
    assert deck.discard_pile_size == 6


def test_automated_discard_recycling():
    deck = Deck(seed=99)
    # Draw all 76 cards
    drawn_cards = deck.draw_multiple(76)
    assert deck.draw_pile_size == 0

    # Add 10 cards to discard pile
    for c in drawn_cards[:10]:
        deck.discard(c)

    assert deck.discard_pile_size == 10

    # Next draw should trigger recycling of discards (leaving 1 top card in discard)
    card = deck.draw()
    assert isinstance(card, Card)
    assert deck.discard_pile_size == 1
    assert deck.draw_pile_size == 8


def test_initial_top_card_never_wild():
    deck = Deck(seed=777)
    top = deck.get_initial_top_card()
    assert not top.is_wild
    assert deck.discard_pile_size == 1
