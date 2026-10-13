if __name__ == "__main__":
	from PythonChess import main
	main()
	raise SystemExit

from io import BytesIO
import math
import queue
import random
import threading
import time
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, ttk

import chess
import chess.pgn
import chess.svg
import resvg_py
from PIL import Image, ImageTk


BACKGROUND = "#11191B"
PANEL = "#1B292B"
PANEL_LIGHT = "#28393B"
TEXT = "#F1F3EC"
MUTED = "#A3B1AC"
ACCENT = "#C5DE83"
LIGHT_SQUARE = "#EFE7D6"
DARK_SQUARE = "#65847B"
SELECTED = "#E8B85C"
HIGHLIGHT = "#C9D88D"
CAPTURE_MARK = "#D85F58"
AI_THINK_DELAYS = {"Casual": 1600, "Club": 900, "Expert": 50}
INITIAL_CLOCK_SECONDS = 10 * 60
ELO_RECOMMENDATIONS = {
	"Casual": "600-1000",
	"Club": "1000-1400",
	"Expert": "1400-1800",
}
BOARD_THEMES = {
	"Greenhouse": {
		"light": LIGHT_SQUARE,
		"dark": DARK_SQUARE,
		"last_light": HIGHLIGHT,
		"last_dark": "#A99D45",
		"selected": SELECTED,
		"description": "Sage green and warm ivory",
	},
	"Bubblegum": {
		"light": "#F7C9DF",
		"dark": "#579CC9",
		"last_light": "#F3A7CA",
		"last_dark": "#397FAE",
		"selected": "#FFE08A",
		"description": "Candy pink and bright blue",
	},
	"Noir": {
		"light": "#F2F2F0",
		"dark": "#303235",
		"last_light": "#C6C8C7",
		"last_dark": "#56595C",
		"selected": "#A6A8A8",
		"description": "Monochrome black and white",
	},
	"Ocean": {
		"light": "#D4E6EB",
		"dark": "#387C89",
		"last_light": "#AFCFD7",
		"last_dark": "#286674",
		"selected": "#E9C76A",
		"description": "Seafoam and deep teal",
	},
	"Sunset": {
		"light": "#FFE0B2",
		"dark": "#B94E68",
		"last_light": "#F5C77E",
		"last_dark": "#963D58",
		"selected": "#F3A65A",
		"description": "Golden apricot and rose",
	},
	"Lavender": {
		"light": "#E8DDF2",
		"dark": "#6D5A84",
		"last_light": "#D3C0E3",
		"last_dark": "#58466D",
		"selected": "#E4C779",
		"description": "Soft lilac and plum",
	},
	"Wood": {
		"light": "#E9D9B7",
		"dark": "#91694E",
		"last_light": "#D8C395",
		"last_dark": "#77543F",
		"selected": "#A9B87A",
		"description": "Quiet end-grain oak and walnut",
		"texture": "wood",
	},
	"Newspaper": {
		"light": "#F3E6C8",
		"dark": "#486B68",
		"last_light": "#E4D29E",
		"last_dark": "#385653",
		"selected": "#D69B62",
		"description": "Warm paper and deep teal ink",
		"texture": "newspaper",
	},
	"Metallic": {
		"light": "#D8DEE0",
		"dark": "#68747B",
		"last_light": "#B9C5C8",
		"last_dark": "#53616A",
		"selected": "#AFC2C2",
		"description": "Satin steel and graphite",
		"texture": "metallic",
	},
}
PIECE_PALETTES = {
	"Greenhouse": ("#F4F0E1", "#31473F", "#596357", "#E0E9DA", "solid"),
	"Bubblegum": ("#FFF0F5", "#245A86", "#A85E7E", "#E0F7FF", "solid"),
	"Noir": ("#F6F6F3", "#171819", "#3E3F41", "#ECEEEB", "solid"),
	"Ocean": ("#E5F4F5", "#164D61", "#447983", "#D3F3F2", "solid"),
	"Sunset": ("#FFF0D8", "#77384F", "#9D7158", "#FBE2D2", "solid"),
	"Lavender": ("#F5EFFA", "#49355E", "#756080", "#F1E9FC", "solid"),
	"Wood": ("#F3D9A7", "#5A392C", "#80613D", "#D5B47A", "wood"),
	"Newspaper": ("#FFF3D5", "#254A4A", "#9B7448", "#B5C6B4", "print"),
	"Metallic": ("#EFF3F2", "#34434D", "#76858A", "#D2E0E2", "metallic"),
}
for theme_name, (light_fill, dark_fill, light_outline, dark_outline, finish) in PIECE_PALETTES.items():
	BOARD_THEMES[theme_name].update({
		"piece_light": light_fill,
		"piece_dark": dark_fill,
		"piece_light_outline": light_outline,
		"piece_dark_outline": dark_outline,
		"piece_finish": finish,
	})
PIECE_VALUES = {
	chess.PAWN: 100,
	chess.KNIGHT: 320,
	chess.BISHOP: 335,
	chess.ROOK: 500,
	chess.QUEEN: 900,
	chess.KING: 20000,
}


def format_clock(seconds):
	remaining = max(0, int(seconds + 0.999))
	minutes, remainder = divmod(remaining, 60)
	return f"{minutes:02d}:{remainder:02d}"


def draw_piece(canvas, center_x, center_y, size, piece, theme=None, image_height=None):
	image_size = max(24, int(round(size)))
	image_height = image_size if image_height is None else max(1, int(round(image_height)))
	theme = theme or BOARD_THEMES["Greenhouse"]
	cache = getattr(canvas, "piece_image_cache", None)
	if cache is None:
		cache = {}
		canvas.piece_image_cache = cache
	key = (piece.piece_type, piece.color, image_size, image_height, theme["piece_light"],
		   theme["piece_dark"], theme["piece_light_outline"],
		   theme["piece_dark_outline"], theme["piece_finish"])
	image = cache.get(key)
	if image is None:
		base_key = (piece.piece_type, piece.color, image_size, image_size,
					theme["piece_light"], theme["piece_dark"],
					theme["piece_light_outline"], theme["piece_dark_outline"],
					theme["piece_finish"])
		base_image = cache.get(base_key)
		if base_image is None:
			base_image = ImageTk.PhotoImage(
				_render_piece_image(image_size, piece, theme), master=canvas
			)
			cache[base_key] = base_image
		if image_height == image_size:
			image = base_image
		else:
			rendered = ImageTk.getimage(base_image).resize(
				(image_size, image_height), Image.Resampling.LANCZOS
			)
			image = ImageTk.PhotoImage(rendered, master=canvas)
		cache[key] = image
	canvas.create_image(center_x, center_y, image=image, anchor="center")


def _themed_piece_svg(piece, theme, size):
	svg = chess.svg.piece(piece, size=size)
	root = ET.fromstring(svg)
	namespace = "http://www.w3.org/2000/svg"
	group = root.find(f"{{{namespace}}}g")
	color_key = "light" if piece.color == chess.WHITE else "dark"
	piece_fill = theme[f"piece_{color_key}"]
	piece_outline = theme[f"piece_{color_key}_outline"]
	group.set("fill", piece_fill)
	group.set("stroke", piece_outline)

	finish = theme["piece_finish"]
	if finish in ("wood", "metallic"):
		definition = ET.Element(f"{{{namespace}}}defs")
		gradient = ET.SubElement(definition, f"{{{namespace}}}linearGradient", {
			"id": "theme-finish", "x1": "0%", "y1": "0%", "x2": "12%", "y2": "100%",
		})
		if finish == "metallic":
			stops = (
				(("0%", "#E5ECEB"), ("48%", "#BFCBCB"), ("100%", "#D8E0DE"))
				if piece.color == chess.WHITE else
				(("0%", "#52636A"), ("52%", "#394A52"), ("100%", "#2C3C44"))
			)
		else:
			stops = (
				(("0%", "#F2DDB2"), ("55%", "#E5C58B"), ("100%", "#D8B578"))
				if piece.color == chess.WHITE else
				(("0%", "#75513D"), ("52%", "#5E4031"), ("100%", "#4B3329"))
			)
		for offset, color in stops:
			ET.SubElement(gradient, f"{{{namespace}}}stop", {
				"offset": offset, "stop-color": color,
			})
		root.insert(0, definition)
		group.set("fill", "url(#theme-finish)")

	for element in group.iter():
		if element is group:
			continue
		styled_fill = "url(#theme-finish)" if finish in ("wood", "metallic") else piece_fill
		fill = element.get("fill")
		if fill and fill.lower() != "none":
			element.set("fill", styled_fill)
		stroke = element.get("stroke")
		if stroke and stroke.lower() != "none":
			element.set("stroke", piece_outline)
		style = element.get("style")
		if style:
			declarations = {}
			for declaration in style.split(";"):
				property_name, separator, value = declaration.partition(":")
				if separator:
					declarations[property_name.strip()] = value.strip()
			if declarations.get("fill", "").lower() != "none":
				declarations["fill"] = styled_fill
			if declarations.get("stroke", "").lower() != "none":
				declarations["stroke"] = piece_outline
			element.set("style", "; ".join(
				f"{property_name}:{value}" for property_name, value in declarations.items()
			) + ";")

	return ET.tostring(root, encoding="unicode")


def _render_piece_image(size, piece, theme=None):
	theme = theme or BOARD_THEMES["Greenhouse"]
	oversampled_size = size * 4
	styled_svg = _themed_piece_svg(piece, theme, oversampled_size)
	png_data = resvg_py.svg_to_bytes(
		svg_string=styled_svg,
		width=oversampled_size,
		height=oversampled_size,
		shape_rendering="geometric_precision",
	)
	with Image.open(BytesIO(png_data)) as rendered:
		return rendered.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)


def evaluate_position(board):
	score = 0
	for square, piece in board.piece_map().items():
		value = PIECE_VALUES[piece.piece_type]
		file_index = chess.square_file(square)
		rank_index = chess.square_rank(square)
		center_distance = abs(3.5 - file_index) + abs(3.5 - rank_index)
		if piece.piece_type in (chess.KNIGHT, chess.BISHOP, chess.QUEEN):
			value += int((7 - center_distance) * 4)
		elif piece.piece_type == chess.PAWN:
			advance = rank_index if piece.color == chess.WHITE else 7 - rank_index
			value += advance * 7
		score += value if piece.color == chess.WHITE else -value
	return score if board.turn == chess.WHITE else -score


def ordered_moves(board):
	moves = list(board.legal_moves)

	def move_priority(move):
		priority = 0
		if board.is_capture(move):
			captured = board.piece_at(move.to_square)
			if captured is None and board.is_en_passant(move):
				captured_value = PIECE_VALUES[chess.PAWN]
			else:
				captured_value = PIECE_VALUES[captured.piece_type] if captured else 0
			attacker = board.piece_at(move.from_square)
			priority += captured_value * 10 - (PIECE_VALUES[attacker.piece_type] if attacker else 0)
		if move.promotion:
			priority += PIECE_VALUES[move.promotion]
		return priority

	moves.sort(key=move_priority, reverse=True)
	return moves


class _SearchStopped(Exception):
	pass


class _SearchTimedOut(Exception):
	pass


class _SearchContext:
	def __init__(self, cancel_event=None, deadline=None):
		self.cancel_event = cancel_event
		self.deadline = deadline
		self.transposition = {}

	def check(self):
		if self.cancel_event and self.cancel_event.is_set():
			raise _SearchStopped
		if self.deadline is not None and time.monotonic() >= self.deadline:
			raise _SearchTimedOut


def draw_claim_reasons(board):
	reasons = []
	if board.can_claim_threefold_repetition():
		reasons.append("threefold repetition")
	if board.can_claim_fifty_moves():
		reasons.append("the 50-move rule")
	return reasons


def read_pgn(path):
	with open(path, encoding="utf-8") as source:
		game = chess.pgn.read_game(source)
	if game is None:
		raise ValueError("The file does not contain a chess game.")
	if game.errors:
		raise ValueError("The PGN contains invalid moves.")

	board = game.board()
	move_sans = []
	for move in game.mainline_moves():
		move_sans.append(board.san(move))
		board.push(move)
	return board, move_sans


def write_pgn(board, draw_claimed=False):
	game = chess.pgn.Game.from_board(board)
	game.headers["Event"] = "Greenhouse Chess"
	if draw_claimed:
		game.headers["Result"] = "1/2-1/2"
	return f"{game}\n"


def search_position(board, depth, alpha=-1000000, beta=1000000, ply=0, context=None):
	if context is None:
		context = _SearchContext()
	context.check()
	if board.is_checkmate():
		return -100000 + ply
	if (board.is_stalemate() or board.is_insufficient_material()
			or board.is_seventyfive_moves() or board.is_fivefold_repetition()
			or board.can_claim_draw()):
		return 0
	if depth <= 0:
		return evaluate_position(board)

	cache_key = (board.fen(), depth)
	if cache_key in context.transposition:
		return context.transposition[cache_key]

	best_score = -1000000
	cutoff = False
	for move in ordered_moves(board):
		board.push(move)
		try:
			score = -search_position(board, depth - 1, -beta, -alpha, ply + 1, context)
		finally:
			board.pop()
		best_score = max(best_score, score)
		alpha = max(alpha, score)
		if alpha >= beta:
			cutoff = True
			break
	if not cutoff:
		context.transposition[cache_key] = best_score
	return best_score


def choose_computer_move(board, depth, cancel_event=None, time_limit=2.5):
	moves = ordered_moves(board)
	if not moves:
		return None
	context = _SearchContext(cancel_event, time.monotonic() + time_limit)
	best_move = moves[0]

	try:
		for current_depth in range(1, depth + 1):
			context.check()
			best_score = -1000000
			best_moves = []
			alpha = -1000000
			for move in moves:
				board.push(move)
				try:
					score = -search_position(board, current_depth - 1,
											-1000000, -alpha, 1, context)
				finally:
					board.pop()
				if score > best_score:
					best_score = score
					best_moves = [move]
				elif score == best_score:
					best_moves.append(move)
				alpha = max(alpha, score)
			best_move = random.choice(best_moves)
	except _SearchTimedOut:
		pass
	except _SearchStopped:
		return None
	return best_move


class ChessGame:
	def __init__(self, root):
		self.root = root
		self.board = chess.Board()
		self.move_sans = []
		self.selected_square = None
		self.legal_targets = []
		self.drag_to_move = False
		self.drag_from = None
		self.drag_pointer = None
		self.move_animation = None
		self.animation_after_id = None
		self.board_flip_animation = None
		self.board_flip_after_id = None
		self.board_flip_scale = 1.0
		self.flipped = False
		self.ai_pending = False
		self.draw_claimed = False
		self.game_mode = "computer"
		self.clock_enabled = True
		self.clock_remaining = {
			chess.WHITE: float(INITIAL_CLOCK_SECONDS),
			chess.BLACK: float(INITIAL_CLOCK_SECONDS),
		}
		self.clock_loser = None
		self.clock_last_tick = time.monotonic()
		self.theme_name = "Greenhouse"
		self.board_theme = BOARD_THEMES[self.theme_name]
		self.search_token = 0
		self.ai_cancel_event = None
		self.ai_after_id = None
		self.ai_results = queue.Queue()
		self.last_ai_error = None

		self.root.title("Python Chess")
		self.root.configure(bg=BACKGROUND)
		self.root.geometry("1120x790")
		self.root.minsize(620, 760)
		self._build_styles()
		self._build_layout()
		self._stacked_layout = None
		self.root.bind("<Configure>", self._on_root_configure)
		self.root.after_idle(lambda: self._on_root_configure())
		self._update_view()
		self._refresh_clock_display()
		self.root.after(100, self._tick_match_clock)
		self.root.after(70, self._poll_ai_results)

	def _build_styles(self):
		style = ttk.Style()
		style.theme_use("clam")
		style.configure("Game.TCombobox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT,
						foreground=TEXT, arrowcolor=ACCENT, bordercolor=PANEL_LIGHT,
						lightcolor=PANEL_LIGHT, darkcolor=PANEL_LIGHT, padding=8)
		style.map("Game.TCombobox", fieldbackground=[("readonly", PANEL_LIGHT)],
				  foreground=[("readonly", TEXT)])
		style.configure("Game.Vertical.TScrollbar", background=PANEL_LIGHT,
						troughcolor=PANEL, arrowcolor=MUTED, bordercolor=PANEL)
		style.configure("Theme.TRadiobutton", background=PANEL, foreground=TEXT,
						font=("Segoe UI", 11, "bold"), padding=0)
		style.map("Theme.TRadiobutton", background=[("active", PANEL)],
				  foreground=[("disabled", MUTED)])
		style.configure("Theme.TCheckbutton", background=BACKGROUND, foreground=TEXT,
						font=("Segoe UI", 10, "bold"), padding=4)
		style.map("Theme.TCheckbutton", background=[("active", BACKGROUND)],
				  foreground=[("disabled", MUTED)])
		style.configure("SettingsTitle.TLabel", background=BACKGROUND, foreground=TEXT,
						font=("Segoe UI", 20, "bold"))
		style.configure("SettingsSubtitle.TLabel", background=BACKGROUND, foreground=MUTED,
						font=("Segoe UI", 10))
		style.configure("ThemeDescription.TLabel", background=PANEL, foreground=MUTED,
						font=("Segoe UI", 9))

	def _build_layout(self):
		menubar = tk.Menu(self.root)
		file_menu = tk.Menu(menubar, tearoff=False)
		file_menu.add_command(label="Import PGN...", command=self.import_pgn)
		file_menu.add_command(label="Export PGN...", command=self.export_pgn)
		file_menu.add_separator()
		file_menu.add_command(label="Settings...", command=self.open_settings)
		file_menu.add_separator()
		file_menu.add_command(label="New game", command=self.new_game)
		menubar.add_cascade(label="File", menu=file_menu)
		self.root.configure(menu=menubar)

		header = tk.Frame(self.root, bg=BACKGROUND)
		header.pack(fill="x", padx=28, pady=(22, 14))

		title_area = tk.Frame(header, bg=BACKGROUND)
		title_area.pack(side="left", fill="x", expand=True)
		tk.Label(title_area, text="PYTHON", bg=BACKGROUND, fg=ACCENT,
				 font=("Segoe UI", 10, "bold")).pack(anchor="w")
		tk.Label(title_area, text="Chess", bg=BACKGROUND, fg=TEXT,
				 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(1, 0))

		self.header_actions = tk.Frame(header, bg=BACKGROUND)
		self.header_actions.pack(side="right", anchor="center")
		self._button(self.header_actions, "↶  Undo", self.undo_move).pack(side="left", padx=(0, 8))
		self.claim_button = self._button(self.header_actions, "Claim draw", self.claim_draw)
		self.claim_button.pack(side="left", padx=(0, 8))
		self._button(self.header_actions, "↻  New game", self.new_game, primary=True).pack(side="left")

		content = tk.Frame(self.root, bg=BACKGROUND)
		content.pack(fill="both", expand=True, padx=28, pady=(0, 24))
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		self.content = content

		self.board_panel = tk.Frame(content, bg=BACKGROUND)
		self.board_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
		self.board_panel.rowconfigure(0, weight=1)
		self.board_panel.columnconfigure(0, weight=1)

		self.canvas = tk.Canvas(self.board_panel, bg=BACKGROUND, highlightthickness=0,
								cursor="hand2")
		self.canvas.grid(row=0, column=0, sticky="nsew")
		self.canvas.bind("<Configure>", lambda _event: self._draw_board())
		self.canvas.bind("<Button-1>", self._on_board_click)
		self.canvas.bind("<B1-Motion>", self._on_board_drag_motion)
		self.canvas.bind("<ButtonRelease-1>", self._on_board_drag_release)

		self.side_panel = tk.Frame(content, bg=PANEL, width=280)
		self.side_panel.grid(row=0, column=1, sticky="ns")
		self.side_panel.grid_propagate(False)
		self.side_panel.configure(width=280, height=470)

		self.status_dot = tk.Canvas(self.side_panel, width=12, height=12,
									bg=PANEL, highlightthickness=0)
		self.status_dot.pack(anchor="w", padx=20, pady=(22, 0))
		self.status_label = tk.Label(self.side_panel, text="Your move", bg=PANEL,
									 fg=TEXT, font=("Segoe UI", 16, "bold"), anchor="w")
		self.status_label.pack(fill="x", padx=20, pady=(7, 0))
		self.detail_label = tk.Label(self.side_panel, text="Play as White",
									 bg=PANEL, fg=MUTED, font=("Segoe UI", 10), anchor="w")
		self.detail_label.pack(fill="x", padx=20, pady=(3, 20))

		tk.Label(self.side_panel, text="MATCH CLOCK", background=PANEL,
				 foreground=MUTED, font=("Segoe UI", 9, "bold")).pack(
			anchor="w", padx=20, pady=(0, 7))
		self.clock_rows = {}
		self.clock_labels = {}
		for color, name in ((chess.WHITE, "YOU"), (chess.BLACK, "COMPUTER")):
			row = tk.Frame(self.side_panel, bg=PANEL_LIGHT, padx=10, pady=5)
			row.pack(fill="x", padx=20, pady=(0, 5))
			name_label = tk.Label(row, text=name, bg=PANEL_LIGHT, fg=MUTED,
								 font=("Segoe UI", 9, "bold"), anchor="w")
			name_label.pack(side="left")
			clock_label = tk.Label(
				row, text=format_clock(INITIAL_CLOCK_SECONDS), bg=PANEL_LIGHT,
				fg=TEXT, font=("Consolas", 15, "bold"), anchor="e",
			)
			clock_label.pack(side="right")
			self.clock_rows[color] = (row, name_label)
			self.clock_labels[color] = clock_label

		self._divider(self.side_panel)
		self.difficulty_title = tk.Label(self.side_panel, text="COMPUTER STRENGTH", bg=PANEL,
									 fg=MUTED, font=("Segoe UI", 9, "bold"))
		self.difficulty_title.pack(anchor="w", padx=20, pady=(18, 8))
		self.difficulty = tk.StringVar(value="Club")
		self.difficulty_box = ttk.Combobox(
			self.side_panel, textvariable=self.difficulty,
			values=("Casual", "Club", "Expert"), state="readonly", style="Game.TCombobox",
		)
		self.difficulty_box.pack(fill="x", padx=20)
		self.difficulty_box.bind("<<ComboboxSelected>>", self._difficulty_changed)
		self.difficulty_hint = tk.Label(self.side_panel,
										 text="Suggested Elo: 1000-1400 · balanced",
										 bg=PANEL, fg=MUTED,
										 font=("Segoe UI", 9), anchor="w")
		self.difficulty_hint.pack(fill="x", padx=20, pady=(7, 18))

		self._divider(self.side_panel)
		moves_header = tk.Frame(self.side_panel, bg=PANEL)
		moves_header.pack(fill="x", padx=20, pady=(18, 9))
		tk.Label(moves_header, text="MOVE HISTORY", bg=PANEL, fg=MUTED,
				 font=("Segoe UI", 9, "bold")).pack(side="left")
		self.move_count = tk.Label(moves_header, text="0 plies", bg=PANEL,
								   fg=MUTED, font=("Segoe UI", 9))
		self.move_count.pack(side="right")

		history_frame = tk.Frame(self.side_panel, bg=PANEL)
		history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 14))
		self.history = tk.Listbox(
			history_frame, bg=PANEL, fg=TEXT, selectbackground=PANEL_LIGHT,
			selectforeground=TEXT, highlightthickness=0, borderwidth=0,
			font=("Consolas", 10), activestyle="none", takefocus=False,
		)
		self.history.pack(side="left", fill="both", expand=True)
		scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history.yview,
								 style="Game.Vertical.TScrollbar")
		scrollbar.pack(side="right", fill="y")
		self.history.configure(yscrollcommand=scrollbar.set)

		self._divider(self.side_panel)
		footer = tk.Frame(self.side_panel, bg=PANEL)
		footer.pack(fill="x", padx=20, pady=16)
		self._button(footer, "Settings", self.open_settings).pack(side="left", padx=(0, 8))
		self._button(footer, "⇄  Flip board", self.flip_board).pack(side="left")

	def _on_root_configure(self, event=None):
		if event is not None and event.widget is not self.root:
			return
		width = self.root.winfo_width()
		stacked = width < 900
		if stacked != self._stacked_layout:
			self.board_panel.grid_forget()
			self.side_panel.grid_forget()
			self.content.grid_columnconfigure(1, weight=0)
			self.content.grid_rowconfigure(1, weight=0)
			self.content.grid_rowconfigure(0, weight=1)
			if stacked:
				self.board_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
				self.side_panel.grid(row=1, column=0, sticky="ew")
			else:
				self.board_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
				self.side_panel.grid(row=0, column=1, sticky="ns")
			self._stacked_layout = stacked
		if stacked:
			self.side_panel.configure(width=max(280, width - 56))
		else:
			self.side_panel.configure(width=280)

	def import_pgn(self):
		path = filedialog.askopenfilename(
			parent=self.root, title="Import chess game", filetypes=(("PGN files", "*.pgn"), ("All files", "*.*")),
		)
		if not path:
			return
		try:
			board, move_sans = read_pgn(path)
		except (OSError, ValueError) as error:
			messagebox.showerror("Import failed", str(error), parent=self.root)
			return

		self._cancel_ai_search()
		self._cancel_move_animation()
		self._reset_match_clock()
		self.board = board
		self.move_sans = move_sans
		self.draw_claimed = False
		self.selected_square = None
		self.legal_targets = []
		self.last_ai_error = None
		self._update_view()
		if (self.game_mode == "computer" and not self.board.is_game_over()
				and self.board.turn == chess.BLACK):
			self._request_ai_move()

	def export_pgn(self):
		path = filedialog.asksaveasfilename(
			parent=self.root, title="Export chess game", defaultextension=".pgn",
			initialfile="greenhouse-chess.pgn",
			filetypes=(("PGN files", "*.pgn"), ("All files", "*.*")),
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8", newline="\n") as target:
				target.write(write_pgn(self.board, self.draw_claimed))
		except OSError as error:
			messagebox.showerror("Export failed", str(error), parent=self.root)

	def _button(self, parent, text, command, primary=False):
		background = ACCENT if primary else PANEL_LIGHT
		foreground = "#172016" if primary else TEXT
		hover_background = "#D5EAA0" if primary else "#354A4C"
		button = tk.Button(
			parent, text=text, command=command, bg=background, fg=foreground,
			activebackground=hover_background, activeforeground=foreground, relief="flat",
			disabledforeground=MUTED, borderwidth=0, padx=14, pady=9, cursor="hand2",
			highlightthickness=0, font=("Segoe UI", 10, "bold"),
		)
		button.bind("<Enter>", lambda _event: button.configure(bg=hover_background)
					 if button["state"] == tk.NORMAL else None)
		button.bind("<Leave>", lambda _event: button.configure(bg=background))
		return button

	@staticmethod
	def _divider(parent):
		tk.Frame(parent, bg="#34443A", height=1).pack(fill="x")

	def _difficulty_changed(self, _event=None):
		hints = {
			"Casual": f"Suggested Elo: {ELO_RECOMMENDATIONS['Casual']} · relaxed pace",
			"Club": f"Suggested Elo: {ELO_RECOMMENDATIONS['Club']} · balanced",
			"Expert": f"Suggested Elo: {ELO_RECOMMENDATIONS['Expert']} · deeper search",
		}
		self.difficulty_hint.configure(text=hints[self.difficulty.get()])

	def _refresh_mode_controls(self):
		if self.game_mode == "friend":
			self.difficulty_title.configure(text="COMPUTER STRENGTH · OFF")
			self.difficulty_box.configure(state="disabled")
			self.difficulty_hint.configure(text="Unavailable in Play A Friend mode")
		else:
			self.difficulty_title.configure(text="COMPUTER STRENGTH")
			self.difficulty_box.configure(state="readonly")
			self._difficulty_changed()

	def open_settings(self):
		dialog = tk.Toplevel(self.root)
		dialog.title("Settings")
		dialog.configure(bg=BACKGROUND)
		dialog.transient(self.root)
		dialog.resizable(False, False)
		dialog.grab_set()
		dialog.geometry("440x620")

		ttk.Label(dialog, text="Settings", style="SettingsTitle.TLabel").pack(
			anchor="w", padx=24, pady=(22, 2))
		ttk.Label(dialog, text="Board theme", style="SettingsSubtitle.TLabel").pack(
			anchor="w", padx=24, pady=(0, 14))

		buttons = tk.Frame(dialog, bg=BACKGROUND)
		buttons.pack(side="bottom", fill="x", padx=24, pady=(12, 20))
		cancel_button = self._button(buttons, "Cancel", dialog.destroy)
		cancel_button.pack(side="right", padx=(8, 0))
		apply_button = self._button(
			buttons, "Apply", lambda: None, primary=True,
		)
		apply_button.pack(side="right")

		mode_selection = tk.StringVar(
			value="Play A Friend" if self.game_mode == "friend" else "Play vs Computer",
		)
		ttk.Label(dialog, text="Game mode", style="SettingsSubtitle.TLabel").pack(
			anchor="w", padx=24, pady=(0, 5))
		mode_box = ttk.Combobox(
			dialog, textvariable=mode_selection,
			values=("Play vs Computer", "Play A Friend"),
			state="readonly", style="Game.TCombobox",
		)
		mode_box.pack(fill="x", padx=24, pady=(0, 10))
		clock_selection = tk.BooleanVar(value=self.clock_enabled)
		ttk.Checkbutton(
			dialog, text="Enable match clock", variable=clock_selection,
			style="Theme.TCheckbutton",
		).pack(anchor="w", padx=24, pady=(0, 2))
		selection = tk.StringVar(value=self.theme_name)
		drag_selection = tk.BooleanVar(value=self.drag_to_move)
		ttk.Checkbutton(
			dialog, text="Drag pieces to move", variable=drag_selection,
			style="Theme.TCheckbutton",
		).pack(anchor="w", padx=24, pady=(0, 10))
		theme_list = tk.Frame(dialog, bg=BACKGROUND)
		theme_list.pack(fill="both", expand=True, padx=24)
		list_canvas = tk.Canvas(theme_list, bg=BACKGROUND, highlightthickness=0,
								borderwidth=0, yscrollincrement=12)
		scrollbar = ttk.Scrollbar(
			theme_list, orient="vertical", command=list_canvas.yview,
				style="Game.Vertical.TScrollbar",
		)
		list_canvas.configure(yscrollcommand=scrollbar.set)
		list_canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		options = tk.Frame(list_canvas, bg=BACKGROUND)
		options_window = list_canvas.create_window((0, 0), window=options, anchor="nw")
		options.bind(
			"<Configure>",
			lambda _event: list_canvas.configure(scrollregion=list_canvas.bbox("all")),
		)
		list_canvas.bind(
			"<Configure>",
			lambda event: list_canvas.itemconfigure(options_window, width=event.width),
		)
		for name, theme in BOARD_THEMES.items():
			row = tk.Frame(options, bg=PANEL, padx=12, pady=8)
			row.pack(fill="x", pady=(0, 8))
			labels = tk.Frame(row, bg=PANEL)
			labels.pack(side="left", fill="x", expand=True)
			ttk.Radiobutton(
				labels, text=name, value=name, variable=selection,
				style="Theme.TRadiobutton",
			).pack(anchor="w")
			ttk.Label(labels, text=theme["description"], style="ThemeDescription.TLabel").pack(
				anchor="w", padx=(24, 0), pady=(1, 0))
			preview = tk.Canvas(row, width=92, height=42, bg=PANEL,
							highlightthickness=0, bd=0)
			preview.pack(side="right")
			for square_row in range(2):
				for square_column in range(4):
					color = theme["dark"] if (square_row + square_column) % 2 else theme["light"]
					preview.create_rectangle(
						square_column * 23, square_row * 21,
						(square_column + 1) * 23, (square_row + 1) * 21,
						fill=color, outline="",
					)
			draw_piece(preview, 23, 21, 24, chess.Piece(chess.PAWN, chess.WHITE), theme)
			draw_piece(preview, 69, 21, 24, chess.Piece(chess.PAWN, chess.BLACK), theme)

		def apply_theme():
			new_mode = "friend" if mode_selection.get() == "Play A Friend" else "computer"
			if new_mode != self.game_mode:
				self._cancel_ai_search()
			self.game_mode = new_mode
			self.clock_enabled = clock_selection.get()
			if not self.clock_enabled:
				self.clock_loser = None
			self.clock_last_tick = time.monotonic()
			self.drag_to_move = drag_selection.get()
			if not self.drag_to_move:
				self.drag_from = None
				self.drag_pointer = None
			self._refresh_mode_controls()
			self._apply_board_theme(selection.get())
			self._update_view()
			dialog.destroy()
			if (self.game_mode == "computer" and self.board.turn == chess.BLACK
					and not self.board.is_game_over() and self.clock_loser is None):
				self._request_ai_move()

		apply_button.configure(command=apply_theme)
		dialog.bind("<Escape>", lambda _event: dialog.destroy())

	def _apply_board_theme(self, name):
		if name not in BOARD_THEMES:
			return
		self.theme_name = name
		self.board_theme = BOARD_THEMES[name]
		self._draw_board()

	def _draw_board(self):
		self.canvas.delete("all")
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()
		if width < 10 or height < 10:
			return
		vertical_margin = 25
		board_size = min(width - 150, height - vertical_margin * 2)
		if board_size <= 0:
			return
		square_size = board_size / 8
		square_height = square_size * self.board_flip_scale
		left = (width - board_size) / 2
		top = (height - square_height * 8) / 2
		self.board_geometry = (left, top, square_size)
		captured_pieces = self._captured_pieces()
		last_move = self.board.peek() if self.board.move_stack else None
		animation = self.move_animation
		hidden_squares = animation["hidden_squares"] if animation else ()

		for row in range(8):
			for column in range(8):
				square = self._display_square(column, row)
				x1 = left + column * square_size
				y1 = top + row * square_height
				x2 = x1 + square_size
				y2 = y1 + square_height
				is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
				color = self.board_theme["light"] if is_light else self.board_theme["dark"]
				if last_move and square in (last_move.from_square, last_move.to_square):
					color = self.board_theme["last_light"] if is_light else self.board_theme["last_dark"]
				if square == self.selected_square:
					color = self.board_theme["selected"]
				self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
				if square in self.legal_targets and self.board.piece_at(square):
					self.canvas.create_rectangle(
						x1, y1, x2, y2, fill=CAPTURE_MARK,
						stipple="gray75", outline="",
					)
				texture = self.board_theme.get("texture")
				if texture == "newspaper":
					texture_color = "#C3AE82" if is_light else "#78938D"
					line_lengths = (0.72, 0.54, 0.66, 0.43)
					for line_index, line_length in enumerate(line_lengths):
						y = y1 + square_height * (0.2 + line_index * 0.16)
						start = x1 + square_size * 0.13
						end = start + square_size * line_length
						self.canvas.create_line(start, y, end, y, fill=texture_color, width=1)
				elif texture == "wood":
					grain_color = "#D9C7A3" if is_light else "#805B44"
					frame_color = "#D4C29F" if is_light else "#805B44"
					self.canvas.create_rectangle(
						x1 + 3, y1 + 3, x2 - 3, y2 - 3,
						outline=frame_color, width=1,
					)
					grain_index = (chess.square_file(square) * 3 + chess.square_rank(square)) % 5
					if grain_index == 0:
						knot_x = x1 + square_size * (0.28 + (row % 2) * 0.12)
						knot_y = y1 + square_height * 0.68
						self.canvas.create_oval(
							knot_x - square_size * 0.10, knot_y - square_height * 0.06,
							knot_x + square_size * 0.10, knot_y + square_height * 0.06,
							outline=grain_color, width=1,
						)
						self.canvas.create_oval(
							knot_x - square_size * 0.045, knot_y - square_height * 0.025,
							knot_x + square_size * 0.045, knot_y + square_height * 0.025,
							outline=grain_color, width=1,
						)
				elif texture == "metallic":
					highlight = "#E6EBEC" if is_light else "#89969B"
					shadow = "#C5CED0" if is_light else "#58666D"
					self.canvas.create_rectangle(
						x1 + 3, y1 + 3, x2 - 3, y2 - 3,
						outline=shadow, width=1,
					)
					self.canvas.create_line(
						x1 + 4, y1 + 4, x2 - 4, y1 + 4,
						fill=highlight, width=1,
					)
					self.canvas.create_line(
						x1 + 4, y1 + 4, x1 + 4, y2 - 4,
						fill=highlight, width=1,
					)

				piece = self.board.piece_at(square)
				if piece and square != self.drag_from and square not in hidden_squares:
					draw_piece(self.canvas, x1 + square_size / 2,
							   y1 + square_height / 2, square_size, piece, self.board_theme,
							   image_height=square_height)
				if square in self.legal_targets:
					center_x = x1 + square_size / 2
					center_y = y1 + square_height / 2
					if not self.board.piece_at(square):
						radius = square_size * .13
						y_radius = square_height * .13
						self.canvas.create_oval(center_x - radius, center_y - y_radius,
											center_x + radius, center_y + y_radius,
												fill=self.board_theme["selected"], outline="")

				if column == 0 and self.board_flip_scale >= 0.7:
					rank_label = 1 + row if self.flipped else 8 - row
					self.canvas.create_text(left - 12, y1 + square_height / 2,
											text=str(rank_label), fill=MUTED,
											font=("Segoe UI", 9, "bold"))
				if row == 7 and self.board_flip_scale >= 0.7:
					file_index = 7 - column if self.flipped else column
					self.canvas.create_text(x1 + square_size / 2, top + board_size + 12,
											text=chess.FILE_NAMES[file_index], fill=MUTED,
											font=("Segoe UI", 9, "bold"))

		self._draw_capture_trays(captured_pieces, left, top, board_size)

		if animation:
			for piece, center_x, center_y in animation["positions"]:
				draw_piece(self.canvas, center_x, center_y, square_size,
						   piece, self.board_theme)

		if self.drag_from is not None and self.drag_pointer is not None:
			piece = self.board.piece_at(self.drag_from)
			if piece:
				draw_piece(self.canvas, *self.drag_pointer, square_size, piece, self.board_theme)

	def _captured_pieces(self):
		captured = {chess.WHITE: [], chess.BLACK: []}
		position = self.board.root()
		for move in self.board.move_stack:
			if position.is_capture(move):
				captured_square = move.to_square
				if position.is_en_passant(move):
					captured_square += -8 if position.turn == chess.WHITE else 8
				piece = position.piece_at(captured_square)
				if piece is not None:
					captured[position.turn].append(piece)
			position.push(move)
		return captured

	def _draw_capture_trays(self, captured_pieces, left, top, board_size):
		tray_y = top + board_size / 2
		right = self.canvas.winfo_width() - left - board_size
		for color, center_x, label in (
			(chess.WHITE, left / 2, "White"),
			(chess.BLACK, left + board_size + right / 2, "Black"),
		):
			pieces = captured_pieces[color]
			self.canvas.create_text(
				center_x, tray_y - 22, text=f"{label} {len(pieces)}",
				fill=TEXT, font=("Segoe UI", 8, "bold"),
			)
			visible_pieces = pieces[-7:]
			icon_size = 24
			offset = min(9, (left - icon_size) / max(1, len(visible_pieces) - 1))
			stack_width = icon_size + max(0, len(visible_pieces) - 1) * offset
			start_x = center_x - stack_width / 2 + icon_size / 2
			for index, piece in enumerate(visible_pieces):
				draw_piece(
					self.canvas, start_x + index * offset, tray_y + 3,
					icon_size, piece, self.board_theme,
				)

	def _display_square(self, column, row):
		file_index = 7 - column if self.flipped else column
		rank_index = row if self.flipped else 7 - row
		return chess.square(file_index, rank_index)

	def _square_from_event(self, event):
		if not hasattr(self, "board_geometry"):
			return None
		left, top, square_size = self.board_geometry
		if square_size <= 0:
			return None
		column = int((event.x - left) // square_size)
		row = int((event.y - top) // square_size)
		if not (0 <= column < 8 and 0 <= row < 8):
			return None
		return self._display_square(column, row)

	def _square_center(self, square):
		left, top, size = self.board_geometry
		file_index = chess.square_file(square)
		rank_index = chess.square_rank(square)
		column = 7 - file_index if self.flipped else file_index
		row = rank_index if self.flipped else 7 - rank_index
		return left + (column + 0.5) * size, top + (row + 0.5) * size

	def _animate_move(self, move):
		tracks = [{
			"piece": self.board.piece_at(move.from_square),
			"source": move.from_square,
			"target": move.to_square,
		}]
		hidden_squares = {move.from_square}
		if self.board.is_capture(move):
			captured_square = move.to_square
			if self.board.is_en_passant(move):
				captured_square += -8 if self.board.turn == chess.WHITE else 8
			hidden_squares.add(captured_square)
		if self.board.is_castling(move):
			rank = chess.square_rank(move.from_square)
			king_side = self.board.is_kingside_castling(move)
			rook_source = chess.square(7 if king_side else 0, rank)
			rook_target = chess.square(5 if king_side else 3, rank)
			tracks.append({
				"piece": self.board.piece_at(rook_source),
				"source": rook_source,
				"target": rook_target,
			})
			hidden_squares.add(rook_source)

		started = time.monotonic()
		animation = {
			"move": move,
			"tracks": tracks,
			"hidden_squares": hidden_squares,
			"started": started,
			"duration": 0.14,
			"positions": [
				(track["piece"], *self._square_center(track["source"]))
				for track in tracks
			],
		}
		self.move_animation = animation
		self.selected_square = None
		self.legal_targets = []
		self._draw_board()

		def animate_frame():
			self.animation_after_id = None
			if self.move_animation is not animation:
				return
			progress = min(1.0, (time.monotonic() - started) / animation["duration"])
			eased = progress * progress * (3 - 2 * progress)
			positions = []
			for track in tracks:
				start_x, start_y = self._square_center(track["source"])
				end_x, end_y = self._square_center(track["target"])
				center_x = start_x + (end_x - start_x) * eased
				center_y = start_y + (end_y - start_y) * eased
				positions.append((track["piece"], center_x, center_y))
			animation["positions"] = positions
			self._draw_board()
			if progress >= 1.0:
				self.move_animation = None
				self._play_move(move)
			else:
				self.animation_after_id = self.root.after(14, animate_frame)
		self.animation_after_id = self.root.after(14, animate_frame)

	def _cancel_move_animation(self):
		self._cancel_board_flip_animation()
		if self.animation_after_id is not None:
			try:
				self.root.after_cancel(self.animation_after_id)
			except tk.TclError:
				pass
			self.animation_after_id = None
		if self.move_animation is not None:
			self.move_animation = None
			self._draw_board()

	def _is_human_turn(self):
		return self.game_mode == "friend" or self.board.turn == chess.WHITE

	def _on_board_click(self, event):
		if (self.move_animation or self.board_flip_animation or self.clock_loser is not None or self.draw_claimed
				or self.board.is_game_over()
				or self.ai_pending or not self._is_human_turn()):
			return
		square = self._square_from_event(event)
		if square is None:
			return

		if self.drag_to_move:
			piece = self.board.piece_at(square)
			if piece and piece.color == self.board.turn:
				self.drag_from = square
				self.drag_pointer = (event.x, event.y)
				self.selected_square = square
				self.legal_targets = [move.to_square for move in self.board.legal_moves
								  if move.from_square == square]
			else:
				self.drag_from = None
				self.drag_pointer = None
				self.selected_square = None
				self.legal_targets = []
			self._draw_board()
			return

		if self.selected_square is not None:
			if self._attempt_move(self.selected_square, square, animate=True):
				return

		piece = self.board.piece_at(square)
		if piece and piece.color == self.board.turn:
			self.selected_square = square
			self.legal_targets = [move.to_square for move in self.board.legal_moves
								  if move.from_square == square]
		else:
			self.selected_square = None
			self.legal_targets = []
		self._draw_board()

	def _on_board_drag_motion(self, event):
		if (not self.drag_to_move or self.drag_from is None or self.move_animation
				or self.board_flip_animation
				or self.clock_loser is not None):
			return
		self.drag_pointer = (event.x, event.y)
		self._draw_board()

	def _on_board_drag_release(self, event):
		if (not self.drag_to_move or self.drag_from is None or self.move_animation
				or self.board_flip_animation
				or self.clock_loser is not None):
			return
		source = self.drag_from
		target = self._square_from_event(event)
		self.drag_from = None
		self.drag_pointer = None
		self.selected_square = None
		self.legal_targets = []
		if target is None or not self._attempt_move(source, target):
			self._draw_board()

	def _attempt_move(self, source, target, animate=False):
		if target is None or self.clock_loser is not None or self.board_flip_animation:
			return False
		candidates = [move for move in self.board.legal_moves
					  if move.from_square == source and move.to_square == target]
		if not candidates:
			return False
		move = candidates[0]
		if move.promotion:
			promotion = self._choose_promotion()
			if promotion is None:
				return False
			move = chess.Move(move.from_square, move.to_square, promotion=promotion)
		if animate:
			self._animate_move(move)
		else:
			self._play_move(move)
		return True

	def _choose_promotion(self):
		dialog = tk.Toplevel(self.root)
		dialog.title("Promote pawn")
		dialog.configure(bg=PANEL)
		dialog.transient(self.root)
		dialog.grab_set()
		dialog.resizable(False, False)
		tk.Label(dialog, text="Choose a piece", bg=PANEL, fg=TEXT,
				 font=("Segoe UI", 12, "bold")).pack(padx=18, pady=(16, 10))
		choice = {"piece": None}
		options = tk.Frame(dialog, bg=PANEL)
		options.pack(padx=12, pady=(0, 14))
		for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
			option = tk.Canvas(options, width=56, height=64, bg=PANEL_LIGHT,
							highlightthickness=0, cursor="hand2")
			draw_piece(option, 28, 31, 52, chess.Piece(piece_type, chess.WHITE), self.board_theme)
			option.pack(side="left", padx=3)
			option.bind(
				"<Button-1>",
				lambda _event, value=piece_type: (choice.update(piece=value), dialog.destroy()),
			)
			option.bind("<Enter>", lambda _event, widget=option: widget.configure(bg="#34483A"))
			option.bind("<Leave>", lambda _event, widget=option: widget.configure(bg=PANEL_LIGHT))
		dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
		self.root.wait_window(dialog)
		return choice["piece"]

	def _play_move(self, move):
		self.move_sans.append(self.board.san(move))
		self.board.push(move)
		self.selected_square = None
		self.legal_targets = []
		self.drag_from = None
		self.drag_pointer = None
		self._update_view()
		if (self.game_mode == "friend" and not self.board.is_game_over()
				and self.clock_loser is None):
			self._animate_board_flip()
		if (self.game_mode == "computer" and not self.board.is_game_over()
				and self.board.turn == chess.BLACK):
			self._request_ai_move()

	def _cancel_ai_search(self):
		self.search_token += 1
		if self.ai_after_id:
			self.root.after_cancel(self.ai_after_id)
			self.ai_after_id = None
		if self.ai_cancel_event:
			self.ai_cancel_event.set()
		self.ai_cancel_event = None
		self.ai_pending = False

	def _request_ai_move(self):
		if (self.game_mode != "computer" or self.board.turn != chess.BLACK
				or self.board.is_game_over() or self.clock_loser is not None):
			return
		depths = {"Casual": 1, "Club": 2, "Expert": 4}
		difficulty = self.difficulty.get()
		depth = depths[difficulty]
		delay = AI_THINK_DELAYS[difficulty]
		self.last_ai_error = None
		position = self.board.copy()
		self.search_token += 1
		token = self.search_token
		cancel_event = threading.Event()
		self.ai_cancel_event = cancel_event
		self.ai_pending = True
		self._update_view()

		def start_search():
			self.ai_after_id = None
			if token != self.search_token or cancel_event.is_set():
				return

			def think():
				try:
					move = choose_computer_move(position, depth, cancel_event=cancel_event)
					result = move.uci() if move else None
					self.ai_results.put((token, result, None))
				except Exception as error:
					self.ai_results.put((token, None, str(error)))

			threading.Thread(target=think, daemon=True).start()

		if delay:
			self.ai_after_id = self.root.after(delay, start_search)
		else:
			start_search()

	def _poll_ai_results(self):
		try:
			token, move_text, error = self.ai_results.get_nowait()
		except queue.Empty:
			self.root.after(70, self._poll_ai_results)
			return
		if token == self.search_token:
			self.ai_pending = False
			self.ai_cancel_event = None
			self.ai_after_id = None
			if error:
				self.last_ai_error = error
			if (move_text and self.game_mode == "computer" and self.board.turn == chess.BLACK
					and self.clock_loser is None and not self.board.is_game_over()):
				move = chess.Move.from_uci(move_text)
				if move in self.board.legal_moves:
					self._animate_move(move)
				else:
					self.last_ai_error = "Computer returned an invalid move."
			self._update_view()
		self.root.after(70, self._poll_ai_results)

	def _clock_running_color(self):
		if (not self.clock_enabled or self.clock_loser is not None or self.draw_claimed or self.board.is_game_over()
				or self.move_animation is not None):
			return None
		return self.board.turn

	def _refresh_clock_display(self):
		active_color = self._clock_running_color()
		for color, (row, name_label) in self.clock_rows.items():
			is_active = color == active_color
			background = "#31413B" if is_active else PANEL_LIGHT
			foreground = "#E97969" if self.clock_remaining[color] <= 60 else (ACCENT if is_active else TEXT)
			row.configure(bg=background)
			name = ("WHITE" if color == chess.WHITE else "BLACK") if self.game_mode == "friend" else (
				"YOU" if color == chess.WHITE else "COMPUTER"
			)
			name_label.configure(text=name, bg=background, fg=ACCENT if is_active else MUTED)
			self.clock_labels[color].configure(
				text=format_clock(self.clock_remaining[color]) if self.clock_enabled else "OFF",
				bg=background, fg=foreground,
			)

	def _tick_match_clock(self):
		now = time.monotonic()
		elapsed = max(0.0, now - self.clock_last_tick)
		self.clock_last_tick = now
		active_color = self._clock_running_color()
		if active_color is not None:
			remaining = max(0.0, self.clock_remaining[active_color] - elapsed)
			self.clock_remaining[active_color] = remaining
			if remaining <= 0:
				self.clock_loser = active_color
				self._cancel_ai_search()
				self.selected_square = None
				self.legal_targets = []
				self.drag_from = None
				self.drag_pointer = None
				self._update_view()
		self._refresh_clock_display()
		self.root.after(100, self._tick_match_clock)

	def _reset_match_clock(self):
		self.clock_remaining = {
			chess.WHITE: float(INITIAL_CLOCK_SECONDS),
			chess.BLACK: float(INITIAL_CLOCK_SECONDS),
		}
		self.clock_loser = None
		self.clock_last_tick = time.monotonic()
		self._refresh_clock_display()

	def _update_view(self):
		self._draw_board()
		self.history.delete(0, tk.END)
		for index in range(0, len(self.move_sans), 2):
			white_move = self.move_sans[index]
			black_move = self.move_sans[index + 1] if index + 1 < len(self.move_sans) else "..."
			self.history.insert(tk.END, f"{index // 2 + 1:>2}.  {white_move:<9} {black_move}")
		self.move_count.configure(text=f"{len(self.move_sans)} plies")

		if self.clock_loser is not None:
			message = "Time expired"
			if self.game_mode == "friend":
				winner = "Black" if self.clock_loser == chess.WHITE else "White"
				detail = f"{winner} wins on time"
			else:
				detail = "Computer wins on time" if self.clock_loser == chess.WHITE else "You win on time"
			dot_color = "#E58A7A" if self.clock_loser == chess.WHITE else ACCENT
		elif self.draw_claimed:
			message, detail, dot_color = "Draw", self.draw_claimed, MUTED
		elif self.board.is_checkmate():
			message = "Checkmate"
			if self.game_mode == "friend":
				detail = "White wins" if self.board.turn == chess.BLACK else "Black wins"
			else:
				detail = "You win" if self.board.turn == chess.BLACK else "Computer wins"
			dot_color = ACCENT if self.board.turn == chess.BLACK else "#E58A7A"
		elif self.board.is_stalemate() or self.board.is_insufficient_material():
			message, detail, dot_color = "Draw", "The game is tied", MUTED
		elif self.board.is_game_over():
			outcome = self.board.outcome()
			reason = outcome.termination.name.replace("_", " ").lower()
			message, detail, dot_color = "Game over", f"Draw: {reason}", MUTED
		elif self.ai_pending:
			message, detail, dot_color = "Thinking", "Computer is considering a move", ACCENT
		elif self.board.is_check():
			message = "Check"
			if self.game_mode == "friend":
				detail = "White king is in check" if self.board.turn == chess.WHITE else "Black king is in check"
			else:
				detail = "Your king is in check" if self.board.turn == chess.WHITE else "Computer king is in check"
			dot_color = "#E58A7A"
		elif self.game_mode == "friend":
			message = "White to move" if self.board.turn == chess.WHITE else "Black to move"
			detail = "Player 1" if self.board.turn == chess.WHITE else "Player 2"
			dot_color = ACCENT
		elif self.board.turn == chess.WHITE:
			message, detail, dot_color = "Your move", "Play as White", ACCENT
		else:
			message, detail, dot_color = "Computer's move", "Play as White", ACCENT

		if self.last_ai_error and not self.board.is_game_over():
			detail = "Computer error: " + self.last_ai_error
		self.status_label.configure(text=message)
		self.detail_label.configure(text=detail)
		can_claim = (
			not self.draw_claimed and not self.ai_pending and self.clock_loser is None
			and (self.game_mode == "friend" or self.board.turn == chess.WHITE)
			and draw_claim_reasons(self.board)
		)
		self.claim_button.configure(state=tk.NORMAL if can_claim else tk.DISABLED)
		self.status_dot.delete("all")
		self.status_dot.create_oval(2, 2, 10, 10, fill=dot_color, outline="")
		if self.move_sans:
			self.history.see(tk.END)
		self._refresh_clock_display()

	def undo_move(self):
		self._cancel_move_animation()
		if not self.board.move_stack:
			return
		self._cancel_ai_search()
		self.draw_claimed = False
		plies = 2 if self.board.turn == chess.WHITE and len(self.board.move_stack) >= 2 else 1
		for _ in range(plies):
			if self.board.move_stack:
				self.board.pop()
				self.move_sans.pop()
		self.selected_square = None
		self.legal_targets = []
		self.drag_from = None
		self.drag_pointer = None
		self.last_ai_error = None
		self._update_view()

	def claim_draw(self):
		if (self.clock_loser is not None or self.ai_pending
			or (self.game_mode == "computer" and self.board.turn != chess.WHITE)
			or not self.board.can_claim_draw()):
			return
		reasons = draw_claim_reasons(self.board)
		self.draw_claimed = "Draw claimed by " + " or ".join(reasons)
		self._update_view()

	def _animate_board_flip(self):
		self._cancel_board_flip_animation()
		animation = {"started": time.monotonic(), "duration": 0.36, "flipped": False}
		self.board_flip_animation = animation

		def animate_frame():
			self.board_flip_after_id = None
			if self.board_flip_animation is not animation:
				return
			progress = min(1.0, (time.monotonic() - animation["started"]) / animation["duration"])
			self.board_flip_scale = max(0.04, abs(math.cos(progress * math.pi)))
			if progress >= 0.5 and not animation["flipped"]:
				self.flipped = not self.flipped
				animation["flipped"] = True
			self._draw_board()
			if progress >= 1.0:
				self.board_flip_scale = 1.0
				self.board_flip_animation = None
				self._update_view()
			else:
				self.board_flip_after_id = self.root.after(16, animate_frame)

		self.board_flip_after_id = self.root.after(0, animate_frame)

	def _cancel_board_flip_animation(self):
		if self.board_flip_after_id is not None:
			try:
				self.root.after_cancel(self.board_flip_after_id)
			except tk.TclError:
				pass
			self.board_flip_after_id = None
		if self.board_flip_animation is not None:
			self.board_flip_animation = None
			self.board_flip_scale = 1.0
			self._draw_board()

	def new_game(self):
		self._cancel_move_animation()
		self._cancel_ai_search()
		self._reset_match_clock()
		self.draw_claimed = False
		self.board.reset()
		self.move_sans.clear()
		self.selected_square = None
		self.legal_targets = []
		self.drag_from = None
		self.drag_pointer = None
		self.last_ai_error = None
		self._update_view()

	def flip_board(self):
		self._cancel_board_flip_animation()
		self.flipped = not self.flipped
		self._draw_board()


def main():
	root = tk.Tk()
	ChessGame(root)
	root.mainloop()


if __name__ == "__main__":
	main()