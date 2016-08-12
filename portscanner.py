import os
import socket
import subprocess
import sys
import threading
import time
from msvcrt import getch
from Queue import Queue

printLock = threading.Lock()
q = Queue()
workers = 256
start = 1
end = 65536
inProgress = False

def forever():
    while not done:
        time.sleep(1)

def maxThreads():
    total = 0
    global done
    done = False
    while True:
        try:
            t = threading.Thread(target = forever)
            t.daemon = True
            t.start()
        except:
            done = True
            return total
        total += 1

def escape():
    global inProgress
    while True:
        if inProgress and ord(getch()) == 27:
            inProgress = False
            q.queue.clear()

def portscan(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn = s.connect((target, port))
        with printLock:
            print port
        conn.close()
    except:
        pass

def threader():
    while True:
        if not inProgress:
            return
        portscan(q.get())
        q.task_done()

def main():
    subprocess.call("title PortScanner", shell = True)
    global target, workers, inProgress
    workers = maxThreads() - 2
    time.sleep(1)
    escapeThread = threading.Thread(target = escape)
    escapeThread.daemon = True
    escapeThread.start()
    while True:
        target = raw_input(">>> ")
        if target == "quit":
            sys.exit()
        if subprocess.call("ping -n 1 -w 3000 " + target, stdout = open(os.devnull, "wb"), stderr = subprocess.STDOUT) == 0:
            inProgress = True
            for i in range(workers):
                t = threading.Thread(target = threader)
                t.daemon = True
                t.start()
            for port in range(start, end):
                q.put(port)
            while not q.empty():
                pass
            inProgress = False
        else:
            print "Failed to connect to the target"

if __name__ == "__main__":
    main()
