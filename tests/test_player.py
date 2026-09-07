"""Unit tests for Player management and AI decision heuristics."""
from zono.card import Card
from zono.player import Player


def test_player_hand_management():
    p = Player(name="ALPHA", is_human=True)
    assert p.hand_size == 0

    c1 = Card("Blue", 3)
    c2 = Card("Red", 3)
    p.add_card(c1)
    p.add_cards([c2])
    assert p.hand_size == 2

    removed = p.remove_card_at(0)
    assert removed == c1
    assert p.hand_size == 1
    assert p.hand[0] == c2


def test_playable_cards_detection():
    p = Player(name="BETA-7")
    p.hand = [
        Card("Blue", 4),
        Card("Green", 9),
        Card("Wild", "Wild"),
        Card("Red", 1),
    ]

    top = Card("Blue", 9)
    playable = p.playable_cards(top)
    # Blue 4 matches color, Green 9 matches value, Wild matches anything
    indices = [idx for idx, _ in playable]
    assert indices == [0, 1, 2]


def test_best_wild_color_frequency():
    p = Player(name="AI-TEST")
    p.hand = [
        Card("Green", 1),
        Card("Green", 5),
        Card("Green", "Skip"),
        Card("Red", 2),
        Card("Wild", "Wild"),
    ]
    # Green is the most common color (3 Green vs 1 Red)
    assert p.best_wild_color() == "Green"


def test_boss_ai_prioritizes_draw_cards():
    boss = Player(name="ZERO-X", ai_strategy="boss")
    boss.hand = [
        Card("Red", 5),
        Card("Red", "Draw3"),
        Card("Wild", "WildDraw5"),
    ]
    top = Card("Red", 2)
    idx, _color = boss.choose_ai_move(top)
    # Boss should prefer WildDraw5 or Draw3 over regular Red 5
    assert idx in {1, 2}
    chosen_card = boss.hand[idx]
    assert chosen_card.is_draw


def test_ai_draw_stack_constraint():
    ai = Player(name="NORMAL-AI", ai_strategy="normal")
    ai.hand = [
        Card("Red", 5),
        Card("Green", 7),
    ]
    top = Card("Red", "Draw3")
    # Draw stack is active (+3), but AI holds no draw cards
    idx, _ = ai.choose_ai_move(top, draw_stack=3)
    # AI must return (None, None) to draw the penalty
    assert idx is None
