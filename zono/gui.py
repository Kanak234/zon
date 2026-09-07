"""Cyberpunk Tkinter Desktop GUI for GUNO ZONO: Horizon Protocol."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from zono.audio import play_sound
from zono.card import COLOR_HEX, COLORS
from zono.engine import GameEngine
from zono.events import EVENT_DESCRIPTIONS
from zono.profile import ProfileManager


class ZonoGUI:
    """Cyberpunk desktop interface for GUNO ZONO."""

    def __init__(self, root: tk.Tk, profile_manager: ProfileManager | None = None) -> None:
        self.root = root
        self.root.title("GUNO ZONO : HORIZON PROTOCOL")
        self.root.geometry("1400x920")
        self.root.configure(bg="#050505")

        self.pm = profile_manager or ProfileManager()
        self.engine = GameEngine(
            human_name=self.pm.profile.name,
            profile_wins=self.pm.profile.wins,
        )

        self.bot_labels: list[tk.Label] = []
        self._build_ui()
        self.refresh_ui()

    def _build_ui(self) -> None:
        """Construct top stats, table center, bot displays, and player hand controls."""
        # Top Stats Bar
        self.stats_lbl = tk.Label(
            self.root,
            fg="#00d2ff",
            bg="#050505",
            font=("Consolas", 12, "bold"),
            anchor="w",
        )
        self.stats_lbl.place(x=25, y=15, width=900, height=30)

        # World Event Banner
        self.event_frame = tk.Frame(self.root, bg="#111", highlightbackground="#f9d423", highlightthickness=1)
        self.event_frame.place(x=450, y=55, width=500, height=65)

        self.event_title_lbl = tk.Label(
            self.event_frame,
            fg="#f9d423",
            bg="#111",
            font=("Impact", 16),
        )
        self.event_title_lbl.pack(anchor="center", pady=(4, 0))

        self.event_desc_lbl = tk.Label(
            self.event_frame,
            fg="#aaa",
            bg="#111",
            font=("Consolas", 9),
            wraplength=480,
        )
        self.event_desc_lbl.pack(anchor="center")

        # Discard Pile (Top Card)
        self.center_card = tk.Canvas(
            self.root,
            width=160,
            height=230,
            bg="#000",
            highlightthickness=2,
            highlightbackground="#333",
        )
        self.center_card.place(x=620, y=250)

        # Declared Color indicator
        self.declared_lbl = tk.Label(
            self.root,
            fg="white",
            bg="#050505",
            font=("Consolas", 12, "bold"),
        )
        self.declared_lbl.place(x=550, y=490, width=300, height=25)

        # Draw Stack / Action Message
        self.action_msg_lbl = tk.Label(
            self.root,
            fg="#00ffcc",
            bg="#050505",
            font=("Consolas", 11),
        )
        self.action_msg_lbl.place(x=300, y=520, width=800, height=25)

        # Bot Display Cards
        self.bot_labels = []
        bot_positions = [(60, 270), (600, 130), (1120, 270)]
        for i in range(3):
            f = tk.Frame(self.root, bg="#1a1a1a", highlightbackground="#444", highlightthickness=1)
            f.place(x=bot_positions[i][0], y=bot_positions[i][1], width=220, height=90)

            lbl = tk.Label(f, fg="white", bg="#1a1a1a", font=("Consolas", 11, "bold"), justify="center")
            lbl.pack(expand=True, fill="both")
            self.bot_labels.append(lbl)

        # Action Controls (Draw Button & Pass Button)
        self.ctrl_frame = tk.Frame(self.root, bg="#050505")
        self.ctrl_frame.place(x=100, y=650, width=1200, height=45)

        self.draw_btn = tk.Button(
            self.ctrl_frame,
            text="DRAW CARD",
            bg="#ff0055",
            fg="white",
            font=("Impact", 14),
            activebackground="#ff3377",
            activeforeground="white",
            cursor="hand2",
            relief="flat",
            command=self.on_human_draw,
        )
        self.draw_btn.pack(side="left", padx=10, ipadx=15, ipady=3)

        self.new_game_btn = tk.Button(
            self.ctrl_frame,
            text="NEW MATCH",
            bg="#333",
            fg="#aaa",
            font=("Consolas", 10, "bold"),
            relief="flat",
            command=self.on_new_match,
        )
        self.new_game_btn.pack(side="right", padx=10)

        # Human Hand Frame
        self.hand_canvas = tk.Canvas(self.root, bg="#080808", highlightthickness=1, highlightbackground="#222")
        self.hand_canvas.place(x=50, y=700, width=1300, height=170)

        self.hand_inner = tk.Frame(self.hand_canvas, bg="#080808")
        self.hand_canvas.create_window((0, 0), window=self.hand_inner, anchor="nw")

    def refresh_ui(self) -> None:
        """Sync UI widgets with the current GameEngine state."""
        prof = self.pm.profile
        stat_text = (
            f"PILOT: {prof.name} | LVL {prof.level} | XP {prof.xp} | "
            f"WINS {prof.wins} (Losses: {prof.losses}) | CREDITS {prof.credits}"
        )
        self.stats_lbl.config(text=stat_text)

        # World Event
        ev = self.engine.event_manager.active_event
        self.event_title_lbl.config(text=f"WORLD ANOMALY : {ev}")
        self.event_desc_lbl.config(text=EVENT_DESCRIPTIONS.get(ev, ""))

        # Top Card
        self._render_top_card()

        # Declared color
        if self.engine.active_color:
            self.declared_lbl.config(
                text=f"ACTIVE COLOR: {self.engine.active_color.upper()}",
                fg=COLOR_HEX.get(self.engine.active_color, "white"),
            )
        else:
            self.declared_lbl.config(text="")

        # Action / Stack Message
        if self.engine.draw_stack > 0:
            self.action_msg_lbl.config(
                text=f"CRITICAL: ACTIVE DRAW STACK +{self.engine.draw_stack} CARDS! (PLAY DRAW CARD OR DRAW)",
                fg="#ff0055",
            )
            self.draw_btn.config(text=f"DRAW PENALTY (+{self.engine.draw_stack})", bg="#990000")
        else:
            self.action_msg_lbl.config(text=self.engine.last_action_message, fg="#00ffcc")
            self.draw_btn.config(text="DRAW CARD", bg="#ff0055")

        # Bot Displays
        for i, lbl in enumerate(self.bot_labels, start=1):
            p = self.engine.players[i]
            is_active = self.engine.turn_index == i
            status = ">>> THINKING..." if is_active else ""
            lbl.config(
                text=f"{p.name}\nCARDS: {p.hand_size}\n{status}",
                bg="#003311" if is_active else "#1a1a1a",
                fg="#00ff66" if is_active else "white",
            )

        # Render Human Hand
        for w in self.hand_inner.winfo_children():
            w.destroy()

        human = self.engine.players[0]
        is_human_turn = self.engine.turn_index == 0 and not self.engine.game_over

        self.draw_btn.config(state="normal" if is_human_turn else "disabled")

        for idx, card in enumerate(human.hand):
            playable = is_human_turn and self.engine.can_play(0, idx)
            card_cv = tk.Canvas(
                self.hand_inner,
                width=90,
                height=130,
                bg="#080808",
                highlightthickness=2 if playable else 1,
                highlightbackground="#00ffcc" if playable else "#333",
            )
            fill_color = "#000" if self.engine.event_manager.is_blackout else COLOR_HEX.get(card.color, "#333")
            border_col = "white" if playable else "#666"
            border_w = 2 if playable else 1
            card_cv.create_rectangle(5, 5, 85, 125, fill=fill_color, outline=border_col, width=border_w)

            display_val = "?" if self.engine.event_manager.is_blackout else str(card.value)
            card_cv.create_text(
                45,
                65,
                text=display_val,
                fill="white",
                font=("Impact" if card.is_action else "Arial", 11 if card.is_action else 16, "bold"),
            )

            if playable:
                card_cv.bind("<Button-1>", lambda e, i=idx: self.on_human_play(i))
                card_cv.config(cursor="hand2")

            card_cv.pack(side="left", padx=4, pady=5)

        self.hand_canvas.update_idletasks()
        self.hand_canvas.config(scrollregion=self.hand_canvas.bbox("all"))

        # Trigger AI if bot's turn
        if not is_human_turn and not self.engine.game_over:
            self.root.after(850, self.on_ai_step)

    def _render_top_card(self) -> None:
        """Draw top discard card with blackout sensitivity."""
        self.center_card.delete("all")
        c = self.engine.top_card
        is_blackout = self.engine.event_manager.is_blackout
        color = "#000" if is_blackout else COLOR_HEX.get(c.color, "#2c3e50")

        self.center_card.create_rectangle(8, 8, 152, 222, fill=color, outline="white", width=3)
        text_val = "SYS BLACKOUT" if is_blackout else str(c.value)
        self.center_card.create_text(
            80,
            115,
            text=text_val,
            fill="#ff0055" if is_blackout else "white",
            font=("Impact", 16 if is_blackout else 28),
        )

    def on_human_play(self, idx: int) -> None:
        """Handle human clicking a card to play."""
        if self.engine.turn_index != 0 or self.engine.game_over:
            return

        card = self.engine.players[0].hand[idx]
        declared_color = None
        if card.is_wild:
            declared_color = self._prompt_color_choice()
            if not declared_color:
                return  # Cancelled

        play_sound("play")
        success, _ = self.engine.play_card(0, idx, declared_color)
        if success:
            self.refresh_ui()
            self._check_game_end()

    def on_human_draw(self) -> None:
        """Handle human clicking the draw button."""
        if self.engine.turn_index != 0 or self.engine.game_over:
            return

        play_sound("draw")
        _drawn, _ = self.engine.player_draw(0)
        self.refresh_ui()

        # If it was a single draw, user can choose to play newly drawn card or pass
        if self.engine.draw_stack == 0 and self.engine.turn_index == 0:
            drawn_idx = len(self.engine.players[0].hand) - 1
            if self.engine.can_play(0, drawn_idx):
                card = self.engine.players[0].hand[drawn_idx]
                resp = messagebox.askyesno(
                    "Card Playable",
                    f"You drew {card}! Do you want to play it immediately?",
                )
                if resp:
                    self.on_human_play(drawn_idx)
                    return
            self.engine.pass_turn(0)
            self.refresh_ui()

    def on_ai_step(self) -> None:
        """Execute bot turn step."""
        if self.engine.game_over or self.engine.turn_index == 0:
            return

        self.engine.step_ai_turn()
        self.refresh_ui()
        self._check_game_end()

    def _prompt_color_choice(self) -> str | None:
        """Display cyber color selection dialog for Wild cards."""
        dialog = tk.Toplevel(self.root)
        dialog.title("SELECT PROTOCOL COLOR")
        dialog.geometry("360x180")
        dialog.configure(bg="#111")
        dialog.transient(self.root)
        dialog.grab_set()

        selected: list[str | None] = [None]

        lbl = tk.Label(dialog, text="CHOOSE OVERRIDE COLOR:", fg="#f9d423", bg="#111", font=("Impact", 14))
        lbl.pack(pady=15)

        btn_frame = tk.Frame(dialog, bg="#111")
        btn_frame.pack(pady=10)

        def pick(col: str) -> None:
            selected[0] = col
            dialog.destroy()

        for c in COLORS:
            btn = tk.Button(
                btn_frame,
                text=c.upper(),
                bg=COLOR_HEX[c],
                fg="white",
                font=("Consolas", 11, "bold"),
                width=7,
                height=2,
                relief="flat",
                command=lambda col=c: pick(col),
            )
            btn.pack(side="left", padx=5)

        self.root.wait_window(dialog)
        return selected[0]

    def _check_game_end(self) -> None:
        """Verify if victory condition was attained and update profile."""
        if not self.engine.game_over:
            return

        winner = self.engine.winner
        if winner and winner.is_human:
            play_sound("win")
            self.pm.profile.add_win()
            self.pm.save()
            messagebox.showinfo(
                "VICTORY CONFIRMED",
                f"PILOT VICTORY!\n\nRank increased to LVL {self.pm.profile.level}.\n+1000 Credits | +500 XP.",
            )
        else:
            play_sound("lose")
            self.pm.profile.add_loss()
            self.pm.save()
            name = winner.name if winner else "BOT"
            messagebox.showinfo(
                "MISSION FAILED",
                f"{name} defeated you.\n\nBetter luck next protocol cycle.",
            )

        self.refresh_ui()

    def on_new_match(self) -> None:
        """Reset match with current career stats."""
        self.engine.deal_new_game()
        self.refresh_ui()
