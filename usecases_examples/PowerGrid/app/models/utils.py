"""PowerGrid Simulator based on Grid2Op platform"""
import io
import os
import base64
import importlib
from grid2op.PlotGrid import PlotMatplot
from grid2op.Agent import BaseAgent
from config.config import logging
import numpy as np
import mpld3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


def create_observation_image(env, obs):
    """
    Generates an image of the observation and returns it in base64.

    Args:
        env: The simulation environment.
        obs: The observation to visualize.

    Returns:
        str: Base64 encoded image, or None in case of error.
    """
    try:
        plot_helper = PlotMatplot(env.observation_space)
        fig = plot_helper.plot_obs(
            obs, line_info="rho", load_info=None, gen_info=None)
        img = io.BytesIO()
        plt.savefig(img, format="svg", bbox_inches="tight")
        img.seek(0)
        img_b64 = base64.b64encode(img.read()).decode('utf-8')
        plt.close(fig)
        return img_b64
    except Exception as e:
        logging.error(e)
        return None


def search_chronic_num_from_name(scenario_name, env):
    """
    Searches for a scenario ID based on its name.

    Args:
        scenario_name: Name of the scenario to search for.
        env: The simulation environment.

    Returns:
        int: ID of the found scenario, or None if not found.
    """
    found_id = None
    # Search scenario with provided name
    for chr_id, sp in enumerate(env.chronics_handler.real_data.subpaths):
        sp_end = os.path.basename(sp)
        if sp_end == scenario_name:
            found_id = chr_id
    return found_id


def get_curent_lines_in_bad_kpi(obs):
    """
    Identifies the grid lines with bad KPIs.

    Args:
        obs: The current observation.

    Returns:
        str: Name of the line with the worst KPI in the following format: {line_or_to_subid}:{line_ex_to_subid}:{name_line}
    """
    res = (obs.rho == obs.rho.max()).tolist().index(True)
    return get_formatted_name_line(obs, res)


def get_curent_lines_lost(obs):
    """
    Identifies the lost lines in the grid.

    Args:
        obs: The current observation.

    Returns:
        str: Name of the first lost line in the following format: {line_or_to_subid}:{line_ex_to_subid}:{name_line}.
    """
    res = (obs.line_status is False).tolist().index(True)
    return get_formatted_name_line(obs, res)


def get_alert_lines(obs):
    """
    Identifies the lines where an alert occured.

    Args:
        obs: The current observation.

    Returns:
        str: Name of the first lost line in the following format: {line_or_to_subid}:{line_ex_to_subid}:{name_line}.
    """
    idx_list = np.where(obs.active_alert)[0]
    return [get_formatted_name_line(obs, idx) for idx in idx_list]


def get_formatted_name_line(obs, idx):
    return f"{obs.line_or_to_subid[idx]}:{obs.line_ex_to_subid[idx]}:{obs.name_line[idx]}"


def get_zone_where_alarm_occured(obs):
    """
    Determines the cardinal zone of the grid where the event occurred.

    Args:
        obs: The current observation.

    Returns:
        str: Name of the zone ('East', 'Center', 'West' or ' ').
    """
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


def expand_act_from_cab(env, act_dict):
    """
    Generates a compliant action from an action dictionary.

    Args:
        env: The simulation environment.
        act_dict: Dictionary describing the action.

    Returns:
        Action: An action compliant with the environment.
    """
    act = env.action_space()
    logging.info("Expanding action received from InteractiveAI: %s", act_dict)
    act.from_json(act_dict)
    act_vect = act.to_vect()
    actnew = env.action_space()
    actnew.from_vect(act_vect)
    return actnew


def summarize_action(act):
    """
    Build a log/UI friendly summary of the concrete impact of a grid2op action.

    Args:
        act: A grid2op BaseAction.

    Returns:
        dict: 'is_do_nothing' flag, the readable 'text' description and a
              best-effort structured 'impact' (set_bus / set_line_status / ...).
    """
    summary = {"is_do_nothing": True, "text": str(act), "impact": {}}
    try:
        summary["is_do_nothing"] = not act.can_affect_something()
    except Exception as e:
        logging.error(e)
    try:
        summary["impact"] = act.impact_on_objects()
    except Exception as e:
        logging.error(e)
    return summary


def verify_action_applied(pending, topo_before, line_status_before,
                          obs_after, info, overwritten=False):
    """
    Determine whether a recommendation was effectively applied to the grid.

    A grid2op action that is illegal or ambiguous is silently ignored by
    ``env.step``: nothing changes on the grid. This compares the grid state
    before and after the step and inspects the ``info`` returned by the step to
    produce an honest verdict.

    Args:
        pending: dict describing the action that was supposed to be applied
                 (keys: 'step_issued', 'summary').
        topo_before: obs.topo_vect captured just before env.step.
        line_status_before: obs.line_status captured just before env.step.
        obs_after: observation returned by env.step.
        info: the info dict returned by env.step.
        overwritten: True if a scripted scenario action overrode the recommendation.

    Returns:
        dict: structured verification result, ready to log and to display.
    """
    is_illegal = bool(info.get("is_illegal", False))
    is_ambiguous = bool(info.get("is_ambiguous", False))
    exceptions = [str(e) for e in info.get("exception", []) if e is not None]

    changes = {"changed": False, "bus_changes": [], "line_status_changes": []}
    try:
        diff_idx = np.where(topo_before != obs_after.topo_vect)[0]
        for i in diff_idx.tolist():
            changes["bus_changes"].append({
                "topo_vect_id": int(i),
                "from_bus": int(topo_before[i]),
                "to_bus": int(obs_after.topo_vect[i]),
            })
        ls_idx = np.where(line_status_before != obs_after.line_status)[0]
        for i in ls_idx.tolist():
            changes["line_status_changes"].append({
                "line_id": int(i),
                "line_name": str(obs_after.name_line[i]),
                "connected": bool(obs_after.line_status[i]),
            })
        changes["changed"] = bool(len(diff_idx) or len(ls_idx))
    except Exception as e:
        logging.error(e)

    is_do_nothing = bool(pending.get("summary", {}).get("is_do_nothing", False))

    if overwritten:
        status = "OVERRIDDEN"
    elif is_illegal or is_ambiguous:
        status = "REJECTED"
    elif changes["changed"]:
        status = "APPLIED"
    elif is_do_nothing:
        status = "NO_OP"
    else:
        status = "NO_EFFECT"

    return {
        "status": status,
        "step_issued": pending.get("step_issued"),
        "step_applied": int(obs_after.current_step),
        "is_illegal": is_illegal,
        "is_ambiguous": is_ambiguous,
        "exceptions": exceptions,
        "changes": changes,
    }


def format_verdict_description(verdict):
    """
    Build a short human-readable description of an action verification verdict.

    Args:
        verdict: dict produced by :func:`verify_action_applied`.

    Returns:
        str: one-line description suitable for the dashboard and the logs.
    """
    parts = []
    bus = verdict["changes"]["bus_changes"]
    lines = verdict["changes"]["line_status_changes"]
    if bus:
        parts.append(f"{len(bus)} bus assignment(s) changed")
    if lines:
        flips = ", ".join(
            f"{c['line_name']} "
            f"{'reconnected' if c['connected'] else 'disconnected'}"
            for c in lines)
        parts.append(f"line status: {flips}")
    if verdict["is_illegal"]:
        parts.append("action was illegal")
    if verdict["is_ambiguous"]:
        parts.append("action was ambiguous")
    if verdict["exceptions"]:
        parts.append("; ".join(verdict["exceptions"]))
    if not parts:
        parts.append("no observable change on the grid")
    return (f"Issued at step {verdict['step_issued']}, "
            f"checked at step {verdict['step_applied']}: "
            + "; ".join(parts))


def load_assistant(assistant_path, assistant_seed, env):
    """
    Loads the assistant agent.

    Args:
        assistant_path: Path to the assistant.
        assistant_seed: Seed for initializing the assistant.
        env: The simulation environment.

    Returns:
        BaseAgent: The loaded assistant agent.
    """
    # lazy loading
    assistant = None
    abs_assistant_path = os.path.abspath(assistant_path)
    submission = importlib.import_module("Ressources.XD_silly_repo.submission")
    assistant = submission.make_agent(
        env.copy(), os.path.join(abs_assistant_path, "submission"))
    if not isinstance(assistant, BaseAgent):
        msg_ = "your assistant you be a grid2op.Agent.BaseAgent"
        raise RuntimeError(msg_)
    assistant.seed(int(assistant_seed))
    return assistant


def local_xd_silly(obs, assistant):
    """
    Generates local recommendations from the assistant.

    Args:
        obs: The current observation.
        assistant: The assistant agent.

    Returns:
        Action: The recommended action, or None.
    """
    recos = assistant.make_recommandations(obs, n_actions=3)
    if len(recos) > 0:
        local_act, _ = recos[0]
        return local_act


def get_nb_of_timestep_since_last_obs(obs_dict, previous_step):
    """
    Calculates the number of timesteps elapsed since the last observation.

    Args:
        obs_dict (dict): A dictionary containing the current observation data.
        previous_step (int): The timestep of the previous observation.

    Returns:
        int: The number of timesteps elapsed since the last observation.
    """
    nb_timestep = int(obs_dict.get("current_step")[0])-int(previous_step)
    return nb_timestep


def targeted_scenario_act_fixed(env, obs):
    """
    Applies targeted actions for specific scenarios.

    Args:
        env: The simulation environment.
        obs: The current observation.

    Returns:
        tuple: (Action, bool) The action to apply and a topological change indicator.
    """
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
        act = env.action_space({
            'set_bus': {
                'substations_id': [
                    (16, (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))
                ]
            }
        })
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


def generate_graph_html(env, obs):
    """
    Generates an HTML graph representation of the current observation.

    Args:
        env (grid2op.Environment): The Grid2Op environment.
        obs (grid2op.Observation): The current observation of the environment.

    Returns:
        str: An HTML string containing the graph representation of the observation.
    """
    try:
        plot_helper = PlotMatplot(env.observation_space)
        fig = plot_helper.plot_obs(obs,
                                   line_info="rho",
                                   load_info=None,
                                   gen_info=None)
        
        # Supprimer les axes
        ax = fig.gca()
        ax.axis('off')
        
        # Ajuster les limites de l'axe pour éliminer la ligne à gauche
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim(xlim[0], xlim[1])
        ax.set_ylim(ylim[0], ylim[1] * 1.02)  # Ajuster également la limite supérieure si nécessaire
        
        # Ajuster les marges pour enlever l'espace blanc autour du graphique
        plt.subplots_adjust(left=0.02, right=1, top=1, bottom=0, wspace=0, hspace=0)
        plt.margins(0, 0)
        
        # Recadrer la figure pour éliminer tout espace blanc résiduel
        fig.tight_layout(pad=0)

        # Convertir la figure en HTML
        graph_html = mpld3.fig_to_html(fig)
        plt.close(fig)
        
        logging.info("Graphique généré avec succès")
        logging.debug(f"Premiers 200 caractères du HTML du graphique : {graph_html[:200]}")
        
        return graph_html
    except Exception as e:
        logging.error(f"Erreur lors de la génération du graphique : {str(e)}")
        return "<p>Erreur lors de la génération du graphique</p>"
