import random
import copy
from constants import *


def next_player(board):
    """Return next player"""
    x = 0
    o = 0
    for line in board:
        for piece in line:
            if piece == X:
                x += 1
            elif piece == O:
                o += 1

    if x == o:
        return X
    if x > o:
        return O
    return X


def next_moves(board):
    """given a board, returns all empty spaces on the board"""

    action_list = []
    for i, line in enumerate(board):
        for j in range(len(line)):
            if board[i][j] == BLANK:
                action_list.append((i, j))
    return action_list


def result(board, action):
    """Returns a new board given the next move"""

    i, j = action
    # must do a deep coopy before modifying the result since the minimax will then use the same board item
    b = copy.deepcopy(board)
    b[i][j] = next_player(b)
    return b


def get_winner(board):
    """returns the winner of the game if there is a winner, otherwise None"""
    # check row
    for line in board:
        if line[0] == line[1] == line[2]:
            if line[0] is not BLANK:
                return line[0]
    # check col
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if board[0][i] is not BLANK:
                return board[0][i]

    # check across
    if board[0][0] == board[1][1] == board[2][2] or board[0][2] == board[1][1] == board[2][0]:
        if board[1][1] is not BLANK:
            return board[1][1]

    # no winner
    return None


def is_game_over(board):
    """returns True if game is over, False otherwise."""
    if get_winner(board):
        return True

    for line in board:
        for item in line:
            if item is BLANK:
                # the board still has empty spaces for the player to go
                return False
    return True


def utility(board):
    """returns 1 if X has won the game, -1 if O has won, 0 otherwise."""

    win = get_winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    return 0


def mini(board, isMaximizingPlayer, player):
    """minimax algorithm"""
    if is_game_over(board):
        if player == X:
            return utility(board)
        else:
            return -utility(board)
    if isMaximizingPlayer:
        bestVal = -MINIMAX_TOP_VALUE
        for action in next_moves(board):
            value = mini(result(board, action), False, player)

            bestVal = max(bestVal, value)
        return bestVal
    else:
        bestVal = MINIMAX_TOP_VALUE
        for action in next_moves(board):
            value = mini(result(board, action), True, player)
            bestVal = min(bestVal, value)
        return bestVal


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if is_game_over(board):
        return None

    board_actions = next_moves(board)
    if len(board_actions) == GAME_SIZE:
        return random.choice(board_actions)

    top_actions = []
    top_value = -MINIMAX_TOP_VALUE
    for action in board_actions:
        new_val = mini(result(board, action), False, next_player(board))
        if new_val > top_value:
            top_value = new_val
            top_actions = [action]
        elif new_val == top_value:
            top_actions.append(action)
    return random.choice(top_actions)
