"""PowerGrid Simulator based on Grid2Op platform"""
from grid2op.Chronics.handlers import PerfectForecastHandler, CSVHandler
import re
import importlib
from grid2op.PlotGrid import PlotMatplot
from grid2op.Agent import recoPowerlineAgent
from grid2op.Agent import BaseAgent
from grid2op.Chronics import FromHandlers
import grid2op
from lightsim2grid import SecurityAnalysis
import numpy as np
import simplejson as json
import requests
import toml
import matplotlib.pyplot as plt
import io
import logging
import getpass
import os
import base64
import time
from datetime import datetime, timedelta, timezone
import matplotlib
matplotlib.use('agg')
try:
    from lightsim2grid import LightSimBackend
    bkClass = LightSimBackend
except ImportError:
    from grid2op.Backend import PandaPowerBackend
    bkClass = PandaPowerBackend

# Add for IA Agent testing (required assistantManager.py file)
# from assistantManager import agent_type,AgentManager


class Listener():
    """Class containing simulator functions to stream and diagnose Grid2Op data and events."""

    def __init__(self, init_obs):
        """Initialize the Listener with initial observation."""
        self._current_issues = None
        self._anticipation = None
        self.line_statuses = init_obs.line_status
        self.subs_on_bus_2 = np.repeat(False, init_obs.n_sub)
        self.objs_on_bus_2 = {id: [] for id in range(init_obs.n_sub)}

    def _stop_if_action(self, act):
        """Check if the given action can affect the grid."""
        if act.can_affect_something():
            logging.info("The current action has a chance to change the grid")
            return True
        return False

    def _stop_if_bad_kpi(self, obs):
        """Check if there is an overload in the grid."""
        # Check if overload
        if obs.rho.max() >= 1.0:
            # logging.info("Overload")
            return True
        return False

    def _stop_if_line_disconnected(self, obs):
        """Check if any line is disconnected."""
        if np.any(obs.line_status == False):
            # logging.info("Line disconnected")
            return True
        return False

    def _stop_if_alarm(self, obs):
        """Check if an alarm is raised by the assistant."""
        do_stop_if_alarm = True
        if do_stop_if_alarm:
            if np.any(obs.time_since_last_alarm == 0):
                logging.info("Assistant raised an alarm")
                return True
        return False

    def _stop_if_anticipation_security_analysis(self, obs, env, contingency_line_ids):
        """Perform security analysis for anticipation of N-1 events."""
        # Launch the security analysis
        anticipation = []
        security_analysis = SecurityAnalysis(env)
        thermal_limit = obs.thermal_limit

        for value in (contingency_line_ids):
            security_analysis.add_single_contingency(value)

        _, res_a, _ = security_analysis.get_flows()
        for i, c_value in enumerate(contingency_line_ids):
            flow = np.array(res_a[i])
            impacted_lines = []
            rho = []
            for j, value in enumerate(flow):
                if value / thermal_limit[j] >= 1.0:
                    impacted_lines = get_formatted_name_line(obs,j)
                    rho.append(value / thermal_limit[j])
            if len(impacted_lines) > 0:
                line_name = get_formatted_name_line(obs,c_value)
                anticipation.append((line_name, impacted_lines, rho))

        self._anticipation = None
        if len(anticipation) > 0:
            self._anticipation = anticipation
            return True
        return False

    def _stop_if_issue(self, obs, f_obs, f_env, contingency_line_ids):
        """Check for various issues in the grid."""
        issues = []
        self._current_issues = []
        if self._stop_if_alarm(obs):
            issues.append("Assistant raised an alarm")

        if self._stop_if_bad_kpi(obs):
            issues.append("Overload")

        if self._stop_if_line_disconnected(obs):  # and obs.current_step == 100
            issues.append("Line lost")

        if f_obs is not None:
            # and obs.current_step == 100
            if self._stop_if_anticipation_security_analysis(f_obs, f_env, contingency_line_ids):
                issues.append("Anticipation N-1")

        if len(issues) > 0:
            self._current_issues = issues
            return True
        return False

    def stop_for_issue_state(self, obs, f_obs, f_env, contingency_line_ids):
        """Transfer private result to the simulator."""
        return self._stop_if_issue(obs, f_obs, f_env, contingency_line_ids)

    def update_objs_on_bus_switch(self, objs_on_bus_2, elem, pos_topo_vect):
        """Update objects on bus 2 after a bus switch."""
        if pos_topo_vect[elem["object_id"]] in objs_on_bus_2[elem["substation"]]:
            # elem was on bus 2,remove it from objs_on_bus_2
            objs_on_bus_2[elem["substation"]] = [
                x
                for x in objs_on_bus_2[elem["substation"]]
                if x != pos_topo_vect[elem["object_id"]]
            ]
        else:
            objs_on_bus_2[elem["substation"]].append(
                pos_topo_vect[elem["object_id"]])
        return objs_on_bus_2

    def update_objs_on_bus_assign(self, objs_on_bus_2, elem, pos_topo_vect):
        """Update objects on bus 2 after a bus assignment."""
        if (
            pos_topo_vect[elem["object_id"]
                          ] in objs_on_bus_2[elem["substation"]]
            and elem["bus"] == 1
        ):
            # elem was on bus 2,remove it from objs_on_bus_2
            objs_on_bus_2[elem["substation"]] = [
                x
                for x in objs_on_bus_2[elem["substation"]]
                if x != pos_topo_vect[elem["object_id"]]
            ]
        elif (
            pos_topo_vect[elem["object_id"]
                          ] not in objs_on_bus_2[elem["substation"]]
            and elem["bus"] == 2
        ):
            objs_on_bus_2[elem["substation"]].append(
                pos_topo_vect[elem["object_id"]])
        return objs_on_bus_2

    def update_objs_on_bus(self, objs_on_bus_2, elem, topo_vect_dict, kind):
        """Update objects on bus 2 based on topology changes."""
        for object_type, pos_topo_vect in topo_vect_dict.items():
            if elem["object_type"] == object_type and elem["bus"]:
                if kind == "bus_switch":
                    objs_on_bus_2 = self.update_objs_on_bus_switch(
                        objs_on_bus_2, elem, pos_topo_vect)
                else:
                    objs_on_bus_2 = self.update_objs_on_bus_assign(
                        objs_on_bus_2, elem, pos_topo_vect
                    )
                break
        return objs_on_bus_2

    def get_distance_from_obs(self, act, line_statuses, subs_on_bus_2, objs_on_bus_2, obs):
        """Calculate the distance from the reference topology."""
        impact_on_objs = act.impact_on_objects()

        # lines reconnetions/disconnections
        line_statuses[
            impact_on_objs["force_line"]["disconnections"]["powerlines"]
        ] = False
        line_statuses[
            impact_on_objs["force_line"]["reconnections"]["powerlines"]
        ] = True
        line_statuses[impact_on_objs["switch_line"]["powerlines"]] = np.invert(
            line_statuses[impact_on_objs["switch_line"]["powerlines"]]
        )

        topo_vect_dict = {
            "load": obs.load_pos_topo_vect,
            "generator": obs.gen_pos_topo_vect,
            "line (extremity)": obs.line_ex_pos_topo_vect,
            "line (origin)": obs.line_or_pos_topo_vect,
        }

        # Bus manipulation
        if impact_on_objs["topology"]["changed"]:
            for modif_type in ["bus_switch", "assigned_bus"]:

                for elem in impact_on_objs["topology"][modif_type]:
                    objs_on_bus_2 = self.update_objs_on_bus(
                        objs_on_bus_2, elem, topo_vect_dict, kind=modif_type
                    )

            for elem in impact_on_objs["topology"]["disconnect_bus"]:
                # Disconnected bus counts as one for the distance
                subs_on_bus_2[elem["substation"]] = True

        subs_on_bus_2 = [
            True if objs_on_2 else False for _, objs_on_2 in objs_on_bus_2.items()
        ]

        distance = len(line_statuses) - \
            line_statuses.sum() + sum(subs_on_bus_2)
        return distance, line_statuses, subs_on_bus_2, objs_on_bus_2

    def trigger_kpis(self, obs, act):
        """Calculate and return various KPIs for the current state."""
        kpis = {}
        if obs.rho.max() > 1:
            kpis["max_overload"] = float(
                np.round(np.float64(obs.rho.max()), decimals=3, out=None))
        else:
            kpis["max_overload"] = ''

        kpis["renewable_energy_share"] = float(np.round(sum(obs.gen_p[np.where((obs.gen_type == "hydro") | (
            obs.gen_type == "solar") | (obs.gen_type == "wind"))])/sum(obs.gen_p), decimals=3, out=None))
        kpis["total_consumption"] = float(
            np.round(sum(obs.load_p), decimals=3, out=None))

        distance, _, _, _ = self.get_distance_from_obs(
            act, self.line_statuses, self.subs_on_bus_2, self.objs_on_bus_2, obs)
        kpis["distance_from_reference_topology"] = float(
            np.round(np.float64(distance), decimals=3, out=None))

        kpis["curtailment_volume"] = float(
            np.round(sum(obs.curtailment_mw), decimals=3, out=None))
        kpis["redispatching_volume"] = float(np.round(max(abs(sum(obs.actual_dispatch[obs.actual_dispatch > 0])), abs(
            sum(obs.actual_dispatch[obs.actual_dispatch < 0]))), decimals=3, out=None))
        return kpis

    @property
    def current_issues(self):
        """Return the current issues detected by the Listener."""
        return self._current_issues

    @property
    def anticipation(self):
        """Return the anticipation results from security analysis."""
        return self._anticipation


class Communicate:
    """Class handling communication with the InteractiveAI API."""

    def __init__(self):
        """Initialize the Communicate class for handling InteractiveAI API communication."""
        logging.info("COMMUNICATIONS' SETUP FOR THIS SESSION : \n")
        try:
            self.outputsConfig = toml.load("API_POWERGRID_CAB.toml")
            if self.outputsConfig['Outputs']['activate'] == 'yes':
                self.CAB_API_on = True
            else:
                self.CAB_API_on = False
                logging.info("According to your communication setup,this session can just run in a standalone mode.\n \
                             Check the file 'API_POWERGRID_CAB.toml' to setup the simulator differently. \n")
        except Exception as e:
            print(e)
            self.CAB_API_on = False
            logging.info("The connection with InteractiveAI is not properly configured.\n \
                         It will therefore not be established. \n \
                         Check the file 'API_POWERGRID_CAB.toml' to setup the simulator differently. \n")

        self.push_step = 1
        self.acces_token = None
        self.cab_url = None
        self.list_of_issues = {}
        # self.datestr = datetime.now(timezone.utc)   #.strftime("%d/%m/%Y %H:%M:%S")

    def choose_a_CAB_application(self):
        """Prompt user to choose a InteractiveAI server application."""
        authorization = False
        connexion_counter = 0
        print(f"Choose the targeted InteractiveAI application between: \n\
              - A '{self.outputsConfig['Connexion']['cab_server_url_1'][:-1]}' \n\
              - B '{self.outputsConfig['Connexion']['cab_server_url_2'][:-1]}' \n\
              - C '{self.outputsConfig['Connexion']['cab_server_url_3'][:-1]}' ")
        while authorization == False:
            if connexion_counter > 3:
                logging.info("The connexion with InteractiveAI will not be established. \n\
                       The Simulator will run in a standalone mode.\n")
                self.CAB_API_on = False
                break
            if connexion_counter >= 1:
                print(
                    "Your choice has to be between the 2 available options. Try again!")
            choice = input("What would be your InteractiveAI server's choice? ")
            if choice is not None:
                if choice == 'A':
                    self.cab_url = self.outputsConfig['Connexion']['cab_server_url_1']
                    logging.info(
                        "The simulator will now perform it connexion with InteractiveAI's server '%s'.\n", self.cab_url[:-1])
                    authorization = True
                elif choice == 'B':
                    self.cab_url = self.outputsConfig['Connexion']['cab_server_url_2']
                    logging.info(
                        "The simulator will now perform it connexion with InteractiveAI's server '%s'.\n", self.cab_url[:-1])
                    authorization = True
                elif choice == 'C':
                    self.cab_url = self.outputsConfig['Connexion']['cab_server_url_3']
                    logging.info(
                        "The simulator will now perform it connexion with InteractiveAI's server '%s'.\n", self.cab_url[:-1])
                    authorization = True
            connexion_counter += 1
        return authorization

    def login(self, username, password):
        """Perform login to the InteractiveAI API."""
        # url = self.outputsConfig['Connexion']['login_url']
        url = self.cab_url + self.outputsConfig['Connexion']['login_port']

        payload = f"username={username}&password={password}&grant_type=password&clientId=opfab-client"
        headers = {
            'Authorization': 'Basic b3BmYWItY2xpZW50Om9wZmFiLWtleWNsb2FrLXNlY3JldA==',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, timeout=15)
        # print(response.text)
        # print(response.json())
        logging.info(f"Login status message: {response}")
        logging.info(f"Login response.reason: {response.reason}")
        self.acces_token = response.json().get("access_token")
        # print(self.acces_token)
        authorization = False
        if self.acces_token is not None:
            authorization = True
        return authorization

    def send_context_online(self, env, obs, scn_first_step, context_date):
        """Send context information to the InteractiveAI API."""
        try:
            plot_helper = PlotMatplot(env.observation_space)
            plot_helper.plot_obs(obs, line_info="rho",
                                 load_info=None, gen_info=None)
            # fig.legend(loc ="lower left")

            img = io.BytesIO()
            plt.savefig(img, format="png", bbox_inches="tight")  # format="png"
            img.seek(0)
            img_b64 = base64.b64encode(img.read()).decode('utf-8')
            plt.close()
            # print('encoded done')
        except Exception as e:
            print(e)

        if obs.current_step >= scn_first_step & self.CAB_API_on is True:
            # logging.info("Simulation step %s",step)
            logging.info("Status: send context to InteractiveAI")

        try:
            # url = self.outputsConfig['Outputs']['Context']['url']
            url = self.cab_url + \
                self.outputsConfig['Outputs']['Context']['context_port']
        except Exception as e:
            print(e)

        try:
            payload = json.dumps({
                # "date": f"{obs.get_time_stamp()}",
                # f"{date + timedelta(minutes=float(30))}",
                # "2024-04-26T18:29:52+02:00",
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

            if obs.current_step >= scn_first_step:
                response = requests.request(
                    "POST", url, headers=headers, data=payload, timeout=15)
                # logging.info(response.text)
                logging.info("Context succesfully sent")
        except Exception as e:
            print(e)
            logging.info(
                "The context has not been sent : the connexion with InteractiveAI failed")

        try:
            img.close()
        except Exception as e:
            print(e)
        '''if obs.current_step == 757:
            with open("obs757.json","w") as f:
                json.dump(obs.to_json(),f,indent=4,ensure_ascii=False)'''

    def send_payload_and_store_it(self, payload, obs, scn_first_step):
        """Send payload to InteractiveAI API and store it locally."""
        try:

            # Use for debug
            '''with open("new_PowerGrid_events","w") as f:
                #f.write(json.dumps({"toto":json.dumps(kpis,indent=4,ensure_ascii=False)}))
                f.write(payload)'''
            # print(payload)

            # Payload updating for same events detected
            try:
                if obs.current_step >= scn_first_step:
                    self.payload = json.loads(payload)
                    if self.payload["title"] in list(self.list_of_issues.keys()):
                        value = self.list_of_issues[self.payload["title"]]
                        self.payload["start_date"] = value["start_date"]
            except Exception as e:
                print(e)

            # Send event
            if obs.current_step >= scn_first_step:
                # if not ((self.payload["title"] in list(self.list_of_issues.keys())) and ("déconnectée" in self.payload["title"])):
                if self.CAB_API_on is True:
                    url = self.cab_url + \
                        self.outputsConfig['Outputs']['Events']['event_port']
                    headers = {
                        'Authorization': f"Bearer {self.acces_token}",
                        'Content-Type': 'application/json'
                    }
                    response = requests.request(
                        "POST", url, headers=headers, data=json.dumps(self.payload), timeout=15)
                text = self.payload["title"]

                if self.CAB_API_on is True:
                    logging.info(f"Event sent to InteractiveAI : {text}")
                else:
                    print(f"Event sent to InteractiveAI : {text}")
                # print("Réponse",response.text)

        except Exception as e:
            print(e)
            logging.info(
                "The event has not been sent : the connexion with InteractiveAI failed")

        # Store event in simulator memory
        try:
            if obs.current_step >= scn_first_step:
                if self.CAB_API_on is True:
                    logging.info(self.payload["title"])
                else:
                    print(self.payload["title"])
                self.issues_follow_up()
        except Exception as e:
            print(e)
            logging.info("The event's follow-up is not working")

    def send_event_online(self,
                          context_date,
                          scn_first_step,
                          kpis,
                          obs,
                          current_issues,
                          line_name="0_0_0",
                          zone=None,
                          line=None,
                          duration=None,
                          case_overload=False,
                          case_assist_alarm=False,
                          case_anticip=False,
                          case_line_lost=False):
        """Generate and send event information to InteractiveAI API."""
        if zone is None:
            zone = []
        if line is None:
            line = []

        # date = obs.get_time_stamp() # Realtime of the record scenrio
        # date =  self.datestr + timedelta(minutes=float(5*obs.current_step)) # Realtime from now date
        # + timedelta(minutes=float(obs.current_step)) # CAB timeline scaling
        date = datetime.now(timezone.utc)
        # print(date)

        if ("Overload" in current_issues) and case_overload:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "HIGH",
                    "title": f"Surcharge sur ligne {line_name}",
                    "description": f"Attention la ligne {line_name} \
                    est en surcharge de \
                        {np.round(np.float64(obs.rho.max() * 100),decimals=1,out=None)}%",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "KPI",
                        "line": f"{line_name}",
                        "flux": np.round(np.float64(obs.rho.max() * 100), decimals=1, out=None),
                        "kpis": kpis
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Overload description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                print(e)

        if ("Assistant raised an alarm" in current_issues) and case_assist_alarm:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "MEDIUM",
                    "title": "Alerte Agent IA",
                    "description": f"Soyez vigilant sur la zone {zone}",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "agent",
                        "zone": zone,
                        "line": "",
                        "kpis": kpis
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Assistant alarm description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                print(e)

        if ("Anticipation N-1" in current_issues) and case_anticip:
            anticip_date = context_date + timedelta(minutes=float(5*duration))
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "MEDIUM",
                    "title": f"Risque sur aléa N-1 sur la ligne {line[0]}",
                    "description": f"Lignes impactées {line[1]},charge max {np.round(max(line[2]) * 100,decimals=1,out=None)}%",
                    "start_date": f"{anticip_date}",
                    "end_date": f"{anticip_date + timedelta(minutes=float(5*duration))}",
                    "data": {
                        "event_type": "anticipation",
                        "line": f"{line[0]}",
                        "flux": np.round(max(line[2]) * 100, decimals=1, out=None),
                        "kpis": kpis
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Anticipation description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                print(e)

        if ("Line lost" in current_issues) and (line_name != "0_0_0") and case_line_lost:
            try:
                self.payload = {}
                payload_dict = {}
                payload_dict = {
                    "criticality": "ROUTINE",
                    "title": f"Ligne {line_name} déconnectée",
                    "description": f"La ligne {line_name} est déconnectée",
                    "start_date": f"{context_date}",
                    "end_date": f"{context_date + timedelta(minutes=float(5))}",
                    "data": {
                        "event_type": "consignation",
                        "line": f"{line_name}",
                        "kpis": kpis
                    },
                    "use_case": "PowerGrid",
                    "is_active": False
                }

                payload = json.dumps(payload_dict)
                # print(f"Line lost description: {payload}")
                self.send_payload_and_store_it(payload, obs, scn_first_step)
            except Exception as e:
                print(e)

    def issues_follow_up(self):
        """Update the list of ongoing issues."""
        # already exist => change start_date and end_date,and update list
        # doesn't exist => create payload and add to list
        self.list_of_issues[self.payload["title"]] = self.payload
        # print("list_of_issues= ",self.list_of_issues)

    def send_issues_ending_online(self,
                                  stepDuration,
                                  context_date):
        """Send information about resolved issues to InteractiveAI API."""
        for key in list(self.list_of_issues.keys()):
            value = self.list_of_issues[key]
            # if value["end_date"] >= obs.get_time_stamp(): # scenario based realtime
            # or (('Surcharge sur ligne' in value["title"]) and (value["title"] != self.payload["title"]))  : # realtime,scenario based
            if datetime.strptime(value["end_date"], "%Y-%m-%d %H:%M:%S.%f%z") < context_date :
                value["criticality"] = "ND"
                payload = json.dumps(value)

                # send restored event
                try:
                    url = self.cab_url + \
                        self.outputsConfig['Outputs']['Events']['event_port']
                    headers = {
                        'Authorization': f"Bearer {self.acces_token}",
                        'Content-Type': 'application/json'
                    }
                    # print(f"Restoration =  {payload}")
                    if self.CAB_API_on is True:
                        response = requests.request(
                            "POST", url, headers=headers, data=payload, timeout=15)
                    # print(response.text)
                    test = value["title"]
                    logging.info(f"END event sent to InteractiveAI : {test}")
                    time.sleep(stepDuration)
                except Exception as e:
                    print(e)
                    logging.info(
                        "The ending event has not been sent : the connexion with InteractiveAI failed \n")

                # Use del to remove the item from the dictionary
                del self.list_of_issues[key]

    def get_act_from_api(self):
        """Retrieve action recommendations from InteractiveAI API."""
        # Function that initiate the connexion with CAB through allowing the user to choose any available server.
        get_act_counter = 0
        act_dict = {}
        while bool(act_dict) is False:
            if get_act_counter == 0:
                val = input(
                    "\n There is an event : Check InteractiveAI for recommendations\n Press 'Enter' once you have made your choice in InteractiveAI application.")
            else:
                val = input(
                    "\n Any recommendation was received. Try again!\n Press 'Enter' once you have made your choice in InteractiveAI application.")
            url = self.outputsConfig['Inputs']['Act']['url']
            payload = {}
            headers = {}
            response = requests.request(
                "GET", url, headers=headers, data=payload, timeout=15)
            # print(response.text)
            # print(response.json())
            act_dict = response.json()
            if bool(act_dict) is False and get_act_counter >= 1:
                logging.info(
                    "\n Any recommendation was received! \n The simulation will continue with a default NULL recommendation.")
                time.sleep(1)
                break
            elif bool(act_dict) :
                logging.info("\n InteractiveAI' s recommendation received! \n")
            get_act_counter += 1
        # print(act_dict)
        return act_dict


def search_chronic_num_from_name(scenario_name,
                                 env):
    """Find the chronic ID from its name in the data storage base."""
    found_id = None
    # Search scenario with provided name
    for id, sp in enumerate(env.chronics_handler.real_data.subpaths):
        sp_end = os.path.basename(sp)
        if sp_end == scenario_name:
            found_id = id
    return found_id


def get_curent_lines_in_bad_KPI(obs):
    """Identify the line with the worst KPI in the grid in the following format: {line_or_to_subid}:{line_ex_to_subid}:{name_line}."""
    res = (obs.rho == obs.rho.max()).tolist().index(True)
    return get_formatted_name_line(obs, res)


def get_curent_lines_lost(obs):
    """Identify disconnected lines in the grid in the following format: {line_or_to_subid}:{line_ex_to_subid}:{name_line}."""
    res = (obs.line_status is False).tolist().index(True)
    return get_formatted_name_line(obs, res)

def get_formatted_name_line(obs, idx):
    """Format line name to {line_or_to_subid}:{line_ex_to_subid}:{name_line}"""
    return f"{obs.line_or_to_subid[idx]}:{obs.line_ex_to_subid[idx]}:{obs.name_line[idx]}"


def get_zone_where_alarm_occured(obs):
    """Determine the cardinal zone where an alarm occurred."""
    zone_idx = np.where(obs.last_alarm > -1)
    # obs.last_alarm = [86 -1 -1] =[EST,CENTRE ,OUEST] => zone = EST
    if zone_idx[0] == 0:
        zone = "Est"
    elif zone_idx[0] == 1:
        zone = "Centre"
    elif zone_idx[0] == 2:
        zone = "Ouest"
    else:
        zone = " "
    return zone


def display_parades_prompt(env, obs):
    """Function that will display the IA recommendations prompt. Still under devellopement"""
    action_do_nothing = env.action_space({})
    ok_act = False
    while not ok_act:
        val = input("Choose action type:\n 1. Injection change.\n 2. Switch line\n 3. Topological change\n 4. Redispatch\n 5. Storage\n 6. Curtailement\n 7. Force line\n 8. Do nothing\nChosen action number: ")
        ok_val = input("You chose action " + val +
                       ". Press enter to validate or 'n' to change.\n")
        if ok_val == 'n':
            continue

        if val == '1':
            # ATTENTION CETTE ACTION A CHANGE ENTRE lES VERSIONS DE GRID2OP
            inject_type = ["load_p", "load_q", "prod_p", "prod_v"]
            ok = False
            while not ok:
                inj_key_id = input(
                    "Choose type of injection to change:\n 1. Load active power.\n 2. Load reactive power.\n 3. Generator active power setpoint.\n 4.Generator voltage magnitude setpoint.\n")
                ok_val = input("You chose injection type '" + inj_key_id +
                               "'. Press enter to validate or 'n' to change.\n")
                if ok_val != 'n':
                    ok = True
            ok = False
            if int(inj_key_id) < 3:
                values_len = env.action_space.n_load
            else:
                values_len = env.action_space.n_gen
            while not ok:
                values = input("Type injection requires " +
                               str(values_len) + ".\n Enter values: ")
                values_list = [float(s) for s in re.findall(r'\d+', values)]
                if len(values_list) == 1:
                    values_list = values_list * values_len
                if len(values_list) == values_len:
                    ok = True
            act2 = env.action_space(
                {"injection": {inject_type[int(inj_key_id) - 1]: values_list}})
            ok_act = True
        if val == '2':
            print("bla switch line")
        if val == '3':
            substation_id = input("Type substation id: ")
            current_config = obs.sub_topology(int(substation_id))
            print("Current config of length ", len(
                current_config), ":", current_config)
            validate = False
            while not validate:
                change_config = input("Choose new config: ")
                config_list = [int(s)
                               for s in re.findall(r'\d+', change_config)]
                if len(config_list) != len(current_config):
                    print("Config length ", len(config_list), " is different from expected length ",
                          len(current_config))
                    continue
                if any(x != 1 and x != 2 for x in config_list):
                    print("Lines can only be assigned to Bus 1 or 2.")
                    continue
                print("Chosen config of length ", len(
                    config_list), ":", config_list)
                act2 = env.action_space(
                    {"set_bus": {"substations_id": [(int(substation_id), config_list)]}})
                validate = input(
                    "Validate by pressing enter or type n to correct.\n")
                if validate != 'n':
                    validate = True
            ok_act = True
        if val == '4':
            name = input("Type generator name: ")
            while name not in obs.name_gen:
                print("Generators: ", obs.name_gen)
                name = input("Type a valid generator name: ")
            idx = np.where(obs.name_gen == name)[0][0]
            validate = False
            while not validate:
                redispatch = input("Type the amount of redispatch: ")
                ok = input("Chosen value " + redispatch +
                           " MW. Press enter to validate or type n to change.\n")
                if ok != 'n':
                    validate = True
            act2 = env.action_space({"redispatch": [(idx, float(redispatch))]})
            ok_act = True
        if val == '5':
            if len(obs.name_storage) > 0:
                print("Storage units", obs.name_storage)
                idx = input("Give storage unit index: ")
                value = input(
                    "Type the amount of power in MW (negative if production and positive if recharge): ")
                act2 = env.action_space(
                    {"set_storage": [(int(idx), float(value))]})  # storage unit of id 0 produce 1.5MW
                ok_act = True
            else:
                print("No storage units available on the grid. Choose another action.\n")
                ok_act = False
        if val == '6':
            print("Renewable generator indices:", [i for i in range(
                len(obs.gen_renewable)) if obs.gen_renewable[i]])
            idx = input("Choose a generator index: ")
            ratio = input("Enter ratio to curtail: ")
            act2 = env.action_space({"curtail": [(int(idx), float(ratio))]})
            ok_act = True
        if val == '7':
            # reconnect_powerline = env.action.space.reconnect_powerline(line_id=5,bus_or=1,bus_ex=2)
            # act2 = env.action_space({"set_bus": {"loads_id": [(4,1)]}})
            print("bla force line")
            ok_act = True
        if val == '8':
            act2 = action_do_nothing
            ok_act = True

    # print(act2)
    return act2


def expand_act_from_cab(env, act_dict):
    """Function that will generate compliant act from act_dict."""
    act = env.action_space()
    act.from_json(act_dict)
    act_vect = act.to_vect()
    actnew = env.action_space()
    actnew.from_vect(act_vect)
    return actnew


def load_assistant(assistant_path,
                   assistant_seed,
                   env,
                   logger=None):
    """utility to load the agent"""
    # lazy loading
    assistant = None
    abs_assistant_path = os.path.abspath(assistant_path)
    submission = importlib.import_module(
        f"Ressources.XD_silly_repo.submission")
    assistant = submission.make_agent(
        env.copy(), os.path.join(abs_assistant_path, "submission"))
    if not isinstance(assistant, BaseAgent):
        msg_ = "your assistant you be a grid2op.Agent.BaseAgent"
        raise RuntimeError(msg_)
    assistant.seed(int(assistant_seed))
    return assistant


def local_XD_Silly(obs,
                   assistant):
    """Get local recommendations from the XD_Silly assistant."""
    recos = assistant.make_recommandations(obs, n_actions=3)
    if len(recos) > 0:
        local_act, _ = recos[0]
        return local_act


def get_nbOfTimestepSinceLastObs(obs_dict,
                                 previous_step):
    """Calculate the number of timesteps since the last observation."""
    nb_timestep = int(obs_dict.get("current_step")[0])-int(previous_step)
    return nb_timestep


def targeted_scenario_act_fixed(env,
                                obs):
    """Apply fixed actions for specific steps in the targeted scenario."""
    act = None
    topo_trigger = False
    # Manual action's correction on specifics steps
    if obs.current_step == 0:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(28, (2, 1, 2, 1, 1))]}})
        topo_trigger = True

    if obs.current_step in [162, 419, 433, 744, 1871]:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space({'set_bus': {'substations_id': [(
            16, (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))]}})
        topo_trigger = True

    if obs.current_step == 799:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(9, (1, 1, 1, 1, 1, 1, 1))]}})
        topo_trigger = True

    if obs.current_step == 800:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(19, (1, 1, 1))]}})
        topo_trigger = True

    if obs.current_step == 801:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(21, (1, 1, 1, 1, 1, 1, 1, 1))]}})
        topo_trigger = True

    if obs.current_step == 802:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(23, (1, 1, 1, 1, 1, 1, 1, 1, 1, 1))]}})
        topo_trigger = True

    if obs.current_step == 1539:
        # print("Simulation step : ",obs.current_step)
        # print("obs_Topology",obs.topo_vect)
        act = env.action_space(
            {'set_bus': {'substations_id': [(26, (1, 1, 1, 1, 1, 1, 1, 1, 1))]}})
        topo_trigger = True
    return act, topo_trigger


def run_simulator():
    """Main function to run the PowerGrid simulator based on Grid2Op platform."""
    # Logger
    logging.getLogger().setLevel(logging.INFO)
    logging.info(" Welcome to PowerGrid Simulator based on Grid2Op platform! \n")

    # Communications module
    com = Communicate()

    # Connexion with InteractiveAI management
    if com.CAB_API_on is True:
        server_choosen = com.choose_a_CAB_application()
        if server_choosen is True:
            connexion = False
            connexion_counter = 0
            while connexion is False:
                if connexion_counter >= 1:
                    print("Try again")
                username = input('Username : ')
                try:
                    password = getpass.getpass('Password : ')
                except:
                    password = input('Password : ')
                connexion = com.login(username, password)
                connexion_counter += 1

    try:
        # Load simulation configuration
        config = toml.load("CONFIG.toml")

        forecasts_horizons = [5, 10, 15, 20, 25, 30]

        # Grid2OP environment definition and loading
        # env = grid2op.make(config['env_name'],backend=bkClass())
        env = grid2op.make(config['env_name'],
                           backend=bkClass(),
                           data_feeding_kwargs={
                               "gridvalueClass": FromHandlers,
                               "gen_p_handler": CSVHandler("prod_p"),
                               "load_p_handler": CSVHandler("load_p"),
                               "gen_v_handler": CSVHandler("prod_v"),
                               "load_q_handler": CSVHandler("load_q"),
                               "h_forecast": forecasts_horizons,
                               "gen_p_for_handler": PerfectForecastHandler("prod_p_forecasted"),
                               "load_p_for_handler": PerfectForecastHandler("load_p_forecasted"),
                               "load_q_for_handler": PerfectForecastHandler("load_q_forecasted")})

        # Initial state
        env.seed(config['env_seed'])
        id_scenario = search_chronic_num_from_name(config['scenario_name'],
                                                   env)
        env.set_id(id_scenario)  # Scenario choice
        obs = env.reset()
        if com.CAB_API_on is True:
            logging.info("The scenario launched is : %s \n",
                         env.chronics_handler.get_name())
        else:
            print("The scenario launched is : %s \n",
                  env.chronics_handler.get_name())

        reward = 0
        done = False
        anticipation_compute_step = config['step_start_security_analysis']

        # Assistant definition and loading
        # Uncomment the following line if required
        assistant_path = config['assistant_path']
        assistant_seed = config['assistant_seed']
        local_assistant = load_assistant(assistant_path, assistant_seed, env)

        # Added for IA Agent testing (required assistantManager.py file)
        # agentM = AgentManager()

        # Agent RecoPowerLine
        agent_reco = recoPowerlineAgent.RecoPowerlineAgent(env.action_space)
        act = agent_reco.act(obs, 0)

        if com.CAB_API_on is True:
            logging.info("The simulation is loaded.\n")
        else:
            print("The Simulation is loaded.\n")

    except Exception as e:
        print(e)
        logging.info(
            "The simulation is not load properly. The program will stop.")
        exit()

    # Listener module
    listen = Listener(obs)

    # Context refreshing rate
    try:
        send_tempo = com.outputsConfig['Outputs']['Context']['tempo']
    except Exception as e:
        print(e)
        send_tempo = 50  # by default

    event_resolved_trigger = False

    # Choose the first step concern by context sending to InteractiveAI
    try:
        com.push_step = config['scenario_first_step']
    except Exception as e:
        print(e)

    silent_mode_msg_trigger = True
    step_counter = 0
    date = datetime.now(timezone.utc)

    while not done:
        context_date = date + timedelta(minutes=float(5))*step_counter

        # Pour corriger la valeur de act à certain pas précis en vue d'avoir notre scénario cible
        act_fixed, _ = targeted_scenario_act_fixed(env,
                                                   obs)
        if act_fixed is not None:
            act = act_fixed

        # Begining of steps : Observation updates
        obs, reward, done, info = env.step(act)  # obs,reward,done,info

        # By default
        act = env.action_space({})

        # To handle between "silent mode" and "stream simulation" (with or without InteractiveAI)
        # (The stream simulation starts at step config['scenario_first_step'])
        if obs.current_step >= config['scenario_first_step']:
            if com.CAB_API_on is True:
                logging.info("Simulation step %s",
                             obs.current_step)
            else:
                print("Simulation step %s",
                      obs.current_step)

        elif obs.current_step == config['scenario_first_step'] - 1:
            print("\n")
            logging.info(f"The simulator is now connected to InteractiveAI\n")
            silent_mode_msg_trigger = False
        else:
            if silent_mode_msg_trigger:
                logging.info(f'''Status: The scenario unfolds in silent mode.\n
                             The simulator will reconnect to InteractiveAI from the step 
                             {config['scenario_first_step']} 
                             (see configuration file) \n''')
                silent_mode_msg_trigger = False
            if obs.current_step % 50 == 0:
                print("step",
                      obs.current_step, end="",
                      flush=True)
            elif obs.current_step % 10 == 0:
                print(' ... ',
                      end="",
                      flush=True)
                # time.sleep(config['stepDuration_s']/10)

        # To handle end of event card and event followup
        com.send_issues_ending_online(config['stepDuration_s'],
                                      context_date)

        # Forecast events checking
        obs_forecast = None
        f_env = None
        if obs.current_step == anticipation_compute_step:
            anticipation_compute_step = obs.current_step + \
                config['refresh_frequency_step']
            # pour dans 15 min (time_step_forecast=3)
            obs_forecast, *_ = obs.simulate(env.action_space(),
                                            config['time_step_forecast'])

            f_env = obs_forecast._obs_env

        # Added to send context online sequentialy
        if obs.current_step >= config['scenario_first_step']:
            context_just_sent = False
            if (obs.current_step == com.push_step or event_resolved_trigger is True) and com.CAB_API_on is True:
                com.push_step = obs.current_step + send_tempo
                com.send_context_online(
                    env, obs, config['scenario_first_step'], context_date)
                event_resolved_trigger = False
                context_just_sent = True

        if listen.stop_for_issue_state(obs,
                                       obs_forecast,
                                       f_env,
                                       env._opponent._lines_ids):
            # logging.info("An alarm is raised")

            # ----------------------------------------------------------------------------------
            if "Overload" in listen.current_issues:
                if obs.current_step >= config['scenario_first_step']:
                    com.push_step = obs.current_step + send_tempo
                    if com.CAB_API_on is True and context_just_sent is False:
                        com.send_context_online(env,
                                                obs,
                                                config['scenario_first_step'],
                                                context_date)
                        context_just_sent = True
                    logging.info("Status: there is an Overload")

                    com.send_event_online(context_date,
                                          config['scenario_first_step'],
                                          listen.trigger_kpis(obs, act),
                                          obs, listen.current_issues,
                                          line_name=get_curent_lines_in_bad_KPI(
                                              obs),
                                          case_overload=True)
                # act = display_parades_prompt(env,obs)
                if (obs.current_step < config['scenario_first_step']) or (com.CAB_API_on is False):
                    # Utiliser XD_Silly en cache (en local)
                    act = local_XD_Silly(obs, local_assistant)
                    if com.CAB_API_on is False:
                        logging.info(f"Parade : {act}")

                else:
                    # Récuperer les parades de InteractiveAI
                    act_dict = com.get_act_from_api()
                    act = expand_act_from_cab(env, act_dict)
                    logging.info(f"Parade : {act}")

                # Added for IA Agent testing (required assistantManager.py file)
                # obs_dict = obs.to_json()
                # recommendation = agentM.recommendate(obs_dict)
                # parades = agentM.getlistOfParadeInfo()
                # act,__ = recommendation[0]

                event_resolved_trigger = True

            if "Assistant raised an alarm" in listen.current_issues:
                if obs.current_step >= config['scenario_first_step']:

                    # com.push_step = obs.current_step + send_tempo
                    # if com.CAB_API_on is True and context_just_sent == False:
                    #     com.send_context_online(env,obs,config['scenario_first_step'],context_date)
                    #     context_just_sent = True

                    logging.info("Status: there is an IA Agent alert")

                    com.send_event_online(context_date,
                                          config['scenario_first_step'],
                                          listen.trigger_kpis(obs, act),
                                          obs,
                                          listen.current_issues,
                                          zone=get_zone_where_alarm_occured(
                                              obs),
                                          case_assist_alarm=True)
                    # act = display_parades_prompt(env,obs)
                    event_resolved_trigger = True

            if "Anticipation N-1" in listen.current_issues:
                if obs.current_step >= config['scenario_first_step']:

                    # #com.push_step = obs.current_step + send_tempo
                    # if com.CAB_API_on is True: # and context_just_sent == False:
                    #     com.send_context_online(obs_forecast._obs_env,obs_forecast,config['scenario_first_step'],context_date)
                    #     #context_just_sent = True
                    # time.sleep(40)

                    logging.info("Status: there is an Anticipation N-1 event")

                    for x in listen.anticipation:
                        logging.info(
                            f"There is a line lost anticipation event {x}")

                        com.send_event_online(context_date,
                                              config['scenario_first_step'],
                                              listen.trigger_kpis(
                                                  obs, env.action_space()),
                                              obs_forecast,
                                              listen.current_issues,
                                              line=x,
                                              duration=config['duration_step_forecast'],
                                              case_anticip=True)
                    # act = display_parades_prompt(env,obs)
                    event_resolved_trigger = True
                    obs_forecast = None
                    if obs.current_step >= config['scenario_first_step']:
                        # time.sleep(40)

                        # pause_simulation = input(
                        # "\n The simulation is on 'pause'!\n Press 'Enter' when you are ready to continue.")
                        pass

            if "Line lost" in listen.current_issues:
                if obs.current_step >= config['scenario_first_step']:
                    # com.push_step = obs.current_step + send_tempo
                    # if com.CAB_API_on == True and context_just_sent == False:
                    #     com.send_context_online(env,obs,config['scenario_first_step'],context_date)
                    #     context_just_sent = True
                    logging.info("Status: there is a Line lost %s",
                                 get_curent_lines_lost(obs))

                    com.send_event_online(context_date,
                                          config['scenario_first_step'],
                                          listen.trigger_kpis(obs, act),
                                          obs,
                                          listen.current_issues,
                                          line_name=get_curent_lines_lost(obs),
                                          case_line_lost=True)
                    event_resolved_trigger = True
                    if obs.current_step >= config['scenario_first_step']:
                        # time.sleep(40)

                        # pause_simulation = input(
                        # "\n The simulation is on 'pause'!\n Press 'Enter' when you are ready to continue.")
                        pass
            # --------------------------------------------------------------------

        # To reconnect lines in the grid any time this agent detect a line disconnection.
        # (This act is ovewriten in case of Oveload and XD_Silly intervene)
        if act == env.action_space({}):
            act = agent_reco.act(obs, 0)
            # print("Recopowerline acted. \n")

        # To handle simulator speed
        if obs.current_step >= config['scenario_first_step']:
            step_counter = step_counter + 1
            time.sleep(config['stepDuration_s'])


if __name__ == '__main__':
    run_simulator()
