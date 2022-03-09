import re
import pandas as pd
import draughts
from draughts import *
from draughts.PDN import PDNReader, _PDNGame
import numpy as np


filepath = "/Users/benakkermans/Downloads/CheckersTest.txt"
#reader = PDNReader(filepath)
#print(reader.games[0].moves)

def PDN_parse(filepath):
    """
    Parse text at given filepath  
    Pasres a PDN FIle as .txt into games

    Parameters
    ----------
    filepath : str
        Filepath for file to be parsed

    Returns
    -------
    data : pd.DataFrame
        Parsed data

    """
    re_startmove = "^1."
    re_movesplit = " "
    terminate_list = ['1-0','0-1','1/2-1/2']

    data = []
    with open(filepath, 'r') as file:
        # Flags to indicate where in the file structure we are
        movesflag = False
        
        ## MOVE LIST FOR EACH GAME
        movelist = []
        
        
        lines = file.readlines()
        
        for line in lines:
            if re.search(re_startmove,line):
                # Change flag to indicate it is a move line
                movesflag = True 
             
            # Parse line of moves   
            if movesflag:
                moves = re.split(re_movesplit, line)
                
                for move in moves:
                    move = move.strip("\n")

                    # Check if ending condition
                    if move in terminate_list:
                        movesflag = False
                        data.append(movelist)
                        movelist = []
                        
                    elif re.search("\.",move) == None:
                        movelist.append(move)
                        
    return data

def get_BoardState(moveslist, game_length=-1):
    ## Pieces denoted in the board as follows
    ## -3: White K, -1: White Piece, 0: No Piece, 1: Black Piece, 3: Black King
    ## Function currently starts with Black at Square 1 (Index 0)
    ###############################################################################
    # Index to Move Dict:
    index_dict = {1:[0,0],2:[0,1],3:[0,2],4:[0,3],
                  5:[1,0],6:[1,1],7:[1,2],8:[1,3],
                  9:[2,0],10:[2,1],11:[2,2],12:[2,3],
                  13:[3,0],14:[3,1],15:[3,2],16:[3,3],
                  17:[4,0],18:[4,1],19:[4,2],20:[4,3],
                  21:[5,0],22:[5,1],23:[5,2],24:[5,3],
                  25:[6,0],26:[6,1],27:[6,2],28:[6,3],
                  29:[7,0],30:[7,1],31:[7,2],32:[7,3]}
    
    # Board Initialzied to starting position of the board
    board = np.array([[1,1,1,1],
                      [1,1,1,1],
                      [1,1,1,1],
                      [0,0,0,0],
                      [0,0,0,0],
                      [-1,-1,-1,-1],
                      [-1,-1,-1,-1],
                      [-1,-1,-1,-1]])
    
    ## Next define the changes made to the board by each type of move
    for strmove in moveslist:
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
                ## First Check if current/target rows are EVEN or ODD
                ## A KING off of a jump can only occur in two scenarios -> 
                ## [Odd-row moving down the board (5->7) BLACK King and Even-row moving up (2->0) WHITE King
                
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
        
        print("Move was: ",strmove)
        print(board)
        
    return board, moveslist
            
test_data = PDN_parse(filepath)
print(get_BoardState(test_data[1]))
