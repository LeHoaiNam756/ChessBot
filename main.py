import pygame
import chess
import chess.engine

# Khởi tạo pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load hình ảnh quân cờ
piece_images = {}
for piece in chess.PIECE_SYMBOLS[1:]:
    piece_images[piece] = pygame.image.load(f'assets/{piece}_white.png')
    piece_images[piece.upper()] = pygame.image.load(f'assets/{piece}_black.png')

highlight_image = pygame.image.load("assets/square_of_highlight.png")
kill_highlight_image = pygame.image.load("assets/square_of_kill.png")
check_highlight_image = pygame.image.load("assets/square_of_in_check.png")

# Chế độ chơi
HUMAN_VS_HUMAN = 1
HUMAN_VS_BOT = 2
BOT_VS_BOT = 3

mode = HUMAN_VS_HUMAN  # Chọn chế độ mặc định

# Load engine cho bot
# engine = chess.engine.SimpleEngine.popen_uci("stockfish")


def draw_board(board, highlighted_squares={}):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    square_size = WIDTH // 8

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))

            square = chess.square(col, 7 - row)
            if square in highlighted_squares:
                highlight_type = highlighted_squares[square]
                img = highlight_image
                if highlight_type == "kill":
                    img = kill_highlight_image
                elif highlight_type == "check":
                    img = check_highlight_image

                screen.blit(pygame.transform.scale(img, (square_size, square_size)),
                            (col * square_size, row * square_size))

            piece = board.piece_at(square)
            if piece:
                img = piece_images[piece.symbol()]
                screen.blit(pygame.transform.scale(img, (square_size, square_size)),
                            (col * square_size, row * square_size))

    pygame.display.flip()


# def get_best_move(board):
#     result = engine.play(board, chess.engine.Limit(time=0.5))
#     return result.move


def main():
    global mode
    board = chess.Board()
    running = True
    selected_square = None
    highlighted_squares = {}

    while running:
        if board.is_check():
            king_square = board.king(board.turn)
            highlighted_squares[king_square] = "check"

        draw_board(board, highlighted_squares)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and mode != BOT_VS_BOT:
                x, y = pygame.mouse.get_pos()
                col, row = x // (WIDTH // 8), 7 - (y // (HEIGHT // 8))
                square = chess.square(col, row)

                if selected_square is None:
                    selected_square = square
                    highlighted_squares = {}
                    for move in board.legal_moves:
                        if move.from_square == selected_square:
                            if board.piece_at(move.to_square):
                                highlighted_squares[move.to_square] = "kill"
                            else:
                                highlighted_squares[move.to_square] = "move"

                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None
                    highlighted_squares = {}

    #                 if mode == HUMAN_VS_BOT and not board.is_game_over():
    #                     bot_move = get_best_move(board)
    #                     board.push(bot_move)
    #
    #     if mode == BOT_VS_BOT and not board.is_game_over():
    #         board.push(get_best_move(board))
    #         pygame.time.delay(500)
    #
    # engine.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
