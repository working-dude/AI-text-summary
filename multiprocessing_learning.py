"""
This script demonstrates the performance difference between sequential execution and multiprocessing 
for performing heavy mathematical operations on a large list of numbers.
Functions:
    operation1(num): Computes the square root of each number raised to the power of 4 in the given list.
    operation2(num): Computes the square root of each number raised to the power of 5 in the given list.
    operation3(num): Computes the square root of each number raised to the power of 6 in the given list.
Main Execution:
    - Sequential execution of operation1, operation2, and operation3 on a list of 30,000,000 numbers.
    - Multiprocessing execution of the same operations using three separate processes.
    - Prints the time taken for both sequential and multiprocessing executions.
"""
import time
import math
import multiprocessing as mp

#  doing heavy math operation without multiprocessing 
'''
numbers1=[]
numbers2=[]
numbers3=[]

def operation1(num):
    start=time.time()
    for n in num:
        numbers1.append(math.sqrt(n**4))
    end=time.time()
    print("operation 1 time {}".format(int(end-start)))

def operation2(num):
    start=time.time()
    for n in num:
        numbers2.append(math.sqrt(n**5))
    end=time.time()
    print("operation 2 time {}".format(int(end-start)))

def operation3(num):
    start=time.time()
    for n in num:
        numbers3.append(math.sqrt(n**6))
    end=time.time()
    print("operation 3 time {}".format(int(end-start)))

if __name__  == "__main__":
    number_list=list(range(50000000))
    start=time.time()
    operation1(number_list)
    operation2(number_list)
    operation3(number_list)
    end=time.time()
    print("{}".format(int(end-start)))
'''

# Using multiprocessing and creating process for the same tasks above 

'''numbers1=[]
numbers2=[]
numbers3=[]
start=time.time()

def operation1(num):
    # start=time.time()
    for n in num:
        numbers1.append(math.sqrt(n**4))
    end=time.time()
    print("operation 1 time {}".format(int(end-start)))

def operation2(num):
    # start=time.time()
    for n in num:
        numbers2.append(math.sqrt(n**5))
    end=time.time()
    print("operation 2 time {}".format(int(end-start)))

def operation3(num):
    # start=time.time()
    for n in num:
        numbers3.append(math.sqrt(n**6))
    end=time.time()
    print("operation 3 time {}".format(int(end-start)))

if __name__ == "__main__":
    nums=list(range(30000000))
    start=time.time()
    operation1(nums)
    operation2(nums)
    operation3(nums)
    end=time.time()
    print("Time taken to do it normally {}".format(int(end-start)))
    p1=mp.Process(target=operation1,args=(nums,))
    p2=mp.Process(target=operation2,args=(nums,))
    p3=mp.Process(target=operation3,args=(nums,))
    start=time.time()
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
    
    end=time.time()
    print("Total time taken for completion {}".format(int(end-start)))'''