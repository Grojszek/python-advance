def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    values = []
    one_type = []
    for line in lines:
        if line == '\n':
            values.append(one_type)
            one_type = []
        else:
            one_type.append(line.replace('\n', ''))
    values.append(one_type)
    return values


def parsing_rules(rules):
    rules_value = {}
    for element in rules:
        key, elem_value = element.split(': ')
        range1, range2 = elem_value.split(' or ')
        min1, max1 = range1.split('-')
        min2, max2 = range2.split('-')
        elem_value = {'min1': int(min1), 'max1': int(max1), 'min2': int(min2), 'max2': int(max2)}
        rules_value[key] = elem_value
    return rules_value


def parsing_tickets(values):
    ticket_elements = []
    for element in values:
        if element != 'nearby tickets:' and element != 'your ticket:':
            ticket = element.split(',')
            ticket_elements.append(ticket)
    return ticket_elements


read_values = read_input('input.txt')
rules = parsing_rules(read_values[0])
my_ticket = parsing_tickets(read_values[1])
tickets = parsing_tickets(read_values[2])
wrong_elem = []
sum = 0
for element in tickets:
    for i in element:
        in_rules = False
        value = int(i)
        for rule in rules:
            if (rules[rule]['min1'] <= value <= rules[rule]['max1']) or \
                    (rules[rule]['min2'] <= value <= rules[rule]['max2']):
                in_rules = True
                break
        if not in_rules:
            sum += value
            wrong_elem.append(value)
            break
print(sum)