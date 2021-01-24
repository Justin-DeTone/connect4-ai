import revised_state
import random
import numpy as np
import nn 

class SearchState(revised_state.State):
    def __init__(self, bin_string, parent, action, model, playing_as_one):
        super().__init__(bin_string)
        self.n = 0
        self.w = 0
        self.q = 0
        
        self.parent = parent #set to None if root        
        self.action = action #action to get here
       
        self.playing_as_one = playing_as_one
        self.model = model
        
        if self.parent:
            self.p = self.get_p()
        
        self.children_pi_raw = {} # likelihood of picking in game (not training); maps column (action from current state) to pi, note: values have no upper limit
        self.children_pi = {} # same as above but pi values add up to one, value that gets fed to nn


        self.children = {}

        self.is_traversed = False
        


    def get_p(self):
        #add: interface with NN to get p
        data_in = nn.convert_input(self.parent.bin_string, self.playing_as_one)
        p= nn.make_prediction(self.model, data_in)[0]
        #print(p)
        p = p[:-1]
        
        return max(p[self.action], 0) #check: ensure nn does not trend towards negative p long term
        #return random.uniform(0, 1)
    
    def get_v(self):
        #add: interface with NN to get expected value (v)
        #return 2 * random.uniform(0, 1) - 1 
        data_in = nn.convert_input(self.bin_string, self.playing_as_one)
        v = nn.make_prediction(self.model, data_in)[0]
        return v[-1]        
    
    def update_parents(self, v=None):
        if self.parent == None:
            return
            
        if not v:
            v = self.get_v()
            #print("v: ", v)
        self.parent.n += 1
        self.parent.w += v
        self.parent.q = self.parent.w/self.parent.n
        
        self.parent.update_parents(v)
     
    def convert_children_pi(self):
        sum = 0
        for pi in self.children_pi_raw.values():
            sum += pi
        for col, pi in self.children_pi_raw.items():
            if sum <= 0.00005:
                self.children_pi[col] = 1/len(self.children_pi_raw)
            else:
                self.children_pi[col] = pi / sum
    
    def get_children(self):
        #called when this state is traversed for first time, returns legal moves, if no legal moves returns empty list
        legal_moves = self.get_legal_moves() #check: no use of super()
        for col in legal_moves:
            bin_string = super().make_move(col, return_obj=False)
            self.children[col] = SearchState(bin_string, self, col, self.model, self.playing_as_one)
        if self.parent:
            self.is_traversed = True
        return legal_moves #used to break out of sim loop
        
    def get_u(self):
        #add: c_puct is increased to up exploration, should decrease as MCTS gets deeper
        c_puct = 1
        other_children_n = 0
        for col, child in self.parent.children.items():
            if col == self.action: 
                continue
            other_children_n += child.n
            #print("p: ", self.p)
        u = c_puct * self.p * other_children_n / (1 + self.n)
        #print("u: ", u)
        return u
        
    def pick_by_qu(self):
        # use this if self.is_traversed == True
        col_to_qu = {}
        for col, child in self.children.items():
            col_to_qu[col] = child.q + child.get_u()
            #print("q: ", child.q)
        #print("col to qu :", col_to_qu)    
        qu_best = -10
        col_best = None
        for col, qu in col_to_qu.items():
            if qu > qu_best:
                col_best = col
                qu_best = qu
        if col_best is None:
            col_best = self.__stochastic_choice(col_to_qu)
            #raise Exception("There should be a choice with some Q + U > 0")
        return col_best
    
    def pick_by_p(self):
        #use this to pick on a leaf node
        best_p = 0
        best_col = None
        col_to_p = {}
        for col, child in self.children.items():
            p = child.p
            col_to_p[col] = p
            if p > best_p:
                best_col = col
                best_p = p
        if best_col is None:
            #raise Exception("There should be a choice with some p > 0")
            print("There should be a choice with some p > 0")
            best_col = self.__stochastic_choice(col_to_p)
            #print("best_col_from stochastic_choice: ", best_col)
        return best_col
    
    def pick_by_pi_random(self, alpha=1, tau=1):
        # as tau approaches infinity -> truly random, tau approaches 0+ -> more deterministic
        # for exploratory play
        col_to_pi = {}
        for col, child in self.children.items():
            pi = alpha * child.n**(1/tau)
            col_to_pi[col] = pi
        self.children_pi_raw = col_to_pi
        return self.__stochastic_choice(col_to_pi)    
        
            
    def pick_by_pi_best(self):
        #for competitive play
        best_p = 0
        best_col = None
        col_to_pi_raw = {}
        for col, child in self.children.items():
            col_to_pi_raw[col] = child.n
            if child.n > best_p:
                best_col = col
                best_p = child.n
        self.children_pi_raw = col_to_pi_raw
        #print(self.children_pi_raw)
        if not best_col:
            assert Exception("There should be a choice with some pi > 0")
        return best_col
        
    @staticmethod    
    def __stochastic_choice(col_to_pi): #accepts each action mapped to probability, does not need to add up to 1, returns action
        
        #print("col_to_pi: ", col_to_pi)
        sum = 0
        for pi in col_to_pi.values():
            sum += pi
        
        rand = random.uniform(0,sum)
        
        sum_up = 0
        for col, pi in col_to_pi.items():
            sum_up += pi
            if rand <= sum_up:
                return col
        assert Exception("Should have made a choice in __stochastic_choice()")
            

        
        
        
        
        
        
        
        
        