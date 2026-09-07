"""Main executable entrypoint for GUNO ZONO: Horizon Protocol."""
from __future__ import annotations

import argparse
import os
import sys

from zono.cli import ZonoCLI


def main() -> None:
    parser = argparse.ArgumentParser(description="GUNO ZONO: Horizon Protocol")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in interactive command-line terminal mode instead of Tkinter GUI",
    )
    args = parser.parse_args()

    # Determine if GUI can be launched
    has_display = bool(os.environ.get("DISPLAY") or sys.platform == "win32" or sys.platform == "darwin")

    if args.cli or not has_display:
        cli = ZonoCLI()
        cli.run_game()
        return

    try:
        import tkinter as tk

        from zono.gui import ZonoGUI

        root = tk.Tk()
        ZonoGUI(root)
        root.mainloop()
    except (ImportError, tk.TclError, RuntimeError, OSError) as exc:
        print(f"[!] Unable to initialize graphical desktop interface: {exc}")
        print("[*] Launching fallback interactive terminal mode...")
        cli = ZonoCLI()
        cli.run_game()


if __name__ == "__main__":
    main()
