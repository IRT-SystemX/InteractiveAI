from flask import Flask, jsonify, request

class Recommendation:
    def __init__(self):
        self.data = {}

recommend = Recommendation()

app = Flask(__name__)

@app.after_request

def add_cors_headers(response):
    """Allow the CAB frontend to POST applied recommendations cross-origin.

    Without these headers the browser's preflight OPTIONS succeeds but the actual
    POST is blocked by CORS. Prefer the nginx same-origin proxy (/powergrid-simu/)
    where possible; these headers only matter for direct plain-HTTP calls.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route("/")
def home_page():
    return "API for PowerGrid recommendations"


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