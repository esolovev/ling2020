# Простой пример с запуском одного потока

from threading import Thread, get_ident, active_count
from time import sleep


def my_job():
    print("Starting my thread")
    print(f'Now {active_count()} threads are running')
    print(get_ident())
    sleep(3)
    print("Finishing my thread")
    print(f'Now {active_count()} threads are running')


print(f'Now {active_count()} threads are running')
thread = Thread(target=my_job, daemon=True)
print(get_ident())
thread.start()
print('Thread has started')
print(f'Now {active_count()} threads are running')
# thread.join()  # дожидаемся, пока поток завершит свою работу
print('Finish main program')
print(f'Now {active_count()} threads are running')


# Запускаем несколько потоков

from threading import Thread


def my_job(value):
    print(f"Print {value}")

#
# numbers = [x**2 for x in range(10)]
#
# print(numbers)
# exit(0)
threads = [
    Thread(target=my_job, args=(i,)) for i in range(5)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Finish")


# Исправленный пример про некорректное итоговое значение счетчика

import threading
import time
import random


def thread_job():
    global counter

    for i in range(50000):
        with lock:
            counter += 1  # += - не thread-safe операция

threading.Semaphore()
lock = threading.Lock()  # лок можно захватить и отпустить
counter = 0
threads = [threading.Thread(target=thread_job) for _ in range(100)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(counter)  # 50 000 000

# Пример про распараллеливание суммы чисел, показывающий, что вычисления плохо параллелятся потоками

import threading
import random
import time
import typing as tp


def partial_sum(list_part: tp.List[float], partial_sums: tp.List[float]):
    partial_sums.append(sum(list_part))  # append - thread-safe


def faster_sum(my_list: tp.List[float], n_threads: int) -> float:
    assert len(my_list) % n_threads == 0

    part_size = len(my_list) // n_threads

    parts = []

    threads = [
        threading.Thread(target=partial_sum, args=(my_list[i * part_size:(i + 1) * part_size], parts)) #kwargs
        for i in range(n_threads)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return sum(parts)
#
# print(time.time(), time.monotonic())


my_list = [random.uniform(-1, 1) for i in range(10**8)]
print('my_list initialized')

t1 = time.time()
print(sum(my_list))
print(f"sum took {time.time()-t1:.5f} seconds")


t1 = time.time()
n_threads = 1
print(faster_sum(my_list, n_threads))
print(f"faster_sum took {time.time()-t1:.5f} seconds with {n_threads} threads")


t1 = time.time()
n_threads = 5
print(faster_sum(my_list, n_threads))
print(f"faster_sum took {time.time()-t1:.5f} seconds with {n_threads} threads")


t1 = time.time()
n_threads = 10
print(faster_sum(my_list, n_threads))
print(f"faster_sum took {time.time()-t1:.5f} seconds with {n_threads} threads")



# Пример, показывающий, что краулинг веб-страничек хорошо параллелится потоками

import requests
import time
import threading

print(time.time())  # leap seconds; перевод часов
print(time.monotonic())
time.sleep(5)
print(time.monotonic())
exit(0)


urls = [
    'https://www.yandex.ru', 'https://www.google.com',
    'https://habrahabr.ru', 'https://www.python.org',
] * 10


def read_url(url):
    # print(url)
    # print(threading.get_ident())
    return requests.get(url).text

print('One thread')

start = time.time()
for url in urls:
    read_url(url)

print(time.time() - start)



print('Many threads')

start = time.time()
threads = [threading.Thread(target=read_url, args=(url,)) for url in urls]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(time.time() - start)






# Создаем процесс

from multiprocessing import Process
import os


def func(value):
    print(value)
    print(f"It's process {os.getpid()}")
    print(f"My parent process is {os.getppid()}")


if __name__ == '__main__':
    print(f"It's process {os.getpid()}")
    p = Process(target=func, args=('hello',))
    p.start()
    print('Started process')
    p.join()
    print('Joined process')


# Пример, показывающий, что процессы не видят версии объектов из главного процесса, и нужно использовать специальные объекты, которые видны всем процессам

import multiprocessing
# import threading


def worker(lst):
    lst.append('item')
    print(lst)
    return 'item'


if __name__ == "__main__":
    manager = multiprocessing.Manager()

    # LIST = []
    LIST = manager.list()

    processes = [
        multiprocessing.Process(target=worker, args=(LIST,))
        # threading.Thread(target=worker, args=(LIST,))
        for _ in range(5)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print(LIST)


 # Пример работы с multiprocessing.Queue
 
 from multiprocessing import Queue, Process
import time


def run(queue: Queue):
    t1 = time.monotonic()  # время запуска

    while True:
        if time.monotonic() - t1 > 30:  # переписать
            return

        el = queue.get(block=False)
        print(f'Processing {el}')


if __name__ == '__main__':
    queue = Queue()
    process = Process(target=run, args=(queue,))
    process.start()

    for i in range(10):
        queue.put(i)
        time.sleep(2)



# Пример работы с пулом процессов

from multiprocessing import Pool


def power(value):
    return value**10


if __name__ == '__main__':
    values = [i for i in range(10000)]
    # results = [power(i) for i in values]
    # results = list(map(power, values))

    pool = Pool(processes=4)
    results = pool.map(power, values)
    print(results[5000:5100])
