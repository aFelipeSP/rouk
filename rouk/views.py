from flask import Blueprint
import socket

bp = Blueprint("api", __name__)

@bp.route("/")
def index():

    if x == b'q': break
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(x.encode('utf8'))
        data = client.recv(1024)
    print('Received', repr(data))