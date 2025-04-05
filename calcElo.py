import chess
import chess.engine
import random
from math import log10

from minmax import get_best_move

STOCKFISH_PATH = "D:/AI/BTL/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"  # Đổi đường dẫn tới Stockfish


def play_game(bot, stockfish_level=8):
    """Chơi một ván giữa bot và Stockfish"""
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    # Thiết lập mức độ của Stockfish (1-20)
    engine.configure({"Skill Level": stockfish_level})

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = bot(board)  # Bot đi trước
        else:
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move  # Stockfish đi

        board.push(move)

    engine.quit()
    return board.result()  # Kết quả "1-0", "0-1", "1/2-1/2"


def calculate_elo(wins, draws, losses, opponent_elo):
    """Tính toán ELO dựa trên số trận thắng/thua/hòa với Stockfish"""
    total_games = wins + draws + losses
    score = (wins + 0.5 * draws) / total_games  # Tính điểm trung bình

    expected_score = 1 / (1 + 10 ** ((opponent_elo - 1500) / 400))  # ELO 1500 là mặc định
    k_factor = 32  # Hệ số điều chỉnh

    new_elo = 1500 + k_factor * (score - expected_score) * total_games  # Tính ELO
    return new_elo


def evaluate_bot(bot, games=50, stockfish_level=8, opponent_elo=1600):
    """Chạy nhiều trận đấu và tính ELO bot"""
    wins, draws, losses = 0, 0, 0

    for _ in range(games):
        result = play_game(bot, stockfish_level)
        if result == "1-0":
            wins += 1
        elif result == "0-1":
            losses += 1
        else:
            draws += 1

    return calculate_elo(wins, draws, losses, opponent_elo)

def my_bot(board):
    """Hàm bot của bạn sử dụng Minimax để chơi"""
    return get_best_move(board, 4)  # Giả sử đã có hàm Minimax tối ưu

elo_score = evaluate_bot(my_bot, games=5, stockfish_level=8, opponent_elo=1600)
print(f"Bot của bạn có ELO khoảng: {round(elo_score)}")