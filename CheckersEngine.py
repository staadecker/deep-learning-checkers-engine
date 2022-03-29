import numpy as np
import re
from copy import deepcopy
import torch
from collections import OrderedDict
from draughts import Game, Move, WHITE, BLACK


game = Game(variant="english", fen="startpos")


board_tensor = torch.tensor([1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,
                  0,0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1])


index_dict = {1:[0,0],2:[0,1],3:[0,2],4:[0,3],
              5:[1,0],6:[1,1],7:[1,2],8:[1,3],
              9:[2,0],10:[2,1],11:[2,2],12:[2,3],
              13:[3,0],14:[3,1],15:[3,2],16:[3,3],
              17:[4,0],18:[4,1],19:[4,2],20:[4,3],
              21:[5,0],22:[5,1],23:[5,2],24:[5,3],
              25:[6,0],26:[6,1],27:[6,2],28:[6,3],
              29:[7,0],30:[7,1],31:[7,2],32:[7,3]}


board_array_ = np.array([[1,1,1,1],
                        [1,1,1,1],
                        [1,1,1,1],
                        [0,0,0,0],
                        [0,0,0,0],
                        [-1,-1,-1,-1],
                        [-1,-1,-1,-1],
                        [-1,-1,-1,-1]])


def run_engine():
    run = True
    game = Game(variant="english", fen="startpos")

    while run:
        
        if game.whose_turn() == 2:  #opponent (Minimax): 1   #player: 2
            ##move = (get the move from the ML model)
            moveslist = game.get_possible_moves()
            captureslist = game.legal_moves()[1]
            move_index = moveslist.index(move)
            game.move(move)
            board = get_BoardState(move, captures, board, index_dict, game_length=-1)
            
        if game.is_over() == True or game.draw() == True:
            run = False            
            
        if game.whose_turn() == 1:
            moveslist = game.get_possible_moves()
            captureslist = game.legal_moves()[1]
            value, new_board = minimax(board_array, 4, True, game)
            game.move(new_board)
            board = get_BoardState(new_board, captures, board, index_dict, game_length=-1)


def test_function():
    game = Game(variant="english", fen="startpos")
    moves, captures = game.legal_moves()
    game.move([22,18])
    board_array = get_BoardState([[22,18]], captures[moves.index([[22,18]])], board_array_, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([12,16])
    board_array = get_BoardState([[12,16]], captures[moves.index([[12,16]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([24,20])
    board_array = get_BoardState([[24,20]], captures[moves.index([[24,20]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([10,15]) 
    board_array = get_BoardState([[10,15]], captures[moves.index([[10,15]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([21,17]) 
    board_array = get_BoardState([[21,17]], captures[moves.index([[21,17]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([15,22]) 
    board_array = get_BoardState([[15,22]], captures[moves.index([[15,22]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([25,18])  
    board_array = get_BoardState([[25,18]], captures[moves.index([[25,18]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([9,14]) 
    board_array = get_BoardState([[9,14]], captures[moves.index([[9,14]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([17,10]) 
    board_array = get_BoardState([[17,10]], captures[moves.index([[17,10]])], board_array, index_dict, game_length=-1)
    print(board_array)
    moves, captures = game.legal_moves()
    game.move([6,15])         
    board_array = get_BoardState([[6,15]], captures[moves.index([[6, 15], [15, 22]])], board_array, index_dict, game_length=-1)
    print(board_array)


def get_BoardState(moveslist, captureslist, board, index_dict, game_length=-1):
    master_list = []
    num_moves = 0
    
    capture_move = False
    multi_capture_move = False
    
    for captures in captureslist:
        if captures != None:
            capture_move = True
    
    for move in moveslist:
        # Breakdown the move first
        
        ## Basic Move
        if capture_move == False and multi_capture_move == False:
            ## Simple as we know there are only two moves, no capture so straight update 
            start_id = index_dict[move[0]]
            end_id = index_dict[move[1]]
            piece = board[start_id[0],start_id[1]]
            
            ## Execute the Update using above info on the move
            board[start_id[0],start_id[1]] = 0
            ## KING CHECK
            if piece == 1 and end_id[0] == 7:
                board[end_id[0],end_id[1]] = 3
            elif piece == -1 and end_id[0] == 0:
                board[end_id[0],end_id[1]] = -3
            else:
                board[end_id[0],end_id[1]] = piece
            
        ## Capture Move / Jump --> x-number of jumps in the move  
        else:
            x = len(move)
            start_id = index_dict[move[0]]
            
            visited_squares = []
            for i in range(x-1):
                id = index_dict[move[i+1]]
                visited_squares.append(id)
            
            #end_id = visited_squares[-1]
            piece = board[start_id[0],start_id[1]]
            
            ## Execute the Update using above info on the move
            board[start_id[0],start_id[1]] = 0
            
            current = start_id
            for target in visited_squares:
                # EVEN ROW RULES
                if current[0] % 2 == 0:
                    if (current[0]<target[0] and current[1]>target[1]) or (current[0]>target[0] and current[1]>target[1]):
                        middle_row = (max([current[0],target[0]])) - 1
                        # Remove piece in middle row, starting column
                        board[middle_row,current[1]] = 0
                        ## KING CHECK (3 conditions: Last Jump, White Piece, Row=0), even row can only be a WHITE KING
                        if (visited_squares.index(target) == (len(visited_squares) - 1)) and (piece == -1) and (target[0] == 0):
                            board[target[0],target[1]] = -3
                        else:
                            board[target[0],target[1]] = piece
                            
                        current = target
                    
                    elif (current[0]<target[0] and current[1]<target[1]) or (current[0]>target[0] and current[1]<target[1]):
                        middle_row = (max([current[0],target[0]])) - 1
                        # Remove piece in middle row, target column
                        board[middle_row,target[1]] = 0
                        ## KING CHECK (3 conditions: Last Jump, White Piece, Row=0), even row can only be a WHITE KING
                        if (visited_squares.index(target) == (len(visited_squares) - 1)) and (piece == -1) and (target[0] == 0):
                            board[target[0],target[1]] = -3
                        else:
                            board[target[0],target[1]] = piece
                            
                        current = target

                # ODD ROW RULES
                else:
                    if (current[0]<target[0] and current[1]>target[1]) or (current[0]>target[0] and current[1]>target[1]):
                        middle_row = (max([current[0],target[0]])) - 1
                        # Remove piece in middle row, starting column
                        board[middle_row,target[1]] = 0
                        ## KING CHECK (3 conditions: Last Jump, Black Piece, Row=7), odd row can only be a BLACK KING
                        if (visited_squares.index(target) == (len(visited_squares) - 1)) and (piece == 1) and (target[0] == 7):
                            board[target[0],target[1]] = 3
                        else:
                            board[target[0],target[1]] = piece
                            
                        current = target

                    
                    elif (current[0]<target[0] and current[1]<target[1]) or (current[0]>target[0] and current[1]<target[1]):
                        middle_row = (max([current[0],target[0]])) - 1
                        # Remove piece in middle row, target column
                        board[middle_row,current[1]] = 0
                        ## KING CHECK (3 conditions: Last Jump, Black Piece, Row=7), odd row can only be a BLACK KING
                        if (visited_squares.index(target) == (len(visited_squares) - 1)) and (piece == 1) and (target[0] == 7):
                            board[target[0],target[1]] = 3
                        else:
                            board[target[0],target[1]] = piece
                            
                        current = target

    return board


def minimax(board, depth, max_player, game):
    temp_board = deepcopy(board)
    
    if depth == 0 or game.is_over() == True or game.is_draw() == True:
        return evaluate(board), board   
    
    if max_player:
        maxEval = float('-inf')
        best_move = None 
        moveslist, captures = game.legal_moves()
        for board in get_future_board_states(temp_board, index_dict, game):
            evaluation = minimax(board, depth - 1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = board
        return maxEval, best_move            
            
    else:
        minEval = float('inf')
        best_move = None   
        moveslist, captures = game.legal_moves()  
        for board in get_future_board_states(temp_board, index_dict, game): 
            evaluation = minimax(board, depth - 1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = board
        return minEval, best_move        


def get_future_board_states(board, index_dict, game):
    board = tensor_to_board(board)
    future_boards = []
    num_possible_moves = 0
    valid_moves, captures = game.legal_moves()
    for moves in valid_moves:
        if len(moves) > 1:
            index = valid_moves.index(moves)
            moves_converted = convert_multi_move(moves)
            valid_moves[index] = moves_converted
    for moves in valid_moves:
        num_possible_moves += 1
        temp_board = deepcopy(board)
        possible_future_board = get_BoardState(moves, captures[valid_moves.index(moves)], temp_board, index_dict, game_length=-1)
        future_boards.append(possible_future_board)
    future_boards_numpy = np.array(future_boards) 
    future_boards_tensor = board_to_tensor(future_boards_numpy)
    future_boards_tensor = torch.reshape(future_boards_tensor, (num_possible_moves, 32))
    return future_boards_tensor


def evaluate(board):
    player_pieces = 0
    AI_pieces = 0
    player_kings = 0
    AI_kings = 0    
    for rows in board:
        for value in rows:
            if value == -1:
                player_pieces += 1
            if value == 1:
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
    board_array = tensor.numpy()
    board_array = np.reshape(board_array,(8,4))
    return board_array


def board_to_tensor(board):
    board_tensor = torch.from_numpy(board)
    board_tensor = board_tensor.flatten()
    return board_tensor

