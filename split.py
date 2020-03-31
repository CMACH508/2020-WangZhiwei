import numpy as np
total = np.load('game.npy')
sz = total.shape[0]
training = total[0:sz*4//5]
validation = total[sz*4//5:sz*4//5+sz//10]
testing = total[sz*4//5+sz//10:sz*4//5+sz//10+sz//10]
print(training.shape)
print(validation.shape)
print(testing.shape)
np.save('training.npy', training)
np.save('validating.npy', validation)
np.save('testing.npy', testing)
