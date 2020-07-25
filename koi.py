import socket
port = 9090
host = '127.0.0.1'

from app import application
import os
import sys

def koi(application, conn):

	environ = {}
	headers_set = []
	headers_sent = []

	def write(data):
		
		if not headers_set:
			raise AssertionError('write() before start_response()')
		
		elif not headers_sent:
			status, response_headers = headers_sent[:] = headers_set
			sys.stdout.write('Status: %s\r\n' % status)
			for header in response_headers:
				sys.stdout.write('%s: %s\r\n'% header)
			sys.stdout.write('\r\n')

		conn.sendall(data.encode('utf8'))

	def start_response(status, response_headers, exec_info=None):
		if exec_info:
			try:
				if headers_sent:
					raise (exec_info[0], exec_info[1], exec_info[2])
			finally:
				exec_info = None
		elif headers_set:
			raise AssertionError('Headers already set.')

		headers_set[:] = [status, response_headers]
		return write

	result = application(environ, start_response)
	print(result)

	try:
		for data in result:
			if data:
				write(data)
		if not headers_sent:
			write('')
	finally:
		if hasattr(result, 'close'):
			result.close()


if __name__ == '__main__':

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((host, port))
		s.listen(1)
		print(f'starting koi server on {host}:{port}')
		conn , addr = s.accept()		
		with conn:
			print(f"connected by addr {addr}")
			koi(application, conn)
			while True:
				data = conn.recv(1024)
				# if not data:break
				# conn.sendall(data)
