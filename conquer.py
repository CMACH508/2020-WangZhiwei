import os
import random
import numpy as np
import hex

sample_num = 500
filelist = []
for name in os.listdir('data'):
    filename = 'data/' + name
    filelist.append(filename)
    #print(filename)

print(len(filelist))
sample_list = random.sample(filelist, sample_num)
print(len(sample_list))
train_data = []
for game in sample_list:
    x = np.load(game, allow_pickle=True)
    for i in range(x.shape[0]):
        if type(x[i][0]) != np.ndarray:
            x[i][0] = x[i][0]()
        train_data.append(x[i])
    os.remove(game)
train_data = random.sample(train_data, len(train_data))
train_data = np.array(train_data)
print(train_data.shape[0])
np.save('games.npy', train_data)
