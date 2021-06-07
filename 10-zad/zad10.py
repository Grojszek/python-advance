def read_input(filename):
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    input_values = [line.strip() for line in lines]
    return input_values


read_values = read_input('input.txt')
x_size = len(read_values[0])
y_size = len(read_values)
tab = [['.' for _ in range(x_size)]for _ in range(y_size)]
for y in range(y_size):
    for x in range(x_size):
        tab[y][x] = read_values[y][x]


x, y, sum = 0, 0, 0
while y < y_size:
    if tab[y][x] == '#':
        sum += 1
    x = (x + 3) % x_size
    y += 1

print(sum)