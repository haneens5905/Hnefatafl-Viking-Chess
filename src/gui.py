import tkinter as tk
from tkinter import font as tkfont
import threading
import time

# ── Game imports ─────────────────────────────────────────────────────────────
from board import (
    create_initial_board, copy_board, print_board,
    ATTACKER, DEFENDER, KING, EMPTY,
    BOARD_SIZE, CORNERS, THRONE_ROW, THRONE_COL,
    find_king, is_corner, is_throne, is_within_bounds,
)
from moves  import get_all_moves, get_valid_moves
from game   import apply_move, check_game_over
from alpha_beta import get_best_move


# ═══════════════════════════════════════════════════════════════════════════ #
#  COLOUR PALETTE  (Norse / dark stone aesthetic)
# ═══════════════════════════════════════════════════════════════════════════ #
PAL = {
    # backgrounds
    "bg"          : "#1a1612",   # near-black parchment
    "panel"       : "#231f1a",   # side-panel
    "cell_light"  : "#3b2e22",   # board light square
    "cell_dark"   : "#2a2018",   # board dark square

    # special squares
    "throne"      : "#4a3520",
    "corner"      : "#1e3a2f",
    "corner_ring" : "#2e6b50",

    # highlights
    "selected"    : "#7a5c2e",
    "valid_move"  : "#2e5c3a",
    "valid_dot"   : "#4caf70",
    "last_move"   : "#3d3020",

    # pieces
    "attacker"    : "#c0392b",   # blood red
    "attacker_hi" : "#e74c3c",
    "attacker_sh" : "#7b2218",
    "defender"    : "#d4b483",   # aged bone
    "defender_hi" : "#f0d090",
    "defender_sh" : "#8b6b3a",
    "king"        : "#f0c040",   # gold
    "king_hi"     : "#ffe066",
    "king_sh"     : "#a07820",
    "king_crown"  : "#fff8dc",

    # text / UI
    "text"        : "#e8dcc8",
    "text_dim"    : "#8b7355",
    "text_accent" : "#d4a017",
    "text_red"    : "#e74c3c",
    "text_green"  : "#4caf70",
    "border"      : "#4a3a28",
    "btn"         : "#3a2e20",
    "btn_hover"   : "#4e3e2a",
    "btn_active"  : "#c0391b",
    "separator"   : "#3a2e1e",
}

DEPTH_MAP = {"Easy": 1, "Medium": 3, "Hard": 5}


# ═══════════════════════════════════════════════════════════════════════════ #
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════ #

class HnefataflGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hnefatafl  ·  Viking Chess  ·  CS361 AI")
        self.configure(bg=PAL["bg"])
        self.resizable(False, False)

        # ── fonts ────────────────────────────────────────────────────────────
        self.font_title  = tkfont.Font(family="Georgia", size=18, weight="bold")
        self.font_head   = tkfont.Font(family="Georgia", size=11, weight="bold")
        self.font_body   = tkfont.Font(family="Georgia", size=9)
        self.font_small  = tkfont.Font(family="Georgia", size=8)
        self.font_mono   = tkfont.Font(family="Courier", size=8)
        self.font_status = tkfont.Font(family="Georgia", size=10, weight="bold")
        self.font_log    = tkfont.Font(family="Courier", size=8)

        # ── state ────────────────────────────────────────────────────────────
        self.board           = create_initial_board()
        self.selected        = None          # (row, col) of selected piece
        self.valid_moves     = []            # list of (tr, tc)
        self.current_player  = ATTACKER      # attackers go first
        self.human_side      = ATTACKER
        self.difficulty      = tk.StringVar(value="Medium")
        self.human_side_var  = tk.StringVar(value="Attacker")
        self.game_over       = False
        self.ai_thinking     = False
        self.last_from       = None
        self.last_to         = None
        self.move_history    = []
        self.captured_att    = 0
        self.captured_def    = 0
        self.cell_size       = 52
        self.margin          = 26

        # ── build UI ─────────────────────────────────────────────────────────
        self._build_layout()
        self._draw_board()
        self._update_side_panel()

        # center the main window on the monitor
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    # ─────────────────────────────────────────────────────────────────────── #
    #  LAYOUT                                                                  #
    # ─────────────────────────────────────────────────────────────────────── #

    def _build_layout(self):
        # Outer frame
        outer = tk.Frame(self, bg=PAL["bg"])
        outer.pack(padx=16, pady=16, fill="both", expand=True)

        # Title bar
        title_bar = tk.Frame(outer, bg=PAL["bg"])
        title_bar.pack(fill="x", pady=(0, 12))
        tk.Label(title_bar, text="⚔  HNEFATAFL", font=self.font_title,
                 fg=PAL["text_accent"], bg=PAL["bg"]).pack(side="left")
        tk.Label(title_bar, text="Viking Chess  ·  CS361 Artificial Intelligence",
                 font=self.font_body, fg=PAL["text_dim"], bg=PAL["bg"]).pack(
                     side="left", padx=12, pady=4)

        # Body: board + sidebar
        body = tk.Frame(outer, bg=PAL["bg"])
        body.pack(fill="both", expand=True)

        # ── Board canvas ──────────────────────────────────────────────────────
        board_px = self.margin * 2 + self.cell_size * BOARD_SIZE
        self.canvas = tk.Canvas(body, width=board_px, height=board_px,
                                bg=PAL["bg"], bd=0, highlightthickness=0)
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self._on_click)

        # ── Side panel ────────────────────────────────────────────────────────
        side = tk.Frame(body, bg=PAL["panel"], width=240,
                        highlightbackground=PAL["border"], highlightthickness=1)
        side.pack(side="left", fill="y", padx=(12, 0))
        side.pack_propagate(False)
        self.side_panel = side
        self._build_side_panel(side)

    def _build_side_panel(self, parent):
        pad = {"padx": 14, "anchor": "w"}

        # ── Status ───────────────────────────────────────────────────────────
        tk.Label(parent, text="GAME STATUS", font=self.font_head,
                 fg=PAL["text_accent"], bg=PAL["panel"]).pack(**pad, pady=(8, 2))
        self._sep(parent)

        self.lbl_turn = tk.Label(parent, text="", font=self.font_status,
                                  fg=PAL["text"], bg=PAL["panel"])
        self.lbl_turn.pack(**pad, pady=2)

        self.lbl_info = tk.Label(parent, text="", font=self.font_body,
                                  fg=PAL["text_dim"], bg=PAL["panel"],
                                  wraplength=210, justify="left")
        self.lbl_info.pack(**pad, pady=(0, 4))

        # ── Captured ─────────────────────────────────────────────────────────
        tk.Label(parent, text="CAPTURED PIECES", font=self.font_head,
                 fg=PAL["text_accent"], bg=PAL["panel"]).pack(**pad, pady=(4, 2))
        self._sep(parent)

        cap_frame = tk.Frame(parent, bg=PAL["panel"])
        cap_frame.pack(fill="x", padx=14, pady=2)
        tk.Label(cap_frame, text="⚔ Att captured:",
                 font=self.font_body, fg=PAL["text_dim"],
                 bg=PAL["panel"]).grid(row=0, column=0, sticky="w")
        self.lbl_cap_att = tk.Label(cap_frame, text="0",
                                     font=self.font_status, fg=PAL["text_green"],
                                     bg=PAL["panel"])
        self.lbl_cap_att.grid(row=0, column=1, padx=8)

        tk.Label(cap_frame, text="🛡 Def captured:",
                 font=self.font_body, fg=PAL["text_dim"],
                 bg=PAL["panel"]).grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_cap_def = tk.Label(cap_frame, text="0",
                                     font=self.font_status, fg=PAL["text_red"],
                                     bg=PAL["panel"])
        self.lbl_cap_def.grid(row=1, column=1, padx=8)

        # ── Piece legend ─────────────────────────────────────────────────────
        tk.Label(parent, text="LEGEND", font=self.font_head,
                 fg=PAL["text_accent"], bg=PAL["panel"]).pack(**pad, pady=(6, 2))
        self._sep(parent)

        legend = [
            ("●", PAL["attacker"],  "Attacker  (24)"),
            ("●", PAL["defender"],  "Defender  (12)"),
            ("♛", PAL["king"],      "King — must escape"),
            ("✦", PAL["corner_ring"], "Corner — escape point"),
            ("＋", PAL["text_dim"], "Throne — central"),
        ]
        for sym, col, desc in legend:
            row = tk.Frame(parent, bg=PAL["panel"])
            row.pack(fill="x", padx=14, pady=0)
            tk.Label(row, text=sym, fg=col, bg=PAL["panel"],
                     font=self.font_head, width=2).pack(side="left")
            tk.Label(row, text=desc, fg=PAL["text_dim"],
                     bg=PAL["panel"], font=self.font_small).pack(side="left", padx=4)

        # ── Settings ─────────────────────────────────────────────────────────
        tk.Label(parent, text="SETTINGS", font=self.font_head,
                 fg=PAL["text_accent"], bg=PAL["panel"]).pack(**pad, pady=(6, 2))
        self._sep(parent)

        # Player side
        tk.Label(parent, text="Play as:", font=self.font_body,
                 fg=PAL["text_dim"], bg=PAL["panel"]).pack(**pad, pady=(2, 0))
        side_frame = tk.Frame(parent, bg=PAL["panel"])
        side_frame.pack(fill="x", padx=14, pady=2)
        for val in ("Attacker", "Defender"):
            rb = tk.Radiobutton(side_frame, text=val,
                                variable=self.human_side_var, value=val,
                                font=self.font_body,
                                fg=PAL["text"], bg=PAL["panel"],
                                selectcolor=PAL["btn_active"],
                                activebackground=PAL["panel"],
                                activeforeground=PAL["text"],
                                cursor="hand2",
                                command=self._new_game)
            rb.pack(side="left", padx=(0, 8))

        # Difficulty
        tk.Label(parent, text="Difficulty:", font=self.font_body,
                 fg=PAL["text_dim"], bg=PAL["panel"]).pack(**pad, pady=(2, 0))
        diff_frame = tk.Frame(parent, bg=PAL["panel"])
        diff_frame.pack(fill="x", padx=14, pady=2)
        for val in ("Easy", "Medium", "Hard"):
            rb = tk.Radiobutton(diff_frame, text=val,
                                variable=self.difficulty, value=val,
                                font=self.font_body,
                                fg=PAL["text"], bg=PAL["panel"],
                                selectcolor=PAL["btn_active"],
                                activebackground=PAL["panel"],
                                activeforeground=PAL["text"],
                                cursor="hand2")
            rb.pack(side="left", padx=(0, 6))

        # New game button
        self.btn_new = tk.Button(parent, text="⟳  NEW GAME",
                                  font=self.font_head,
                                  fg=PAL["text_accent"], bg=PAL["btn"],
                                  activebackground=PAL["btn_hover"],
                                  activeforeground=PAL["text_accent"],
                                  relief="flat", cursor="hand2",
                                  command=self._new_game)
        self.btn_new.pack(fill="x", padx=14, pady=(6, 2))
        self.btn_new.bind("<Enter>", lambda e: self.btn_new.config(bg=PAL["btn_hover"]))
        self.btn_new.bind("<Leave>", lambda e: self.btn_new.config(bg=PAL["btn"]))

        # ── Move log ─────────────────────────────────────────────────────────
        tk.Label(parent, text="MOVE LOG", font=self.font_head,
                 fg=PAL["text_accent"], bg=PAL["panel"]).pack(**pad, pady=(6, 2))
        self._sep(parent)

        log_frame = tk.Frame(parent, bg=PAL["panel"])
        log_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        scrollbar = tk.Scrollbar(log_frame, bg=PAL["panel"], troughcolor=PAL["bg"])
        scrollbar.pack(side="right", fill="y")
        self.log_box = tk.Text(log_frame, height=10, width=26,
                               font=self.font_log,
                               bg=PAL["bg"], fg=PAL["text_dim"],
                               relief="flat", state="disabled",
                               yscrollcommand=scrollbar.set,
                               insertbackground=PAL["text"],
                               selectbackground=PAL["selected"],
                               wrap="none")
        self.log_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_box.yview)

    def _sep(self, parent):
        tk.Frame(parent, height=1, bg=PAL["separator"]).pack(
            fill="x", padx=14, pady=2)

    # ─────────────────────────────────────────────────────────────────────── #
    #  BOARD DRAWING                                                           #
    # ─────────────────────────────────────────────────────────────────────── #

    def _cell_to_px(self, row, col):
        """Top-left pixel of a cell."""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return x, y

    def _px_to_cell(self, x, y):
        """Pixel → (row, col), or None if outside board."""
        col = (x - self.margin) // self.cell_size
        row = (y - self.margin) // self.cell_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None

    def _draw_board(self):
        self.canvas.delete("all")
        cs  = self.cell_size
        mar = self.margin

        # ── Outer board frame ────────────────────────────────────────────────
        bx0, by0 = mar - 4, mar - 4
        bx1 = mar + cs * BOARD_SIZE + 4
        by1 = mar + cs * BOARD_SIZE + 4
        self.canvas.create_rectangle(bx0-3, by0-3, bx1+3, by1+3,
                                     fill="#0d0b09", outline="#1a1612", width=2)
        self.canvas.create_rectangle(bx0, by0, bx1, by1,
                                     fill="", outline=PAL["border"], width=2)

        # ── Row / col labels ─────────────────────────────────────────────────
        for i in range(BOARD_SIZE):
            cx = mar + i * cs + cs // 2
            cy = mar + i * cs + cs // 2
            self.canvas.create_text(mar - 14, cy, text=str(i),
                                    font=self.font_small, fill=PAL["text_dim"])
            self.canvas.create_text(cx, mar - 14, text=str(i),
                                    font=self.font_small, fill=PAL["text_dim"])

        # ── Cells ────────────────────────────────────────────────────────────
        valid_set  = set(self.valid_moves)
        sel_row, sel_col = self.selected if self.selected else (-1, -1)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x0, y0 = self._cell_to_px(row, col)
                x1, y1 = x0 + cs, y0 + cs

                # base colour
                if is_corner(row, col):
                    fill = PAL["corner"]
                elif is_throne(row, col):
                    fill = PAL["throne"]
                elif (row + col) % 2 == 0:
                    fill = PAL["cell_light"]
                else:
                    fill = PAL["cell_dark"]

                # overlays
                if row == sel_row and col == sel_col:
                    fill = PAL["selected"]
                elif (row, col) in valid_set:
                    fill = PAL["valid_move"]
                elif self.last_from and (row, col) == self.last_from:
                    fill = PAL["last_move"]
                elif self.last_to and (row, col) == self.last_to:
                    fill = PAL["last_move"]

                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=fill, outline=PAL["bg"], width=1)

                # corner decoration
                if is_corner(row, col):
                    cx, cy = x0 + cs // 2, y0 + cs // 2
                    r = cs // 2 - 4
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                            outline=PAL["corner_ring"], width=2, fill="")

                # throne cross mark
                if is_throne(row, col) and self.board[row][col] == EMPTY:
                    cx, cy = x0 + cs // 2, y0 + cs // 2
                    off = 8
                    self.canvas.create_line(cx - off, cy, cx + off, cy,
                                            fill=PAL["text_dim"], width=1)
                    self.canvas.create_line(cx, cy - off, cx, cy + off,
                                            fill=PAL["text_dim"], width=1)

                # valid-move dot
                if (row, col) in valid_set and self.board[row][col] == EMPTY:
                    cx, cy = x0 + cs // 2, y0 + cs // 2
                    r = 5
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                            fill=PAL["valid_dot"], outline="")

                # draw piece
                piece = self.board[row][col]
                if piece != EMPTY:
                    self._draw_piece(row, col, piece,
                                     selected=(row == sel_row and col == sel_col))

    def _draw_piece(self, row, col, piece, selected=False):
        cs = self.cell_size
        x0, y0 = self._cell_to_px(row, col)
        cx = x0 + cs // 2
        cy = y0 + cs // 2

        if piece == KING:
            # Large gold circle with crown symbol
            r = cs // 2 - 6
            shadow_off = 3
            self.canvas.create_oval(cx - r + shadow_off, cy - r + shadow_off,
                                    cx + r + shadow_off, cy + r + shadow_off,
                                    fill=PAL["king_sh"], outline="")
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=PAL["king_hi"] if selected else PAL["king"],
                                    outline=PAL["king_crown"], width=2)
            self.canvas.create_text(cx, cy, text="♛",
                                    font=tkfont.Font(family="Georgia", size=cs // 4,
                                                     weight="bold"),
                                    fill=PAL["king_sh"])

        elif piece == ATTACKER:
            r = cs // 2 - 8
            shadow_off = 3
            self.canvas.create_oval(cx - r + shadow_off, cy - r + shadow_off,
                                    cx + r + shadow_off, cy + r + shadow_off,
                                    fill=PAL["attacker_sh"], outline="")
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=PAL["attacker_hi"] if selected else PAL["attacker"],
                                    outline="#8b1a10" if not selected else "#ff6060",
                                    width=2)
            # inner highlight
            self.canvas.create_oval(cx - r + 4, cy - r + 4,
                                    cx - 2, cy - 2,
                                    fill="#e06050", outline="")

        elif piece == DEFENDER:
            r = cs // 2 - 8
            shadow_off = 3
            self.canvas.create_oval(cx - r + shadow_off, cy - r + shadow_off,
                                    cx + r + shadow_off, cy + r + shadow_off,
                                    fill=PAL["defender_sh"], outline="")
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=PAL["defender_hi"] if selected else PAL["defender"],
                                    outline="#8b6b3a" if not selected else "#ffe0a0",
                                    width=2)
            self.canvas.create_oval(cx - r + 4, cy - r + 4,
                                    cx - 2, cy - 2,
                                    fill="#ffe0b0", outline="")

    # ─────────────────────────────────────────────────────────────────────── #
    #  SIDE PANEL UPDATE                                                       #
    # ─────────────────────────────────────────────────────────────────────── #

    def _update_side_panel(self):
        if self.game_over:
            return

        if self.ai_thinking:
            self.lbl_turn.config(text="⌛  AI Thinking…",
                                 fg=PAL["text_dim"])
            self.lbl_info.config(
                text=f"Difficulty: {self.difficulty.get()}  "
                     f"(depth {DEPTH_MAP[self.difficulty.get()]})")
        else:
            is_human = (self.current_player == self.human_side)
            if self.current_player == ATTACKER:
                name  = "⚔  ATTACKERS"
                color = PAL["attacker_hi"]
            else:
                name  = "🛡  DEFENDERS"
                color = PAL["defender_hi"]

            who  = "Your turn" if is_human else "Computer's turn"
            self.lbl_turn.config(
                text=f"{name}  ({who})", fg=color)
            self.lbl_info.config(
                text="Click a piece to select it, then click its destination.")

        # captured counts
        att_count = sum(
            1 for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.board[r][c] == ATTACKER)
        def_count = sum(
            1 for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.board[r][c] == DEFENDER)
        cap_att = 24 - att_count
        cap_def = 12 - def_count
        self.lbl_cap_att.config(text=str(cap_att))
        self.lbl_cap_def.config(text=str(cap_def))

    def _log(self, text, tag="normal"):
        self.log_box.config(state="normal")
        colors = {
            "normal" : PAL["text_dim"],
            "human"  : PAL["text"],
            "ai"     : PAL["text_accent"],
            "win"    : PAL["text_green"],
            "lose"   : PAL["text_red"],
            "sep"    : PAL["separator"],
        }
        col = colors.get(tag, PAL["text_dim"])
        move_num = len(self.move_history)
        self.log_box.insert("end", f"{move_num:>3}. {text}\n")
        self.log_box.tag_add(tag, f"end - 2 lines", "end - 1 lines")
        self.log_box.tag_config(tag, foreground=col)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ─────────────────────────────────────────────────────────────────────── #
    #  CLICK HANDLER                                                           #
    # ─────────────────────────────────────────────────────────────────────── #

    def _on_click(self, event):
        if self.game_over or self.ai_thinking:
            return
        if self.current_player != self.human_side:
            return

        cell = self._px_to_cell(event.x, event.y)
        if cell is None:
            return
        row, col = cell

        # ── Case 1: a valid-move destination is clicked ───────────────────
        if self.selected and (row, col) in self.valid_moves:
            self._execute_human_move(self.selected[0], self.selected[1], row, col)
            return

        # ── Case 2: clicking own piece — select it ────────────────────────
        piece = self.board[row][col]
        is_own = (
            (self.human_side == ATTACKER and piece == ATTACKER) or
            (self.human_side == DEFENDER and piece in (DEFENDER, KING))
        )
        if is_own:
            self.selected    = (row, col)
            self.valid_moves = get_valid_moves(self.board, row, col)
            self._draw_board()
            return

        # ── Case 3: clicking elsewhere — deselect ────────────────────────
        self.selected    = None
        self.valid_moves = []
        self._draw_board()

    # ─────────────────────────────────────────────────────────────────────── #
    #  MOVE EXECUTION                                                          #
    # ─────────────────────────────────────────────────────────────────────── #

    def _execute_human_move(self, fr, fc, tr, tc):
        self.last_from = (fr, fc)
        self.last_to   = (tr, tc)
        self.selected  = None
        self.valid_moves = []

        apply_move(self.board, fr, fc, tr, tc)
        self.move_history.append((fr, fc, tr, tc))
        tag = "human" if self.current_player == self.human_side else "ai"
        who = "You" if tag == "human" else "AI"
        self._log(f"{who}: ({fr},{fc})→({tr},{tc})", tag)

        self._draw_board()

        winner = check_game_over(self.board)
        if winner:
            self._announce_winner(winner)
            return

        self._switch_player()
        self._update_side_panel()
        self._draw_board()
        self.after(200, self._maybe_ai_move)

    def _switch_player(self):
        self.current_player = DEFENDER if self.current_player == ATTACKER else ATTACKER

    # ─────────────────────────────────────────────────────────────────────── #
    #  AI MOVE                                                                 #
    # ─────────────────────────────────────────────────────────────────────── #

    def _maybe_ai_move(self):
        if self.game_over:
            return
        if self.current_player != self.human_side:
            self._trigger_ai()

    def _trigger_ai(self):
        self.ai_thinking = True
        self._update_side_panel()
        self._draw_board()
        threading.Thread(target=self._ai_worker, daemon=True).start()

    def _ai_worker(self):
        depth = DEPTH_MAP[self.difficulty.get()]
        move  = get_best_move(self.board, self.current_player, depth)
        self.after(0, lambda: self._apply_ai_move(move))

    def _apply_ai_move(self, move):
        self.ai_thinking = False
        if move is None:
            self._log("AI has no moves!", "lose")
            self.game_over = True
            return

        fr, fc, tr, tc = move
        self.last_from = (fr, fc)
        self.last_to   = (tr, tc)
        self.selected  = None
        self.valid_moves = []

        # Draw the board once so the user can see the AI's origin and target.
        self._draw_board()
        self.after(700, lambda: self._finalize_ai_move(move))

    def _finalize_ai_move(self, move):
        fr, fc, tr, tc = move
        apply_move(self.board, fr, fc, tr, tc)
        self.move_history.append(move)
        self._log(f"AI: ({fr},{fc})→({tr},{tc})", "ai")

        self._draw_board()

        winner = check_game_over(self.board)
        if winner:
            self._announce_winner(winner)
            return

        self._switch_player()
        self._update_side_panel()
        self._draw_board()

    # ─────────────────────────────────────────────────────────────────────── #
    #  GAME OVER                                                               #
# ─────────────────────────────────────────────────────────────────────── #

    def _announce_winner(self, winner):
        self.game_over = True
        human_won = (
            (winner == "defender" and self.human_side == DEFENDER) or
            (winner == "attacker" and self.human_side == ATTACKER)
        )

        if winner == "defender":
            msg   = "👑  KING ESCAPED!\nDefenders WIN!"
            color = PAL["king"]
            log_t = "win"
        else:
            msg   = "⚔  KING CAPTURED!\nAttackers WIN!"
            color = PAL["attacker_hi"]
            log_t = "lose"

        self._log(msg.replace("\n", " — "), log_t)
        self._draw_board()

        # Overlay
        cs  = self.cell_size
        mar = self.margin
        bw  = cs * BOARD_SIZE
        bh  = cs * BOARD_SIZE
        cx  = mar + bw // 2
        cy  = mar + bh // 2

        self.canvas.create_rectangle(mar, mar, mar + bw, mar + bh,
                                     fill="#000000", stipple="gray50", outline="")
        self.canvas.create_rectangle(cx - 180, cy - 60, cx + 180, cy + 60,
                                     fill=PAL["panel"], outline=color, width=3)
        self.canvas.create_text(cx, cy - 18, text=msg.split("\n")[0],
                                font=self.font_title, fill=color)
        self.canvas.create_text(cx, cy + 18, text=msg.split("\n")[1],
                                font=self.font_head, fill=PAL["text"])
        self.canvas.create_text(cx, cy + 44,
                                text=f"{'Victory! 🎉' if human_won else 'Defeat...'}  "
                                     f"Game over after {len(self.move_history)} moves.",
                                font=self.font_body, fill=PAL["text_dim"])

        self.lbl_turn.config(
            text="♛  GAME OVER",
            fg=color)
        self.lbl_info.config(
            text=f"{'You won!' if human_won else 'Computer won.'}  "
                 f"Press ⟳ NEW GAME to play again.")

    # ─────────────────────────────────────────────────────────────────────── #
    #  NEW GAME                                                                #
    # ─────────────────────────────────────────────────────────────────────── #

    def _new_game(self):
        self.board          = create_initial_board()
        self.selected       = None
        self.valid_moves    = []
        self.current_player = ATTACKER
        self.human_side     = ATTACKER if self.human_side_var.get() == "Attacker" else DEFENDER
        self.game_over      = False
        self.ai_thinking    = False
        self.last_from      = None
        self.last_to        = None
        self.move_history   = []

        # Clear log
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        self._draw_board()
        self._update_side_panel()

        # If human is defender, AI (attacker) goes first
        if self.human_side == DEFENDER:
            self.after(400, self._trigger_ai)


# ═══════════════════════════════════════════════════════════════════════════ #
#  SPLASH SCREEN
# ═══════════════════════════════════════════════════════════════════════════ #

class SplashScreen(tk.Toplevel):
    def __init__(self, master, on_start):
        super().__init__(master)
        self.title("Hnefatafl")
        self.configure(bg=PAL["bg"])
        self.resizable(False, False)
        self.on_start = on_start
        self._build()
        self.grab_set()

        # center the splash screen on the monitor
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build(self):
        f = tk.Frame(self, bg=PAL["bg"], padx=50, pady=30)
        f.pack()

        # ── title block ──────────────────────────────────────────────────────
        tk.Label(f, text="⚔", font=tkfont.Font(size=48),
                 fg=PAL["text_accent"], bg=PAL["bg"]).pack()
        tk.Label(f, text="HNEFATAFL",
                 font=tkfont.Font(family="Georgia", size=28, weight="bold"),
                 fg=PAL["text_accent"], bg=PAL["bg"]).pack(pady=(0, 2))
        tk.Label(f, text="Viking Chess",
                 font=tkfont.Font(family="Georgia", size=11, slant="italic"),
                 fg=PAL["text_dim"], bg=PAL["bg"]).pack()

        tk.Frame(f, height=1, bg=PAL["border"]).pack(fill="x", pady=16)

        # ── how to play ──────────────────────────────────────────────────────
        tk.Label(f, text="HOW TO PLAY",
                 font=tkfont.Font(family="Georgia", size=9, weight="bold"),
                 fg=PAL["text_accent"], bg=PAL["bg"]).pack(pady=(0, 8))

        rules = [
            ("♛", "King",       "Defenders win if the King reaches any corner"),
            ("⚔", "Capture",    "Surround the King on all four sides to win"),
            ("→", "Movement",   "All pieces slide any number of squares (like a Rook)"),
            ("⬡", "Sandwich",   "Trap an enemy piece between two of yours to capture it"),
        ]

        rules_frame = tk.Frame(f, bg=PAL["bg"])
        rules_frame.pack(fill="x")

        for icon, label, desc in rules:
            row = tk.Frame(rules_frame, bg=PAL["bg"])
            row.pack(fill="x", pady=3)

            # icon
            tk.Label(row, text=icon, font=tkfont.Font(family="Georgia", size=12),
                     fg=PAL["text_accent"], bg=PAL["bg"], width=2).pack(side="left")

            # label + description
            text_frame = tk.Frame(row, bg=PAL["bg"])
            text_frame.pack(side="left", padx=6)
            tk.Label(text_frame, text=label,
                     font=tkfont.Font(family="Georgia", size=9, weight="bold"),
                     fg=PAL["text"], bg=PAL["bg"], anchor="w").pack(anchor="w")
            tk.Label(text_frame, text=desc,
                     font=tkfont.Font(family="Georgia", size=8),
                     fg=PAL["text_dim"], bg=PAL["bg"], anchor="w").pack(anchor="w")

        tk.Frame(f, height=1, bg=PAL["border"]).pack(fill="x", pady=16)

        # ── course info block ────────────────────────────────────────────────
        course_frame = tk.Frame(f, bg=PAL["bg"])
        course_frame.pack(pady=(0, 16))

        tk.Label(course_frame,
                 text="Cairo University  ·  Faculty of Computing and AI",
                 font=tkfont.Font(family="Georgia", size=9, weight="bold"),
                 fg=PAL["text_dim"], bg=PAL["bg"]).pack()
        tk.Label(course_frame,
                 text="CS361: Artificial Intelligence",
                 font=tkfont.Font(family="Georgia", size=9),
                 fg=PAL["text_dim"], bg=PAL["bg"]).pack(pady=(2, 0))

        # ── begin button ─────────────────────────────────────────────────────
        btn = tk.Button(f, text="▶  BEGIN",
                        font=tkfont.Font(family="Georgia", size=13, weight="bold"),
                        fg=PAL["text_accent"], bg=PAL["btn"],
                        activebackground=PAL["btn_hover"],
                        activeforeground=PAL["text_accent"],
                        relief="flat", cursor="hand2",
                        padx=30, pady=10,
                        command=self._start)
        btn.pack()

    def _start(self):
        self.destroy()
        self.on_start()


# ═══════════════════════════════════════════════════════════════════════════ #
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════ #

def main():
    app = HnefataflGUI()
    app.withdraw()   # hide main window until splash is dismissed

    def show_main():
        app.deiconify()

    splash = SplashScreen(app, show_main)
    app.mainloop()


if __name__ == "__main__":
    main()