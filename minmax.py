import heapq

import chess
import random
import time

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

pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0, ],
               [78, 83, 86, 73, 102, 82, 85, 90],
               [7, 29, 21, 44, 40, 31, 44, 7],
               [-17, 16, -2, 15, 14, 0, 15, -13],
               [-26, 3, 10, 9, 6, 1, 0, -23],
               [-22, 9, 5, -11, -10, -2, 3, -19],
               [-31, 8, -7, -37, -36, -14, 3, -31],
               [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[-59, -78, -82, -76, -23, -107, -37, -50],
                 [-11, 20, 35, -42, -39, 31, 2, -22],
                 [-9, 39, -32, 41, 52, -10, 28, -14],
                 [25, 17, 20, 34, 26, 25, 15, 10],
                 [13, 10, 17, 23, 17, 16, 0, 7],
                 [14, 25, 24, 15, 8, 25, 20, 15],
                 [19, 20, 11, 6, 7, 6, 20, 16],
                 [-7, 2, -15, -12, -14, -15, -10, -10]]

rook_scores = [[35, 29, 33, 4, 37, 33, 56, 50],
               [55, 29, 56, 67, 55, 62, 34, 60],
               [19, 35, 28, 33, 45, 27, 25, 15],
               [0, 5, 16, 13, 18, -4, -9, -6],
               [-28, -35, -16, -21, -13, -29, -46, -30],
               [-42, -28, -42, -25, -25, -35, -26, -46],
               [-53, -38, -31, -26, -29, -43, -44, -53],
               [-30, -24, -18, 5, -2, -18, -31, -32]]

queen_scores = [[6, 1, -8, -104, 69, 24, 88, 26],
                [14, 32, 60, -10, 20, 76, 57, 24],
                [-2, 43, 32, 60, 72, 63, 43, 2],
                [1, -16, 22, 17, 25, 20, -13, -6],
                [-14, -15, -2, -5, -1, -10, -20, -22],
                [-30, -6, -13, -11, -16, -11, -16, -27],
                [-36, -18, 0, -19, -15, -15, -21, -38],
                [-39, -30, -31, -13, -31, -36, -34, -42]]

knight_scores = [[-66, -53, -75, -75, -10, -55, -58, -70],
                 [-3, -6, 100, -36, 4, 62, -4, -14],
                 [10, 67, 1, 74, 73, 27, 62, -2],
                 [24, 24, 45, 37, 33, 41, 25, 17],
                 [-1, 5, 31, 21, 22, 35, 2, 0],
                 [-18, 10, 13, 22, 18, 15, 11, -14],
                 [-23, -15, 2, 0, 2, 0, -23, -20],
                 [-66, -53, -75, -75, -10, -55, -58, -70]]


def get_position_scores_table(piece_type, piece_color):
    piece_position_scores = {2: knight_scores,
                             3: bishop_scores,
                             5: queen_scores,
                             4: rook_scores,
                             1: pawn_scores}

    if piece_color:  # White piece
        return piece_position_scores[piece_type]
    else:
        return piece_position_scores[piece_type][::-1]


piece_score = {6: 6000, 5: 929, 4: 512, 3: 320, 2: 280, 1: 100}
killer_moves = {}  # killer_moves[depth] = [move1, move2]
history_heuristic = {}  # history_heuristic[(from_square, to_square)] = score

def score_move_cached(move, board, depth, tt_move):
    if tt_move and move == tt_move:
        return 10000
    # Ưu tiên nước ăn quân (MVV-LVA)
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        victim_val = piece_score.get(victim.piece_type) if victim else 0
        attacker_val = piece_score.get(attacker.piece_type) if attacker else 1
        return 5000 + victim_val - attacker_val
    # Killer move
    if move in killer_moves.get(depth, []):
        return 4000
    # History heuristic
    return history_heuristic.get((move.from_square, move.to_square), 0)

center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
def evaluate_board(board):
    """Hàm đánh giá bàn cờ, ưu tiên quân có ảnh hưởng lớn nhất trước"""
    score = 0
    influential_moves = []  # Lưu các quân có ảnh hưởng lớn nhất (tấn công, check, central, etc.)

    # Ưu tiên các quân có ảnh hưởng lớn: check, capture, quân gần trung tâm, quân có số nước đi cao
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.piece_type
            piece_color = piece.color
            piece_position_score = 0

            # Bỏ qua quân vua (king) khi đánh giá vị trí
            if piece_type != chess.KING:
                piece_position_score = get_position_scores_table(piece_type, piece_color)[square // 8][square % 8]

            # Ưu tiên quân gây check hoặc chiếu (gây đe dọa trực tiếp đến quân vua đối phương)
            if board.is_checkmate() or board.gives_check(chess.Move(square, square)):  # Kiểm tra quân đang gây check
                influential_moves.append(piece)

            # Ưu tiên quân đi vào các ô trung tâm hoặc có tầm ảnh hưởng lớn (queen, rook)
            if square in center_squares or piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
                influential_moves.append(piece)

            # Thêm điểm cho quân khi chúng có tầm ảnh hưởng hoặc kiểm soát nhiều ô
            if piece_color == chess.WHITE:
                score += piece_score[piece_type] + piece_position_score
            else:
                score -= piece_score[piece_type] + piece_position_score

    # Sắp xếp các quân có ảnh hưởng nhất
    influential_moves.sort(key=lambda x: piece_score[x.piece_type], reverse=True)

    # Đảm bảo rằng bạn đánh giá các quân có ảnh hưởng lớn trước
    for piece in influential_moves:
        score += piece_score.get(piece.piece_type, 0)

    return score


def zobrist_hash(board: chess.Board):
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


def update_hash_key(board: chess.Board, move: chess.Move, old_hash: int):
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
    if hash_key is None:
        hash_key = zobrist_hash(board)

    if (hash_key in transposition_tables) and (transposition_tables[hash_key]['depth'] >= depth):
        entry = transposition_tables[hash_key]
        if entry['flag'] == 'exact':
            return entry['value']
        if entry['flag'] == 'upper' and entry['value'] <= alpha:
            return entry['value']
        if entry['flag'] == 'lower' and entry['value'] >= beta:
            return entry['value']

    if depth == 0 or board.is_game_over():
        value = evaluate_board(board)
        transposition_tables[hash_key] = {'value': value, 'depth': 0, 'flag': 'exact'}
        return value

    legal_moves = list(board.legal_moves)
    top_k = max(6, 20 - depth * 2)

    if maximizing_player:
        max_eval = -float("inf")
        tt_move = None
        if hash_key in transposition_tables:
            tt_move = transposition_tables[hash_key].get('best_move')

        scored_moves = [(score_move_cached(move, board, depth, tt_move), move) for move in legal_moves]
        top_moves = heapq.nlargest(top_k, scored_moves, key=lambda x: x[0])
        legal_moves = [move for (_, move) in top_moves]
        # scored_moves = []
        # for move in legal_moves:
        #     score = score_move_cached(move, board, depth, tt_move)
        #     scored_moves.append((score, move))
        #
        # # Sắp xếp theo điểm giảm dần
        # scored_moves.sort(key=lambda x: x[0], reverse=True)
        #
        # # Chỉ lấy danh sách move
        # legal_moves = [move for (_, move) in scored_moves]

        for move in legal_moves:
            new_hash_key = update_hash_key(board, move, hash_key)
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False, new_hash_key, move)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if not board.is_capture(move):
                killer_moves.setdefault(depth, [])
                if move not in killer_moves[depth]:
                    killer_moves[depth].insert(0, move)
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth] = killer_moves[depth][:2]

            if beta <= alpha:
                if not board.is_capture(move):
                    key = (move.from_square, move.to_square)
                    history_heuristic[key] = history_heuristic.get(key, 0) + depth * depth

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
        tt_move = None
        if hash_key in transposition_tables:
            tt_move = transposition_tables[hash_key].get('best_move')

        scored_moves = [(score_move_cached(move, board, depth, tt_move), move) for move in legal_moves]
        top_moves = heapq.nlargest(top_k, scored_moves, key=lambda x: x[0])
        legal_moves = [move for (_, move) in top_moves]
        scored_moves = []
        for move in legal_moves:
            score = score_move_cached(move, board, depth, tt_move)
            scored_moves.append((score, move))

        # Sắp xếp theo điểm giảm dần
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        # Chỉ lấy danh sách move
        legal_moves = [move for (_, move) in scored_moves]

        for move in legal_moves:
            new_hash_key = update_hash_key(board, move, hash_key)
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True, new_hash_key, move)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if not board.is_capture(move):
                killer_moves.setdefault(depth, [])
                if move not in killer_moves[depth]:
                    killer_moves[depth].insert(0, move)
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth] = killer_moves[depth][:2]

            if beta <= alpha:
                if not board.is_capture(move):
                    key = (move.from_square, move.to_square)
                    history_heuristic[key] = history_heuristic.get(key, 0) + depth * depth

                break

        if min_eval <= alpha:  # alpha không thay đổi, đây là upper bound
            flag = 'upper'
        elif min_eval >= beta:  # beta cắt, đây là lower bound
            flag = 'lower'
        else:  # giá trị nằm giữa alpha và beta, exact
            flag = 'exact'
        transposition_tables[hash_key] = {'value': min_eval, 'depth': depth, 'flag': flag}
        return min_eval


def minimax_with_aspiration(board, depth, prev_max_eval, margin, maximizing_player):
    """
        Thực hiện tìm kiếm minimax với Aspiration Window.
        Nếu kết quả tìm kiếm nằm ngoài cửa sổ (fail high/low), sẽ thực hiện tìm lại với cửa sổ toàn phần.
    """
    alpha = prev_max_eval - margin
    beta = prev_max_eval + margin
    eval_score = minimax(board, depth, alpha, beta, maximizing_player, None, None)
    # Nếu kết quả ngoài phạm vi cửa sổ, thực hiện re-search với cửa sổ toàn phần:
    if eval_score <= alpha or eval_score >= beta:
        eval_score = minimax(board, depth, -float("inf"), float("inf"), maximizing_player, None, None)
    return eval_score


ASPIRATION_WINDOW_MARGIN = 50

MAX_TIME = 20


def get_best_move(board, max_depth=10, margin=ASPIRATION_WINDOW_MARGIN):
    best_move = None
    start_time = time.time()
    prev_max_eval = evaluate_board(board)

    for depth in range(1, max_depth + 1):
        max_eval = -float("inf")
        current_best_move = None

        for move in board.legal_moves:
            if time.time() - start_time > MAX_TIME:
                print("Timeout reached! Returning the best move found so far.")
                break

            board.push(move)
            eval_score = minimax_with_aspiration(board, depth - 1, prev_max_eval, margin, False)
            board.pop()

            if eval_score > max_eval:
                max_eval = eval_score
                current_best_move = move
                prev_max_eval = max_eval

        if current_best_move:
            best_move = current_best_move

    return best_move