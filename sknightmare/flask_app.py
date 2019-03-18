from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from restaurant import Restaurant
from queue import Queue
import time
import json
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)


class RestaurantDayQueue(Queue):
    def put(self, report, block=True, timeout=None):
        print(report)
        emit('day_report', report.get_report())
        super().put(report, block, timeout)


<<<<<<< HEAD
@app.route('/', methods=['GET'])
def hello():
    return("Welcome to the SKNightmare!")
=======
>>>>>>> 4dc0e62a3eafdb29355c247dcfd3beb84208ca2a
# @app.route('/simulate', methods=['POST'])
# def simulate():
#     layout = request.get_json(force=True)
#     print(layout)
#     r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"])
#     r.simulate(days=int(layout["days"]))
#     return jsonify({"report": r.final_report()})
<<<<<<< HEAD
=======

@app.route('/', methods=['GET'])
def hello():
    return "Welcome to the SKNightmare"
>>>>>>> 4dc0e62a3eafdb29355c247dcfd3beb84208ca2a


@socketio.on('connect')
def handle_connect():
    sess = str(time.time())
    emit('session_id', sess)


@socketio.on('simulate')
def socket_simulate(restaurant):
    layout = json.loads(restaurant)
    rdq = RestaurantDayQueue()
    r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"], layout["staff"], day_log=rdq)
    r.simulate(days=int(layout["days"]))
    emit("sim_report", r.ledger.generate_final_report())


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
