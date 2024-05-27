import multiprocessing as mp
import psutil

print(psutil.cpu_count(logical=True))

print(mp.cpu_count())
