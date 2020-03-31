import os
import random
import numpy as np

sample_num = 10000
file_list = []
train_data = []
for name in os.listdir('data'):
    filename = 'data/' + name
    file_list.append(filename)

while len(file_list) >= 10000:
    f = min(file_list)
    file_list.remove(f)
    os.remove(f)


for filename in file_list:
    if os.path.exists(filename):
        x = np.load(filename, allow_pickle=True)
        for i in range(x.shape[0]):
            train_data.append(x[i])
    #print(filename)

train_data = random.sample(train_data, sample_num)
train_data = np.array(train_data)
print(train_data.shape[0])
np.save('games.npy', train_data)

sample_num = 10000
file_list = []
train_data = []
for name in os.listdir('pc_data'):
    filename = 'pc_data/' + name
    file_list.append(filename)

while len(file_list) >= 10000:
    f = min(file_list)
    file_list.remove(f)
    os.remove(f)


for filename in file_list:
    if os.path.exists(filename):
        x = np.load(filename, allow_pickle=True)
        for i in range(x.shape[0]):
            train_data.append(x[i])
    #print(filename)

train_data = random.sample(train_data, sample_num)
train_data = np.array(train_data)
print(train_data.shape[0])
np.save('consistency.npy', train_data)