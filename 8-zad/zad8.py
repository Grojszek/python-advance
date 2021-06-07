def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        cube = [[[element for element in line.strip()] for line in read_file.readlines()]]
    return cube


def create_empty_cube(x_size: int, y_size: int, z_size: int):
    return [[['.' for _ in range(x_size)] for _ in range(y_size)] for _ in range(z_size)]


def inject_initial_layer(initial_layer, cube):
    for y in range(len(initial_layer[0])):
        for x in range(len(initial_layer[0][0])):
            cube[cycles][cycles + y][cycles + x] = initial_layer[0][y][x]


cycles = 6
init_layer = read_input('input.txt')
xy_size = cycles * 2 + len(init_layer[0])
z_size = cycles * 2 + 1
unit_vector = [-1, 0, 1]

new_cube = create_empty_cube(xy_size, xy_size, z_size)
copy_cube = create_empty_cube(xy_size, xy_size, z_size)
inject_initial_layer(init_layer, new_cube)
inject_initial_layer(init_layer, copy_cube)




