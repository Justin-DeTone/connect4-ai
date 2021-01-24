from search_state import SearchState
from revised_state import EvaluateState
import nn
 
class MCTS():
    def __init__(self, root_str, parent, action, model, is_best_play=True, playing_as = 1, sims_threshold=10):
        

        self.is_best_play = is_best_play
        self.evaluate = EvaluateState()
        self.playing_as_one = playing_as
        if self.playing_as_one == 2:
            self.playing_as_one = False
        else:
            self.playing_as_one = True
        
        self.root = SearchState(root_str, parent, action, model, self.playing_as_one)
        self.current = self.root
        
        self.data = []
        self.num_sims = 0
        self.sims_thresh = sims_threshold
        
        
        #print(self.current)
        
        
    def __one_sim_game(self):
        is_draw = False
        while not self.evaluate.is_winner(self.current):
            print(self.current)
            if self.current.children: #if node has children already, pick with Q and U and keep going
                action = self.current.pick_by_qu()
                self.current = self.current.children[action]
                self.current.update_parents()
                
            
            else: #if node does not have children, get them, pick one based on p then repeat from root unless win or draw reached
                legal_moves = self.current.get_children()
                if not legal_moves:
                    print("Draw")
                    is_draw = True
                    break
                action = self.current.pick_by_p()
                #print("action: ", action)
                #print("children: ", self.current.children)
                self.current.children[action].update_parents()
                self.current = self.root # resets search within one sim
        #reaches here when game ends
        #raise Exception("End of one sim game at one move")
        
        if is_draw:
            outcome = 0
        else:
            #player one wins: +1, 2 wins: -1
            outcome = self.evaluate.is_winner(self.current)
            if outcome == 1:
                outcome = 1
            else:
                outcome = -1        
        self.__generate_nn_data(outcome)
        self.current = self.root
        self.num_sims += 1
        #print("sim outcome: ", outcome)
                        
        #store state somehow also check for win/draw
        
    def __generate_nn_data(self, outcome):
        #start at current position (end game state - this function should be called when game ends only
        #outcome: -1, 0, 1
        nn_data = []
        while self.root != self.current:
            #print("start at bottom")
            bin_string = self.current.parent.bin_string
            
            #always want to train on p values for best move, though we won't always play best move
            self.current.parent.pick_by_pi_best()
            self.current.parent.convert_children_pi()
            pi = self.current.parent.children_pi # return all children moves
            pi_list = []
            for col in range(7):
                if col in pi:
                    pi_list.append(pi[col])
                else:
                    pi_list.append(0)
            
            #adds line of format: (bin_string, pi, outcome, playing as one?)
            line_reward_self = (bin_string, outcome, pi_list, self.playing_as_one)
            line_reward_other = (bin_string, -outcome, pi_list, not self.playing_as_one) 
            self.data.append(line_reward_self)
            self.data.append(line_reward_other)
            self.current = self.current.parent
    
    def pick_move(self, is_best = True):
        #runs num_sims and then returns a moves and all p values
        while self.num_sims < self.sims_thresh:
            self.__one_sim_game()
        #raise Exception("You have simulated 5 games")
        if is_best:
            return self.root.pick_by_pi_best(), self.root.children_pi
        else:
            return self.root.pick_by_pi_random(tau=1), self.root.children_pi
        

    @staticmethod #check, function not needed after some thought
    def __flip_bin_perspective(bin_string):
        #flips bin_state between player 1 and 2
        player1 = bin_string[:42]
        player2 = bin_string[42:-6]
        last = bin_string[-6:]
        
        return player2 + player1 + last