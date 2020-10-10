from flask import Flask

app = application = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return {'message': 'Pong'}


#def application(environ, start_response):
#	status = '200 ok'
#	response_headers = [('Content-type', 'text/plain')]
#	start_response(status, response_headers)
#	return ['hello world \n']
