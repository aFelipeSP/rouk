import threading
import time
import traceback

from rouk import create_app
from rouk.player import Player


def run_player(app, event):
    with app.app_context():
        player = Player()

        player.create_server()
        try:
            while not event.is_set():
                time.sleep(0.1)
                player.process()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting player")
        except Exception:
            traceback.print_exc()
        finally:
            player.teardown()

if __name__ == '__main__':

    event = threading.Event()

    app = create_app()
    process = threading.Thread(target=run_player, args=[app, event])
    process.start()
    try:
        app.run(host='0.0.0.0', port=14281)
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting rouk")
    except Exception:
        traceback.print_exc()
    finally:
        event.set()
        process.join()
