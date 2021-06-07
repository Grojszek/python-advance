import timeit

setup = '''
inputs = [i for i in range(100000)]
power_lambda = lambda a,b: a*b
def power(a,b):
    return a*b
'''

first_method = '''
for i in inputs:
    power_lambda(1,4)
'''

second_method = '''
for i in inputs:
    power(1,4)
'''

first_method_del = '''
inputs.pop(0)
'''

second_method_del = '''
del inputs[0]
'''


iterations = 100000
time1 = timeit.timeit(first_method_del, setup=setup, number=iterations)
time2 = timeit.timeit(second_method_del, setup=setup, number=iterations)

print(f'Difference: {((time2-time1)/time2)*100}%')
