"""Terminal-based Command Line Interface for GUNO ZONO."""
from __future__ import annotations

from zono.card import COLORS
from zono.engine import GameEngine
from zono.profile import ProfileManager


class ZonoCLI:
    """Provides a playable terminal UI for GUNO ZONO without requiring a GUI."""

    def __init__(self, profile_manager: ProfileManager | None = None) -> None:
        self.pm = profile_manager or ProfileManager()
        self.engine = GameEngine(
            human_name=self.pm.profile.name,
            profile_wins=self.pm.profile.wins,
        )

    def print_banner(self) -> None:
        """Print game header and profile status."""
        p = self.pm.profile
        print("=" * 60)
        print("    GUNO ZONO : HORIZON PROTOCOL (TERMINAL EDITION)")
        print(f"    PILOT: {p.name} | LVL {p.level} | XP {p.xp} | WINS {p.wins} | CREDITS {p.credits}")
        print("=" * 60)

    def print_state(self) -> None:
        """Display current game table, world event, and bot hands."""
        print(f"\n[!] WORLD EVENT: {self.engine.event_manager.active_event}")
        color_info = f" (Declared: {self.engine.active_color})" if self.engine.active_color else ""
        print(f"[>] TOP CARD: {self.engine.top_card}{color_info}")

        if self.engine.draw_stack > 0:
            print(f"[!] WARNING: ACTIVE DRAW STACK = +{self.engine.draw_stack} CARDS!")

        print("\n--- COMBATANTS ---")
        for i, player in enumerate(self.engine.players):
            active_marker = " >>> [ACTIVE] " if i == self.engine.turn_index else "     "
            print(f"{active_marker}{player.name}: {player.hand_size} cards")

        human = self.engine.players[0]
        print("\n--- YOUR HAND ---")
        for idx, card in enumerate(human.hand):
            playable = "[PLAYABLE]" if self.engine.can_play(0, idx) else "          "
            print(f"  ({idx}) {card} {playable}")
        print()

    def play_turn_human(self) -> bool:
        """Prompt human player for command and execute action. Return False to quit."""
        self.print_state()
        while True:
            try:
                raw = input("Enter command ('p <idx> [color]', 'd' to draw, 'q' to quit): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nMatch aborted.")
                return False

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd == "q":
                print("Exiting game.")
                return False

            if cmd == "d":
                _drawn, msg = self.engine.player_draw(0)
                print(f"[>] {msg}")
                # If draw stack was resolved, turn ended automatically
                if self.engine.turn_index != 0:
                    break

                # If drawn single card is playable, offer choice to play it
                drawn_idx = len(self.engine.players[0].hand) - 1
                if self.engine.can_play(0, drawn_idx):
                    prompt_text = f"Drawn card {self.engine.players[0].hand[drawn_idx]} is playable! Play now? (y/n): "
                    choice = input(prompt_text)
                    if choice.strip().lower().startswith("y"):
                        card = self.engine.players[0].hand[drawn_idx]
                        dec_color = None
                        if card.is_wild:
                            dec_color = self._prompt_color()
                        self.engine.play_card(0, drawn_idx, dec_color)
                        break

                self.engine.pass_turn(0)
                break

            if cmd == "p":
                if len(parts) < 2 or not parts[1].isdigit():
                    print("Usage: p <card_index> [color]")
                    continue

                idx = int(parts[1])
                if not self.engine.can_play(0, idx):
                    print("That card cannot be legally played right now!")
                    continue

                card = self.engine.players[0].hand[idx]
                declared_color = None
                if card.is_wild:
                    if len(parts) >= 3 and parts[2].capitalize() in COLORS:
                        declared_color = parts[2].capitalize()
                    else:
                        declared_color = self._prompt_color()

                success, msg = self.engine.play_card(0, idx, declared_color)
                print(f"[>] {msg}")
                if success:
                    break

        return True

    def _prompt_color(self) -> str:
        """Prompt player to choose color for Wild card."""
        while True:
            raw = input("Choose Wild Color (Red, Green, Blue, Yellow): ").strip().capitalize()
            if raw in COLORS:
                return raw
            print("Invalid color. Options: Red, Green, Blue, Yellow")

    def run_game(self) -> None:
        """Run full interactive game loop."""
        self.print_banner()
        while not self.engine.game_over:
            if self.engine.current_player.is_human:
                cont = self.play_turn_human()
                if not cont:
                    return
            else:
                _success, msg = self.engine.step_ai_turn()
                print(f"[*] {msg}")

        # Game Over
        winner = self.engine.winner
        print("\n" + "=" * 60)
        if winner and winner.is_human:
            print("    VICTORY CONFIRMED! PILOT RANK ADVANCED.")
            self.pm.profile.add_win()
        else:
            name = winner.name if winner else "UNKNOWN"
            print(f"    MISSION FAILED. {name} TOOK THE MATCH.")
            self.pm.profile.add_loss()

        self.pm.save()
        prof = self.pm.profile
        print(f"    FINAL STATS: LVL {prof.level} | WINS {prof.wins} | CREDITS {prof.credits}")
        print("=" * 60)


def main() -> None:
    """CLI Entrypoint."""
    cli = ZonoCLI()
    cli.run_game()


if __name__ == "__main__":
    main()
