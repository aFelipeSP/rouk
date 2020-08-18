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
            client.sendall(b'i')
            while True:
                data = client.recv(1024).decode('utf8')
                # while True:
                #     data_ = client.recv(1024)
                #     if not data_: break
                #     data += data_.decode('utf8')
                yield 'event:' + data[0] + '\ndata:' + data[2:] + '\n\n'
        except:
            pass
        finally:
            client.close()

    resp = Response(stream_with_context(fn()))
    resp.headers['Content-Type'] = 'text/event-stream'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Connection'] = 'keep-alive'
    return resp