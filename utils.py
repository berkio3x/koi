def make_response(server, content_type):
    response =  f"HTTP/1.1 200 OK\r\n Server: {server}\r\n Content-Type: {content_type}\r\n"
    response = response.encode('utf8')
    return response
