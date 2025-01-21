import threading
"""
This script demonstrates the use of threading in Python to perform multiple tasks concurrently.
It includes three functions: working_out, eating, and sleep, each simulating a time-consuming task.

Functions:
    working_out(): Simulates a workout by sleeping for 3 seconds and then prints a completion message.
    eating(): Simulates eating by sleeping for 4 seconds and then prints a completion message.
    sleep(): Simulates sleeping by sleeping for 6 seconds and then prints a completion message.

The script measures and prints the time taken for each task individually and the total time taken for all tasks.
"""
import time

'''
# function  calling without thread

def working_out():
    time.sleep(3)
    print("Work out completed after 3 sec")

def eating():
    time.sleep(4)
    print("Eating done after 4 sec")

def sleep():
    time.sleep(6)
    print("Sleeping for 6 sec")

start=time.time()

working_out()

# end=time.time()
print("Time taken to workout  {}".format(int(time.time()-start)))

eating()

print("Time taken to eat  {}".format(int(time.time()-start)))

sleep()

print("Time taken to sleep  {}".format(int(time.time()-start)))

end = time.time()

print("Total time taken {}".format(int(end-start)) )

'''

# using threading to make process run in parallel 
'''
def working_out(day):
    time.sleep(3)
    print(f"{day} day completed after 3 sec")
    print("Time taken to working out  {}".format(int(time.time()-start)))

def eating():
    time.sleep(4)
    print("Eating done after 4 sec")
    print("Time taken to eating  {}".format(int(time.time()-start)))

def sleep():
    time.sleep(6)
    print("Sleeping for 6 sec")
    print("Time taken to sleep  {}".format(int(time.time()-start)))
start=time.time()

# print(type(working_out))

task1=threading.Thread(target=working_out,args=("chest",))
task1.start()
task2=threading.Thread(target=eating)
task2.start()
task3=threading.Thread(target=sleep)
# time.sleep(2)
task3.start()
task1.join()
task2.join()
task3.join()
end=time.time()
print("Total time taken  {}".format(int(end-start)))
'''

# using user input while running a thread

'''
done=True
flag=True
def counter():
    count=0
    global flag
    while done:
        count+=1
        time.sleep(1)
        print(count)
    flag=False

def counter2():
    count=0
    while flag:
        count+=1
        time.sleep(1)
        print(count*10)
    print("Exitingggg")

thread_example=threading.Thread(target=counter)
thread_example2=threading.Thread(target=counter2)
thread_example.start()
thread_example2.start()
# thread_example.run()
# counter()

input("Enter something")
done=False'''