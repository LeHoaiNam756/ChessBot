import chess
import pytest  # Giả sử bot của bạn có hàm này
from minmax import get_best_move


# Test 1: Chiếu hết trong 1 nước
@pytest.mark.parametrize("fen, best_move", [
    ("6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1", "h2h4"),
    ("6k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1", "g8h8"),
    ("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1", "e1e2"),
    ("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR b KQkq - 0 1", "e8e7"),
])
def test_checkmate_in_one(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Test 2: Đòn chiến thuật Fork (Chĩa)
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/2n5/8/4N3/8/4K3/8 w - - 0 1", "e4c5"),  # Mã chĩa vua và hậu
    ("8/8/4q3/8/3N4/8/4K3/8 w - - 0 1", "d4e6"),  # Mã chĩa vua và xe
])
def test_fork(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Test 3: Đòn Pin
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/8/8/2r5/8/2Q5/4K3 w - - 0 1", "c2c4"),  # Xe pin hậu
])
def test_pin(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Test 4: Tàn cuộc chuẩn xác
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/8/8/8/4k3/5P2/4K3 w - - 0 1", "f2f3"),  # Tiến tốt để chiếu hết
])
def test_endgame(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=5)
    assert move == chess.Move.from_uci(best_move)

# Test 5: Đòn Skewer (Xiên)
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/4q3/8/3R4/8/4K3/8 w - - 0 1", "d4e4"),  # Xe tấn công hậu, hậu buộc phải rời
])
def test_skewer(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Test 6: Đòn hy sinh để tạo ưu thế
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/8/8/3B4/8/4k3/4K3 w - - 0 1", "d4h8"),  # Tượng hy sinh để chiếu hết
])
def test_sacrifice(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Test 7: Phòng thủ quan trọng
@pytest.mark.parametrize("fen, best_move", [
    ("8/8/8/8/4k3/8/4Q3/4K3 w - - 0 1", "e2e4"),  # Tránh chiếu hết
])
def test_defensive_move(fen, best_move):
    board = chess.Board(fen)
    move = get_best_move(board, depth=3)
    assert move == chess.Move.from_uci(best_move)

# Chạy pytest bằng lệnh: pytest test_chess_bot.py
