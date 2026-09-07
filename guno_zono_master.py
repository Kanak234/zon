"""GUNO ZONO : HORIZON PROTOCOL - Master Launcher.

Flat entrypoint launching the cyberpunk desktop GUI or terminal CLI mode.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from zono.cli import ZonoCLI
from zono.gui import ZonoGUI
from zono.profile import ProfileManager

# Alias for backward compatibility
GunoZonoMaster = ZonoGUI


def main() -> None:
    profile_path = Path(__file__).resolve().parent / "zono_master_profile.json"
    pm = ProfileManager(profile_path)

    has_display = bool(os.environ.get("DISPLAY") or sys.platform == "win32" or sys.platform == "darwin")
    if not has_display or "--cli" in sys.argv:
        cli = ZonoCLI(pm)
        cli.run_game()
    else:
        try:
            import tkinter as tk

            root = tk.Tk()
            ZonoGUI(root, profile_manager=pm)
            root.mainloop()
        except Exception as exc:
            print(f"[!] Unable to initialize GUI ({exc}). Falling back to terminal mode...")
            cli = ZonoCLI(pm)
            cli.run_game()


if __name__ == "__main__":
    main()
