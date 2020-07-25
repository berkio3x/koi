def application(environ, start_response):
	status = '200 ok'
	response_headers = [('Content-type', 'text/plain')]
	start_response(status, response_headers)
	return ['hello world \n']
