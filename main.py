import socket
import os
from app import application
from worker import worker
from app import application

port = 9090
host = "127.0.0.1"

if __name__ == "__main__":

    r, w = os.pipe()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(f"starting koi server on {host}:{port}")
        workers = 10
        pid = None
        for i in range(workers):
            try:
                if pid != 0:
                    pid = os.fork()
            except OSError:
                sys.stderr.write("could not create workers")
        if pid == 0:
            os.close(r)
            worker(application, s)

    os.read(r, 1) # trick master into waiting for its dear childern
    os.close(r)
