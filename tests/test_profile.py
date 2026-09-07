"""Unit tests for PlayerProfile and ProfileManager persistence."""
from zono.profile import PlayerProfile, ProfileManager


def test_profile_initial_defaults():
    p = PlayerProfile()
    assert p.name == "PILOT"
    assert p.level == 1
    assert p.xp == 0
    assert p.credits == 500
    assert p.wins == 0
    assert p.losses == 0
    assert p.win_rate == 0.0


def test_profile_win_and_level_progression():
    p = PlayerProfile()
    p.add_win()
    assert p.wins == 1
    assert p.games_played == 1
    assert p.credits == 1500
    assert p.xp == 500
    assert p.level == 1
    assert p.win_rate == 100.0

    # Another win reaches 1000 XP -> Level 2
    p.add_win()
    assert p.wins == 2
    assert p.xp == 1000
    assert p.level == 2


def test_profile_persistence(tmp_path):
    prof_file = tmp_path / "test_profile.json"
    pm = ProfileManager(prof_file)
    assert pm.profile.wins == 0

    pm.profile.add_win()
    pm.save()

    # Reload from disk
    pm2 = ProfileManager(prof_file)
    assert pm2.profile.wins == 1
    assert pm2.profile.credits == 1500
