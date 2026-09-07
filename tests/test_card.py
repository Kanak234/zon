"""Unit tests for Card model and legal play logic."""
import pytest

from zono.card import Card


def test_card_initialization_and_properties():
    c_red_5 = Card("Red", 5)
    assert c_red_5.color == "Red"
    assert c_red_5.value == 5
    assert not c_red_5.is_wild
    assert not c_red_5.is_draw
    assert not c_red_5.is_action
    assert c_red_5.draw_amount == 0

    c_skip = Card("Blue", "Skip")
    assert c_skip.is_action
    assert not c_skip.is_wild
    assert not c_skip.is_draw

    c_draw3 = Card("Green", "Draw3")
    assert c_draw3.is_draw
    assert c_draw3.draw_amount == 3

    c_wild = Card("Wild", "Wild")
    assert c_wild.is_wild
    assert c_wild.is_action
    assert c_wild.draw_amount == 0

    c_wild5 = Card("Wild", "WildDraw5")
    assert c_wild5.is_wild
    assert c_wild5.is_draw
    assert c_wild5.draw_amount == 5


def test_invalid_card_raises():
    with pytest.raises(ValueError):
        Card("Purple", 5)

    with pytest.raises(ValueError):
        Card("Wild", 5)


def test_playable_on():
    top = Card("Red", 7)

    # Same color
    assert Card("Red", 2).playable_on(top)
    # Same value
    assert Card("Green", 7).playable_on(top)
    # Wild is always playable
    assert Card("Wild", "Wild").playable_on(top)
    assert Card("Wild", "WildDraw5").playable_on(top)
    # Different color and value
    assert not Card("Blue", 4).playable_on(top)


def test_playable_on_wild_with_active_color():
    top_wild = Card("Wild", "Wild")

    # If active declared color is Blue
    assert Card("Blue", 9).playable_on(top_wild, active_color="Blue")
    assert not Card("Red", 9).playable_on(top_wild, active_color="Blue")
    # Another Wild can still be played
    assert Card("Wild", "WildDraw5").playable_on(top_wild, active_color="Blue")


def test_serialization():
    card = Card("Yellow", "Reverse")
    d = card.to_dict()
    assert d == {"color": "Yellow", "value": "Reverse"}

    restored = Card.from_dict(d)
    assert restored == card
    assert str(card) == "[Yellow Reverse]"
