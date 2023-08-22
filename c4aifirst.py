import numpy as np
import random
import pygame
import pygame_menu
import sys
import math
from copy import deepcopy


# onedark
# BLUE = (97,175,239)
# BLACK = (40,44,52)
# RED = (190,80,70)
# YELLOW = (229,192,123)

# original colors
# BLUE = (0,0,150)
# BLACK = (0,0,0)
# RED = (150,0,0)
# YELLOW = (200,200,0)

# Nord
# BLUE = (94,129,172)
# BLACK = (46,52,64)
# RED = (191,97,106)
# YELLOW = (235,203,139)

WHITE = (255,255,255)
DARKBLUE = (32,32,192)

# Gruvbox
BLUE = (69, 133, 136)
BLACK = (40, 40, 40)
# RED = (204,36,29)
RED = (251, 73, 52)
YELLOW = (250, 189, 47)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
# height = (ROW_COUNT + 1) * SQUARESIZE
# changed  to 2, for each column score
height = (ROW_COUNT + 2) * SQUARESIZE

RADIUS = int(SQUARESIZE / 2 - 5)

pygame.init()
surface = pygame.display.set_mode((width, height))
pygame.display.set_caption("Connect4")

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    # print(np.flip(board, 0))
    board = 0


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True
    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True
    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    elif window.count(piece) == 1 and window.count(EMPTY) == 3:
        score += 1  # bdg 3/2/23
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 1
    return score


def score_position(board, piece):
    score = 0
    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c : c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r : r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score


def is_terminal_node(board):
    return (
        winning_move(board, PLAYER_PIECE)
        or winning_move(board, AI_PIECE)
        or len(get_valid_locations(board)) == 0
    )


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col


def draw_board(board, screen):

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            color = BLACK
            if board[r][c] == PLAYER_PIECE:
                color = RED
            elif board[r][c] == AI_PIECE:
                color = YELLOW

            pygame.draw.circle(
                screen,
                color,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    (height - SQUARESIZE) - int(r * SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    # for c in range(COLUMN_COUNT):
    #     pygame.draw.rect(
    #         screen,
    #         WHITE,
    #         (
    #         (c*SQUARESIZE,height-SQUARESIZE,SQUARESIZE-5,SQUARESIZE)
    #         )
    #     )
    pygame.display.update()

def ai02():
    pass


def algo2(key_positions,mirror_move,board,screen):
    ##
    # Recommends next move using a different algorithm
    # The key positions are based off the master thesis by Victor Allis Diagram 3.14
    move = mirror_move
    if(board[2][1] == 0 and board[0][1] != 0):
        move = 1
    elif(len(key_positions) > 0):
        move = key_positions.pop(0)
    elif(is_valid_location(board,mirror_move) == False):
        move = 6
        if(is_valid_location(board,move) == False):
            move = get_next_open_row(board,6)

    if(move != None):
        pygame.draw.rect(screen,DARKBLUE,
            ((move*SQUARESIZE,height-SQUARESIZE+(SQUARESIZE-3),SQUARESIZE-3,SQUARESIZE))
        )
    return move

def print_score(board,screen):

    #Recommends the next best move
    calc_col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
    print(f"Player: 1 Column: {calc_col} Score: {minimax_score}")
    if(calc_col != None):
        pygame.draw.rect(
            screen,
            RED,
            (
            (calc_col*SQUARESIZE,height-SQUARESIZE-3,SQUARESIZE-3,SQUARESIZE)
            )
        )

    # Calculates the score for both players in each column
    myfont = pygame.font.SysFont("monospace", 25)
    valid_locations = get_valid_locations(board)

    for col in range(COLUMN_COUNT):
        if (col in valid_locations):
            row = get_next_open_row(board, col)
            temp_board_AI = board.copy()
            drop_piece(temp_board_AI, row, col, AI_PIECE)
            temp_board_PLAYER = board.copy()
            drop_piece(temp_board_PLAYER,row,col,PLAYER_PIECE)

            score_PLAYER = score_position(temp_board_PLAYER, PLAYER_PIECE)
            score_AI = score_position(temp_board_AI, AI_PIECE)

            if(col != None):
                pygame.draw.rect(
                    screen,
                    BLACK,
                    (
                    (col*SQUARESIZE,height-SQUARESIZE,SQUARESIZE-3,SQUARESIZE)
                    )
                )
                score_text = myfont.render(str(score_PLAYER), 1, RED)
                screen.blit(score_text, (col*SQUARESIZE+32,height-SQUARESIZE+16,SQUARESIZE-3,SQUARESIZE))
                score_text = myfont.render(str(score_AI), 1, YELLOW)
                screen.blit(score_text, (col*SQUARESIZE+32,height-SQUARESIZE+44,SQUARESIZE-3,SQUARESIZE))
        else:
            # Column is full, no more scores to show
            pygame.draw.rect(
                screen,
                BLACK,
                (
                (col*SQUARESIZE,height-SQUARESIZE,SQUARESIZE-3,SQUARESIZE)
                )
            )

def animate_drop(row, col, piece, screen):
    color = RED
    if piece == AI_PIECE:
        color = YELLOW
    for r in range(ROW_COUNT - row):
        pygame.draw.circle(
            screen,
            color,
            (
                int(col * SQUARESIZE + SQUARESIZE / 2),
                height - (height - int(r * SQUARESIZE + SQUARESIZE / 2)),
            ),
            RADIUS,
        )
        pygame.display.update()
        pygame.time.wait(90)
        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(col * SQUARESIZE + SQUARESIZE / 2),
                height - (height - int(r * SQUARESIZE + SQUARESIZE / 2)),
            ),
            RADIUS,
        )


def set_turn(_turn, value):
    print(f"Player plays {_turn[0]} ({value})")

# turn = random.randint(PLAYER, AI)
def save_board(board_history,board):
    b = deepcopy(board)
    board_history.append(np.array(b))

def undo_move(board_history,board):
    if((len(board_history)) > 0):
        board_history.pop()
        if (len(board_history) > 0):
            board = deepcopy(board_history[-1])
        else:
            board = create_board()
            board_history.clear()
            save_board(board_history,board)
    return board

def bot_game():
    board = create_board()
    print_board(board)
    game_over = False
    size = (width, height)
    screen = pygame.display.set_mode(size)
    draw_board(board, screen)
    pygame.display.update()
    turn = _turn.get_value()[1]
    myfont = pygame.font.SysFont("monospace", 75)
    print_score(board,screen)

    #algo2 setup and variables
    key_positions = list([3,3,3,2,0])
    pygame.draw.rect(screen,DARKBLUE,((3*SQUARESIZE,height-SQUARESIZE+(SQUARESIZE-3),SQUARESIZE-3,SQUARESIZE)))
    col = 3

    while not game_over:
        col = algo2(key_positions,col,board,screen)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            animate_drop(row, col, PLAYER_PIECE, screen)
            drop_piece(board, row, col, PLAYER_PIECE)
            if winning_move(board, PLAYER_PIECE):
                label = myfont.render("algo2 wins", 1, RED)
                screen.blit(label, (40, 10))
                game_over = True
            turn += 1
            turn = turn % 2
            # print_board(board)
            draw_board(board, screen)

        # # Ask for Player 2 Input
        if turn == AI and not game_over:

            # col = random.randint(0, COLUMN_COUNT-1)
            # col = pick_best_move(board, AI_PIECE)
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                # pygame.time.wait(500)
                row = get_next_open_row(board, col)
                animate_drop(row, col, AI_PIECE, screen)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins :(", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True
                draw_board(board, screen)


                turn += 1
                turn = turn % 2
                print_score(board,screen)
        if game_over:
            end_game = False
            while not end_game:
                for event in pygame.event.get():
                    if (event.type == pygame.MOUSEBUTTONDOWN):
                        end_game = True
                        game_over = True

def start_game():
    board = create_board()
    board_history = list()
    print_board(board)
    game_over = False
    size = (width, height)
    screen = pygame.display.set_mode(size)
    draw_board(board, screen)
    pygame.display.update()
    turn = _turn.get_value()[1]
    myfont = pygame.font.SysFont("monospace", 75)
    save_board(board_history,board)
    print_score(board,screen)

    #algo2 setup and variables
    key_positions = list([3,3,2,0])
    pygame.draw.rect(screen,DARKBLUE,((3*SQUARESIZE,height-SQUARESIZE+(SQUARESIZE-3),SQUARESIZE-3,SQUARESIZE)))

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                return
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                # print("posx" + str(posx))
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

            pygame.display.update()

            if (pygame.mouse.get_pressed()[2] and event.type == pygame.MOUSEBUTTONDOWN):
                # print(f'right click')
                board = undo_move(board_history,board)
                draw_board(board,screen)
                print_score(board,screen)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                # print(event.pos)
                # Ask for Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        animate_drop(row, col, PLAYER_PIECE, screen)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("User wins!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True
                            save_board(board_history,board)
                        turn += 1
                        turn = turn % 2
                        # print_board(board)
                        draw_board(board, screen)

        # # Ask for Player 2 Input
        if turn == AI and not game_over:

            # col = random.randint(0, COLUMN_COUNT-1)
            # col = pick_best_move(board, AI_PIECE)
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
            print(f"AI Column: {col} Score: {minimax_score}")
            if is_valid_location(board, col):
                # pygame.time.wait(500)
                row = get_next_open_row(board, col)
                animate_drop(row, col, AI_PIECE, screen)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins :(", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True
                # print(f'{board_history}')
                save_board(board_history,board)
                draw_board(board, screen)


                turn += 1
                turn = turn % 2
                print_score(board,screen)
                algo2(key_positions,col,board,screen) # shows blue tab where to play next
                # mirror_move(col,screen)
                # print_score(board,screen)
                # col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
                # # print_score(col,minimax_score,screen,RED)
                # print(f"Player: 1 Column: {col} Score: {minimax_score}")

        if game_over:
            # pygame.time.wait(3000)
            check_undo = False
            while not check_undo:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                        return
                    if (pygame.mouse.get_pressed()[2] and event.type == pygame.MOUSEBUTTONDOWN):
                        board = undo_move(board_history,board)
                        draw_board(board,screen)
                        print_score(board,screen)
                        check_undo = True
                        game_over = False
                        turn += 1
                        turn = turn % 2
                    elif (event.type == pygame.MOUSEBUTTONDOWN):
                        check_undo = True
                        game_over = True

menu = pygame_menu.Menu(
    "Connect4", width - 100, height - 100, theme=pygame_menu.themes.THEME_BLUE
)
menu.add.button("algo2 vs ai", bot_game)
# menu.add.text_input("Name :", default="Player 1")
_turn = menu.add.selector("Play :", [("First", 0), ("Second", 1)], onchange=set_turn)
# print(turn)
menu.add.button("Play", start_game)
menu.add.button("Quit", pygame_menu.events.EXIT)
menu.mainloop(surface)
