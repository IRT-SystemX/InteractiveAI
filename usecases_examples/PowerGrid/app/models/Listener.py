import numpy as np
from config.config import logging
from lightsim2grid import SecurityAnalysis

from app.models.utils import get_formatted_name_line


class Listener:
    """This class has all the simulator's functions 
    that will stream and diagnose any Grid2Op selected data and events."""

    def __init__(self, init_obs):
        """
        Initializes the Listener with the initial observation.

        Args:
            init_obs: The initial observation of the network.
        """
        self._current_issues = None
        self._anticipation = None
        self.line_statuses = init_obs.line_status
        self.subs_on_bus_2 = np.repeat(False, init_obs.n_sub)
        self.objs_on_bus_2 = {id: [] for id in range(init_obs.n_sub)}

    def _stop_if_action(self, act):
        """
        Checks if the action can affect anything in the network.

        Args:
            act: The action to check.

        Returns:
            bool: True if the action can affect the network, False otherwise.
        """
        if act.can_affect_something():
            logging.info("The current action has a chance to change the grid")
            return True
        return False

    def _stop_if_bad_kpi(self, obs):
        """
        Checks if there is an overload in the network.

        Args:
            obs: The current observation of the network.

        Returns:
            bool: True if there is an overload, False otherwise.
        """
        # Check if overload
        if obs.rho.max() >= 1.0:
            # logging.info("Overload")
            return True
        return False

    def _stop_if_line_disconnected(self, obs):
        """
        Checks if a line is disconnected in the network.

        Args:
            obs: The current observation of the network.

        Returns:
            bool: True if a line is disconnected, False otherwise.
        """
        if np.any(obs.line_status is False):
            logging.info("Line disconnected")
            return True
        return False

    def _stop_if_alarm(self, obs, otherwise__=""):
        """
        Checks if an alarm has been triggered by the assistant.

        Args:
            obs: The current observation of the network.

        Returns:
            bool: True if an alarm has been triggered, False otherwise.
        """
        if np.any(obs.time_since_last_alarm == 0):
            logging.info("Assistant raised an alarm")
            return True
        return False

    def _stop_if_alert(self, obs, otherwise__=""):
        """
        Checks if an alert has been triggered by the assistant.

        Args:
            obs: The current observation of the network.

        Returns:
            bool: True if an alert has been triggered, False otherwise.
        """
        if np.any(obs.time_since_last_alert == 0):
            logging.info("Assistant raised an alert")
            return True
        return False

    def _stop_if_anticipation_security_analysis(self, obs, env, contingency_line_ids):
        """
        Performs a security analysis and checks for anticipations.

        Args:
            obs: Grid2Op environment observation.
            env: Grid2Op environment.
            contingency_line_ids: List of line IDs for contingencies.

        Returns:
            bool: True if anticipations are detected, False otherwise.
        """
        security_analysis = SecurityAnalysis(env)
        for value in contingency_line_ids:
            security_analysis.add_single_contingency(value)

        _, res_a, _ = security_analysis.get_flows()
        anticipation = []
        thermal_limit = obs.thermal_limit

        for i, c_value in enumerate(contingency_line_ids):
            flow = np.array(res_a[i])
            impacted_lines = [(get_formatted_name_line(obs,j), value / thermal_limit[j])
                            for j, value in enumerate(flow)
                            if value / thermal_limit[j] >= 1.0]
            
            if impacted_lines:
                line_name = get_formatted_name_line(obs,c_value)
                anticipation.append((line_name, *zip(*impacted_lines)))

        self._anticipation = anticipation if anticipation else None
        return bool(anticipation)

    def _stop_if_issue(self, obs, f_obs, f_env, contingency_line_ids):
        """
        Checks if there are issues in the current or anticipated network state.

        Args:
            obs: The current observation of the network.
            f_obs: The future observation of the network (if available).
            f_env: The future environment (if available).
            contingency_line_ids: The IDs of the lines to analyze for anticipation.

        Returns:
            bool: True if there are issues, False otherwise.
        """
        issues = []
        self._current_issues = []
        if self._stop_if_alarm(obs):
            issues.append("Assistant raised an alarm")

        if self._stop_if_alert(obs):
            issues.append("Assistant raised an alert")

        if self._stop_if_bad_kpi(obs):
            issues.append("Overload")

        if self._stop_if_line_disconnected(obs):  # and obs.current_step == 100
            issues.append("Line lost")

        if f_obs is not None:
            if self._stop_if_anticipation_security_analysis(f_obs, f_env, contingency_line_ids):
                issues.append("Anticipation N-1")

        if len(issues) > 0:
            self._current_issues = issues
            return True
        return False

    def stop_for_issue_state(self, obs, f_obs, f_env, contingency_line_ids):
        """
        Checks the network state for issues and returns the result.

        Args:
            obs: The current observation of the network.
            f_obs: The future observation of the network (if available).
            f_env: The future environment (if available).
            contingency_line_ids: The IDs of the lines to analyze for anticipation.

        Returns:
            bool: True if there are issues, False otherwise.
        """
        return self._stop_if_issue(obs, f_obs, f_env, contingency_line_ids)

    def update_objs_on_bus_switch(self, objs_on_bus_2, elem, pos_topo_vect):
        """
        Updates the list of objects on bus 2 when a bus switch occurs.

        Args:
            objs_on_bus_2: Dictionary of objects currently on bus 2.
            elem: The element changing buses.
            pos_topo_vect: The topological position vector.

        Returns:
            dict: The updated dictionary of objects on bus 2.
        """
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
        """
        Updates the list of objects on bus 2 when a bus assignment occurs.

        Args:
            objs_on_bus_2: Dictionary of objects currently on bus 2.
            elem: The element assigned to a bus.
            pos_topo_vect: The topological position vector.

        Returns:
            dict: The updated dictionary of objects on bus 2.
        """
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
        """
        Updates the list of objects on bus 2 based on the type of change.

        Args:
            objs_on_bus_2: Dictionary of objects currently on bus 2.
            elem: The element changing buses.
            topo_vect_dict: Dictionary of topological position vectors.
            kind: Type of change ('bus_switch' or 'assigned_bus').

        Returns:
            dict: The updated dictionary of objects on bus 2.
        """
        for object_type, pos_topo_vect in topo_vect_dict.items():
            if elem["object_type"] == object_type and elem["bus"]:
                if kind == "bus_switch":
                    objs_on_bus_2 = self.update_objs_on_bus_switch(
                        objs_on_bus_2, elem, pos_topo_vect
                    )
                else:
                    objs_on_bus_2 = self.update_objs_on_bus_assign(
                        objs_on_bus_2, elem, pos_topo_vect
                    )
                break
        return objs_on_bus_2

    def get_distance_from_obs(self, act, line_statuses, subs_on_bus_2, objs_on_bus_2, obs):
        """
        Calculates the distance between the current state and the reference state of the network.

        Args:
            act: The applied action.
            line_statuses: Statuses of the lines.
            subs_on_bus_2: Substations on bus 2.
            objs_on_bus_2: Objects on bus 2.
            obs: The current observation of the network.

        Returns:
            tuple: Calculated distance and updated states of lines and buses.
        """
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
        """
        Calculates and returns the KPIs (Key Performance Indicators) of the network.

        Args:
            obs: The current observation of the network.
            act: The applied action.

        Returns:
            dict: Dictionary containing the calculated KPIs.
        """
        kpis = {}
        if obs.rho.max() > 1:
            kpis["max_overload"] = float(
                np.round(np.float64(obs.rho.max()), decimals=3, out=None))
        else:
            kpis["max_overload"] = ''
        kpis["renewable_energy_share"] = float(
            np.round(
                sum(
                    obs.gen_p[
                        np.where((obs.gen_type == "hydro")
                                 | (obs.gen_type == "solar")
                                 | (obs.gen_type == "wind"))
                    ])
                / sum(obs.gen_p),
                decimals=3,
                out=None))
        kpis["total_consumption"] = float(
            np.round(
                sum(obs.load_p),
                decimals=3,
                out=None))

        distance, _, _, _ = self.get_distance_from_obs(act,
                                                       self.line_statuses,
                                                       self.subs_on_bus_2,
                                                       self.objs_on_bus_2,
                                                       obs)
        kpis["distance_from_reference_topology"] = float(
            np.round(
                np.float64(distance),
                decimals=3, out=None))

        kpis["curtailment_volume"] = float(
            np.round(sum(obs.curtailment_mw), decimals=3, out=None))
        kpis["redispatching_volume"] = float(
            np.round(
                max(
                    abs(
                        sum(
                            obs.actual_dispatch[
                                obs.actual_dispatch > 0
                            ])),
                    abs(
                        sum(
                            obs.actual_dispatch[
                                obs.actual_dispatch < 0
                            ]))),
                decimals=3,
                out=None))
        return kpis

    @property
    def current_issues(self):
        """
        Returns the current issues detected in the network.

        Returns:
            list: A list of current issues.
        """
        return self._current_issues

    @property
    def anticipation(self):
        """
        Returns the anticipated issues in the network.

        Returns:
            list: A list of anticipated issues.
        """
        return self._anticipation