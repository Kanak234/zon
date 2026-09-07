"""Unit tests for ZonoCLI non-interactive methods."""
from zono.cli import ZonoCLI
from zono.profile import ProfileManager


def test_cli_initialization(tmp_path):
    prof_file = tmp_path / "cli_profile.json"
    pm = ProfileManager(prof_file)
    cli = ZonoCLI(profile_manager=pm)

    assert cli.engine.players[0].name == "PILOT"
    total_cards_in_play = cli.engine.deck.total_cards + sum(p.hand_size for p in cli.engine.players)
    assert total_cards_in_play == 76

    # Test output methods run without raising exceptions
    cli.print_banner()
    cli.print_state()
