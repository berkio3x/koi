import sys
import os
from signal import SIGCHLD

def signal_term_handler(app, signal, frame):
    print ('got SIGTERM')
    sys.exit(0)

def signal_handler(worker, signal, frame):

    print("Got a request to kill the child from parent:(")
    if signal == SIGCHLD:
        pid, status = os.waitpid(-1, os.WNOHANG|os.WUNTRACED|os.WCONTINUED)
        if os.WIFCONTINUED(status) or os.WIFSTOPPED(status):
            return
        if os.WIFSIGNALED(status) or os.WIFEXITED(status):
            worker.start()
    sys.exit(0)
