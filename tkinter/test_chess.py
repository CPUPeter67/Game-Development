import io
import os
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET

import chess
import chess.pgn

from PythonChess import (
	AI_THINK_DELAYS,
	BOARD_THEMES,
	ELO_RECOMMENDATIONS,
	INITIAL_CLOCK_SECONDS,
	choose_computer_move,
	draw_claim_reasons,
	format_clock,
	read_pgn,
	_themed_piece_svg,
	_render_piece_image,
	write_pgn,
)


class ChessLogicTests(unittest.TestCase):
	def test_match_clock_format_and_initial_time(self):
		self.assertEqual(INITIAL_CLOCK_SECONDS, 600)
		self.assertEqual(format_clock(INITIAL_CLOCK_SECONDS), "10:00")
		self.assertEqual(format_clock(59.2), "01:00")
		self.assertEqual(format_clock(0), "00:00")

	def test_board_theme_palettes_cover_requested_styles(self):
		self.assertEqual(
			set(BOARD_THEMES),
			{"Greenhouse", "Bubblegum", "Noir", "Ocean", "Sunset", "Lavender",
			 "Wood", "Newspaper", "Metallic"},
		)
		bubblegum = BOARD_THEMES["Bubblegum"]
		noir = BOARD_THEMES["Noir"]
		self.assertTrue(bubblegum["light"].startswith("#F"))
		self.assertEqual(noir["light"], "#F2F2F0")
		self.assertEqual(noir["dark"], "#303235")
		for theme in BOARD_THEMES.values():
			self.assertIn("last_light", theme)
			self.assertIn("last_dark", theme)
			self.assertIn("selected", theme)
			self.assertIn("description", theme)
			self.assertIn("piece_light", theme)
			self.assertIn("piece_dark", theme)
			self.assertIn("piece_light_outline", theme)
			self.assertIn("piece_dark_outline", theme)
			self.assertIn("piece_finish", theme)
		self.assertEqual(BOARD_THEMES["Newspaper"]["texture"], "newspaper")
		self.assertEqual(BOARD_THEMES["Wood"]["texture"], "wood")
		self.assertEqual(BOARD_THEMES["Metallic"]["texture"], "metallic")

	def test_piece_renderer_returns_transparent_art_for_both_colors(self):
		for piece_type in chess.PIECE_TYPES:
			white_image = _render_piece_image(96, chess.Piece(piece_type, chess.WHITE))
			black_image = _render_piece_image(96, chess.Piece(piece_type, chess.BLACK))

			self.assertEqual(white_image.size, (96, 96))
			self.assertEqual(black_image.size, (96, 96))
			self.assertEqual(white_image.getpixel((0, 0))[3], 0)
			self.assertEqual(black_image.getpixel((0, 0))[3], 0)
			self.assertNotEqual(white_image.tobytes(), black_image.tobytes())

		for theme in BOARD_THEMES.values():
			for piece_type in chess.PIECE_TYPES:
				for color in (chess.WHITE, chess.BLACK):
					image = _render_piece_image(48, chess.Piece(piece_type, color), theme)
					self.assertEqual(image.size, (48, 48))
					self.assertEqual(image.getpixel((0, 0))[3], 0)

		for color in (chess.WHITE, chess.BLACK):
			color_key = "light" if color == chess.WHITE else "dark"
			for piece_type in chess.PIECE_TYPES:
				theme = BOARD_THEMES["Greenhouse"]
				root = ET.fromstring(
					_themed_piece_svg(chess.Piece(piece_type, color), theme, 96)
				)
				namespace = "{http://www.w3.org/2000/svg}"
				group = root.find(f"{namespace}g")
				self.assertEqual(group.get("fill"), theme[f"piece_{color_key}"])
				self.assertEqual(group.get("stroke"), theme[f"piece_{color_key}_outline"])
				for element in group.iter():
					if element is group:
						continue
					fill = element.get("fill")
					stroke = element.get("stroke")
					if fill and fill != "none":
						self.assertEqual(fill, theme[f"piece_{color_key}"])
					if stroke and stroke != "none":
						self.assertEqual(stroke, theme[f"piece_{color_key}_outline"])
					style = element.get("style", "")
					declarations = {
						name.strip(): value.strip()
						for name, value in (item.split(":", 1) for item in style.split(";") if ":" in item)
					}
					if declarations.get("fill", "none") != "none":
						self.assertEqual(declarations["fill"], theme[f"piece_{color_key}"])
					if declarations.get("stroke", "none") != "none":
						self.assertEqual(declarations["stroke"], theme[f"piece_{color_key}_outline"])

		wood_piece = _render_piece_image(
			96, chess.Piece(chess.QUEEN, chess.WHITE), BOARD_THEMES["Wood"]
		)
		metallic_piece = _render_piece_image(
			96, chess.Piece(chess.QUEEN, chess.WHITE), BOARD_THEMES["Metallic"]
		)
		greenhouse_queen = _render_piece_image(
			96, chess.Piece(chess.QUEEN, chess.WHITE), BOARD_THEMES["Greenhouse"]
		)
		self.assertNotEqual(wood_piece.tobytes(), metallic_piece.tobytes())
		self.assertNotEqual(wood_piece.tobytes(), greenhouse_queen.tobytes())
		self.assertNotEqual(metallic_piece.tobytes(), greenhouse_queen.tobytes())
		greenhouse_piece = _render_piece_image(
			96, chess.Piece(chess.KING, chess.WHITE), BOARD_THEMES["Greenhouse"]
		)
		bubblegum_piece = _render_piece_image(
			96, chess.Piece(chess.KING, chess.WHITE), BOARD_THEMES["Bubblegum"]
		)
		self.assertNotEqual(greenhouse_piece.tobytes(), bubblegum_piece.tobytes())

	def test_easier_bots_have_longer_think_delays(self):
		self.assertGreater(AI_THINK_DELAYS["Casual"], AI_THINK_DELAYS["Club"])
		self.assertGreater(AI_THINK_DELAYS["Club"], AI_THINK_DELAYS["Expert"])
		self.assertEqual(set(ELO_RECOMMENDATIONS), set(AI_THINK_DELAYS))

	def test_computer_returns_legal_move_without_mutating_board(self):
		board = chess.Board()
		original_fen = board.fen()

		move = choose_computer_move(board, depth=1, time_limit=1)

		self.assertIn(move, board.legal_moves)
		self.assertEqual(board.fen(), original_fen)

	def test_cancelled_search_returns_no_move(self):
		cancel_event = threading.Event()
		cancel_event.set()

		self.assertIsNone(choose_computer_move(chess.Board(), 3, cancel_event=cancel_event))

	def test_threefold_claim_is_reported(self):
		board = chess.Board()
		for san in ["Nf3", "Nf6", "Ng1", "Ng8"] * 2:
			board.push_san(san)

		self.assertIn("threefold repetition", draw_claim_reasons(board))

	def test_fifty_move_claim_is_reported(self):
		board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 99 50")

		self.assertIn("the 50-move rule", draw_claim_reasons(board))

	def test_pgn_round_trip_preserves_position_and_moves(self):
		board = chess.Board()
		for san in ("e4", "e5", "Nf3", "Nc6"):
			board.push_san(san)
		pgn = write_pgn(board)
		with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".pgn", delete=False) as target:
			target.write(pgn)
			path = target.name
		try:
			loaded_board, move_sans = read_pgn(path)
		finally:
			os.unlink(path)

		self.assertEqual(loaded_board.fen(), board.fen())
		self.assertEqual(move_sans, ["e4", "e5", "Nf3", "Nc6"])

	def test_export_marks_claimed_draw_as_draw(self):
		game = chess.pgn.read_game(io.StringIO(write_pgn(chess.Board(), draw_claimed=True)))

		self.assertEqual(game.headers["Result"], "1/2-1/2")


if __name__ == "__main__":
	unittest.main()