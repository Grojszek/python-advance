import time
time1 = time.time()
iter1 = 0
while time.time() - time1 < 1:
    iter1 += 1

iter2 = 0
time_start = time.time()
for i in range(1, iter1):
    iter2 += 1
    # pass
time_finish = time.time()
print(time_finish - time_start)
