f = open('ratings.txt', 'r')

res = []

while True:
    line = f.readline().strip()
    if line == '':
        break


    x = line.split(' ')
    for i in range(len(x)):
        if i == 0 or i == 1:
            continue
        if x[i] != ' ' and x[i] != '':
            res.insert(0, int(x[i]))
            break

print(res)
