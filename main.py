import pygame
from pygame_chess_api.api import Board, Piece, Move, Pawn, Knight, Bishop, Rook, Queen, Check
from pygame_chess_api.render import Gui
import time
from concurrent.futures import ThreadPoolExecutor

MAX_DEPTH = 2  # Tăng độ sâu để cải thiện độ mạnh của bot

# Define position tables for chess pieces
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

ROOK_TABLE = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, -5, 0, 0, 0, 0, -5, -5],
    [-5, -5, 0, 0, 0, 0, -5, -5],
    [-5, -5, 0, 0, 0, 0, -5, -5],
    [-5, -5, 0, 0, 0, 0, -5, -5],
    [-5, -5, 0, 0, 0, 0, -5, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]
# Other piece tables remain unchanged

position_tables = {
    Pawn: PAWN_TABLE,
    Knight: KNIGHT_TABLE,
    Bishop: BISHOP_TABLE,
    Rook: ROOK_TABLE,
    Queen: QUEEN_TABLE,
    Check: KING_TABLE
}

transposition_table = {}  # Initialize transposition table


def evaluate_board(board: Board):
    evaluation = 0
    for piece in board.pieces_by_color[Piece.WHITE]:
        value = piece.SCORE_VALUE
        row, col = piece.pos[1], piece.pos[0]  # (x, y) → (col, row)
        value += position_tables.get(type(piece), [[0] * 8] * 8)[row][col]
        value += len(piece.get_moves_allowed()) * 0.1  # Mobility bonus
        evaluation -= value

    for piece in board.pieces_by_color[Piece.BLACK]:
        value = piece.SCORE_VALUE
        row, col = piece.pos[1], piece.pos[0]  # (x, y) → (col, row)
        value += position_tables.get(type(piece), [[0] * 8] * 8)[row][col]
        value += len(piece.get_moves_allowed()) * 0.1  # Mobility bonus
        evaluation += value

    return evaluation


# Improved Minimax with iterative deepening

def minimax(board: Board, depth: int, alpha: float, beta: float, maximizing: bool, start_time: float):
    board_hash = hash(board)  # Use a hash of the board state
    if board_hash in transposition_table:
        return transposition_table[board_hash]

    if time.time() - start_time > MAX_TIME:
        return evaluate_board(board), None

    if depth == 0 or board.game_ended:
        return quiescence_search(board, alpha, beta, maximizing), None

    best_move = None
    if maximizing:
        max_eval = float("-inf")
        for piece in board.pieces_by_color[board.cur_color_turn]:
            moves = order_moves(piece, piece.get_moves_allowed())
            for move in moves:
                hypo_board = board.create_hypothesis_board({piece: move})
                evaluation, _ = minimax(hypo_board, depth - 1, alpha, beta, False, start_time)

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Cắt tỉa Alpha-Beta

        transposition_table[board_hash] = (max_eval, best_move)
        return max_eval, best_move

    else:
        min_eval = float("inf")
        for piece in board.pieces_by_color[board.cur_color_turn]:
            moves = order_moves(piece, piece.get_moves_allowed())
            for move in moves:
                hypo_board = board.create_hypothesis_board({piece: move})
                evaluation, _ = minimax(hypo_board, depth - 1, alpha, beta, True, start_time)

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move

                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Cắt tỉa Alpha-Beta

        transposition_table[board_hash] = (min_eval, best_move)
        return min_eval, best_move


def parallel_minimax(board: Board, depth: int, alpha: float, beta: float, maximizing: bool, start_time: float):
    with ThreadPoolExecutor() as executor:
        futures = []
        for piece in board.pieces_by_color[board.cur_color_turn]:
            moves = order_moves(piece, piece.get_moves_allowed())
            for move in moves:
                hypo_board = board.create_hypothesis_board({piece: move})
                futures.append(executor.submit(minimax, hypo_board, depth - 1, alpha, beta, not maximizing, start_time))

        results = [future.result() for future in futures]
        if maximizing:
            return max(results, key=lambda x: x[0])
        else:
            return min(results, key=lambda x: x[0])


def quiescence_search(board: Board, alpha: float, beta: float, maximizing: bool):
    stand_pat = evaluate_board(board)
    if maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    for piece in board.pieces_by_color[board.cur_color_turn]:
        moves = [move for move in piece.get_moves_allowed() if piece.board.pieces_by_pos.get(move.destination)]  # Only consider captures
        for move in moves:
            hypo_board = board.create_hypothesis_board({piece: move})
            score = -quiescence_search(hypo_board, -beta, -alpha, not maximizing)
            if maximizing:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            if beta <= alpha:
                break

    return alpha if maximizing else beta


def order_moves(piece, moves):
    """
    Order moves to improve alpha-beta pruning efficiency.
    Prioritize capturing moves and moves that put the opponent in check.
    """
    def move_score(move):
        # Check if the move is a capturing move
        target_square = move.destination  # Assuming `move.destination` gives the target square
        target_piece = piece.board.pieces_by_pos.get(target_square)  # Get the piece at the target square
        if target_piece and target_piece.color != piece.color:
            return target_piece.SCORE_VALUE  # Higher score for capturing valuable pieces
        if move.special_type == Move.TO_PROMOTE_TYPE:
            return 900  # High score for pawn promotion
        return 0  # Default score for non-capturing moves

    return sorted(moves, key=move_score, reverse=True)


# AI move function using iterative deepening search

import time

MAX_TIME = 2  # Giới hạn thời gian tìm kiếm là 10 giây


def function_for_ai(board: Board):
    """
    AI sẽ chọn nước đi tốt nhất trong vòng 10 giây bằng Iterative Deepening.
    """
    start_time = time.time()
    best_move = None
    depth = 1

    while time.time() - start_time < MAX_TIME:
        _, move = minimax(board, depth, float("-inf"), float("inf"), True, start_time)

        if move:
            best_move = move  # Lưu nước đi tốt nhất cho đến lúc này

        depth += 1  # Tăng độ sâu tìm kiếm dần dần

    if best_move:
        best_move.piece.move(best_move)

    print(f"AI Move: {best_move} | Depth Searched: {depth - 1} | Time Taken: {time.time() - start_time:.2f}s")


pygame.init()

board = Board()
gui = Gui(board, (Piece.WHITE,))
gui.run_pygame_loop(function_for_ai)
