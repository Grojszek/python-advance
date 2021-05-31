def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    num = []
    for line in lines:
        num.append(int(line))
    return result_numbers(num)


def result_numbers(numbers_list: list) -> int:
    year_to_compare = 2020
    for number1 in numbers_list:
        for number2 in numbers_list[1:]:
            if number1 + number2 == year_to_compare:
                return number1 * number2
        numbers_list.pop(0)


numbers = read_input('input.txt')
print(numbers)
