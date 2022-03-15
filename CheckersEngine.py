import numpy as np
import re
from copy import deepcopy
from draughts import Game, Move, WHITE, BLACK


board_vector = np.array([1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,
                  0,0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1])


index_dict = {1:[0,0],2:[0,1],3:[0,2],4:[0,3],
              5:[1,0],6:[1,1],7:[1,2],8:[1,3],
              9:[2,0],10:[2,1],11:[2,2],12:[2,3],
              13:[3,0],14:[3,1],15:[3,2],16:[3,3],
              17:[4,0],18:[4,1],19:[4,2],20:[4,3],
              21:[5,0],22:[5,1],23:[5,2],24:[5,3],
              25:[6,0],26:[6,1],27:[6,2],28:[6,3],
              29:[7,0],30:[7,1],31:[7,2],32:[7,3]}


board_array = np.array([[1,1,1,1],
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
            game.move()
            board = get_BoardState([22,17], index_dict, board_array, 2, False, game_length=-1)
            
        if game.is_over() == True or game.draw() == True:
            run = False            
            
        if game.whose_turn() == 1:
            value, new_board = minimax(board_array, 4, True, game)
            game.ai_move(new_board)


def test_function():
    game = Game(variant="english", fen="startpos")
    print(game.get_board())
    print(game.whose_turn())
    moves, captures = game.legal_moves()
    print(moves, captures)    
    game.move([22,17])
    moves, captures = game.legal_moves()
    print(moves, captures)    
    game.move([9,14])
    moves, captures = game.legal_moves()
    print(moves, captures) 
    

def get_BoardState(moveslist, board, index_dict, game_length=-1):
    cols = ['num_moves','board_state','next_move']
    #master_list = pd.DataFrame(columns=cols)
    master_list = []
    num_moves = 0
    ## Flip the board if it is Black's move (Board currently set so player-to-move is at the bottom)
    #flip_flag = True
    
    ## Next define the changes made to the board by each type of move
    for strmove in moveslist:
        move_index = moveslist.index(strmove)
        ## Output with next move
        # Set board, flip if flip_flag
        #c_board = board.copy()
        #if flip_flag:
            #for i in range(len(c_board)):
                #c_board[i] = c_board[i].reverse()
            #c_board = np.flip(c_board, axis=0)
            #c_board = np.flip(c_board, axis=1)
                
        if move_index == (len(moveslist)-1):
            master_list.append((num_moves,c_board,"Game Over"))
        else:
            #print(board)
            master_list.append((num_moves,c_board,moveslist[move_index]))
            
        # Breakdown the move first
        ## Basic Move
        if re.search("-",strmove) != None:
            ## Simple as we know there are only two moves, no capture so straight update 
            move = strmove.split("-")
            start_id = index_dict[int(move[0])]
            end_id = index_dict[int(move[1])]
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
            move = strmove.split("x")
            x = len(move)
            start_id = index_dict[int(move[0])]
            
            visited_squares = []
            for i in range(x-1):
                id = index_dict[int(move[i+1])]
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
    
    if depth == 0 or game.is_over() == True or game.draw() == True:
        return evaluate(board), board   
    
    if max_player:
        maxEval = float('-inf')
        best_move = None     
        for move in game.legal_moves():
            evaluation = minimax(get_BoardState(move, temp_board, index_dict, game_length=-1), depth - 1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        return maxEval, best_move            
            
    else:
        minEval = float('inf')
        best_move = None     
        for move in get_all_possible_opponent_moves(temp_board, move, game): ##gotta figure this part out
            evaluation = minimax(get_BoardState(move, temp_board, index_dict, game_length=-1), depth - 1, True, game)[0]
            minEval = max(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        return minEval, best_move        


def simulate_move(move, board, game, skip):
    game.move(move[0], move[1])
    if skip:
        get_BoardState(moves, board, index_dict, game_length=-1)
    return board


def get_all_possible_opponent_moves(board, move, game):
    moves = []
    valid_moves = game.legal_moves()
    for move, skip in valid_moves.items():
        temp_board = deepcopy(board)
        new_board = simulate_move(move, temp_board, game, skip)
        moves.append(new_board)
    return moves


def evaluate(board):
    player_pieces = 0
    AI_pieces = 0
    player_kings = 0
    AI_kings = 0    
    for rows in board:
        for value in row:
            if value == -1:
                player_pieces += 1
            if value == 1:
                AI_pieces += 1
            if value == -3:
                player_kings += 1
            if value == 3:
                AI_kings += 1                
    return AI_pieces - player_pieces + (AI_kings * 0.5 - player_kings* 0.5)

