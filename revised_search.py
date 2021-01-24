class Search():
    def __init__(self, evaluate_obj,):
        self.evaluate_obj = evaluate_obj
        self.unique_count = 1
        
    def dfs(self, state_obj):
        if self.evaluate_obj.is_winner(state_obj):
            return
    
        legal_moves = state_obj.get_legal_moves()
        if not legal_moves:
            print("draw")
            return
        else:
            for col in legal_moves:
                next_obj = state_obj.make_move(col)
                if self.evaluate_obj.is_unique(next_obj):
                    self.unique_count += 1
                    print("unique states found: ", self.unique_count)
                    self.dfs(next_obj)
            return    
        