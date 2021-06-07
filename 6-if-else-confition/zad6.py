def read_input(filename):
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    input_values = [line.strip() for line in lines]
    return parsing_value(input_values)


def parsing_value(input_value):
    instruction = []
    for element in input_value:
        operation, value_elem = element.split(' ')
        instruction.append({'oper': operation, 'value': value_elem})
    return instruction


def operation_parse(input_value, acc, element_number):
    operation = input_value[element_number]['oper']
    sign = input_value[element_number]['value'][:1]
    value_elem = int(input_value[element_number]['value'][1:])
    if operation == 'nop':
        element_number += 1
    elif operation == 'acc':
        element_number += 1
        if sign == '+':
            acc += value_elem
        else:
            acc -= value_elem
    elif operation == 'jmp':
        if sign == '+':
            element_number += value_elem
        else:
            element_number -= value_elem
    return acc, element_number


input_information = read_input('input.txt')
elements = []
element_number = 0
acc = 0
while element_number not in elements:
    elements.append(element_number)
    acc, element_number = operation_parse(input_information, acc, element_number)

print(acc)
