import numpy as np
import re
from copy import deepcopy
import torch
from collections import OrderedDict
from draughts import Game, Move, WHITE, BLACK


game_object = Game(variant="english", fen="startpos")


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
    game.move([23,19])
    print(game.get_moves())
    minimax_ = minimax(create_board_tensor(game), 4, True, game)
    print(minimax_)
    '''
    game.move(minimax_[2])
    game.move([24,20])
    print(game.get_moves())
    minimax_ = minimax(create_board_tensor(game), 4, True, game)
    print(minimax_)
    game.move(minimax_[2])
    print(game.get_possible_moves())
    game.move([20,16])
    minimax_ = minimax(create_board_tensor(game), 4, True, game)
    print(minimax_)
    game.move(minimax_[2])  
    #moves = game.get_possible_moves()
    #game.move(moves[2]) 
    #minimax_ = minimax(create_board_tensor(game), 4, True, game)
    #print(minimax_)
    #game.move(minimax_[2])      
    '''
    

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
        return evaluate(board), board

    if max_player:
        maxEval = float('-inf')
        best_board = None 
        best_move = None
        future_boards, possible_moves, possible_games = get_future_board_states(game, False)
        for i in range(0,len(future_boards)):
            evaluation = minimax(future_boards[i], depth - 1, False, possible_games[i])[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_board = future_boards[i]
                best_move = possible_moves[i]
            
        return maxEval, best_board, best_move         
            
    else:
        minEval = float('inf')
        best_board = None
        best_move = None
        future_boards, possible_moves, possible_games = get_future_board_states(game, True)
        for i in range(0,len(future_boards)): 
            evaluation = minimax(future_boards[i], depth - 1, True, possible_games[i])[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_board = future_boards[i]
                best_move = possible_moves[i]
            
        return minEval, best_board, best_move   
    

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
    return torch.Tensor(future_boards), possible_moves, possible_games


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
    return AI_pieces - player_pieces + (AI_kings * 0.5 - player_kings* 0.5)


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

