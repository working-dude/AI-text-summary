#  using synchronos function to execute and calculate the time taken to execute the code
"""
This script demonstrates various methods to execute and measure the time taken for synchronous and asynchronous code execution in Python.

Methods:
1. Synchronous Execution:
    - Uses time.sleep() to simulate code execution.
    - Measures the elapsed time for sequential execution of tasks.

2. Asynchronous Execution:
    - Uses asyncio.sleep() to simulate code execution.
    - Demonstrates basic async/await syntax for sequential execution of tasks.
    - Measures the elapsed time for sequential execution of tasks.

3. Asynchronous Execution with asyncio.create_task:
    - Uses asyncio.create_task() to run tasks concurrently.
    - Measures the elapsed time for concurrent execution of tasks.

4. Asynchronous Execution with asyncio.gather:
    - Uses asyncio.gather() to run tasks concurrently.
    - Measures the elapsed time for concurrent execution of tasks.

5. Asynchronous Execution with asyncio.TaskGroup:
    - Uses asyncio.TaskGroup() to run tasks concurrently.
    - Stops execution if an error occurs in any task.
    - Measures the elapsed time for concurrent execution of tasks.

Each method prints the elapsed time in seconds for the execution of tasks.
"""

import time
'''

def main_sync(t):
    print("Executing code..")
    time.sleep(t)
    print("Code executed..")
    end_seconds = time.time()
    elapsed_seconds = end_seconds - start_seconds
    print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))


start_seconds = time.time()

main_sync(2)
main_sync(3)
main_sync(1)

end_seconds = time.time()
elapsed_seconds = end_seconds - start_seconds
print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))
'''

# using asynchronos function to execute and calculate the time taken to execute the code

import asyncio
'''
async def delayed(t):
    print("Executing code..")
    await asyncio.sleep(t)
    print("Code executed..",t)

    end_seconds = time.time()
    elapsed_seconds = end_seconds - start_seconds
    print("Elapsed time: {}".format(int(elapsed_seconds)))
    return "Done"

async def main_async():
    task1=delayed(2)
    task2=delayed(3)
    result1=await task1
    print(result1)
    result2=await task2
    print(result2)


start_seconds = time.time()
asyncio.run(main_async())
end_seconds = time.time()
elapsed_seconds = end_seconds - start_seconds
print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))'''


# using create task of asyncio to execute the code concurrently   

'''async def tasks(t,id):
    print("Executing code..",id)
    await asyncio.sleep(t)
    print("Code executed..",t)

    end_seconds = time.time()
    elapsed_seconds = end_seconds - start_seconds
    print("Elapsed time: {}".format(int(elapsed_seconds)))
    return "Done "+str(id)

async def main_async():
    task1=asyncio.create_task(tasks(1,1))
    task2=asyncio.create_task(tasks(3,2))
    result2= await task2
    task3=asyncio.create_task(tasks(5,3))
    result1= await task1
    result3= await task3
    print(result1)
    print(result2)
    print(result3)

start_seconds = time.time()

asyncio.run(main_async())
end_seconds = time.time()
elapsed_seconds = end_seconds - start_seconds
print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))
'''

# using gather of asyncio to execute the code concurrently

'''async def tasks(t,id):
    print("Executing code..",id)
    await asyncio.sleep(t)
    print("Code executed..",t)

    end_seconds = time.time()
    elapsed_seconds = end_seconds - start_seconds
    print("Elapsed time: {}".format(int(elapsed_seconds)))
    return "Done "+str(id)

async def main_async():
    results=await asyncio.gather(tasks(1,1),tasks(3,2),tasks(5,3))
    # results= await results
    print(results)

start_seconds = time.time()
asyncio.run(main_async())
end_seconds = time.time()
elapsed_seconds = end_seconds - start_seconds
print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))
'''

#  using taskgroup of asyncio to execute the code concurrently. It blocks one an error 
# is occured and stops further execution unlike above ones
'''
async def task(id,t):
    print("Executing code..",id)
    await asyncio.sleep(t)
    print("Code executed..",t)

    end_seconds = time.time()
    elapsed_seconds = end_seconds - start_seconds
    print("Elapsed time: {}".format(int(elapsed_seconds)))
    return "Done "+str(id)

async def main_async():
    tasks=[]
    async with asyncio.TaskGroup() as tg:
        for i, t in enumerate([1, 3, 5]):
            tasks.append(tg.create_task(task(i + 1, t)))
    # print(tasks)
    results=[task.result() for task in tasks]
    print(results)

start_seconds = time.time()
asyncio.run(main_async())
end_seconds = time.time()
elapsed_seconds = end_seconds - start_seconds
print("Elapsed time in seconds: {}".format(int(elapsed_seconds)))
'''