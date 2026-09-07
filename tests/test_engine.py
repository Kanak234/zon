"""Unit and simulation tests for GameEngine state transitions."""
from zono.card import Card
from zono.engine import GameEngine


def test_engine_initial_state():
    engine = GameEngine(human_name="TEST_HUMAN", profile_wins=0, seed=42)
    assert len(engine.players) == 4
    for p in engine.players:
        assert p.hand_size == 7

    assert engine.players[0].name == "TEST_HUMAN"
    assert engine.players[0].is_human
    assert engine.players[2].name == "GAMMA-9"  # <10 wins -> standard bot

    assert not engine.top_card.is_wild
    assert engine.turn_index == 0
    assert engine.direction == 1
    assert engine.draw_stack == 0
    assert not engine.game_over


def test_boss_spawns_at_10_wins():
    engine = GameEngine(profile_wins=10)
    assert engine.players[2].name == "ZERO-X (BOSS)"
    assert engine.players[2].ai_strategy == "boss"


def test_play_action_skip():
    engine = GameEngine(seed=10)
    engine.top_card = Card("Blue", 5)
    engine.active_color = None

    # Give player 0 a Blue Skip card
    skip_card = Card("Blue", "Skip")
    engine.players[0].hand = [skip_card]

    # Player 0 plays Skip -> skips Player 1, next turn should be Player 2!
    # Wait, in play_card, if player 0 plays their last card, they win immediately!
    # Let's give them 2 cards so they don't immediately win.
    engine.players[0].hand = [skip_card, Card("Red", 1)]

    success, _ = engine.play_card(0, 0)
    assert success
    # Skipped player 1 -> current player should be player 2
    assert engine.turn_index == 2


def test_play_action_reverse():
    engine = GameEngine(seed=20)
    engine.top_card = Card("Green", 2)
    engine.active_color = None

    rev_card = Card("Green", "Reverse")
    engine.players[0].hand = [rev_card, Card("Red", 1)]

    success, _ = engine.play_card(0, 0)
    assert success
    # Reversing from 0 with 4 players steps backwards -> (0 + (-1)) % 4 = 3
    assert engine.direction == -1
    assert engine.turn_index == 3


def test_draw_penalty_action_and_victim_skip():
    engine = GameEngine(seed=30)
    engine.top_card = Card("Yellow", 4)
    engine.active_color = None

    player1 = engine.players[1]
    initial_hand = player1.hand_size

    # Player 0 plays Draw3 -> Player 1 draws 3 and is skipped
    draw3_card = Card("Yellow", "Draw3")
    engine.players[0].hand = [draw3_card, Card("Blue", 1)]
    success, msg = engine.play_card(0, 0)
    assert success
    assert "drew 3 cards and was skipped" in msg
    assert player1.hand_size == initial_hand + 3
    # Turn advanced past Player 1 directly to Player 2
    assert engine.turn_index == 2


def test_winning_condition():
    engine = GameEngine(seed=40)
    engine.top_card = Card("Red", 1)
    engine.active_color = None

    engine.players[0].hand = [Card("Red", 5)]
    success, msg = engine.play_card(0, 0)
    assert success
    assert engine.game_over is True
    assert engine.winner == engine.players[0]
    assert "WON" in msg


def test_full_autonomous_game_simulation():
    """Simulate 10 complete games with all-AI bots to ensure no deadlocks or exceptions."""
    for seed in range(10):
        engine = GameEngine(human_name="BOT_0", profile_wins=15, seed=seed)
        # Turn human player into AI for full automated simulation
        engine.players[0].is_human = False
        engine.players[0].ai_strategy = "aggressive"

        turns = 0
        max_turns = 500  # Safety threshold against infinite games
        while not engine.game_over and turns < max_turns:
            turns += 1
            success, _ = engine.step_ai_turn()
            assert success

        assert engine.game_over is True
        assert engine.winner is not None
        assert engine.winner.hand_size == 0
