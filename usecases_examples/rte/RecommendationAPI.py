from flask import Flask, jsonify, request

class Recommendation:
    def __init__(self):
        self.data = {}

recommend = Recommendation()

app = Flask(__name__)

@app.route("/")
def home_page():
    return "API for RTE recommendations"


@app.route('/api/v1/recommendations', methods=['POST'])
def receive_act():
    recommend.data = (request.get_json())
    print(recommend.data)
    return jsonify({
        "message" : "OK"
    })

@app.route('/api/v1/recommendations', methods=['GET'])
def send_act():
    act_dict = {}
    act_dict = recommend.data
    recommend.data = {}
    print(act_dict)
    return jsonify(act_dict)



app.run(debug=True, host='0.0.0.0', port=5000)