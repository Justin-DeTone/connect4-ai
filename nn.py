from tensorflow import keras
from tensorflow.keras import initializers
import numpy as np
import math
import copy

#Run this script to create a new model with below name
model_dir = "models/0001"

def custom_loss(y_act, y_pred):
    p = y_pred[0]
    v = y_pred[1]
    pi = y_act[0]
    z = y_act[1]
    
    term1 = (v-z)**2
    term2 = 0
    for p_, pi_ in zip(p, pi):
        term2 += pi_ * math.log(p_, 10)
    return term1 - term2
    

def convert_data(raw_data):
    board_list = []
    perspective_list = []
    output_list = []
    for idx, line in enumerate(raw_data):
        #data_tuple = data_tuple[0]
        bin_string = line[0] #input - string representing board
        outcome = line[1] #output - int -1, 0, 1
        pi = copy.deepcopy(line[2]) #output - float 0 to 1
        #print("start")
        #print("pi: ", pi)
        perspective = np.asarray([int(line[3])]) #input: T/F
        pi.append(outcome)
        
        pi_arr = np.asarray(pi)
        #print("output: ", pi)
        player = np.empty([7, 6, 2])
        #print("bin_string: ", bin_string)
        for idx, value in enumerate(bin_string[:42]):
            x = idx % 7
            y = int(idx / 7)
            player[x, y, 0] = value
        for idx, value in enumerate(bin_string[42:-6]):
            x = idx % 7
            y = int(idx / 7)
            player[x, y, 1] = value
        board_list.append(player)
        perspective_list.append(perspective) #fix
        output_list.append(pi_arr)
        #print("END")
    print("START")
    board_arr = np.asarray(board_list)
    perspective_arr = np.asarray(perspective_list)
    output_arr = np.asarray(output_list)
    print(output_arr)
    print(perspective_arr)
    print(board_arr)
    #raise Exception("Stop here")
    return board_arr, perspective_arr, output_arr

def train(model, data):
    print("DATA BELOW:")
    #print(data) #debug
    board = data[0]
    perspective = data[1]
    output = data[2]
    print("board: ", board.shape)
    print("perspective: ", perspective.shape)
    print("output: ", output.shape)
    #raise Exception("Stop here2")
    #outcome = data[3]
    
    
    model.fit({"board": board, "player": perspective}, np.array([output]), epochs=3, batch_size = 16)
    raise Exception("You just trained")
    return model

def convert_input(bin_string, perspective): # is from player 1 perspective?
    player = np.empty([7, 6, 2])
    
    for idx, value in enumerate(bin_string[:42]):
        x = idx % 7
        y = int(idx / 7)
        player[x, y, 0] = value
    for idx, value in enumerate(bin_string[42:-6]):
        x = idx % 7
        y = int(idx / 7)
        player[x, y, 1] = value
    return player, int(perspective)
    
def make_prediction(model, data_input):
    board = np.array([data_input[0]])
    #print(board.size)
    perspective = np.array([data_input[1]])
    return model.predict([board, perspective])
    
def save(model, dir):
    model.save(dir)
    
def load(dir):
    return keras.models.load_model(dir, custom_objects={"custom_loss": custom_loss})

def make_model():
    input_board = keras.Input(shape=(7, 6, 2), name="board")
    input_playing_as_1 = keras.Input(shape=(1), name="player")

    conv1 = keras.layers.Conv2D(filters=1, kernel_size=2, strides=1, padding="valid", activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.01),
        bias_initializer=initializers.Zeros()) #change to three filters?
    conv2 = keras.layers.Conv2D(filters=1, kernel_size=3, strides=1, padding="same", activation="relu", kernel_initializer=initializers.RandomNormal(stddev=0.01),
        bias_initializer=initializers.Zeros())
    pool = keras.layers.MaxPooling2D(pool_size=2)
    flat = keras.layers.Flatten()

    #next layer takes both input from player1 and output of flat layer
    concat = keras.layers.Concatenate() # takes in a list of all inputs

    dense1 = keras.layers.Dense(10, activation="tanh", kernel_initializer=initializers.RandomNormal(stddev=0.01),
        bias_initializer=initializers.Zeros())
    dense2 = keras.layers.Dense(5, activation="tanh", kernel_initializer=initializers.RandomNormal(stddev=0.01),
        bias_initializer=initializers.Zeros())

    output = keras.layers.Dense(8, activation="tanh", kernel_initializer=initializers.RandomNormal(stddev=0.01),
        bias_initializer=initializers.Zeros())

    a = conv1(input_board)
    #b = conv2(a)
    c = pool(a)
    d = flat(c)

    e = concat([d, input_playing_as_1])
    f = dense1(e)
    #g = dense2(e)
    out = output(f)

    return keras.Model(inputs=[input_board, input_playing_as_1], outputs=out)



if __name__ == "__main__":
    model = make_model()
    model.summary()
    model.compile(optimizer=keras.optimizers.RMSprop(), loss=custom_loss)
    model.save(model_dir)
