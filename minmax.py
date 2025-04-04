import chess
import random

zobrist_table = {}
for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
    for square in chess.SQUARES:
        zobrist_table[(piece, square)] = random.getrandbits(64)

zobrist_table['white_turn'] = random.getrandbits(64)

zobrist_table['castling_wk'] = random.getrandbits(64)
zobrist_table['castling_wq'] = random.getrandbits(64)
zobrist_table['castling_bk'] = random.getrandbits(64)
zobrist_table['castling_bq'] = random.getrandbits(64)


# key: zobrist_hash, value = (value, depth, flag, best_move)
transposition_tables = {}


def evaluate_board(board):
    """Hàm đánh giá bàn cờ dựa trên giá trị quân cờ"""
    piece_values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            score += value if piece.color == chess.WHITE else -value
    return score


def zobrist_hash(board : chess.Board):
    hash_key = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            hash_key ^= zobrist_table[(piece.symbol(), square)]
    if board.turn == chess.WHITE:
        hash_key ^= zobrist_table['white_turn']

    if board.castling_rights & chess.BB_H1:
        hash_key ^= zobrist_table['castling_wk']
    if board.castling_rights & chess.BB_A1:
        hash_key ^= zobrist_table['castling_wq']
    if board.castling_rights & chess.BB_H8:
        hash_key ^= zobrist_table['castling_bk']
    if board.castling_rights & chess.BB_A8:
        hash_key ^= zobrist_table['castling_bq']

    return hash_key


def update_hash_key(board : chess.Board, move : chess.Move, old_hash : int):
    piece = board.piece_at(move.from_square).symbol()
    hash_key = old_hash
    hash_key ^= zobrist_table[piece, move.from_square]
    hash_key ^= zobrist_table[piece, move.to_square]

    hash_key ^= zobrist_table['white_turn']

    old_castling = board.castling_rights
    board.push(move)  # Thực hiện nước đi để lấy castling mới
    new_castling = board.castling_rights
    board.pop()  # Quay lại

    if (old_castling & chess.BB_H1) and not (new_castling & chess.BB_H1):
        hash_key ^= zobrist_table['castling_wk']
    if (old_castling & chess.BB_A1) and not (new_castling & chess.BB_A1):
        hash_key ^= zobrist_table['castling_wq']
    if (old_castling & chess.BB_H8) and not (new_castling & chess.BB_H8):
        hash_key ^= zobrist_table['castling_bk']
    if (old_castling & chess.BB_A8) and not (new_castling & chess.BB_A8):
        hash_key ^= zobrist_table['castling_bq']

    return hash_key




def minimax(board, depth, alpha, beta, maximizing_player, hash_key, move):
    if (hash_key is None):
        hash_key = zobrist_hash(board)

    if (hash_key in transposition_tables) and (transposition_tables[hash_key]['depth'] >= depth):
        entry = transposition_tables[hash_key]
        if entry['flag'] == 'exact':
            return entry['value']
        if entry['flag'] == 'upper' and entry['value']  <= alpha:
            return entry['value']
        if entry['flag'] == 'lower' and entry['value'] >= beta:
            return entry['value']


    if depth == 0 or board.is_game_over():
        value = evaluate_board(board)
        transposition_tables[hash_key] = {'value' : value,'depth': 0 ,'flag' : 'exact'}
        return value

    legal_moves = list(board.legal_moves)

    if maximizing_player:
        max_eval = -float("inf")
        for move in legal_moves:
            new_hash_key = update_hash_key(board, move, hash_key)
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False, new_hash_key, move)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        if max_eval <= alpha:  # alpha không thay đổi, đây là upper bound
            flag = 'upper'
        elif max_eval >= beta:  # beta cắt, đây là lower bound
            flag = 'lower'
        else:  # giá trị nằm giữa alpha và beta, exact
            flag = 'exact'
        transposition_tables[hash_key] = {'value': max_eval, 'depth': depth, 'flag': flag}
        return max_eval
    else:
        min_eval = float("inf")
        for move in legal_moves:
            new_hash_key = update_hash_key(board, move, hash_key)
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True, new_hash_key, move)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        if min_eval <= alpha:  # alpha không thay đổi, đây là upper bound
            flag = 'upper'
        elif min_eval >= beta:  # beta cắt, đây là lower bound
            flag = 'lower'
        else:  # giá trị nằm giữa alpha và beta, exact
            flag = 'exact'
        transposition_tables[hash_key] = {'value': min_eval, 'depth': depth, 'flag': flag}
        return min_eval

def get_best_move(board, depth=4):
    """Tìm nước đi tốt nhất với Minimax"""
    best_move = None
    max_eval = -float("inf")
    alpha, beta = -float("inf"), float("inf")

    for move in board.legal_moves:
        board.push(move)
        eval_score = minimax(board, depth - 1, alpha, beta, False, None, None)
        board.pop()

        if eval_score > max_eval:
            max_eval = eval_score
            best_move = move

    return best_move