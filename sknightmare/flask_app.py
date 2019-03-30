from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from sknightmare.restaurant import Restaurant
from sknightmare.gp import run_gp_flask
from queue import Queue
import time
import json
import numpy as np
import eventlet
import os

eventlet.monkey_patch()

REDIS_URL = (os.environ.get('REDIS_URL','redis://localhost:6379'))
print(REDIS_URL)


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,message_queue=REDIS_URL,engineio_logger=True)


class RestaurantDayQueue(Queue):
    def __init__(self,room):
        self.room = room
        self.socketio = SocketIO(message_queue=REDIS_URL)
        super().__init__()
    def put(self, report, block=True, timeout=None):
        self.socketio.emit('day_report', report.get_report(),room=self.room)
        #print(report.get_report())
        super().put(report, block, timeout)
        self.socketio.sleep(0)

from celery import Celery


def make_celery(app):
    celery = Celery(
        'flask_app',
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        redis_max_connections=20
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL=REDIS_URL,
    CELERY_RESULT_BACKEND=REDIS_URL
)
celery = make_celery(app)


# @app.route('/simulate', methods=['POST'])
# def simulate():
#     layout = request.get_json(force=True)
#     print(layout)
#     r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"])
#     r.simulate(days=int(layout["days"]))
#     return jsonify({"report": r.final_report()})



@celery.task()
def simulate(restaurant,sid):
    simsocket = SocketIO(message_queue=REDIS_URL)
    layout = json.loads(restaurant)
    print("making rdq here")
    rdq = RestaurantDayQueue(sid)
    print("rdq has been made")
    r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"], layout["staff"], day_log=rdq, verbose=False)
    r.simulate(days=int(layout["days"]))
    report = r.ledger.generate_final_report()
    simsocket.emit("sim_report", report, room=sid)

def int_default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError


@celery.task()
def opt():
    res = run_gp_flask()
    print(res)
    return json.dumps(res, default=int_default)

@app.route('/', methods=['GET'])
def hello():
    return "Welcome to the SKNightmare"


@app.route('/bayesopt', methods=['GET'])
def bayesopt():
    r = opt.delay()
    res = r.wait()
    return res


@socketio.on('connect')
def handle_connect():
    sess = str(time.time())
    emit('session_id', sess)


@socketio.on('simulate')
def socket_simulate(restaurant):
    r = simulate.delay(restaurant,request.sid)
    # report = r.wait()
    # emit("sim_report", report)

@socketio.on('simulate_sock')
def socket_simulate(restaurant):
    report = simulate(restaurant,request.sid)
    emit("sim_report", report)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
