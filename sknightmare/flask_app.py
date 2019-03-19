from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from restaurant import Restaurant
from gp import run_gp_flask
from queue import Queue
import time
import json
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)


class RestaurantDayQueue(Queue):
    def put(self, report, block=True, timeout=None):

        emit('day_report', report.get_report())
        print(report.get_report())
        super().put(report, block, timeout)


# @app.route('/simulate', methods=['POST'])
# def simulate():
#     layout = request.get_json(force=True)
#     print(layout)
#     r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"])
#     r.simulate(days=int(layout["days"]))
#     return jsonify({"report": r.final_report()})

@app.route('/', methods=['GET'])
def hello():
    return "Welcome to the SKNightmare"


@app.route('/bayesopt', methods=['GET'])
def bayesopt():
    res = run_gp_flask()
    print("RES:", res)
    return json.dumps(res)


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
