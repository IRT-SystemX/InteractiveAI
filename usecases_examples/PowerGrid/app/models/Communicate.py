import logging
import toml
import json
import requests
import time
from datetime import datetime, timedelta
import numpy as np
from config.config import logging, set_pause, get_pause_status
from app.models.recommendation_store import store as recommendation_store

class Communicate:
    """
    Manages communication between the simulator and the InteractiveAI API.
    
    This class contains methods for sending and receiving data,
    managing connections, and processing simulator events.
    """

    def __init__(self):
        logging.info("COMMUNICATIONS' SETUP FOR THIS SESSION : \n")
        self.cab_api_on = False
        self.push_step = 1
        self.acces_token = None
        self.cab_url = None
        self.list_of_issues = {}
        self.act_dict = {}
        self.payload = {}

        # Load parameters from configuration file
        self.load_config()

    def load_config(self):
        """
        Loads the configuration from the 'config/API_POWERGRID_CAB.toml' file.
        """
        try:
            self.outputs_config = toml.load("config/API_POWERGRID_CAB.toml")
            if self.outputs_config['Outputs']['activate'] == 'yes':
                self.cab_api_on = True
            else:
                logging.info(
                    "According to your communication setup, "
                    "this session can just run in a standalone mode.\n"
                    "Check the file 'config/API_POWERGRID_CAB.toml' to setup the simulator "
                    "differently."
                )
        except FileNotFoundError:
            logging.error("File 'config/API_POWERGRID_CAB.toml' not found.")
        except toml.TomlDecodeError:
            logging.error("Failed to decode 'config/API_POWERGRID_CAB.toml'.")
        except Exception as e:
            logging.error("An unexpected error occurred: %s", str(e))

    def edit_parameters(self, parameter_name, new_value):
        """
        Modifies a parameter in the configuration and saves the changes.

        Args:
            parameter_name: Name of the parameter to modify.
            new_value: New value of the parameter.
        """
        # Reload config in case it was modified
        self.load_config()

        # Update parameters in self.outputs_config
        keys = parameter_name.split('.')
        current_param = self.outputs_config
        for key in keys[:-1]:
            if key in current_param:
                current_param = current_param[key]
            else:
                logging.error(
                    "Parameter %s does not exist in the configuration.", parameter_name)
                return
        current_param[keys[-1]] = new_value

        # Save changes to configuration file
        with open("config/API_POWERGRID_CAB.toml", "w", encoding="utf-8") as file:
            toml.dump(self.outputs_config, file)

    def add_cab_server_url(self, url):
        """
        Adds a new CAB server URL to the configuration.

        Args:
            url: URL of the new CAB server to add.

        Returns:
            bool: True if the server was successfully added, False otherwise.
        """
        try:
            config = toml.load("config/API_POWERGRID_CAB.toml")
            if 'Connexion' not in config:
                config['Connexion'] = {}
            
            # Find next available server number
            server_count = sum(1 for key in config['Connexion'] if key.startswith('cab_server_url_'))
            new_key = f'cab_server_url_{server_count + 1}'
            
            config['Connexion'][new_key] = url
            
            with open("config/API_POWERGRID_CAB.toml", "w") as configfile:
                toml.dump(config, configfile)
            
            return True
        except Exception as e:
            print(f"An error occurred while adding the server: {e}")
            return False

    def delete_cab_server_url(self, url):
        """
        Deletes a InteractiveAI server URL from the configuration.

        Args:
            url: URL of the InteractiveAI server to delete.

        Returns:
            bool: True if the server was successfully deleted, False otherwise.
        """
        try:
            config_file = "config/API_POWERGRID_CAB.toml"
            config = toml.load(config_file)
            if 'Connexion' in config:
                for key, value in list(config['Connexion'].items()):
                    if value == url:
                        del config['Connexion'][key]
                        with open(config_file, "w") as configfile:
                            toml.dump(config, configfile)
                        print(f"Server removed: key={key}, url={url}")
                        return True, url
                print(f"URL not found: {url}")
                return False, ""
            else:
                print("Section 'Connexion' not found in configuration file")
                return False, ""
        except Exception as e:
            print(f"An error occurred while deleting the server: {e}")
            return False, ""

    def get_cab_server_urls(self):
        """
        Retrieves the InteractiveAI server URLs from the configuration file.

        Returns:
            dict: Dictionary of InteractiveAI server URLs.
        """
        try:
            config = toml.load("config/API_POWERGRID_CAB.toml")
            # Access [Connexion] section and retrieve all URLs
            urls = {
                key: value
                for key, value in config['Connexion'].items()
                if key.startswith('cab_server_url_')
            }
            return urls
        except KeyError:
            print(
                "Section 'Connexion' is missing from the configuration file.")
            return {}
        except FileNotFoundError:
            print("Configuration file not found.")
            return {}
        except Exception as e:
            print(
                f"Error reading configuration file: {e}")
        return {}

    def choose_a_cab_application(self, server_choice):
        """
        Selects a InteractiveAI application based on the user's choice.

        Args:
            server_choice: User's choice for the InteractiveAI server.

        Returns:
            str: URL of the chosen InteractiveAI server, or None if the choice is invalid.
        """
        try:
            server_url = server_choice
            if server_url:
                self.cab_url = server_url
                return server_url
            return None
        except KeyError:
            print("Invalid server choice.")
            return None
        except FileNotFoundError:
            print("Configuration file not found.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def login(self, username, password):
        """
        Performs login to the InteractiveAI API.

        Args:
            username: Username for login.
            password: Password for login.

        Returns:
            tuple: Login URL and authorization status (bool).
        """
        # url = self.outputs_config['Connexion']['login_url']
        url = self.cab_url + self.outputs_config['Connexion']['login_port']

        payload = (
            f"username={username}&password={password}&grant_type=password&clientId=opfab-client"
        )
        headers = {
            'Authorization': 'Basic b3BmYWItY2xpZW50Om9wZmFiLWtleWNsb2FrLXNlY3JldA==',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, timeout=15)
        print(response.text)
        response.raise_for_status()
        # print(response.json())
        logging.info("Login status message: %s", response)
        logging.info("Login response.reason: %s", response.reason)
        self.acces_token = response.json().get("access_token")
        # print(self.acces_token)
        authorization = False
        if self.acces_token is not None:
            authorization = True
        return url, authorization

    def send_context_online(self, obs, scn_first_step, context_date, img_b64):
        """
        Sends the context online with the observation image.

        Args:
            obs: The current observation of the network.
            scn_first_step: First step of the scenario.
            context_date: Date of the context.
            img_b64: Base64 encoded image.
        """
        if obs.current_step < scn_first_step or not self.cab_api_on:
            return

        try:
            url = self.cab_url + \
                self.outputs_config['Outputs']['Context']['context_port']
            payload = json.dumps({
                "date": f"{context_date}",
                "data": {
                    "observation": obs.to_json(),
                    "topology": img_b64
                },
                "use_case": "PowerGrid"
            })
            headers = {
                'Authorization': f"Bearer {self.acces_token}",
                'Content-Type': 'application/json'
            }
            response = requests.request(
                "POST", url, headers=headers, data=payload, timeout=15)
            response.raise_for_status()
            logging.info("Context sent successfully.")
        except Exception as e:
            logging.error(e)
            logging.info(
                "Failed to send context: connection with InteractiveAI failed.")

    def send_payload_and_store_it(self, payload, obs, scn_first_step):
        """
        Sends the payload to the InteractiveAI API and stores it locally.

        Args:
            payload: The payload to send.
            obs: The current observation of the network.
            scn_first_step: First step of the scenario.
        """
        try:
            # Payload updating for same events detected
            try:
                if obs.current_step >= scn_first_step:
                    self.payload = json.loads(payload)
                    if self.payload["title"] in self.list_of_issues:
                        value = self.list_of_issues[self.payload["title"]]
                        self.payload["start_date"] = value["start_date"]
            except Exception as e:
                logging.error(e)

            # Send event
            if obs.current_step >= scn_first_step:
                if self.cab_api_on is True:
                    url = self.cab_url + \
                        self.outputs_config['Outputs']['Events']['event_port']
                    headers = {
                        'Authorization': f"Bearer {self.acces_token}",
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("POST",
                                                url,
                                                headers=headers,
                                                data=json.dumps(self.payload),
                                                timeout=15)
                    # logging.info("FULL EVENT : %s", self.payload)
                    # print(response.text)
                    response.raise_for_status()
                text = self.payload["title"]

                if self.cab_api_on is True:
                    logging.info("Event sent to InteractiveAI : %s", text)
                else:
                    logging.info("Event not sent to InteractiveAI : %s", text)
                # logging.info("Reponse event: %s", response.text)

        except Exception as e:
            logging.error(e)
            logging.info(
                "The event has not been sent : the connexion with InteractiveAI failed")

        # Store event in simulator memory
        try:
            if obs.current_step >= scn_first_step:
                if self.cab_api_on is True:
                    logging.info(self.payload["title"])
                else:
                    print(self.payload["title"])
                self.issues_follow_up()
        except Exception as e:
            logging.error(e)
            logging.info("The event's follow-up is not working")

    def send_event_online(self,
                          context_date,
                          scn_first_step,
                          kpis, obs, current_issues,
                          img_b64, line_name="0_0_0",
                          zone=None, line=None,
                          duration=None,
                          case_overload=False,
                          case_assist_alarm=False,
                          case_assist_alert=False,
                          case_anticip=False,
                          case_line_lost=False):
        """
        Function that generate InteractiveAI compliant Event and send it online.

        Args:
            context_date: Date of the context.
            scn_first_step: First step of the scenario.
            kpis: Dictionary of KPIs.
            obs: The current observation of the network.
            current_issues: List of current issues.
            img_b64: Base64 encoded image.
            line_name: Name of the line (default is "0_0_0").
            zone: Cardinal zone (default is None).
            line: Line information (default is None).
            duration: Duration of the event (default is None).
            case_overload: Flag for overload case (default is False).
            case_assist_alarm: Flag for assistant alarm case (default is False).
            case_anticip: Flag for anticipation case (default is False).
            case_line_lost: Flag for line lost case (default is False).
        """
        if zone is None:
            zone = []
        if line is None:
            line = []

        if ("Overload" in current_issues) and case_overload:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "HIGH",
                    "title": f"Overload in line {line_name}",
                    "description": (
                        f"Warning: the {line_name} line is overloaded by "
                        f"{np.round(np.float64(obs.rho.max() * 100),decimals=1,out=None)}%"
                    ),
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "KPI",
                        "line": f"{line_name}",
                        "flux": np.round(np.float64(obs.rho.max() * 100), decimals=1, out=None),
                        "kpis": kpis,
                        "event_context": img_b64
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Overload description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                logging.error(e)

        if ("Assistant raised an alarm" in current_issues) and case_assist_alarm:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "MEDIUM",
                    "title": "AI agent Alarm",
                    "description": f"Be vigilant in zone {zone}",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "agent",
                        "zone": zone,
                        "line": "",
                        "kpis": kpis,
                        "event_context": img_b64
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Assistant alarm description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                logging.error(e)

        if ("Assistant raised an alert" in current_issues) and case_assist_alert:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "MEDIUM",
                    "title": "AI agent Warning",
                    "description": f"Risk on lines: {line}",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "agent",
                        "line": line,
                        "kpis": kpis,
                        "event_context": img_b64
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Assistant alarm description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                logging.error(e)

        if ("Anticipation N-1" in current_issues) and case_anticip:
            anticip_date = context_date + timedelta(minutes=float(5*duration))
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "MEDIUM",
                    "title": f"Risk of N-1 contingency on line {line[0]}",
                    "description": (
                        f"Impacted lines {line[1]}, "
                        f"Maximum charge {np.round(max(line[2]) * 100, decimals=1, out=None)}%"
                    ),
                    "start_date": f"{anticip_date}",
                    "end_date": f"{anticip_date + timedelta(minutes=float(5*duration))}",
                    "data": {
                        "event_type": "anticipation",
                        "line": f"{line[0]}",
                        "flux": np.round(max(line[2]) * 100, decimals=1, out=None),
                        "kpis": kpis,
                        "event_context": img_b64,
                        "creation_date": f"{context_date}"  # New
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Anticipation description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                logging.error(e)

        if ("Line lost" in current_issues) and (line_name != "0_0_0") and case_line_lost:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "ROUTINE",
                    "title": f"Line {line_name} disconnected",
                    "description": f"Line {line_name} is disconnected",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "consignation",
                        "line": f"{line_name}",
                        "kpis": kpis,
                        "event_context": img_b64
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Line lost description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                logging.error(e)

    def issues_follow_up(self):
        """
        Updates the list of ongoing issues in the simulator.
        """
        # already exist => change start_date and end_date,and update list
        # doesn't exist => create payload and add to list
        self.list_of_issues[self.payload["title"]] = self.payload
        # print("list_of_issues= ",self.list_of_issues)

    def send_issues_ending_online(self, step_duration, context_date):
        """
        Sends the end-of-issue events to the CAB API.

        Args:
            step_duration: Duration of a simulation step.
            context_date: Current context date.
        """
        for key in list(self.list_of_issues.keys()):
            value = self.list_of_issues[key]
            if datetime.strptime(value["end_date"], "%Y-%m-%d %H:%M:%S.%f%z") < context_date:
                value["criticality"] = "ND"
                payload = json.dumps(value)

                # send restored event
                try:
                    url = self.cab_url + \
                        self.outputs_config['Outputs']['Events']['event_port']
                    headers = {
                        'Authorization': f"Bearer {self.acces_token}",
                        'Content-Type': 'application/json'
                    }
                    # print(f"Restoration =  {payload}")
                    if self.cab_api_on is True:
                        response = requests.request("POST",
                                                    url,
                                                    headers=headers,
                                                    data=payload,
                                                    timeout=15)
                        # print(response.text)
                        # response.raise_for_status()
                    test = value["title"]
                    logging.info("END event sent to InteractiveAI : %s", test)
                    time.sleep(step_duration)
                except Exception as e:
                    logging.error(e)
                    logging.info(
                        "The ending event has not been sent : the connexion with InteractiveAI failed \n"
                    )

                # Use del to remove the item from the dictionary
                del self.list_of_issues[key]

    def get_act_from_api(self):
        """
        Retrieves recommended actions from the InteractiveAI API.

        Yields:
            str: Formatted messages for the user interface.
        """
        get_act_counter = 0
        self.act_dict = {}
        try:
            while bool(self.act_dict) is False:
                if get_act_counter == 0:
                    message = {
                        "div": "message-container",
                        "content": "The simulation is paused. Please consult the recommendations from InteractiveAI before taking any further action here!"
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    time.sleep(1)
                    yield (
                        "data: {\"div\": \"status-div\", \"content\": "
                        "\"Click 'Resume' after making your selection in InteractiveAI\"}\n\n"
                    )
                    time.sleep(1)
                    yield f"data: {json.dumps({'div': 'simulation-state', 'content': 'paused'})}\n\n"
                    set_pause(True)
                    while get_pause_status():
                        yield ": keepalive\n\n"
                        time.sleep(1)
                    yield f"data: {json.dumps({'div': 'simulation-state', 'content': 'running'})}\n\n"
                else:
                    message = {
                        "div": "message-container",
                        "content": "No recommendation has been received from InteractiveAI!"
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    time.sleep(1)
                    yield (
                        "data: {\"div\": \"status-div\", \"content\": "
                        "\"Repeat your selection in InteractiveAI, then click 'Resume' again\"}\n\n"
                    )
                    time.sleep(1)
                    yield f"data: {json.dumps({'div': 'simulation-state', 'content': 'paused'})}\n\n"
                    set_pause(True)
                    while get_pause_status():
                        yield ": keepalive\n\n"
                        time.sleep(1)
                    yield f"data: {json.dumps({'div': 'simulation-state', 'content': 'running'})}\n\n"
                # The recommendation is delivered to this same process via the
                # POST /api/v1/recommendations endpoint and held in a shared
                # in-memory store. Read it directly instead of issuing an HTTP
                # request back to ourselves (which is fragile behind a reverse
                # proxy / loopback and was returning 404).
                self.act_dict = recommendation_store.pop()
                if bool(self.act_dict) is True:
                    logging.info(
                        "Recommendation payload received from InteractiveAI: %s",
                        json.dumps(self.act_dict))
                if bool(self.act_dict) is False and get_act_counter >= 1:
                    logging.info(
                        "\n No recommendation has been received! \n"
                        " The simulation will continue with the default Do Nothing recommendation."
                    )
                    message = {
                        "div": "message-container",
                        "content": "No recommendation has been received! The simulation will continue with the default Do Nothing recommendation."
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    time.sleep(1)
                    break
                if bool(self.act_dict) is True:
                    logging.info("\n InteractiveAI' s recommendation received! \n")
                    message = {
                        "div": "message-container",
                        "content": "The recommendation from InteractiveAI has just been received!"
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    time.sleep(1)
                get_act_counter += 1

        except Exception as e:
            logging.error(e)
