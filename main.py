import pygame
import chess
import chess.engine

from minmax import *

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

piece_images = {}
for piece in chess.PIECE_SYMBOLS[1:]:
    piece_images[piece] = pygame.image.load(f'assets/{piece}_black.png')
    piece_images[piece.upper()] = pygame.image.load(f'assets/{piece}_white.png')

highlight_image = pygame.image.load("assets/square_of_highlight.png")
kill_highlight_image = pygame.image.load("assets/square_of_kill.png")
check_highlight_image = pygame.image.load("assets/square_of_in_check.png")  

HUMAN_VS_HUMAN = 1
HUMAN_VS_BOT = 2
BOT_VS_BOT = 3

mode = HUMAN_VS_HUMAN
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


def play_human_vs_human():
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
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

    pygame.quit()


def play_human_vs_bot(bot_color=chess.WHITE):
    board = chess.Board()
    running = True
    selected_square = None
    highlighted_squares = {}

    while running:
        if board.is_check():
            king_square = board.king(board.turn)
            highlighted_squares[king_square] = "check"

        draw_board(board, highlighted_squares)
        
        if board.turn == bot_color and not board.is_game_over():
            bot_move = get_best_move(board, 4)
            board.push(bot_move)
        else: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and board.turn != bot_color:
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
                    draw_board(board, highlighted_squares)
        if board.is_game_over():
            print("Game Over!", board.result())
            running = False

    pygame.quit()


def play_bot_vs_bot(delay=10000):
    board = chess.Board()
    running = True

    while running:
        draw_board(board)

        if not board.is_game_over():
            bot_move = get_best_move(board)
            board.push(bot_move)
            pygame.time.delay(delay)
        else:
            print("Game Over!", board.result())
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    font = pygame.font.SysFont("Arial", 30)
    options = [
        ("Human vs Human", HUMAN_VS_HUMAN),
        ("Human vs Bot", HUMAN_VS_BOT),
        ("Bot vs Bot", BOT_VS_BOT)
    ]
    selected = 0

    while True:
        screen.fill((255, 255, 255))
        for i, (text, _) in enumerate(options):
            color = (0, 0, 255) if i == selected else (0, 0, 0)
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (50, 50 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    _, mode = options[selected]
                    if mode == HUMAN_VS_HUMAN:
                        play_human_vs_human()
                    elif mode == HUMAN_VS_BOT:
                        play_human_vs_bot(chess.WHITE)
                    elif mode == BOT_VS_BOT:
                        play_bot_vs_bot()
                    return


if __name__ == "__main__":
    main()
