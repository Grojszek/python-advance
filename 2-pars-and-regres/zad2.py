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
    for i in information:
        if i != '\n':
            i = i.split(' ')
            for x in i:
                key, value = x.split(':')
                person[key] = value.replace('\n', '')
        else:
            persons.append(person)
            person = {}
    persons.append(person)
    return verify_correctnes_fields(persons)


def verify_passport(passports):
    passport_field = ['byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid']
    no_active_passports = []
    for i in passports:
        for field in passport_field:
            try:
                i[field]
            except KeyError:
                no_active_passports.append(i)
                break
    return len(passports) - len(no_active_passports)


def year(year, min, max):
    try:
        if 1920 <= int(year) <= 2002:
            return True
    except ValueError:
        return False
    return False


def byr(year):
    year(year, 1920, 2002)


def iyr(year):
    year(year, 2010, 2020)


def eyr(year):
    year(year, 2020, 2030)


def hgt(field):
    unit = field[-2:]
    value = field[:-2]
    try:
        if unit == 'in' and 59 <= int(value) <= 76:
            return True
        if unit =='cm' and 170 <= int(value) <= 195:
            return True
    except ValueError:
        return False
    return False


def verify_correctnes_fields(passports):
    no_active_passports =[]
    for i in passports:
        for field in i:
            if field == 'hgt':
                unit = i[field][-2:]
                value = i[field][:-2]


    return no_active_passports


print(read_input('input.txt'))
