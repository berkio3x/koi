try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser
import io
from koi import koi


def worker(application, socket):
    while True:
        body = []
        conn, addr = socket.accept()
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
                application,
                conn,
                body=buffered_body,
                request_method=http_parser.get_method(),
                content_length=http_parser.get_headers().get('content-length',0)
            )
