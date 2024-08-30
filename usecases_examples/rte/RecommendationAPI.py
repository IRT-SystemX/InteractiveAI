from flask import Flask, jsonify, request

class Recommendation:
    def __init__(self):
        self.data = {}

Recommend = Recommendation

app = Flask(__name__)

@app.route("/")
def home_page():
    return "API for RTE recommendations"


@app.route('/api/v1/recommendations', methods=['POST'])
def receive_act():
    Recommend.data = (request.get_json())
    print(Recommend.data)
    return jsonify({
        "message" : "OK"
    })

@app.route('/api/v1/recommendations', methods=['GET'])
def send_act():
    act_dict = {}
    act_dict = Recommend.data
    Recommend.data = {}
    print(act_dict)
    return jsonify(act_dict)



app.run(debug=True)