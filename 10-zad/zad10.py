import os
import logging


def read_input(filename):
    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
    with open(input_path, 'r') as read_file:
        lines = read_file.readlines()
    input_values = [line.strip() for line in lines]
    return input_values


def count_trees(tree_map, x_pointer, y_pointer):
    x_size = len(tree_map[0])
    y_size = len(tree_map)
    x, y, tree_sum = 0, 0, 0
    for y in range(0, y_size, y_pointer):
        if tree_map[y][x] == '#':
            tree_sum += 1
        x = (x + x_pointer) % x_size
    return tree_sum


message_format = '%(asctime)s: %(message)s'
logging.basicConfig(format=message_format, level=logging.INFO, datefmt='%H:%M:%S')

tree_map = read_input('input.txt')
moves = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]
trees_number = 1
for step in moves:
    trees_number *= count_trees(tree_map, *step)

logging.info(f'Total number trees: {trees_number}')
