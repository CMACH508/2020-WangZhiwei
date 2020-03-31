import numpy as np
import os

for name in os.listdir('data'):
    filename = 'data/' + name
    x = np.load(filename, allow_pickle=True)
    print(x.shape[0])
    if x.shape[0] < 15:
        os.remove(filename)
