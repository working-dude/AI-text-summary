import multiprocessing as mp
import threading
import time

def thread_task(name):
    print(f"Thread {name} starting")
    time.sleep(2)
    print(f"Thread {name} finished")

def process_task(name):
    print(f"Process {name} starting")
    threads = []
    for i in range(3):
        t = threading.Thread(target=thread_task, args=(f"{name}-{i}",))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"Process {name} finished in ",time.perf_counter())

if __name__ == '__main__':
    processes = []
    for i in range(2):
        p = mp.Process(target=process_task, args=(f"P{i}",))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("All processes finished")


import multiprocessing as mp
import threading
import time

def process_task(name):
    print(f"Process {name} starting")
    time.sleep(2)
    print(f"Process {name} finished")

def thread_task(name):
    print(f"Thread {name} starting")
    processes = []
    for i in range(2):
        p = mp.Process(target=process_task, args=(f"{name}-{i}",))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(f"Thread {name} finished")

if __name__ == '__main__':
    threads = []
    for i in range(3):
        t = threading.Thread(target=thread_task, args=(f"T{i}",))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("All threads finished")