import os
import socket
import subprocess
import sys
import thread
import threading
import time
from Queue import Queue

class PortScanError(Exception):
    pass

class PortScanner:
    def __init__(self, target = "127.0.0.1", start = 1, end = 65536, workers = None):
        self.target = target
        self.start = start
        self.end = end
        self.workers = workers
        self.printLock = threading.Lock()
        self.q = Queue()
        self.doneCountingThreads = True
        self.kill = False
        self.ports = []

    def ping(self):
        if subprocess.call("ping -n 1 -w 3000 " + self.target, stdout = open(os.devnull, "wb"), stderr = subprocess.STDOUT) != 0:
            raise PortScanError("failed to connect to the target '" + self.target + "'")
    
    def wait(self):
        while not self.doneCountingThreads:
            time.sleep(1)

    def maxThreads(self):
        total = 0
        self.doneCountingThreads = False
        while True:
            try:
                t = threading.Thread(target = self.wait)
                t.daemon = True
                t.start()
            except:
                self.doneCountingThreads = True
                return total
            total += 1

    def portscan(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn = s.connect((self.target, port))
            with self.printLock:
                self.ports.append(port)
            conn.close()
        except:
            pass

    def threader(self):
        while not self.q.empty() and not self.kill:
            self.portscan(self.q.get())
            self.q.task_done()

    def scan(self):
        self.ping()
        maxthreads = self.maxThreads()
        if self.workers is None:
            self.workers = maxthreads
        elif self.workers > maxthreads:
            self.workers = maxthreads
        time.sleep(1)
        for port in range(self.start, self.end + 1):
            self.q.put(port)
        for _ in range(self.workers):
            try:
                t = threading.Thread(target = self.threader)
                t.daemon = True
                t.start()
            except thread.error:
                pass
        while not self.q.empty() and not self.kill:
            pass
        self.ports.sort()
        return self.ports

    def stop(self):
        self.kill = True

def main():
    subprocess.call("title PortScanner", shell = True)
    while True:
        args = raw_input(">>> ")
        if args == "quit":
            sys.exit()
        args = args.split()
        try:
            if len(args) == 0:
                s = PortScanner()
            elif len(args) == 1:
                s = PortScanner(args[0])
            elif len(args) == 2:
                s = PortScanner(args[0], int(args[1]))
            elif len(args) == 3:
                s = PortScanner(args[0], int(args[1]), int(args[2]))
            elif len(args) >= 4:
                s = PortScanner(args[0], int(args[1]), int(args[2]), int(args[3]))
        except:
            print "ERROR: failed to parse arguments\nUsage: <target (str)> [start (int)] [end (int)] [workers (int)]"
        try:
            ports = s.scan()
        except PortScanError:
            print "ERROR: failed to connect to the target"
        else:
            for p in ports:
                print p

if __name__ == "__main__":
    main()
