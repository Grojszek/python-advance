def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    return [line.strip() for line in lines]


def read_mask(mask_value):
    mask_and = ''
    mask_or = ''
    for element in mask_value:
        mask_and = mask_and + (element if element != 'X' else '1')
        mask_or = mask_or + (element if element != 'X' else '0')
    return {'AND': int(mask_and, 2), 'OR': int(mask_or, 2)}


mem = {}
values = read_input('input.txt')
sum = 0
for element in values:
    key, value_elem = element.split(' = ')
    if key == 'mask':
        mask = read_mask(value_elem)
    else:
        score_value = int(value_elem) | mask['OR']
        score_value = score_value & mask['AND']
        mem[key[4:len(key)-1]] = score_value

for element in mem:
    sum += mem[element]
print(sum)