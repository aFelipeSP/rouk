from flask import current_app
from rouk.db import get_db
import socket

def send_request(msg):
    conf = current_app.config
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
        client.sendall(msg.encode('utf8'))
        return client.recv(1024)