import numpy as np
import random
import pygame
import math
import pygame_menu
import time
import matplotlib.pyplot as plt
import asyncio

# some constant values to use it in the Game and the Color of the GUI
R = (255, 0, 0)
B = (51, 110, 254)
Y = (255, 255, 0)
W = (255, 255, 255)

WINDOW_LENGTH = 4
nodes_explored = 0
nodes_explored_pc = 0
execution_times_ai = []
execution_times_minimax = []
nodes_explored_ai = []
nodes_explored_minimax = []




ROWS = 6

COLUMNS = 7

PLAYER = 0

BOT = 1

EMPTY = 0

PLAYER_PIECE = 1

BOT_PIECE = 2

def plot_the_algorithm():
    print(f"Nodes explored by AI: {sum(nodes_explored_ai)}")
    print(f"Time explored by AI: {sum(execution_times_ai)}")
    print(f"Nodes explored by Minimax: {sum(nodes_explored_minimax)}")
    print(f"Time explored by Minimax: {sum(execution_times_minimax)}")
    # Plotting the execution times
    labels = ['PC', 'Minimax']
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
    plt.plot(range(1, len(nodes_explored_ai) + 1), nodes_explored_ai, label='PC')
    plt.plot(range(1, len(nodes_explored_minimax) + 1), nodes_explored_minimax, label='Minimax')
    plt.xlabel('Game Iteration')
    plt.ylabel('Nodes Explored')
    plt.title('Comparison of Nodes Explored')
    plt.legend()

    # Show the plots
    plt.show()


#this code provides a framework for playing Connect Four against an AI opponent.
#The AI uses either the minimax algorithm or a simplified scoring approach (pick_best_move()) to make its decisions.




## this function  to start and creat the Game
#This is the main function that runs the Connect Four game.
#It takes a difficult parameter, which is likely used to control the AI's level of difficulty.
#The function contains several nested functions that are used internally.
async def START(difficult):
    #initializes the game board as a 2D array filled with zeros using the np.zeros() function from the NumPy library.
    def _2D_ARRAYBOARD():
        board = np.zeros((ROWS, COLUMNS))
        return board
    # places a game piece (indicated by piece) on the board at the specified row and col.
    def PLAY(board, row, col, piece):
        board[row][col] = piece
    #checks if a given column is a valid location to place a game piece.
    def OK(board, col):
        return board[ROWS - 1][col] == 0
    #finds the next available row in the specified column where a game piece can be placed.
    def NEXTPLAYROW(board, col):
        for r in range(ROWS):
            if board[r][col] == 0:
                return r
    #displays the game board on the console by printing it after flipping it vertically using np.flip()
    def SHOWBOARD(board):
        print(np.flip(board, 0))




    #This function evaluates a window of four adjacent locations in the game board.
    #It calculates a score for the window based on the number of pieces of the specified piece and the presence of empty spaces.
    #Higher scores are given for windows that have more of the specified piece and fewer empty spaces.
    #Lower scores are given if the opponent's piece is present in the window and there are empty spaces.
    #The score is then returned.
    def four_adjacent_locations_evaluatetion_window(window, piece):
        RESULT = 0
        opp_piece = PLAYER_PIECE if piece == BOT_PIECE else BOT_PIECE

        if window.count(piece) == 4:
            RESULT += 100
        elif window.count(piece) == 3 and EMPTY in window:
            RESULT += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            RESULT += 2

        if window.count(opp_piece) == 3 and EMPTY in window:
            RESULT -= 4

        return RESULT


        # This function checks if a player with the specified piece has won the game.
        # It checks for four consecutive pieces in all possible winning configurations: horizontally, vertically, and diagonally.
        # If a winning configuration is found, the function returns True; otherwise, it returns False.
    def KILLSHOTMOVE(board, piece):
        #  vertical  for win
        for c in range(COLUMNS):
            for r in range(ROWS - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True

        # horizontal for win
        for r in range(ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True

        # Check positively diagonals
        for r in range(ROWS - 3):
            for c in range(COLUMNS - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True

        # Check negatively  diagonals
        for r in range(3, ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True

            # Check negatively sloped diaganols
            for c in range(COLUMNS - 3):
                for r in range(3, ROWS):
                    if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                            board[r - 3][c + 3] == piece:
                        return True

    #This function checks if the game has reached a terminal state, meaning the game is over.
    #It returns True if either the AI or the player has won (winning_move() returns True), or if there are no more valid locations to place pieces.
    #Otherwise, it returns False.
    def GAME_OVER(board):
        return KILLSHOTMOVE(board, PLAYER_PIECE) or KILLSHOTMOVE(board, BOT_PIECE) or len(get_valid_locations(board)) == 0



    #This function implements the minimax algorithm with alpha-beta pruning to determine the best move for the AI player.
    #It recursively evaluates the possible moves and their outcomes for the AI and the player.
    #The depth parameter controls the depth of the search tree to limit the algorithm's computation time.
    #The alpha and beta parameters are used for pruning to eliminate branches that will not affect the final decision.
    #The maximizingPlayer parameter indicates whether the current player is the AI player or the opponent.
    #The function returns the best move (column) and its associated score.
    def minimax(board, depth, alpha, beta, maximizingPlayer):
        global nodes_explored
        valid_locations = get_valid_locations(board)
        is_terminal = GAME_OVER(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if KILLSHOTMOVE(board, BOT_PIECE):
                    return (None, 100000000000000)
                elif KILLSHOTMOVE(board, PLAYER_PIECE):
                    return (None, -10000000000000)
                else:  # Game is over, no more valid moves
                    return (None, 0)
            else:  # Depth is zero
                return (None, All_possible_windows(board, BOT_PIECE))
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = NEXTPLAYROW(board, col)
                b_copy = board.copy()
                PLAY(b_copy, row, col, BOT_PIECE)
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
                row = NEXTPLAYROW(board, col)
                b_copy = board.copy()
                PLAY(b_copy, row, col, PLAYER_PIECE)
                nodes_explored += 1
                new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
        # This function calculates a score for the entire game board for the specified piece.
        # It considers the center column as more advantageous and assigns it a higher score.
        # It then iterates over all possible windows of four adjacent locations and uses evaluate_window() to calculate scores for each window.
        # The scores are accumulated and returned as the final score for the position.

    def All_possible_windows(board, piece):
        RESULT = 0

        # Score center column
        center_count = list(board[:, COLUMNS // 2]).count(piece)
        RESULT += center_count * 3

        # Score Horizontal, Vertical, and Diagonal
        for r in range(ROWS):
            for c in range(COLUMNS - 3):
                # Horizontal scoring
                RESULT += four_adjacent_locations_evaluatetion_window(list(board[r, c:c + WINDOW_LENGTH]), piece)

                # Vertical scoring
                RESULT += four_adjacent_locations_evaluatetion_window(list(board[r:r + WINDOW_LENGTH, c]), piece)

                if r <= ROWS - WINDOW_LENGTH:
                    # Positive sloped diagonal scoring
                    RESULT += four_adjacent_locations_evaluatetion_window(
                        [board[r + i][c + i] for i in range(WINDOW_LENGTH)], piece)

                    # Negative sloped diagonal scoring
                    RESULT += four_adjacent_locations_evaluatetion_window(
                        [board[r + WINDOW_LENGTH - 1 - i][c + i] for i in range(WINDOW_LENGTH)], piece)

        return RESULT

    #This function returns a list of valid column locations where a game piece can be placed in the current board state.
    #It iterates over all columns and checks if the bottom row of each column is empty (is_valid_location()).
    #If a column is valid, it is added to the list of valid locations, which is then returned.
    def get_valid_locations(board):
        return [col for col in range(COLUMNS) if OK(board, col)]


    #This function determines the best move for the AI player using a simplified scoring approach.
    #It iterates over all valid column locations and simulates placing a piece in each location.
    #For each simulated move, it calculates a score using score_position() and selects the move with the highest score.
    #The function returns the column of the best move.
    def pick_best_move(board, piece):
        global nodes_explored_pc
        valid_locations = get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = NEXTPLAYROW(board, col)
            temp_board = board.copy()
            PLAY(temp_board, row, col, piece)
            nodes_explored_pc += 1
            score = All_possible_windows(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
                nodes_explored_pc += 1

        return best_col
    # ----------------------------- the GUI of the board --------------------------------
    def draw_board(board):
        for c in range(COLUMNS):
            for r in range(ROWS):
                pygame.draw.rect(screen, B, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE), 0)
                pygame.draw.circle(screen, W, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

        for c in range(COLUMNS):
            for r in range(ROWS):
                if board[r][c] == PLAYER_PIECE:
                    pygame.draw.circle(screen, R, (
                        int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
                elif board[r][c] == BOT_PIECE:
                    pygame.draw.circle(screen, Y, (
                        int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

    board = _2D_ARRAYBOARD()
    SHOWBOARD(board)
    SQUARESIZE = 80
    width = COLUMNS * SQUARESIZE
    height = (ROWS + 1) * SQUARESIZE
    size = (width, height)
    RADIUS = int(SQUARESIZE / 2 - 5)
    screen = pygame.display.set_mode(size)
    draw_board(board)
    pygame.display.update()
    myfont = pygame.font.SysFont("Calibri", 50)
    # to change between the AI and PLAYER
    # ----------------------------------------- the start of the Game -----------------------------

    game_over = False
    turn = random.randint(PLAYER, BOT)

    while not game_over:
        pygame.time.wait(1000)
        pygame.draw.rect(screen, W, (0, 0, width, SQUARESIZE))
        # print(event.pos)
        # Ask for Player 1 Input
        if turn == PLAYER:
            start_time0 = time.time()
            # col = random.randint(0, 6)
            col = pick_best_move(board, BOT_PIECE)
            end_time0 = time.time()
            execution_time = end_time0 - start_time0
            execution_times_ai.append(execution_time)
            nodes_explored_ai.append(nodes_explored_pc)
            print(col)
            if OK(board, col):
                row = NEXTPLAYROW(board, col)
                PLAY(board, row, col, PLAYER_PIECE)

                if KILLSHOTMOVE(board, PLAYER_PIECE):
                    label = myfont.render("Computer wins!!", 1, Y)
                    screen.blit(label, (40, 10))
                    game_over = True

                turn += 1
                turn = turn % 2

                SHOWBOARD(board)
                draw_board(board)

        # # Ask for Player 2 Input
        if turn == BOT and not game_over:
            start_time = time.time()

            col, minimax_score = minimax(board, difficult, -math.inf, math.inf, True)
            end_time = time.time()
            execution_time = end_time - start_time
            execution_times_minimax.append(execution_time)
            nodes_explored_minimax.append(nodes_explored)
            if OK(board, col):
                # pygame.time.wait(500)
                row = NEXTPLAYROW(board, col)
                PLAY(board, row, col, BOT_PIECE)

                if KILLSHOTMOVE(board, BOT_PIECE):
                    label = myfont.render("AI wins!!", 1, B)
                    screen.blit(label, (40, 10))
                    game_over = True

                SHOWBOARD(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)

        # asyncio.sleep(0)


## ------------------------------------------ the RUN of the GUI -------------------------------------------
pygame.init()
surface = pygame.display.set_mode((600, 400))
selected_difficulty = 5


def set_difficulty(value, difficulty):
    global selected_difficulty
    selected_difficulty = difficulty
    return difficulty
    pass



def start_the_game():
    print(f"the difficulty = {selected_difficulty}")
    asyncio.run(START(selected_difficulty))
    plot_the_algorithm()

    pass


menu = pygame_menu.Menu('CONECT 4 GAME', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
menu.add.selector('Difficulty :', [('Hard', 5), ('Medium', 3), ('Easy', 1)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(surface)
pygame.time.wait(3000)