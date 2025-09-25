import time
from datetime import datetime, timedelta, timezone
import grid2op
from grid2op.Chronics.handlers import PerfectForecastHandler, CSVHandler
from grid2op.Agent import recoPowerlineAgent
from grid2op.Chronics import FromHandlers
from lightsim2grid import LightSimBackend
import numpy as np
import toml
import json
import matplotlib
matplotlib.use('agg')
from app.models.Listener import Listener
from config.config import logging, set_pause, get_pause_status
from app.models.utils import (create_observation_image, get_alert_lines, search_chronic_num_from_name,
                   get_curent_lines_in_bad_kpi, get_curent_lines_lost,
                   get_zone_where_alarm_occured, expand_act_from_cab,
                   load_assistant, local_xd_silly, targeted_scenario_act_fixed, generate_graph_html)

BkClass = LightSimBackend


class Simulator:
    """Class to manage the PowerGrid simulation environment and interactions."""

    def __init__(self, socketio):
        """
        Initialize the Simulator instance.

        Args:
            socketio: The SocketIO instance for real-time communication.
        """
        self.config = {}
        self.env = None
        self.obs = None
        self.act = None
        self.listen = None
        self.local_assistant = None
        self.com = None
        self.agent_reco = None
        self.socketio = socketio

    def load_and_edit_config(self, params=None):
        """
        Load and optionally edit the configuration from a TOML file.

        Args:
            params (dict, optional): New parameters to update the configuration.
        """
        config_path = "config/CONFIG.toml"
        self.config = toml.load(config_path)
        if params:
            # Mettre à jour le fichier de configuration avec les nouveaux paramètres
            self.config.update(params)
            with open(config_path, 'w', encoding='utf-8') as config_file:
                toml.dump(self.config, config_file)

    def initialize_simulation(self, com, session):
        """
        Initialize the simulation with configuration parameters.

        Args:
            com: Communication object for interacting with the environment.
            session: Flask session object for storing messages.

        Returns:
            grid2op.Action.BaseAction: Initial action for the simulation.
        """
        if 'message' not in session or not isinstance(session['message'], list):
            session['message'] = []

        forecasts_horizons = [5, 10, 15, 20, 25, 30]
        self.env = grid2op.make(self.config['env_name'],
                                backend=BkClass(),
                                data_feeding_kwargs={
                                    "gridvalueClass": FromHandlers,
                                    "gen_p_handler": CSVHandler("prod_p"),
                                    "load_p_handler": CSVHandler("load_p"),
                                    "gen_v_handler": CSVHandler("prod_v"),
                                    "load_q_handler": CSVHandler("load_q"),
                                    "h_forecast": forecasts_horizons,
                                    "gen_p_for_handler": PerfectForecastHandler(
                                        "prod_p_forecasted"),
                                    "load_p_for_handler": PerfectForecastHandler(
                                        "load_p_forecasted"),
                                    "load_q_for_handler": PerfectForecastHandler(
                                        "load_q_forecasted")})
        self.env.seed(int(self.config['env_seed']))
        id_scenario = search_chronic_num_from_name(
            self.config['scenario_name'], self.env)
        self.env.set_id(id_scenario)  # Scenario choice
        self.obs = self.env.reset()
        logging.info("Le scénario chargé est : %s \n",
                    self.env.chronics_handler.get_name())
        session['message'].append(f"Le scénario chargé est : {self.env.chronics_handler.get_name()}")

        assistant_path = self.config['assistant_path']
        assistant_seed = int(self.config['assistant_seed'])
        self.local_assistant = load_assistant(
            assistant_path, assistant_seed, self.env)

        self.agent_reco = recoPowerlineAgent.RecoPowerlineAgent(
            self.env.action_space)
        act = self.agent_reco.act(self.obs, 0)

        # Update simulation parameters
        try:
            scenario_first_step = self.config['scenario_first_step']
            com.push_step = scenario_first_step
        except Exception as e:
            logging.error(e)

        logging.info("Le scénario est chargé.\n")
        session['message'].append("Le scénario est chargé.")
        self.listen = Listener(self.obs)
        return act

    def run_simulator(self, com):
        """
        Run the PowerGrid simulator.

        This function manages the main simulation loop, handling events, 
        updating observations, and interacting with the InteractiveAI system.

        Args:
            com: Communication object for interacting with the environment.

        Yields:
            str: Status updates and messages for the simulation interface.
        """
        paris_timezone = timezone(timedelta(hours=2))
        date = datetime.now(paris_timezone)
        # date = datetime.now(timezone.utc)
        send_tempo = com.outputs_config['Outputs']['Context']['tempo']
        step_start_security_analysis = self.config['step_start_security_analysis']
        event_resolved_trigger = True
        done = False
        silent_mode_msg_trigger = True
        step_counter = 0
        clear_parade_flag = False

        while not done:
            context_date = date + timedelta(minutes=float(5))*step_counter
            img_b64_current = None
            img_b64_forecast = None

            # Pour corriger la valeur de act à certain pas précis
            # en vue d'avoir notre scénario cible
            act_fixed, _ = targeted_scenario_act_fixed(self.env, self.obs)
            if act_fixed is not None:
                act = act_fixed

            # Begining of steps : Observation updates
            self.obs, _, done, _ = self.env.step(act)

            # Vider le div des parades
            if self.obs.current_step >= self.config['scenario_first_step'] and clear_parade_flag:
                empty_message = {
                    "title": "",
                    "description": ""
                }
                yield f"data: {{\"div\": \"actions-div\", \"content\": {json.dumps(empty_message)}}}\n\n"
                clear_parade_flag = False

            if self.obs.current_step >= self.config['scenario_first_step']:
                # Pour l'affichage du graphique dans le simulateur
                graph_html = generate_graph_html(self.env,
                                    self.obs)
                # print("Contenu du graphique:", graph_html[:200]) 
                self.socketio.emit('update_graph',
                                    {'data': graph_html})
                

            # To handle between "silent mode" and "stream simulation" (with or without InteractiveAI)
            # (The stream simulation starts at step scenario_first_step)
            if self.obs.current_step >= self.config['scenario_first_step']:
                logging.info("Pas de simulation : %s",
                             self.obs.current_step)
                yield (
                    f"data: {{\"div\": \"status-div\", \"content\": "
                    f"\"Pas de simulation : {self.obs.current_step}\"}}\n\n"
                )
            elif self.obs.current_step == self.config['scenario_first_step'] - 1:
                print("\n")
                logging.info("Le simulateur est à présent connecté à InteractiveAI.\n")
                message = {
                    "div": "message-container",
                    "content": "Le simulateur est à présent connecté à InteractiveAI."
                }
                yield f"data: {json.dumps(message)}\n\n"
                silent_mode_msg_trigger = False
            else:
                if silent_mode_msg_trigger:
                    logging.info('Status: Le scénario se déroule en arrière plan.\n'
                                 'Le simulateur va se connecter à InteractiveAI à partir du pas : %s',
                                 self.config['scenario_first_step'])
                    message = (
                        f"Status: Le scénario se déroule en arrière plan.\n"
                        f"Le simulateur va se connecter à InteractiveAI à partir du pas : "
                        f"{self.config['scenario_first_step']} (Voir les paramètres de configuration)"
                    )
                    yield f"data: {{ \"div\": \"status-div\", \"content\": {json.dumps(message)} }}\n\n"
                    silent_mode_msg_trigger = False
                if self.obs.current_step % 50 == 0:
                    print("step",
                          self.obs.current_step, end="",
                          flush=True)
                elif self.obs.current_step % 10 == 0:
                    print(' ... ',
                          end="",
                          flush=True)
                    # time.sleep(config['stepDuration_s']/10)

            # To handle end of event card and event followup
            com.send_issues_ending_online(self.config['stepDuration_s'],
                                          context_date)

            # Forecast events checking
            obs_forecast = None
            f_env = None
            if self.obs.current_step == step_start_security_analysis:
                step_start_security_analysis = (
                    self.obs.current_step +
                    self.config['refresh_frequency_step']
                )
                # pour dans 15 min (time_step_forecast=3)
                obs_forecast, *_ = self.obs.simulate(self.env.action_space(),
                                                     self.config['time_step_forecast'])
                f_env = obs_forecast._obs_env

            # Added to send context online sequentialy
            if self.obs.current_step >= self.config['scenario_first_step']:
                context_just_sent = False
                if (self.obs.current_step == com.push_step or event_resolved_trigger) \
                        and com.cab_api_on:
                    com.push_step = self.obs.current_step + send_tempo
                    img_b64_current = create_observation_image(
                        self.env,
                        self.obs)
                    if img_b64_current:
                        com.send_context_online(self.obs,
                                                self.config['scenario_first_step'],
                                                context_date,
                                                img_b64_current)
                        event_resolved_trigger = False
                        context_just_sent = True

            if self.listen.stop_for_issue_state(self.obs,
                                                obs_forecast,
                                                f_env,
                                                self.env._opponent._lines_ids):
                # logging.info("An alarm is raised")

                # -------------------------------------------------------------------
                if "Overload" in self.listen.current_issues:
                    if self.obs.current_step >= self.config['scenario_first_step']:

                        com.push_step = self.obs.current_step + send_tempo
                        if com.cab_api_on is True and context_just_sent is False:
                            if not img_b64_current:
                                img_b64_current = create_observation_image(self.env,
                                                                           self.obs)
                            if img_b64_current:
                                com.send_context_online(self.obs,
                                                        self.config['scenario_first_step'],
                                                        context_date,
                                                        img_b64_current)
                                context_just_sent = True

                        logging.info("Status: Il y a une surcharge sur le réseau")
                        message = {
                            "div": "message-container",
                            "content": "Status: Il y a une surcharge sur le réseau"
                        }
                        yield f"data: {json.dumps(message)}\n\n"
                        yield (
                            f"data: {{\"div\": \"events-div\", \"content\": {{ \"title\": "
                            f"\"Status: Il y a une surcharge sur la ligne "
                            f"{get_curent_lines_in_bad_kpi(self.obs)}\" , "
                            f"\"description\": \"La surcharge est de "
                            f"{np.round(np.float64(self.obs.rho.max()*100),decimals=1,out=None)}%\""
                            f" }}}}\n\n"
                        )

                        if not img_b64_current:
                            img_b64_current = create_observation_image(self.env,
                                                                       self.obs)
                        com.send_event_online(context_date,
                                              self.config['scenario_first_step'],
                                              self.listen.trigger_kpis(
                                                  self.obs, act),
                                              self.obs, self.listen.current_issues,
                                              img_b64_current,
                                              line_name=get_curent_lines_in_bad_kpi(
                                                  self.obs),
                                              case_overload=True)
                        
                    if (self.obs.current_step < self.config['scenario_first_step']) or (com.cab_api_on is False):
                        # Utiliser XD_Silly en cache (en local)
                        act = local_xd_silly(self.obs, self.local_assistant)
                        if com.cab_api_on is False:
                            logging.info("Parade : %s", act)
                            parade_message = {
                                "title": "Parade",
                                "description": f"{str(act)}"
                            }
                            yield f"data: {{\"div\": \"actions-div\", \"content\": {json.dumps(parade_message)}}}\n\n"
                            clear_parade_flag = True

                    else:
                        # Récuperer les parades de InteractiveAI
                        yield from com.get_act_from_api()
                        act = expand_act_from_cab(self.env, com.act_dict)
                        logging.info("Parade : %s", act)
                        parade_message = {
                                "title": "Parade",
                                "description": f"{str(act)}"
                            }
                        yield f"data: {{\"div\": \"actions-div\", \"content\": {json.dumps(parade_message)}}}\n\n"
                        clear_parade_flag = True

                    event_resolved_trigger = True

                if "Assistant raised an alarm" in self.listen.current_issues:
                    if self.obs.current_step >= self.config['scenario_first_step']:

                        com.push_step = self.obs.current_step + send_tempo
                        if com.cab_api_on is True and context_just_sent is False:
                            if not img_b64_current:
                                img_b64_current = create_observation_image(self.env,
                                                                           self.obs)
                            if img_b64_current:
                                com.send_context_online(self.obs,
                                                        self.config['scenario_first_step'],
                                                        context_date,
                                                        img_b64_current)
                                context_just_sent = True

                        logging.info("Status: Il y a une alarme de l'agent IA")
                        yield (
                            "data: {\"div\": \"events-div\", \"content\": "
                            "{ \"title\": \"Status: Il y a une alerte de l'agent IA\", "
                            "\"description\": \"\" } }\n\n"
                        )

                        if not img_b64_current:
                            img_b64_current = create_observation_image(self.env,
                                                                       self.obs)
                        com.send_event_online(context_date,
                                              self.config['scenario_first_step'],
                                              self.listen.trigger_kpis(self.obs, act),
                                              self.obs,
                                              self.listen.current_issues,
                                              img_b64_current,
                                              zone=get_zone_where_alarm_occured(
                                                  self.obs),
                                              case_assist_alarm=True)
                        event_resolved_trigger = True

                if "Assistant raised an alert" in self.listen.current_issues:
                    if self.obs.current_step >= self.config['scenario_first_step']:

                        com.push_step = self.obs.current_step + send_tempo
                        if com.cab_api_on is True and context_just_sent is False:
                            if not img_b64_current:
                                img_b64_current = create_observation_image(self.env,
                                                                           self.obs)
                            if img_b64_current:
                                com.send_context_online(self.obs,
                                                        self.config['scenario_first_step'],
                                                        context_date,
                                                        img_b64_current)
                                context_just_sent = True

                        logging.info("Status: Il y a une alerte de l'agent IA")
                        yield (
                            "data: {\"div\": \"events-div\", \"content\": "
                            "{ \"title\": \"Status: Il y a une alerte de l'agent IA\", "
                            "\"description\": \"\" } }\n\n"
                        )

                        if not img_b64_current:
                            img_b64_current = create_observation_image(self.env,
                                                                       self.obs)
                        com.send_event_online(context_date,
                                              self.config['scenario_first_step'],
                                              self.listen.trigger_kpis(self.obs, act),
                                              self.obs,
                                              self.listen.current_issues,
                                              img_b64_current,
                                              line=get_alert_lines(self.obs),
                                              case_assist_alert=True)
                        event_resolved_trigger = True

                if "Anticipation N-1" in self.listen.current_issues:
                    if self.obs.current_step >= self.config['scenario_first_step']:
                        com.push_step = self.obs.current_step + send_tempo
                        if com.cab_api_on is True and context_just_sent is False:
                            if not img_b64_current:
                                img_b64_current = create_observation_image(self.env,
                                                                           self.obs)
                            if img_b64_current:
                                com.send_context_online(self.obs,
                                                        self.config['scenario_first_step'],
                                                        context_date,
                                                        img_b64_current)
                                context_just_sent = True

                        logging.info(
                            "Status: Il y a un événement de type 'anticipation N-1' ")
                        message = {
                            "div": "message-container",
                            "content": "Status: Il y a un événement de type 'anticipation N-1' "
                        }
                        yield f"data: {json.dumps(message)}\n\n"

                        for x in self.listen.anticipation:
                            logging.info(
                                "Il y a un événement d'anticipation de perte de ligne %s", x)
                            yield (
                                f"data: {{\"div\": \"events-div\", \"content\": "
                                f"{{ \"title\": \"Il y a un événement d'anticipation de perte de ligne\", "
                                f"\"description\": \"{x}\"}} }}\n\n"
                            )

                            n_1_line_name = x[0].split(":")[-1]
                            n_1_line_id = self.obs.name_line.tolist().index(n_1_line_name)
                            obs_forecast_n_1, *_ = self.obs.simulate(self.env.action_space({"set_line_status":[(n_1_line_id,-1)]}), self.config['time_step_forecast'])
                            img_b64_forecast = create_observation_image(obs_forecast_n_1._obs_env,
                                                                        obs_forecast_n_1)
                            com.send_event_online(context_date,
                                                  self.config['scenario_first_step'],
                                                  self.listen.trigger_kpis(
                                                      self.obs,
                                                      self.env.action_space()),
                                                  obs_forecast,
                                                  self.listen.current_issues,
                                                  img_b64_forecast,
                                                  line=x,
                                                  duration=self.config['duration_step_forecast'],
                                                  case_anticip=True)
                        event_resolved_trigger = True
                        obs_forecast = None
                        if self.obs.current_step >= self.config['scenario_first_step']:
                            message = {
                                "div": "message-container",
                                "content": "La simulation est en pause."
                            }
                            yield f"data: {json.dumps(message)}\n\n"
                            yield (
                                "data: {\"div\": \"status-div\", \"content\": "
                                "\"Cliquez sur 'Continuer' pour poursuivre la simulation.\"}\n\n"
                            )
                            set_pause(True)
                            while get_pause_status():
                                time.sleep(1)

                if "Line lost" in self.listen.current_issues:
                    if self.obs.current_step >= self.config['scenario_first_step']:

                        com.push_step = self.obs.current_step + send_tempo
                        if com.cab_api_on is True and context_just_sent is False:
                            if not img_b64_current:
                                img_b64_current = create_observation_image(self.env,
                                                                           self.obs)
                            if img_b64_current:
                                com.send_context_online(self.obs,
                                                        self.config['scenario_first_step'],
                                                        context_date,
                                                        img_b64_current)
                                context_just_sent = True

                        logging.info("Status: Il y a une perte de ligne %s",
                                     get_curent_lines_lost(self.obs))
                        
                        logging.info(
                            "Status: Il y a un événement de type 'perte de ligne' ")
                        message = {
                            "div": "message-container",
                            "content": "Status: Il y a une perte de ligne ' "
                        }
                        yield f"data: {json.dumps(message)}\n\n"
                        yield (
                            f"data: {{\"div\": \"events-div\", \"content\": "
                            f"{{ \"title\": \"Status: Il y a une perte de ligne \" , "
                            f"\"description\": \"{get_curent_lines_lost(self.obs)}\" }}}}\n\n"
                        )

                        if not img_b64_current:
                            img_b64_current = create_observation_image(self.env,
                                                                       self.obs)
                        com.send_event_online(context_date,
                                              self.config['scenario_first_step'],
                                              self.listen.trigger_kpis(
                                                  self.obs, act),
                                              self.obs,
                                              self.listen.current_issues,
                                              img_b64_current,
                                              line_name=get_curent_lines_lost(
                                                  self.obs),
                                              case_line_lost=True)
                        event_resolved_trigger = True
                        if self.obs.current_step >= self.config['scenario_first_step']:
                            message = {
                                "div": "message-container",
                                "content": "La simulation est en pause."
                            }
                            yield f"data: {json.dumps(message)}\n\n"
                            yield (
                                "data: {\"div\": \"status-div\", \"content\": "
                                "\"Cliquez sur 'Continuer' pour poursuivre la simulation.\"}\n\n"
                            )
                            set_pause(True)
                            while get_pause_status():
                                time.sleep(1)
                # --------------------------------------------------------------------

            # To reconnect lines in the grid any time this agent detect a line disconnection.
            # (This act is ovewriten in case of Oveload and XD_Silly intervene)
            if act == self.env.action_space({}):
                act = self.agent_reco.act(self.obs, 0)
                # print("Recopowerline acted. \n")

            # To handle simulator speed
            if self.obs.current_step >= self.config['scenario_first_step']:
                step_counter = step_counter + 1
                time.sleep(self.config['stepDuration_s'])
