def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    person = []
    for line in lines:
        person.append(line)
    return read_persons(person)


def read_persons(information):
    persons, person = [], {}
    for i in information:
        if i != '\n':
            i = i.split(' ')
            for x in i:
                key, value = x.split(':')
                person[key] = value.replace('\n', '')
        else:
            person = {}
        persons.append(person)
    return persons


print(read_input('input.txt'))
