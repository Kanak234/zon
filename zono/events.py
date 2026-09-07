"""World Event anomaly simulation for GUNO ZONO: Horizon Protocol."""
from __future__ import annotations

import random
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zono.engine import GameEngine


class WorldEventType(str, Enum):
    """World anomaly states affecting gameplay mechanics."""

    STABLE = "STABLE"
    GLITCH = "GLITCH"
    GRAVITY_SWAP = "GRAVITY SWAP"
    BLACKOUT = "BLACKOUT"
    DOUBLE_DATA = "DOUBLE DATA"


EVENT_DESCRIPTIONS: dict[str, str] = {
    WorldEventType.STABLE.value: "Sub-space communication channels stable. Standard protocol rules apply.",
    WorldEventType.GLITCH.value: "System glitch detected! Hand buffers corrupted and swapped with the deck.",
    WorldEventType.GRAVITY_SWAP.value: "Gravitational flux anomaly! Direction of play inverted immediately.",
    WorldEventType.BLACKOUT.value: "Sensory blackout! Terminal card displays are blinded.",
    WorldEventType.DOUBLE_DATA.value: "Bandwidth surge! All draw penalties and data loads are doubled!",
}


class WorldEventManager:
    """Manages world event triggering, state tracking, and gameplay modifications."""

    ALL_EVENTS: ClassVar[tuple[str, ...]] = (
        WorldEventType.STABLE.value,
        WorldEventType.GLITCH.value,
        WorldEventType.GRAVITY_SWAP.value,
        WorldEventType.BLACKOUT.value,
        WorldEventType.DOUBLE_DATA.value,
    )

    def __init__(self, cycle_interval: int = 5, rng_seed: int | None = None) -> None:
        self.cycle_interval = cycle_interval
        self._rng = random.Random(rng_seed)
        self.active_event: str = WorldEventType.STABLE.value
        self.event_counter: int = 0
        self.event_history: list[str] = [self.active_event]

    def step_turn(self, engine: GameEngine) -> str:
        """Advance the turn counter and trigger world event shifts at cycle boundaries."""
        self.event_counter += 1
        if self.event_counter % self.cycle_interval == 0:
            # Pick a non-stable anomaly
            anomalies = [e for e in self.ALL_EVENTS if e != WorldEventType.STABLE.value]
            new_event = self._rng.choice(anomalies)
        else:
            new_event = WorldEventType.STABLE.value

        self.active_event = new_event
        self.event_history.append(new_event)
        self._apply_event_effects(engine)
        return self.active_event

    def _apply_event_effects(self, engine: GameEngine) -> None:
        """Apply active state mutations caused by the world event."""
        if self.active_event == WorldEventType.GRAVITY_SWAP.value:
            engine.direction *= -1

        elif self.active_event == WorldEventType.GLITCH.value:
            # Glitch: swap one random card from each player with draw deck if available
            for player in engine.players:
                if player.hand and engine.deck.draw_pile_size > 0:
                    idx = self._rng.randrange(len(player.hand))
                    discarded = player.hand.pop(idx)
                    new_card = engine.deck.draw()
                    player.add_card(new_card)
                    engine.deck.discard(discarded)

    @property
    def is_blackout(self) -> bool:
        """Check if visual blackout event is active."""
        return self.active_event == WorldEventType.BLACKOUT.value

    @property
    def draw_multiplier(self) -> int:
        """Multiplier for draw penalties under DOUBLE DATA."""
        return 2 if self.active_event == WorldEventType.DOUBLE_DATA.value else 1
