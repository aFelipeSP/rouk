from flask import Blueprint, current_app, Response, stream_with_context
import socket

bp = Blueprint("stream", __name__, url_prefix='/api')

@bp.route('/stream')
def stream():
    def fn ():
        client = None
        try:
            conf = current_app.config
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
            client.sendall(b'i')
            while True:
                data = client.recv(4096).decode('utf8')
                if data == 'end' or data == '' or data == None: break
                yield 'event:update\ndata:' + data + '\n\n'
        except:
            pass
        finally:
            if client:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except:
                    pass
            yield 'event:close\n\n'

    return Response(stream_with_context(fn()), headers={
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache'
    })