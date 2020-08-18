from flask import Blueprint, current_app, Response
import socket

bp = Blueprint("commands", __name__, url_prefix='/api')

def send_request(msg):
    conf = current_app.config
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
        client.sendall(msg.encode('utf8'))
        return client.recv(1024)

@bp.route('/update', methods=['POST'])
def update():
    send_request('u')
    return Response('OK', 200)

@bp.route('/random', methods=['POST'])
def random():
    send_request('d')
    return Response('OK', 200)

@bp.route('/last', methods=['POST'])
def last():
    send_request('l')
    return Response('OK', 200)

@bp.route('/toggle-play', methods=['POST'])
def toggle_play():
    send_request('p')
    return Response('OK', 200)

@bp.route('/next', methods=['POST'])
def next():
    send_request('n')
    return Response('OK', 200)

@bp.route('/repeat', methods=['POST'])
def repeat():
    send_request('r')
    return Response('OK', 200)