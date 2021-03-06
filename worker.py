try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser
import io
from koi import koi
import os
import signal
import sys

from signals import signal_term_handler
from functools import partial

from signal import SIG_DFL


class Worker:
    def __init__(self, application, socket):
        self.app = application
        self.socket = socket

    def start(self):
        signal.signal(signal.SIGTERM, SIG_DFL)
        print(f"Worker booted with pid: {os.getpid()}")
        while True:
            body = []
            conn, addr = self.socket.accept()
            http_parser = HttpParser()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    recved = len(data)
                    nparsed = http_parser.execute(data, recved)
                    assert nparsed == recved

                    if http_parser.is_headers_complete():
                        print(http_parser.get_headers())

                    if http_parser.is_partial_body():
                        body.append(http_parser.recv_body())

                    if http_parser.is_message_complete():
                        break

                buffered_body = io.StringIO("".join(body))
                koi(
                    self.app,
                    conn,
                    request_method=http_parser.get_method(),
                    headers=http_parser.get_headers(),
                    body=buffered_body,
                    content_length=http_parser.get_headers().get('content-length',0)
                )
