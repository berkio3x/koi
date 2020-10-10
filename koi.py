import traceback
import os
import sys

from utils import make_response

def koi(application, conn, body, request_method, path_info=None, query_string=None,
         content_type='Application/json', content_length=None):
    print(f"handled by worker : [ {os.getpid()} ]")

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
