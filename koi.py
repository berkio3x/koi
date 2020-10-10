import socket
import array
import traceback
import io

port = 9090
host = "127.0.0.1"

from app import application
import os
import sys

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


def make_response(server, content_type):
    response =  f"HTTP/1.1 200 OK\r\n Server: {server}\r\n Content-Type: {content_type}\r\n"
    response = response.encode('utf8')
    return response


def koi(application, conn, body, request_method, path_info=None, query_string=None,
         content_type='Application/json', content_length=None):
    print(f"accepting from {os.getpid()}")

    environ = dict()

    environ['SERVER_NAME'] = 'koi'
    environ['SERVER_PORT'] = '9090'
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'

    environ['wsgi.version'] = (1, 0)
    environ['wsgi.input'] = body

    if environ.get('HTTPS' , 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    environ['REQUEST_METHOD'] = request_method
    environ['CONTENT_LENGTH'] = content_length
    environ['PATH_INFO'] ="/ping"

    headers_set = []
    headers_sent = []

    def write(data):

        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            status, response_headers = headers_sent[:] = headers_set
            sys.stdout.write("Status: %s\r\n" % status)
            for header in response_headers:
                sys.stdout.write("%s: %s\r\n" % header)
            sys.stdout.write("\r\n")

        print(data,"....response data from applications..", type(data))
        conn.sendall(data)

    def start_response(status, response_headers, exec_info=None):
        if exec_info:
            try:
                if headers_sent:
                    raise (exec_info[0], exec_info[1], exec_info[2])
            finally:
                exec_info = None
        elif headers_set:
            raise AssertionError("Headers already set.")

        headers_set[:] = [status, response_headers]
        return write

    result = []

    try:
        result = application(environ, start_response)
    except Exception as e:
        print(traceback.format_exc())
    else:
        conn.send(make_response('koi',content_type))
        conn.send("\r\n".encode('utf8'))
        for data in result:
            if data:
                conn.send(data)
        if not headers_sent:
            print("")

if __name__ == "__main__":

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)

        print(f"starting koi server on {host}:{port}")

        # workers = 2
        # for i in range(workers):
        #     try:
        #         pid = os.fork()
        #     except OSError:
        #         sys.stderr.write("could not create workers")

        #     if pid == 0:
        #         print(f"Started worker with pid: {os.getpid()}")

        while True:
            body = []
            conn, addr = s.accept()
            http_parser = HttpParser()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # conn.sendall(data)
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
