import grid2op
from grid2op.Agent import BaseAgent
try:
    from lightsim2grid import LightSimBackend
    bkClass = LightSimBackend
except ImportError:
    from grid2op.Backend import PandaPowerBackend
    bkClass = PandaPowerBackend

import toml
import sys
import os
import json
from settings import logger
import numpy as np
from flask import current_app
from enum import Enum
import importlib


class AgentType(Enum):
    onto = 1
    IA = 2

class AgentManager:
    def __init__(self):
        # Load RTE simulator configuration
        self.root_path = current_app.config['ROOT_PATH']
        abs_path = os.path.join(
            self.root_path, "resources/rte/rtegrid2op_poc_simulator/")

        config_assistant = toml.load(abs_path + "CONFIG_RTE.toml")

        # grid2op Environment and observation definition and loading
        env_name = os.path.join(
            self.root_path, "resources/rte/rtegrid2op_poc_simulator/env_icaps_input_data_test")
        self.env = grid2op.make(env_name, backend=bkClass())
        self.env.seed(config_assistant['env_seed'])
        # Search scenario with provided name
        for id, sp in enumerate(self.env.chronics_handler.real_data.subpaths):
            sp_end = os.path.basename(sp)
            if sp_end == config_assistant['scenario_name']:
                id_scenario = id
        #id_scenario = search_chronic_num_from_name(config_assistant['scenario_name'], self.env)
        self.env.set_id(id_scenario)  # Scenario choice
        self.obs = self.env.reset()

        #self.obs = self.env.observation_space(self.env)
        if self.obs.current_step is None:
            self.previous_step = "1"
        else:
            self.previous_step = self.obs.current_step

        # assistant definition and loading
        assistant_path = os.path.join(
            self.root_path, "resources/rte/rtegrid2op_poc_simulator/XD_silly_repo")
        assistant_seed = config_assistant['assistant_seed']

        # lazy loading
        abs_assistant_path = os.path.abspath(assistant_path)

        submission = importlib.import_module(f"resources.rte.rtegrid2op_poc_simulator.XD_silly_repo.submission")
        self.assistant = submission.make_agent(
            self.env.copy(), os.path.join(abs_assistant_path, "submission"))
        if not isinstance(self.assistant, BaseAgent):
            msg_ = "your assistant you be a grid2op.Agent.BaseAgent"
            raise RuntimeError(msg_)

        self.assistant.seed(int(assistant_seed))
        self.nb_timestep = int(0)

        # Action "do nothing"
        self.action_do_nothing = self.env.action_space({})


    def get_nbOfTimestepSinceLastObs(self, obs_dict):
        self.nb_timestep = int(obs_dict.get("current_step")[
                               0]) - int(self.previous_step)
        return self.nb_timestep

    def recommendate(self, obs_dict, n_actions=3):
        self.get_nbOfTimestepSinceLastObs(obs_dict)
        if self.nb_timestep > 0:
            self.env.fast_forward_chronics(self.nb_timestep)
            self.previous_step = obs_dict.get("current_step")[0]
        self.obs = self.env.get_obs()
        self.obs.from_json(obs_dict)
        self.recommendations = self.assistant.make_recommandations(
            self.obs, n_actions)
        return self.recommendations

    def getParadeInfo(self, act):
        title = []
        description = []
        impact = act.impact_on_objects()

        # redispatch
        if act._modif_redispatch:
            title.append(
                "Parade injection: redispatch de source de production"
            )
            cpt = 0
            for gen_idx in range(act.n_gen):
                if act._redispatch[gen_idx] != 0.0:
                    gen_name = act.name_gen[gen_idx]
                    r_amount = act._redispatch[gen_idx]
                    if cpt > 0:
                        description.append(", ")
                    cpt = 1
                    description.append(
                        '"{}" de {:.2f} MW'.format(gen_name, r_amount))

        # storage
        if act._modif_storage:
            title.append("Parade stockage")
            cpt = 0
            for stor_idx in range(act.n_storage):
                amount_ = act._storage_power[stor_idx]
                if np.isfinite(amount_) and amount_ != 0.0:
                    name_ = act.name_storage[stor_idx]
                    if cpt > 0:
                        description.append(", ")
                    cpt = 1
                    description.append('Demande à l\'unité "{}" de {} {:.2f} MW (setpoint: {:.2f} MW)'
                                     "".format(
                                         name_,
                                         "charger" if amount_ > 0.0 else "decharger",
                                         np.abs(amount_),
                                         amount_,
                                     )
                                     )

        # curtailment
        if act._modif_curtailment:
            title.append("Parade injection")
            cpt = 0
            for gen_idx in range(act.n_gen):
                amount_ = act._curtail[gen_idx]
                if np.isfinite(amount_) and amount_ != -1.0:
                    name_ = act.name_gen[gen_idx]
                    if cpt > 0:
                        description.append(", ")
                    cpt = 1
                    description.append('Limiter l\'unité "{}" à {:.1f}% de sa capacité max (setpoint: {:.3f})'
                                     "".format(name_, 100.0 * amount_, amount_)
                                     )

        # force line status
        force_line_impact = impact["force_line"]
        if force_line_impact["changed"]:
            title.append(
                'Parade topologique: connection/deconnection de ligne')
            reconnections = force_line_impact["reconnections"]
            if reconnections["count"] > 0:
                description.append("Reconnection de {} lignes ({})".format(
                    reconnections["count"], reconnections["powerlines"]
                )
                )

            disconnections = force_line_impact["disconnections"]
            if disconnections["count"] > 0:
                description.append("Déconnection de {} lignes ({})".format(
                    disconnections["count"], disconnections["powerlines"]
                )
                )

        # swtich line status
        swith_line_impact = impact["switch_line"]
        if swith_line_impact["changed"]:
            title.append('Parade topologique: changer l\'état d\'une ligne')
            description.append(
                "Changer le statut de {} lignes ({})".format(
                    swith_line_impact["count"], swith_line_impact["powerlines"]
                )
            )

        # topology
        bus_switch_impact = impact["topology"]["bus_switch"]
        if len(bus_switch_impact) > 0:
            title.append(
                'Parade topologique: prise de schéma au poste ' + str(switch["substation"]))
            description.append("Changement de bus:")
            for switch in bus_switch_impact:
                description.append(
                    "\t \t - Switch bus de {} id {} [au poste {}]".format(
                        switch["object_type"], switch["object_id"], switch["substation"]
                    )
                )

        assigned_bus_impact = impact["topology"]["assigned_bus"]
        disconnect_bus_impact = impact["topology"]["disconnect_bus"]
        if len(assigned_bus_impact) > 0 or len(disconnect_bus_impact) > 0:
            title.append('Parade topologique: prise de schéma au poste ' +
                         str(assigned_bus_impact[0]["substation"]))
            if assigned_bus_impact:
                description.append("")
            cpt = 0
            for assigned in assigned_bus_impact:
                if cpt > 0:
                    description.append(", ")
                cpt = 1
                description.append(
                    " Assigner le bus {} à {} id {}".format(
                        assigned["bus"],
                        assigned["object_type"],
                        assigned["object_id"]
                    )
                )
            if disconnect_bus_impact:
                description.append("")
            cpt = 0
            for disconnected in disconnect_bus_impact:
                if cpt > 0:
                    description.append(", ")
                cpt = 1
                description.append(
                    "Déconnecter {} id {} \t".format(
                        disconnected["object_type"],
                        disconnected["object_id"],
                        disconnected["substation"],
                    )
                )

        # Any of the above cases, then the recommendation is most likely "Do nothing"
        if not title and act == self.action_do_nothing :
            title.append('Poursuivre')
            description.append("Poursuite du scénario sans intervention extérieur")

        title = "".join(title)
        description = "".join(description)
        return {"title":title, "description":description, "use_case":"RTE", "agent_type":AgentType.IA.name, "actions":[act.to_json()]}

    def getlistOfParadeInfo(self):
        list_of_act_dict = []
        for rec in self.recommendations:
            act, max_forecasted_rho_0 = rec
            act_dict = self.getParadeInfo(act)
            list_of_act_dict.append(act_dict)
        return list_of_act_dict


if __name__ == '__main__':
    # Parameters for this example
    iteration_in_cab = range(10)
    event_received = False
    context_received = False

    # Init (must be used in CAB)
    agentM = AgentManager()

    # Input from RTE simulator (for this example)
    obs_backup = agentM.obs
    with open('obs88.json') as mon_fichier:
        obs_dict = json.load(mon_fichier)
    # print(obs_dict)

    for ii in iteration_in_cab:
        print('Simulation iteration : ', ii)
        if ii == 3:
            event_received = True
            context_received = True
        else:
            event_received = False
            context_received = False

        if event_received and context_received:
            # Main calls to use in CAB in this same order any time both an event and a context is received
            nb_of_timestep = agentM.get_nbOfTimestepSinceLastObs(obs_dict)
            recommendation = agentM.recommendate(obs_dict)
            parades = agentM.getlistOfParadeInfo()

            # Test for this example (Should be remove)
            print("nb_of_timestep = ", nb_of_timestep)
            print("recommendation = ", recommendation)
            print("parades = ", parades)