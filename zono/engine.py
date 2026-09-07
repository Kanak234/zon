"""Headless core game engine for GUNO ZONO: Horizon Protocol."""
from __future__ import annotations

from zono.card import Card
from zono.deck import Deck
from zono.events import WorldEventManager
from zono.player import Player


class GameEngine:
    """Orchestrates state, turn progression, and rule validation."""

    def __init__(
        self,
        human_name: str = "ALPHA (YOU)",
        profile_wins: int = 0,
        seed: int | None = None,
        event_cycle_interval: int = 5,
    ) -> None:
        self.deck = Deck(seed=seed)
        self.event_manager = WorldEventManager(cycle_interval=event_cycle_interval, rng_seed=seed)
        self.players: list[Player] = []
        self.profile_wins = profile_wins
        self.human_name = human_name

        self.top_card: Card = Card("Red", 0)
        self.active_color: str | None = None
        self.turn_index: int = 0
        self.direction: int = 1
        self.draw_stack: int = 0
        self.winner: Player | None = None
        self.game_over: bool = False
        self.last_action_message: str = ""

        self._initialize_players()
        self.deal_new_game()

    def _initialize_players(self) -> None:
        """Set up 4 combatants based on career win threshold."""
        boss_active = self.profile_wins >= 10
        player_3_name = "ZERO-X (BOSS)" if boss_active else "GAMMA-9"
        player_3_strategy = "boss" if boss_active else "normal"

        self.players = [
            Player(name=self.human_name, is_human=True, ai_strategy=None),
            Player(name="BETA-7", is_human=False, ai_strategy="normal"),
            Player(name=player_3_name, is_human=False, ai_strategy=player_3_strategy),
            Player(name="DELTA-2", is_human=False, ai_strategy="normal"),
        ]

    def deal_new_game(self) -> None:
        """Reset deck, hands, and game status for a fresh match."""
        self.deck.reset()
        for p in self.players:
            p.hand = self.deck.draw_multiple(7)

        self.top_card = self.deck.get_initial_top_card()
        self.active_color = None
        self.turn_index = 0
        self.direction = 1
        self.draw_stack = 0
        self.winner = None
        self.game_over = False
        self.last_action_message = f"Game initiated. Top card is {self.top_card}."

    @property
    def current_player(self) -> Player:
        """Return the player whose turn is currently active."""
        return self.players[self.turn_index]

    def can_play(self, player_idx: int, card_idx: int) -> bool:
        """Validate whether the indexed card can be played legally right now."""
        if self.game_over or player_idx != self.turn_index:
            return False

        player = self.players[player_idx]
        if not (0 <= card_idx < len(player.hand)):
            return False

        card = player.hand[card_idx]
        return card.playable_on(self.top_card, self.active_color)

    def play_card(
        self,
        player_idx: int,
        card_idx: int,
        declared_color: str | None = None,
    ) -> tuple[bool, str]:
        """Execute card play, handle action effects, and advance turn if valid."""
        if not self.can_play(player_idx, card_idx):
            return False, "Illegal move."

        player = self.players[player_idx]
        card = player.remove_card_at(card_idx)
        self.deck.discard(card)
        self.top_card = card

        # Handle Wild color declaration
        if card.is_wild:
            self.active_color = declared_color or player.best_wild_color()
        else:
            self.active_color = None

        # Check immediate victory
        if player.hand_size == 0:
            self.winner = player
            self.game_over = True
            msg = f"{player.name} played {card} and WON the match!"
            self.last_action_message = msg
            return True, msg

        # Handle Action Card Effects
        mult = self.event_manager.draw_multiplier
        if card.value == "Draw3":
            victim_idx = (self.turn_index + self.direction) % len(self.players)
            victim = self.players[victim_idx]
            penalty = 3 * mult
            victim.add_cards(self.deck.draw_multiple(penalty))
            self._advance_pointer()  # Victim is skipped
            self.last_action_message = (
                f"{player.name} played {card}! {victim.name} drew {penalty} cards and was skipped."
            )
        elif card.value == "WildDraw5":
            victim_idx = (self.turn_index + self.direction) % len(self.players)
            victim = self.players[victim_idx]
            penalty = 5 * mult
            victim.add_cards(self.deck.draw_multiple(penalty))
            self._advance_pointer()  # Victim is skipped
            self.last_action_message = (
                f"{player.name} played {card} ({self.active_color})! "
                f"{victim.name} drew {penalty} cards and was skipped."
            )
        elif card.value == "Reverse":
            self.direction *= -1
            if len(self.players) == 2:
                self._advance_pointer()
            self.last_action_message = f"{player.name} played {card} - direction reversed."
        elif card.value == "Skip":
            victim_idx = (self.turn_index + self.direction) % len(self.players)
            victim = self.players[victim_idx]
            self._advance_pointer()  # Victim is skipped
            self.last_action_message = f"{player.name} played {card}! {victim.name} was skipped."
        else:
            self.last_action_message = f"{player.name} played {card}."

        self._advance_turn()
        return True, self.last_action_message

    def player_draw(self, player_idx: int) -> tuple[list[Card], str]:
        """Process player drawing a single card from deck."""
        if self.game_over or player_idx != self.turn_index:
            return [], "Cannot draw out of turn."

        player = self.players[player_idx]
        card = self.deck.draw()
        player.add_card(card)
        msg = f"{player.name} drew 1 card."
        self.last_action_message = msg
        return [card], msg

    def pass_turn(self, player_idx: int) -> tuple[bool, str]:
        """Manually conclude turn after drawing."""
        if self.game_over or player_idx != self.turn_index:
            return False, "Cannot pass out of turn."

        player = self.players[player_idx]
        self._advance_turn()
        msg = f"{player.name} passed turn."
        self.last_action_message = msg
        return True, msg

    def _advance_pointer(self) -> None:
        """Increment turn pointer based on current direction."""
        self.turn_index = (self.turn_index + self.direction) % len(self.players)

    def _advance_turn(self) -> None:
        """Advance to next player and step world event simulator."""
        self._advance_pointer()
        self.event_manager.step_turn(self)

    def step_ai_turn(self) -> tuple[bool, str]:
        """Execute one complete automated turn for the active AI player."""
        if self.game_over:
            return False, "Game over."

        player = self.current_player
        if player.is_human:
            return False, "Awaiting human action."

        idx, chosen_color = player.choose_ai_move(
            self.top_card,
            self.active_color,
            0,
        )

        if idx is not None:
            return self.play_card(self.turn_index, idx, chosen_color)

        # AI needs to draw
        drawn, msg = self.player_draw(self.turn_index)
        if drawn:
            drawn_idx = player.hand_size - 1
            if self.can_play(self.turn_index, drawn_idx):
                card = player.hand[drawn_idx]
                color = player.best_wild_color() if card.is_wild else None
                return self.play_card(self.turn_index, drawn_idx, color)

        self.pass_turn(self.turn_index)
        return True, msg
