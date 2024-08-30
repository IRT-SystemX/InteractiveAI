import urllib.parse
import time
from flask import Flask, jsonify, request
from flask import render_template, redirect
from flask import url_for, session, g
from flask import Response, stream_with_context
from flask_socketio import SocketIO
from app.models.Communicate import Communicate
from app.models.Simulator import Simulator
from app.models.utils import  generate_graph_html
from config.config import set_pause


class Recommendation:
    """Class to manage recommendations."""

    def __init__(self):
        """Initialize a new Recommendation instance."""
        self.data = {}


Recommend = Recommendation

app = Flask(__name__,template_folder='app/templates')
app.secret_key = 'votre_clé_secrète_ici'
socketio = SocketIO(app)

com = Communicate()
simu = Simulator(socketio)


# def background_thread():
#     """Generate and send the graph periodically."""
#     while True:
#         time.sleep(10)  # Mettre à jour le graphique toutes les 10 secondes
#         graph_html = generate_graph_html(simu.env, simu.obs, socketio)
#         socketio.emit('update_graph', {'html': graph_html})


@app.route("/")
def index():
    """Display the home page."""
    urls = com.get_cab_server_urls()
    return render_template('index.html', urls=urls)


@app.route('/dashboard')
def dashboard():
    """Display the dashboard."""
    # com_tempo = com.outputsConfig['Outputs']['Context']['tempo']
    # Récupérer le nom d'utilisateur
    username = session.get('username', 'Invité')
    server = session.get('server', 'Null')
    # act = session.get('act', None)
    message = session.get('message', '')
    return render_template('dashboard.html',
                           username=username,
                           server=server,
                           config=simu.config,
                           com=com,
                           message=message)


@app.route('/load_simulation')
def load_simulation():
    """Load the simulation."""
    if 'username' in session:
        simu.load_and_edit_config()
        simu.initialize_simulation(com)
        session['message'] = "The simulation is loaded."
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/add_server', methods=['POST'])
def add_server():
    """
    Add a new server to the configuration file.
    
    Expects a JSON with 'url' key. Returns JSON with 'success' if successful.
    """
    new_server_url = request.json.get('url')
    if new_server_url:
        # Ajouter le nouveau serveur à la configuration
        success = com.add_cab_server_url(new_server_url)
        
        if success:
            return jsonify({"success": True})
    
    return jsonify({"success": False})

@app.route('/delete_server', methods=['POST'])
def delete_server():
    """
    Delete a server from the configuration file.
    
    Expects a JSON with 'url' and 'key'. Returns JSON with 'success' status and deleted Url.
    """
    server_url = request.json.get('url')
    if server_url:
        success, deleted_url = com.delete_cab_server_url(server_url)
        return jsonify({"success": success, "deletedUrl": deleted_url})
    return jsonify({"success": False, "deletedUrl": ""})


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        server = request.form['server_url']
        username = request.form['username']
        password = request.form['password']
        com.choose_a_cab_application(urllib.parse.unquote(server))
        is_authorized = com.login(username, password)
        if com.cab_url:
            if is_authorized:
                session['username'] = username
                session['server'] = server
                return redirect(url_for('load_simulation'))
            return redirect(url_for('index',
                                    error="Échec de la connexion. Veuillez réessayer."))
        return redirect(url_for('index',
                                error="Serveur non disponible. Veuillez choisir un autre serveur."))
    return redirect(url_for('index'))


@app.route('/edit_config', methods=['POST'])
def edit_config():
    """Modify the simulation configuration."""
    # session.pop('act', None)
    session.pop('message', None)
    new_params = {
        'env_seed': int(request.form['env_seed']),
        'scenario_name': request.form['scenario_name'],
        'assistant_seed':   int(request.form['assistant_seed']),
    }
    simu.load_and_edit_config(new_params)
    simu.initialize_simulation(com)
    session['message'] = "The simulation is loaded."
    return redirect(url_for('dashboard'))


@app.route('/edit_simulation_settings', methods=['POST'])
def edit_simulation_settings():
    """Modify simulation parameters."""
    # session.pop('act', None)
    session.pop('message', None)
    # Charger et éditer la configuration
    new_params = {
        'refresh_frequency_step': int(request.form['refresh_frequency_step']),
        'time_step_forecast': int(request.form['time_step_forecast']),
        'duration_step_forecast': int(request.form['duration_step_forecast']),
        'step_start_security_analysis': int(request.form['step_start_security_analysis']),
        'stepDuration_s': int(request.form['stepDuration_s']),
        'scenario_first_step': int(request.form['scenario_first_step']),
    }
    new_tempo = int(request.form['tempo'])
    simu.load_and_edit_config(new_params)
    com.edit_parameters('Outputs.Context.tempo', new_tempo)
    simu.initialize_simulation(com)
    # session['act'] = act
    session['message'] = "The simulation is loaded."
    return redirect(url_for('dashboard'))


socketio.start_background_task(simu.run_simulator, com)


@app.route('/start_simulation', methods=['GET'])
def start_simulation():
    """Start the simulation."""
    if 'username' in session:
        if not hasattr(g, 'thread_started') or not g.thread_started:
            # thread = Thread(target=background_thread)
            # thread.start()
            # g.thread_started = True  # Marquer le thread comme démarré

            response = Response(stream_with_context(simu.run_simulator(com)),
                                mimetype='text/event-stream')
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
        return response
    return redirect(url_for('dashboard'))


@app.route('/continue_simulation', methods=['POST'])
def continue_simulation():
    """Resume the simulation after a pause."""
    set_pause(False)
    return "Continued", 200


@app.route('/logout')
def logout():
    """Log out the user."""
    # Effacer les données de session
    session.pop('username', None)
    session.pop('config', None)
    session.pop('act', None)
    session.pop('message', None)
    # Rediriger vers la page de connexion
    return redirect(url_for('index'))


@app.route('/reset_simulation', methods=['POST'])
def reset_simulation():
    """Reset the simulation."""
    simu.initialize_simulation(com)
    return jsonify({"message": "Simulation reset successfully"})


@app.route('/get-last-payloads')
def get_last_payloads():
    """Retrieve the latest payloads."""
    return jsonify(com.list_of_issues)


@app.route('/api/v1/recommendations', methods=['POST'])
def receive_act():
    """Receive recommendations."""
    Recommend.data = request.get_json()
    print(Recommend.data)
    return jsonify({
        "message": "OK"
    })


@app.route('/api/v1/recommendations', methods=['GET'])
def send_act():
    """Send recommendations."""
    act_dict = {}
    act_dict = Recommendation.data
    Recommendation.data = {}
    print(act_dict)
    return jsonify(act_dict)


if __name__ == '__main__':
    socketio.run(app, debug=True)
