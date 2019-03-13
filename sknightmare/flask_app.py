from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from restaurant import Restaurant
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)


@app.route('/simulate', methods=['POST'])
def simulate():
    layout = request.get_json(force=True)
    print(layout)
    r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"])
    r.simulate(days=int(layout["days"]))
    return jsonify({"report": r.final_report()})


@socketio.on('connect')
def handle_connect():
    sess = str(time.time())
    emit('session_id', sess)


@socketio.on('simulate')
def socket_simulate(restaurant):
    pass


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
