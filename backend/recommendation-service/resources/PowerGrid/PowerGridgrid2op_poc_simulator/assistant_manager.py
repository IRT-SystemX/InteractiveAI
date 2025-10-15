import os
from enum import Enum
import importlib.util
import sys
import numpy as np
import toml
from lightsim2grid import LightSimBackend
import grid2op
from grid2op.Chronics import FromHandlers
from grid2op.Chronics.handlers import PerfectForecastHandler, CSVHandler
from grid2op.Agent import BaseAgent

BkClass = LightSimBackend

class AgentType(Enum):
    """Recomendations' agent type

    Args:
        Enum (): Type "onto" or "IA"
    """
    onto = 1
    IA = 2


def lazy_import_package(package_name, package_path):
    """Import a package dynamically from a given path

    Args:
        package_name (string): Name of the package to be imported
        package_path (string): Path to the package directory

    Returns:
        module: Imported package
    """
    spec = importlib.util.spec_from_file_location(package_name,
                                                  os.path.join(package_path, '__init__.py'))
    if spec and spec.loader:
        package = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = package
        spec.loader.exec_module(package)
        return package
    else:
        raise ImportError(f"Cannot import package {package_name} from {package_path}")


class AgentManager:
    """PowerGrid IA agent object based on Grid2Op and XD_silly
    """
    def __init__(self):
        # Load PowerGrid simulator configuration
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Build the path to the config file
        config_path = os.path.join(script_dir, "CONFIG_POWERGRID.toml")
        config_assistant = toml.load(config_path)

        # grid2op Environment and observation definition and loading
        env_name = os.path.join(script_dir, config_assistant["env_name"])

        forecasts_horizons = [5, 10, 15, 20, 25, 30]
        self.env = grid2op.make(
            env_name,
            backend=BkClass(),
            data_feeding_kwargs={
                "gridvalueClass": FromHandlers,
                "gen_p_handler": CSVHandler("prod_p"),
                "load_p_handler": CSVHandler("load_p"),
                "gen_v_handler": CSVHandler("prod_v"),
                "load_q_handler": CSVHandler("load_q"),
                "h_forecast": forecasts_horizons,
                "gen_p_for_handler": PerfectForecastHandler(
                    "prod_p_forecasted"
                ),
                "load_p_for_handler": PerfectForecastHandler(
                    "load_p_forecasted"
                ),
                "load_q_for_handler": PerfectForecastHandler(
                    "load_q_forecasted"
                ),
            },
        )
        self.env.seed(config_assistant["env_seed"])
        # Search scenario with provided name
        for sc_id, sp in enumerate(self.env.chronics_handler.real_data.subpaths):
            sp_end = os.path.basename(sp)
            if sp_end == config_assistant["scenario_name"]:
                self.id_scenario = sc_id

        self.env.set_id(self.id_scenario)  # Scenario choice
        self.obs = self.env.reset()

        if self.obs.current_step is None:
            self.previous_step = "1"
        else:
            self.previous_step = self.obs.current_step
        # assistant definition and loading
        assistant_path = os.path.join(
            script_dir, config_assistant["assistant_name"])
        assistant_seed = config_assistant["assistant_seed"]
        submission_path = os.path.join(assistant_path, "submission")
        submission = lazy_import_package("submission", submission_path)

        self.assistant = submission.make_agent(
            self.env.copy(),
            submission_path,
        )
        if not isinstance(self.assistant, BaseAgent):
            msg_ = "Your assistant must be a grid2op.Agent.BaseAgent"
            raise RuntimeError(msg_)

        self.assistant.seed(int(assistant_seed))
        self.nb_timestep = 0  # Initialize timestep count

        # Action "do nothing"
        self.action_do_nothing = self.env.action_space({})

        self.recommendations = []

    def reset_obs_if_needed(self, obs_dict):
        """Reset obs

        Args:
            obs_dict (dict): Observation dictionary
        """
        if self.nb_timestep < 0:
            self.env.set_id(self.id_scenario)
            self.obs = self.env.reset()
            self.previous_step = "1"
            self.get_nb_of_timestep_since_last_obs(obs_dict)

    def get_nb_of_timestep_since_last_obs(self, obs_dict):
        """Count number of simulation timestep bewteen 2 consecutive
        call to this function.

        Args:
            obs_dict (dict): Observation dictionary

        Returns:
            int : Number of timesteps
        """
        self.nb_timestep = int(obs_dict.get("current_step")[0]) - int(
            self.previous_step
        )
        return self.nb_timestep

    def create_recommendation(self, obs_dict, n_actions=3):
        """Create PowerGrid IA agent recomendations

        Args:
            obs_dict (dict): Observation dictionary
            n_actions (int, optional): Number of recomendations
                that should be generated.Defaults to 3.

        Returns:
            [act_dict]: Recomendations objects compliant with PowerGrid simulator
        """
        self.get_nb_of_timestep_since_last_obs(obs_dict)
        self.reset_obs_if_needed(obs_dict)
        if (
            self.nb_timestep > 1
        ):  # no sense to fast-forward only for next time step ?
            self.env.fast_forward_chronics(self.nb_timestep)
            self.previous_step = obs_dict.get("current_step")[0]
        elif self.nb_timestep == 1:
            self.env.step(self.action_do_nothing)
            self.previous_step = obs_dict.get("current_step")[0]
        self.obs = self.env.get_obs()
        self.obs.from_json(
            obs_dict
        )  # il faut aussi modifier les _env_internal_params
        self.obs._env_internal_params["_line_status_env"] = (
            self.obs.line_status.astype(int)
        )
        self.recommendations = self.assistant.make_recommandations(
            self.obs, n_actions
        )
        return self.recommendations

    def get_parade_info(self, act):
        """Compile unitary recomendation in json format for InteractiveAI's frontend compliance

        Args:
            act (): Unitary action object

        Returns:
            dict: Recomendations data in json format
        """
        kpis = {}
        title = []
        description = []
        impact = act.impact_on_objects()

        # redispatch
        if act._modif_redispatch:
            kpis["type_of_the_reco"] = (
                "Redispatch"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append(
                "Injection recommendation: production source redispatch"
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
                        f'"{gen_name}" de {r_amount:.2f} MW'
                    )

        # storage
        if act._modif_storage:
            kpis["type_of_the_reco"] = (
                "Storage"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append("Storage recommendation")
            cpt = 0
            for stor_idx in range(act.n_storage):
                amount_ = act._storage_power[stor_idx]
                if np.isfinite(amount_) and amount_ != 0.0:
                    name_ = act.name_storage[stor_idx]
                    if cpt > 0:
                        description.append(", ")
                    cpt = 1
                    description.append(
                        f'Ask unit "{name_}" to '
                        f'{"charge" if amount_ > 0.0 else "discharge"} '
                        f'{abs(amount_):.2f} MW (setpoint: {amount_:.2f} MW)'
                    )

        # curtailment
        if act._modif_curtailment:
            kpis["type_of_the_reco"] = (
                "Injection"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append("Injection recommendation")
            cpt = 0
            for gen_idx in range(act.n_gen):
                amount_ = act._curtail[gen_idx]
                if np.isfinite(amount_) and amount_ != -1.0:
                    name_ = act.name_gen[gen_idx]
                    if cpt > 0:
                        description.append(", ")
                    cpt = 1
                    description.append(
                        f'Limit unit "{name_}" to '
                        f'{100.0 * amount_:.1f}% of its maximum capacity '
                        f'(setpoint: {amount_:.3f})'
                    )

        # force line status
        force_line_impact = impact["force_line"]
        if force_line_impact["changed"]:
            kpis["type_of_the_reco"] = (
                "Topological"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append(
                "Topological recommendation: connection/disconnection of line"
            )
            reconnections = force_line_impact["reconnections"]
            if reconnections["count"] > 0:
                description.append(
                    f"Reconnection of {reconnections['count']} lines "
                    f"({reconnections['powerlines']})"
                )

            disconnections = force_line_impact["disconnections"]
            if disconnections["count"] > 0:
                description.append(
                    f"Disconnection of {disconnections['count']} lines "
                    f"({disconnections['powerlines']})"
                )

        # swtich line status
        swith_line_impact = impact["switch_line"]
        if swith_line_impact["changed"]:
            kpis["type_of_the_reco"] = (
                "Topological"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append("Topological: change a line state")
            description.append(
                f"Change the state of {swith_line_impact['count']} lines "
                f"({swith_line_impact['powerlines']})"
            )

        # topology
        bus_switch_impact = impact["topology"]["bus_switch"]
        if len(bus_switch_impact) > 0:
            kpis["type_of_the_reco"] = (
                "Topological"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append(
                "Topological recommendation: Schematic acquisition at substation "
                + str(bus_switch_impact["substation"])
            )
            description.append("Busbar change:")
            for switch in bus_switch_impact:
                description.append(
                    f"\t \t - Switch bus of {switch['object_type']} id "
                    f"{switch['object_id']} [at station {switch['substation']}]"
                )

        assigned_bus_impact = impact["topology"]["assigned_bus"]
        disconnect_bus_impact = impact["topology"]["disconnect_bus"]
        if len(assigned_bus_impact) > 0 or len(disconnect_bus_impact) > 0:
            kpis["type_of_the_reco"] = (
                "Topological"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append(
                "Topological recommendation: Schematic acquisition at substation "
                + str(assigned_bus_impact[0]["substation"])
            )
            if assigned_bus_impact:
                description.append("")
            cpt = 0
            for assigned in assigned_bus_impact:
                if cpt > 0:
                    description.append(", ")
                cpt = 1
                description.append(
                    f" Assign bus {assigned['bus']} to "
                    f"{assigned['object_type']} id {assigned['object_id']}"
                )
            if disconnect_bus_impact:
                description.append("")
            cpt = 0
            for disconnected in disconnect_bus_impact:
                if cpt > 0:
                    description.append(", ")
                cpt = 1
                description.append(
                    f"Disconnect {disconnected['object_type']} with id "
                    f"{disconnected['object_id']} [at the substation level "
                    f"{disconnected['substation']}]"
                )

        # Any of the above cases,
        # then the recommendation is most likely "Do nothing"
        if not title and act == self.action_do_nothing:
            kpis["type_of_the_reco"] = (
                "Do nothing"  # pour renvoyer le kpi type_of_the_reco
            )
            title.append("Poursuivre")
            description.append(
                "Continuation of the scenario without operator action"
            )

        title = "".join(title)
        description = "".join(description)

        if title:
            obs_simulate, _, _, _ = (
                self.obs.simulate(act, time_step=1)
            )
            kpis["efficiency_of_the_reco"] = float(
                np.float32(obs_simulate.rho.max())
            )  # pour renvoyer le kpi efficiency_of_the_reco

        return {
            "title": title,
            "description": description,
            "use_case": "PowerGrid",
            "agent_type": AgentType.IA.name,
            "actions": [act.to_json()],
            "kpis": kpis,
        }

    def get_list_of_parade_info(self):
        """Compile PowerGrid IA agent recomendations in a single list
            for InteractiveAI's frontend compliance

        Returns:
            [act_dict]: List of action dictionary
        """
        list_of_act_dict = []
        for rec in self.recommendations:
            act, _ = rec
            act_dict = self.get_parade_info(act)
            list_of_act_dict.append(act_dict)
        return list_of_act_dict
