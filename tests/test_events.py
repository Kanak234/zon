"""Unit tests for World Event anomalies."""
from zono.engine import GameEngine
from zono.events import WorldEventManager, WorldEventType


def test_world_event_manager_cycling():
    mgr = WorldEventManager(cycle_interval=3, rng_seed=42)
    engine = GameEngine(human_name="TEST_PILOT", seed=42)

    assert mgr.active_event == WorldEventType.STABLE.value

    # Turn 1
    ev1 = mgr.step_turn(engine)
    assert ev1 == WorldEventType.STABLE.value

    # Turn 2
    ev2 = mgr.step_turn(engine)
    assert ev2 == WorldEventType.STABLE.value

    # Turn 3 (boundary)
    ev3 = mgr.step_turn(engine)
    assert ev3 in mgr.ALL_EVENTS
    assert ev3 != WorldEventType.STABLE.value


def test_gravity_swap_reverses_direction():
    mgr = WorldEventManager(cycle_interval=1, rng_seed=1)
    engine = GameEngine(human_name="TEST_PILOT", seed=1)
    initial_dir = engine.direction

    mgr.active_event = WorldEventType.GRAVITY_SWAP.value
    mgr._apply_event_effects(engine)

    assert engine.direction == -initial_dir


def test_double_data_multiplier():
    mgr = WorldEventManager()
    mgr.active_event = WorldEventType.STABLE.value
    assert mgr.draw_multiplier == 1

    mgr.active_event = WorldEventType.DOUBLE_DATA.value
    assert mgr.draw_multiplier == 2


def test_blackout_flag():
    mgr = WorldEventManager()
    mgr.active_event = WorldEventType.BLACKOUT.value
    assert mgr.is_blackout is True

    mgr.active_event = WorldEventType.STABLE.value
    assert mgr.is_blackout is False
