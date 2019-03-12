from flask import Flask, request, jsonify
from flask_cors import CORS
from restaurant import Restaurant
app = Flask(__name__)
CORS(app)
@app.route('/simulate', methods=['POST'])
def simulate():
    layout = request.get_json(force=True)
    print(layout)
    r = Restaurant("Sophie's Kitchen", layout["equipment"], layout["tables"])
    r.simulate(days=int(layout["days"]))
    return jsonify({"report":r.final_report()})
    

if __name__ == "__main__":
    app.run()