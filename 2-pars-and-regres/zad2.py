import re


def read_input(filename: str) -> list:
    with open(filename, 'r') as read_file:
        lines = read_file.readlines()
    person = []
    for line in lines:
        person.append(line)
    return read_persons(person)


def read_persons(information):
    persons, person = [], {}
    for element in information:
        if element == '\n':
            persons.append(person)
            person = {}
        else:
            element = element.split(' ')
            for iterator in element:
                key_elem, elem_value = iterator.split(':')
                person[key_elem] = elem_value.replace('\n', '')

    persons.append(person)
    return verify_passport(persons)


def verify_passport(all_passports):
    passport_field = ['byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid']
    no_active = []
    active_passports = []
    for single_passport in all_passports:
        for field in passport_field:
            if field not in single_passport:
                no_active.append(single_passport)
                break
        if single_passport not in no_active:
            active_passports.append(single_passport)
    return active_passports


def range_value(elem_value, minimum, maximum):
    try:
        if minimum <= int(elem_value) <= maximum:
            return True
    except ValueError:
        return False
    return False


def byr(year):
    minimum, maximum = 1920, 2002
    return range_value(year, minimum, maximum)


def iyr(year):
    minimum, maximum = 2010, 2020
    return range_value(year, minimum, maximum)


def eyr(year):
    minimum, maximum = 2020, 2030
    return range_value(year, minimum, maximum)


def hgt(field):
    unit = field[-2:]
    elem_value = field[:-2]
    if unit == 'in':
        minimum, maximum = 59, 76
        return range_value(int(elem_value), minimum, maximum)
    if unit == 'cm':
        minimum, maximum = 150, 193
        return range_value(int(elem_value), minimum, maximum)


def hcl(elem_value):
    return bool(re.findall('^#[0-9a-f]{6}$', elem_value))


def ecl(elem_value):
    ecl_possibly_value = {'amb', 'blu', 'brn', 'gry', 'grn', 'hzl', 'oth'}
    return bool(elem_value in ecl_possibly_value)


def pid(elem_value):
    return bool(re.findall('^[0-9]{9}$', elem_value))


def cid(elem_value):
    return bool(elem_value)


passports = read_input('input.txt')
no_active_passports = []
for passport in passports:
    for key in passport.keys():
        if not locals()[key](passport[key]):
            no_active_passports.append(passport)
            break

print(len(passports) - len(no_active_passports))
