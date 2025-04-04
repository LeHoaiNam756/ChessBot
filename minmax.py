import chess

ASPIRATION_WINDOW_MARGIN = 50 #Bien do mac dinh

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

def minimax_with_aspiration(board, depth, prev_best_eval, margin, maximizing_player):
    """
        Thực hiện tìm kiếm minimax với Aspiration Window.
        Nếu kết quả tìm kiếm nằm ngoài cửa sổ (fail high/low), sẽ thực hiện tìm lại với cửa sổ toàn phần.
    """
    alpha = prev_best_eval - margin
    beta = prev_best_eval + margin
    eval_score = minimax(board, depth, alpha, beta, maximizing_player)

    # Nếu kết quả ngoài phạm vi cửa sổ, thực hiện re-search với cửa sổ toàn phần:
    if eval_score <= alpha or eval_score >= beta:
        eval_score = minimax(board, depth, -float("inf"), float("inf"), maximizing_player)
    return eval_score

def get_best_move(board, depth=5, margin=ASPIRATION_WINDOW_MARGIN):
    """Tìm nước đi tốt nhất với Minimax"""
    best_move = None
    max_eval = -float("inf")
    # Dùng đánh giá hiện tại của bàn cờ làm ước lượng ban đầu
    prev_best_eval = evaluate_board(board)

    for move in board.legal_moves:
        board.push(move)
        # Sử dụng aspiration window trong tìm kiếm ở nhánh này
        eval_score = minimax_with_aspiration(board, depth - 1, prev_best_eval, margin, False)
        board.pop()

        if eval_score > max_eval:
            max_eval = eval_score
            best_move = move
            #Cập nhật ước lượng cho nhánh sau
            prev_best_eval = max_eval

    return best_move