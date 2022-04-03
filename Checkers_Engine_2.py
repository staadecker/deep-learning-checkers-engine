import numpy as np
import re
from copy import deepcopy
import torch
from collections import OrderedDict
from draughts import Game, Move, WHITE, BLACK


def run_engine():
    run = True
    game = Game(variant="english", fen="startpos")

    while run:
        
        if game.whose_turn() == 2:  #opponent (Minimax): 1   #player: 2
            ##move = (get the move from the ML model)
            game.move(move)
            
        if game.is_over() == True or game.draw() == True:
            run = False            
            
        if game.whose_turn() == 1:
            value, best_board, best_move = minimax(create_board_tensor(game), 4, True, game)
            game.move(best_move)


def test_function(game):
    game = game.move(game.get_moves()[0][0][0])
    minimax_ = minimax(create_board_tensor(game), 3, True, game)
    print(minimax_)
    game = game.move(minimax_[2][0])
    game = game.move(game.get_moves()[0][0][0])
    minimax_ = minimax(create_board_tensor(game), 3, True, game)
    print(minimax_)
    game = game.move(minimax_[2][0])
    game = game.move(game.get_moves()[0][0][0])
    minimax_ = minimax(create_board_tensor(game), 3, True, game)
    print(minimax_)
    game = game.move(minimax_[2][0])
    game = game.move(game.get_moves()[0][0][0])    
    minimax_ = minimax(create_board_tensor(game), 3, True, game)
    print(minimax_)     
    

def create_board_tensor(game):
    board_string = game.get_fen()
    board_string_list = list(board_string)
    board_string_list.pop(0)
    for i in range(0,len(board_string_list)):
        if board_string_list[i] == 'b':
            board_string_list[i] = -1
        elif board_string_list[i] == 'B':
            board_string_list[i] = -3        
        elif board_string_list[i] == 'e':
            board_string_list[i] = 0
        elif board_string_list[i] == 'w':
            board_string_list[i] = 1
        elif board_string_list[i] == 'W':
            board_string_list[i] = 3              
    return torch.Tensor(board_string_list)


def minimax(board, depth, max_player, game):
    if depth == 0 or game.is_over() == True or game.is_draw() == True:
        return evaluate(board), torch.Tensor(board)

    if max_player:
        maxEval = float('-inf')
        best_board = None 
        best_move = None
        for games in get_future_game_states(game, False):
            evaluation = minimax(create_board_tensor(games), depth - 1, False, games)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_board = create_board_tensor(games)
                best_move = get_move_from_board(game, tensor_to_board(best_board))
            
        return maxEval, best_board, best_move     
            
    else:
        minEval = float('inf')
        best_board = None
        best_move = None
        for games in get_future_game_states(game, True):
            evaluation = minimax(create_board_tensor(games), depth - 1, True, games)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_board = create_board_tensor(games)
                best_move = get_move_from_board(game, tensor_to_board(best_board))
            
        return minEval, best_board, best_move  
 

def get_move_from_board(game, board):
    valid_moves, captures = game.get_moves()
    for moves in valid_moves:
        temp_game = game.copy()
        temp_game = temp_game.move(moves[0])
        #if len(moves) > 1:
            #temp_game = temp_game.move(moves[1])
        possible_board = tensor_to_board(create_board_tensor(temp_game))
        if possible_board == board:
            return moves
 
 
def get_future_game_states(game, switch_turn):
    if switch_turn:
        game = game.switch_turn()
    possible_games = []
    valid_moves, captures = game.get_moves()
    for moves in valid_moves:
        temp_game = game.copy()
        temp_game = temp_game.move(moves[0])
        #if len(moves) > 1:
            #temp_game = temp_game.move(moves[1])
        possible_games.append(temp_game)
    return possible_games   


def get_future_board_states(game, switch_turn):
    if switch_turn:
        game = game.switch_turn()
    possible_moves = []
    future_boards = []
    possible_games = []
    board = create_board_tensor(game)
    valid_moves, captures = game.get_moves()
    for moves in valid_moves:
        temp_game = game.copy()
        temp_game = temp_game.move(moves[0])
        possible_future_board = tensor_to_board(create_board_tensor(temp_game))
        future_boards.append(possible_future_board)
        possible_moves.append(moves[0])
        possible_games.append(temp_game)
    return future_boards, possible_moves, possible_games


def evaluate(board):
    player_pieces = 0
    AI_pieces = 0
    player_kings = 0
    AI_kings = 0    
    for value in board:
        if value == 1:
            player_pieces += 1
        if value == -1:
            AI_pieces += 1
        if value == -3:
            player_kings += 1
        if value == 3:
            AI_kings += 1                
    return (AI_pieces - player_pieces + (AI_kings * 0.5 - player_kings* 0.5))


def convert_multi_move(moveslist):
    multi_move = []
    for moves in moveslist:
        for move in moves:
            multi_move.append(move)
    multi_move_list = list(OrderedDict.fromkeys(multi_move))
    return multi_move_list


def tensor_to_board(tensor):
    board_list = tensor.tolist()
    return board_list


def board_to_tensor(board):
    board_tensor = torch.from_numpy(board)
    board_tensor = board_tensor.flatten()
    return board_tensor


game_object = Game(variant="english", fen="startpos")
#game_object.move([23,18])
#board = create_board_tensor(game_object)


test_function(game_object)
#print(minimax(board, 4, True, game_object))