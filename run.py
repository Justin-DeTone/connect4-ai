from mcts_implementation import MCTS
from revised_state import State, EvaluateState
import random
import nn

playing_as = 1
#ask for my input to set player

old_model_dir = "models/0001"
new_model_dir = "models/0002"

class Run():   
    def __init__(self, train_both=False):
        self.playing_as = 1 #must flip every time when playing itself        
        #self.current_str = "0" * 84 + "101010" #starts new game
        self.state = State("0" * 84 + "101010")
        self.last_move = None
        self.last_state = None
        
        self.old_model_dir = "models/0001"
        self.new_model_dir = "models/0002"
        
        self.old_model = nn.load(old_model_dir)
        self.new_model = nn.load(new_model_dir)
        
        self.current_game_in_batch_odd = False
        self.turn_is_odd = False
    
        self.train_both = train_both
    def updateNN(self, data):
        print("all data")
        print(data)
        nn_data = nn.convert_data(data)
        self.new_model = nn.train(self.new_model, nn_data)
    
    def update_old(self, data):
        nn_data = nn.convert(data)
        self.old_model = nn.train(self.old_model, nn_data)
        
    def run_training(self, first_time=False):
        #print(self.state)
        if self.current_game_in_batch_odd:
            if self.turn_is_odd:
                model_playing = self.old_model
            else:
                model_playing = self.new_model
        else:
            if self.turn_is_odd:
                model_playing = self.new_model
            else:
                model_playing = self.old_model
        
        if first_time and model_playing == self.new_model:
            mcts_instance = MCTS(self.state.bin_string, self.last_state, self.last_move, model_playing, is_best_play=False, playing_as=self.playing_as, sims_threshold=1)
        else:
            mcts_instance = MCTS(self.state.bin_string, self.last_state, self.last_move, model_playing, is_best_play=False, playing_as=self.playing_as)
        if not self.state.get_legal_moves():
            return 3
        move_to_play, p_values = mcts_instance.pick_move(is_best=False)
        
        print("move to play: ", move_to_play)
        
        self.last_move = move_to_play
        self.last_state = mcts_instance.root        
        self.state = self.state.make_move(move_to_play)
        
        #print(mcts_instance.data) #debug
        
        self.updateNN(mcts_instance.data) # list of tuples (bin_string, outcome, pi, playing as one?)
        
        if self.train_both:
            self.update_old(mcts_instance.data)
        
        winner = EvaluateState().is_winner(self.state)
        if winner:
            print("winning state:\n", self.state, "\n", self.state.bin_string)
        return winner
        #run until returns a value
        self.turn_is_odd = not turn_is_odd
        
    def my_move_vs(self):
        #Will provide pi values based on absolute move strength, I pick move
        mcts_instance = MCTS(self.state.bin_string, self.last_state, self.last_move, self.nn_dir, is_best_play=True, playing_as=self.playing_as)
        best_move, p_values = mcts_instance.pick_move()
        
        print(self.state)
        print("P values for each move: ", p_values) #add: v values from nn
        
        input0 = "dummy"
        valid = self.sate.get_legal_moves()
        if not valid:
            print("tie")
            return 3
        while input0 not in valid:
            input0 = input("Make a move: ")
            input0 = int(input0)
        
        self.state = self.state.make_move(input0)
        winner = EvaluateState().is_winner(self.state)
        if winner:
            print("player {} won".format(winner))
        return winner
        #this function should repeat until it returns a non zero value
        
    def other_move_vs(self):
        print(self.state)
        
        input0 = "dummy"
        valid = self.sate.get_legal_moves()
        if not valid:
            print("tie")
            return 3
        while input0 not in valid:
            input0 = input("Enter opponent move: ")
            input0 = int(input0)
        
        self.state = self.state.make_move(input0)
        winner = EvaluateState().is_winner(self.state)
        if winner:
            print("player {} won".format(winner))
        return winner
        
def vs_game_loop(playing_as_2=False):
    winner = None
    turn_count = 0
    
    game = Run(None, playing_as_2 + 1)
    
    while not winner:
        if turn_count % 2 == playing_as_2:
            winner = game.my_move_vs(self)
        else:
            winner = game.other_move_vs
            
def training_loop(game):
    winner = None
    player_to_move = 1
   
    #game = Run()
    first_time = 2
    while not winner:
        winner = game.run_training(bool(first_time))
        if game.playing_as == 1:
            game.playing_as = 2
        else:
            game.playing_as = 1
        #raise Exception("have made a move")
        first_time -= 1
        if first_time < 0:
            first_time = 0
    self.current_game_in_batch_odd = not self.current_game_in_batch_odd
    
    raise Exception("One game finished")
    return winner
   
def train_both_once():
    winner = None
    player_to_move = 1
   
    game = Run(train_both=True)
    
    while not winner:
        winner = game.run_training(True)
        if game.playing_as == 1:
            game.playing_as = 2
        else:
            game.playing_as = 1
        #raise Exception("have made a move")
    self.current_game_in_batch_odd = not self.current_game_in_batch_odd
    
    raise Exception("One game finished")
    return winner

    
def train_play_games(num_games):
        num_so_far = 0 
        old_wins = 0
        new_wins = 0
        game = 1
        while num_so_far < num_games:
            game = Run()
            winner = training_loop(game)
            if self.current_game_in_batch_odd: 
                if winner == 1:
                    new_wins += 1
                elif winner == -1:
                    old_wins += 1
            else:
                if winner == 1:
                    old_winds += 1
                elif winner == -1:
                    new_wins += 1
            num_so_far += 1
        print("old wins: {}, new wins : {}".format(old_wins, new_wins))
        
        nn.save(game.new_model, new_model_dir)
        
        if new_wins > old_wins:
            print("new model has beaten old model: ", new_model_dir)
            
        elif new_wins == old_wins:
            print("models performed equally")
        else:
            print("old model prevails: ", old_model_dir)
        
    
if __name__ == "__main__":
    train_both_once()
    
    #train_play_games(10)




        