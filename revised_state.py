import numpy as np

class State():
    def __init__(self, bin_string):
        self.token = {1: "X", 2: "O"}
        self.board, self.last_move_by = self.bin_to_array(bin_string)
        self.bin_string = bin_string

                
    def make_move(self, col, return_obj=True): # test
        #alter binary string not object then use string to create a new object
        player_to_move = self.last_move_by
        
        if player_to_move == 1:
            player_to_move = 2
        else:
            player_to_move = 1
            
        
        state_str = self.bin_string
        
        #last_move = self.bin_string[-6:] #don't need here
        player1 = self.bin_string[:-48]
        player2 = self.bin_string[-48:-6]
        
            
        if player_to_move == 1:
            player = self.bin_string[:-48]            
        else:
            player = self.bin_string[-48:-6]
        
        height_idx = 0
        value = "A"
        while (value != "-"):
            value = self.board[col, height_idx]
            if value == "-":
                str_idx_edit = 7 * height_idx + col
                player = (player[:str_idx_edit] + "1" + player[str_idx_edit + 1:])
                break
            else:
                pass
            height_idx += 1
            if height_idx > 5:
                raise TypeError("Not a valid move")
        
        last_move_bin = bin(str_idx_edit)
        last_move_str = str(last_move_bin)[2:]
        
        while len(last_move_str) < 6:
            last_move_str = "0" + last_move_str
        
        if player_to_move == 1:
            final_str = player + player2 + last_move_str
        else:
            final_str = player1 + player + last_move_str
        
        if not return_obj:
            return final_str
        
        new_state_obj = State(final_str)
        
        return new_state_obj
        
    def get_legal_moves(self):
        legal_moves = []
        for idx, col in enumerate(self.board):
            if col[-1] != self.token[1] and col[-1] != self.token[2]:
                legal_moves.append(idx)
        return legal_moves
        
    def __str__(self):
        str = ""
        
        for height_idx in range(5, -1, -1):
            line = ""
            for row_idx in range(7):
                line += self.board[row_idx, height_idx] + " "
            line += "\n"
            str += line
        
        return str
    
    def bin_to_array(self, bin_string):
        last_move = bin_string[-6:]
        player2 = bin_string[-48:-6]
        player1 = bin_string[:42]
        
        
        board = np.full((7,6), "-") 
        
        for idx, (piece1, piece2) in enumerate(zip(player1, player2)):
            col_idx = int(idx / 7)
            row_idx = idx % 7
            
            one = int(piece1)
            two = int(piece2)            

            if one and two:
                raise Exception("Cannot have two pieces in same state")
            elif one:
                board[row_idx, col_idx] = self.token[1]
            elif two:
                board[row_idx, col_idx] = self.token[2]
            else:
                board[row_idx, col_idx] = "-"
                
        
        last_move_by = 2
        
        last_move_int = int(last_move, 2) # 0-41, 42 if first move not yet made

        if last_move_int == 42:
            #break
            return board, last_move_by
 
        if int(player1[last_move_int]) and int(player2[last_move_int]):
            raise Exception("Cannot have two pieces occupy the same space")
        elif int(player1[last_move_int]):
            last_move_by = 1
        elif int(player2[last_move_int]):
            pass
        else:
            raise Exception("Must have a last move")
        
        return board, last_move_by      
        #returns an array with X, O, or -, and last player to move
    

class EvaluateState():
    def __init__(self):
        self.bin_state_hist = {} # maps state to number of times arrived at

    @staticmethod
    def is_winner(state_obj):
        #print("state to evaluate for win:\n", state_obj)
        #only evaluates possible wins from last move
        last_move_idx_str = state_obj.bin_string[-6:]
        last_move_idx = int(last_move_idx_str, 2)
        
        if last_move_idx > 41:
            return None
        
        x = last_move_idx % 7
        y = int(last_move_idx / 7)
        
        piece = state_obj.board[x, y]
        
        horizontal = EvaluateState.offset_lookup(state_obj, x, y, 1, 0, piece) + EvaluateState.offset_lookup(state_obj, x, y, -1, 0, piece)
        if horizontal > 2:
            print("horiz winner")
            return state_obj.last_move_by
        
        #vertical
        vertical = EvaluateState.offset_lookup(state_obj, x, y, 0, 1, piece) + EvaluateState.offset_lookup(state_obj, x, y, 0, -1, piece)
        if vertical > 2:
            print("vert winner")
            return state_obj.last_move_by
            
        #forward diagonal
        diag1 = EvaluateState.offset_lookup(state_obj, x, y, 1, 1, piece) + EvaluateState.offset_lookup(state_obj, x, y, -1, -1, piece)
        if diag1 > 2:
            print("diag1 winner")
            return state_obj.last_move_by
        
        #backwards diagonal
        diag2 = EvaluateState.offset_lookup(state_obj, x, y, 1, -1, piece) + EvaluateState.offset_lookup(state_obj, x, y, -1, 1, piece)
        if diag2 > 2:
            print("diag2 winner")
            return state_obj.last_move_by
        
        return None
        #return player num or none
    
    @staticmethod
    def offset_lookup(state_obj, x, y, delta_x, delta_y, piece, count = 0):
        #recursive function to count number of pieces in a direction, starts at x and yet
        board = state_obj.board
        new_x = x + delta_x
        new_y = y + delta_y
        
        if new_x not in range(0, 7) or new_y not in range(0, 6):
            return count
        
        #try: 
        elif board[x+delta_x, y+delta_y] != piece:
            #print("num found in direction: ", count)
            return count
            
        else:      
            return EvaluateState.offset_lookup(state_obj, x+delta_x, y+delta_y, delta_x, delta_y, piece, count+1)
        #except IndexError:
            #print("num found in direction: ", count)
            return count
        
    def is_unique(self, state_obj):
        try:
            instances = self.bin_state_hist[state_obj.bin_string]
            self.bin_state_hist[state_obj.bin_string] = instances + 1
            return False
        except KeyError:
            self.bin_state_hist[state_obj.bin_string] = 1
            return True
        #is this a unique state

if __name__ == "__main__":        
    start_bin = "0" * 84 + "101010"
    full_bin = "10" * 21 + "01" * 21 + str(bin(41))[2:]
    missing_top_right = "10" * 21 + "01" * 22 + "00" + str(bin(40))[2:]

             
    state = State(start_bin)
    print("legal moves (all): {}".format(state.get_legal_moves()))
    move0 = state.make_move(0)
    print("1st col:\n", move0)
    move1 = move0.make_move(3)
    print("4th col:\n")
    print(move1)
    move2 = move1.make_move(3)
    print("4th col:\n", move2)
    print(EvaluateState().is_winner(move2))
    move3 = move2.make_move(0)
    move4 = move3.make_move(3)
    move5 = move4.make_move(0)
    move6 = move5.make_move(3)
    move7 = move6.make_move(0)
    print(EvaluateState().is_winner(move7))
    move8 = move7.make_move(3)
    print(EvaluateState().is_winner(move8))
    print(EvaluateState().is_unique(move8))

    state2 = State(full_bin)
    print("legal moves (none): {}".format(state2.get_legal_moves()))

    state3 = State(missing_top_right)
    print("legal moves (6): {}".format(state3.get_legal_moves()))
    state3_1 = state3.make_move(6)
    print("now full\n", state3_1)
    print(EvaluateState().is_winner(state3_1))