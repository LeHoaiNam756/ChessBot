import chess


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


def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing_player:
        max_eval = -float("inf")
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board, depth=4):
    """Tìm nước đi tốt nhất với Minimax"""
    best_move = None
    max_eval = -float("inf")
    alpha, beta = -float("inf"), float("inf")

    for move in board.legal_moves:
        board.push(move)
        eval_score = minimax(board, depth - 1, alpha, beta, False)
        board.pop()

        if eval_score > max_eval:
            max_eval = eval_score
            best_move = move

    return best_move