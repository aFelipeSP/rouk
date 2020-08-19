from flask import Blueprint, current_app, Response, stream_with_context
import socket

bp = Blueprint("stream", __name__, url_prefix='/api')

@bp.route('/stream')
def stream():
    def fn ():
        try:
            conf = current_app.config
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((conf['PLAYER_HOST'], conf['PLAYER_PORT']))
            client.settimeout(0)
            client.sendall(b'i')
            while True:
                data = ''
                while True:
                    try: data += client.recv(1024).decode('utf8')
                    except: break
                yield 'event:update\ndata:' + data + '\n\n'
        except:
            pass
        finally:
            client.close()

    resp = Response(stream_with_context(fn()))
    resp.headers['Content-Type'] = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'
    return resp