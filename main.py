import socket
import os
from app import application
from app import application
from worker import Worker
from signal import signal, SIGINT, SIGTERM, SIGQUIT, SIGCHLD

from functools import partial

port = 9090
host = "127.0.0.1"

from signals import signal_handler

if __name__ == "__main__":
    r, w = os.pipe()

    s = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((host, port))
    s.listen(1)

    for sig in [SIGINT, SIGTERM, SIGQUIT, SIGCHLD]:
        signal(sig, partial(signal_handler, Worker(application,s)))

    print(f"starting koi server on {host}:{port} with master pid({os.getpid()})")
    workers = 3
    pid = None
    for i in range(workers):
        try:
            if pid != 0:
                pid = os.fork()
        except OSError:
            sys.stderr.write("could not create workers")
    if pid == 0:
        os.close(r)
        Worker(application, s).start()

    os.read(r, 1) # trick master into waiting for its dear childern
    os.close(r)
    sock.close()
