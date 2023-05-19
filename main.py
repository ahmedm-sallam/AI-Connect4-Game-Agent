# 20210614
# 20201126
# 20201146
# 20200055

import numpy as np
import random
import pygame
import math
import pygame_menu
import time
import matplotlib.pyplot as plt
import asyncio

# some constant values to use it in the Game and the Color of the GUI
BLUE = (51, 110, 254)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4
nodes_explored = 0
nodes_explored_pc = 0
execution_times_ai = []
execution_times_minimax = []
nodes_explored_ai = []
nodes_explored_minimax = []


## this function  to start and creat the Game
async def RunGame(difficult):

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
        print(np.flip(board, 0))

    def winning_move(board, piece):
        # Check horizontal locations for win
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                    c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                    c] == piece:
                    return True

        # Check positively sloped diaganols
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and \
                        board[r + 3][
                            c + 3] == piece:
                    return True

        # Check negatively sloped diaganols
        for c in range(COLUMN_COUNT - 3):
            for r in range(3, ROW_COUNT):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                        board[r - 3][
                            c + 3] == piece:
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

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

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
                window = row_array[c:c + WINDOW_LENGTH]
                score += evaluate_window(window, piece)

        ## Score Vertical
        for c in range(COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(ROW_COUNT - 3):
                window = col_array[r:r + WINDOW_LENGTH]
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
        return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(
            get_valid_locations(board)) == 0

    def minimax(board, depth, alpha, beta, maximizingPlayer):
        global nodes_explored
        valid_locations = get_valid_locations(board)
        is_terminal = is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if winning_move(board, AI_PIECE):
                    return (None, 100000000000000)
                elif winning_move(board, PLAYER_PIECE):
                    return (None, -10000000000000)
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
                nodes_explored += 1
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
                nodes_explored += 1
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
        global nodes_explored_pc
        valid_locations = get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, piece)
            nodes_explored_pc += 1
            score = score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
                nodes_explored_pc += 1

        return best_col

    # ----------------------------- the GUI of the board --------------------------------
    def draw_board(board):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE), 0)
                pygame.draw.circle(screen, WHITE, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                if board[r][c] == PLAYER_PIECE:
                    pygame.draw.circle(screen, RED, (
                        int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
                elif board[r][c] == AI_PIECE:
                    pygame.draw.circle(screen, YELLOW, (
                        int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        pygame.display.update()


    board = create_board()
    print_board(board)
    SQUARESIZE = 80
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)
    RADIUS = int(SQUARESIZE / 2 - 5)
    screen = pygame.display.set_mode(size)
    draw_board(board)
    pygame.display.update()
    myfont = pygame.font.SysFont("Calibri", 50)
    # to change between the AI and PLAYER
    # ----------------------------------------- the start of the Game -----------------------------
    
    game_over = False
    turn = random.randint(PLAYER, AI)

    while not game_over:
            pygame.time.wait(1000)
            pygame.draw.rect(screen, WHITE, (0, 0, width, SQUARESIZE))
            # print(event.pos)
            # Ask for Player 1 Input
            if turn == PLAYER:
                start_time0 = time.time()
                #col = random.randint(0, 6)
                col = pick_best_move(board, AI_PIECE)
                end_time0 = time.time()
                execution_time = end_time0 - start_time0
                execution_times_ai.append(execution_time)
                nodes_explored_ai.append(nodes_explored_pc)
                print(col)
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Computer wins!!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

            # # Ask for Player 2 Input
            if turn == AI and not game_over:
                start_time = time.time()

                col, minimax_score = minimax(board, difficult, -math.inf, math.inf, True)
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times_minimax.append(execution_time)
                nodes_explored_minimax.append(nodes_explored)
                if is_valid_location(board, col):
                    # pygame.time.wait(500)
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)

                    if winning_move(board, AI_PIECE):
                        label = myfont.render("AI wins!!", 1, BLUE)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

            if game_over:
                pygame.time.wait(3000)
            
            asyncio.sleep(0)

## ------------------------------------------ the RUN of the GUI -------------------------------------------
pygame.init()
surface = pygame.display.set_mode((600, 400))
selected_difficulty = 5


def set_difficulty(value, difficulty):
    global selected_difficulty
    selected_difficulty = difficulty
    return difficulty
    pass


def plot_the_algorithm():
    print(f"Nodes explored by AI: {sum(nodes_explored_ai)}")
    print(f"Time explored by AI: {sum(execution_times_ai)}")
    print(f"Nodes explored by Minimax: {sum(nodes_explored_minimax)}")
    print(f"Time explored by Minimax: {sum(execution_times_minimax)}")
    # Plotting the execution times
    labels = ['AI', 'Minimax']
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, [sum(execution_times_ai), sum(execution_times_minimax)], width)

    ax.set_ylabel('Execution Time')
    ax.set_title('Comparison of Execution Time')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    # Plotting the number of nodes explored
    plt.figure()
    plt.plot(range(1, len(nodes_explored_ai) + 1), nodes_explored_ai, label='AI')
    plt.plot(range(1, len(nodes_explored_minimax) + 1), nodes_explored_minimax, label='Minimax')
    plt.xlabel('Game Iteration')
    plt.ylabel('Nodes Explored')
    plt.title('Comparison of Nodes Explored')
    plt.legend()

    # Show the plots
    plt.show()


def start_the_game():
    print(f"the difficulty = {selected_difficulty}")
    asyncio.run(RunGame(selected_difficulty))
    plot_the_algorithm()

    pass


menu = pygame_menu.Menu('CONECT 4 GAME', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
menu.add.selector('Difficulty :', [('Hard', 5), ('Medium', 3), ('Easy', 1)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(surface)
pygame.time.wait(3000)
