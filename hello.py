import matplotlib.pyplot as plt
import random
f = open('20190312/err.txt', 'r')

x = []
y = []
i = 1
times = 0
temp = 0
interval = 100
while True:
    line = f.readline()
    #print("str: ", i, line)
    if line == '':
        break
    if line == 'nan':
        continue
    try:
        line = float(line)
    except:
        continue
    temp += line
    times += 1

    if times % interval == 0:
        i += 1
        res = temp / interval
        x.append(i)
        y.append(res)
        temp = 0
        times = 0
f.close()

#plt.scatter(x, y, s=1)
#plt.plot(x, beta, color='red', label='model-beta')
#plt.plot(x_axix, gamma, color='blue', label='model-gamma')
#plt.legend()

'''plt.xlabel('Iteration number(hundred)', fontsize=14)
plt.ylabel('Average lambda on a batch', fontsize=14)
plt.show()'''

plt.plot(x, y)
plt.show()

