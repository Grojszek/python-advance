def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    values = [line.strip() for line in lines]
    return values


max_row = 127
max_column = 7
read_values = read_input('input.txt')
score = []

for element in read_values:
    row = element[:7].replace('B', '1').replace('F', '0')
    column = element[7:].replace('R', '1').replace('L', '0')
    row_int = int(row, 2)
    column_int = int(column, 2)
    set_id = row_int * 8 + column_int
    score.append({'element': element, 'column': column_int, 'row': row_int, 'id': set_id})

full_seats = [[0 for col in range(0, 8)] for row in range(0, 128)]
for element in score:
    full_seats[element['row']][element['column']] = 1

for x in range(1, 127):
    for y in range(1, 7):
        if full_seats[x][y + 1] == 1 and full_seats[x][y - 1] == 1 and full_seats[x][y] == 0:
            empty_seat_id = x * 8 + y
            break
print(empty_seat_id)
