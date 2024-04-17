from flask_socketio import SocketIO

from flaskr import app



if __name__ == '__main__':
    HOST = "0.0.0.0"
    PORT = 8087
    socketio = SocketIO(app, cors_allowed_origins='*')
    socketio.run(app, HOST, PORT, use_reloader=False, allow_unsafe_werkzeug=True)

