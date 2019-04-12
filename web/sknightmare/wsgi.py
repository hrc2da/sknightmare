from flask_app import socketio, app

if __name__ == "__main__":
    print("legooo")
    socketio.run(app, host='0.0.0.0')
