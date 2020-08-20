from flask import Blueprint, current_app, Response, stream_with_context
import socket

bp = Blueprint("stream", __name__, url_prefix='/api')

@bp.route('/stream')
def stream():
    def fn ():
        conf = current_app.config
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
        client.sendall(b'i')
        try:
            while True:
                data = client.recv(4096).decode('utf8')
                yield 'event:update\ndata:' + data + '\n\n'
        except:
            pass
        finally:
            yield 'event:end\n\n'
            client.close()

    return Response(stream_with_context(fn()), headers={
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    })