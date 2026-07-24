import json
import re


def parse_delay_to_minutes(delay_str):
    if delay_str is None:
        return 0
    delay_str = delay_str.lower().strip()
    hours = 0
    minutes = 0
    h_match = re.search(r'(\d+)h', delay_str)
    m_match = re.search(r'(\d+)\s*min', delay_str)
    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))
    if "h" in delay_str and "min" not in delay_str:
        parts = delay_str.split("h")
        if len(parts) > 1 and parts[1].isdigit():
            minutes = int(parts[1])
    return hours * 60 + minutes


def SNCF_RECO3(event_json, context_json, recommendation_catalog):
    """
    Selects recommendations using IF–THEN rules based on id_event.
    Returns 4 recommendations ordered with best=True first.
    """
    event = json.loads(event_json)
    id_event = event["data"].get("id_event")

    if id_event not in recommendation_catalog:
        return [json.dumps({"error": f"No recommendations defined for event_id {id_event}"})]

    recos = recommendation_catalog[id_event]

    def best_first(reco_json):
        reco = json.loads(reco_json)
        return 0 if reco["data"]["kpis"].get("best") == "True" else 1

    return sorted(recos, key=best_first)


def SNCF_deontic(event_json, context_json, recommendation_catalog, type="passengers", threshold_value=200):
    """
    Filters recommendations by a KPI threshold, then sorts by that KPI ascending.

    Parameters
    ----------
    type : str
        KPI to filter and sort on: "passengers", "delay", "cost", "total_cost"
    threshold_value : int | str
        Upper bound for the KPI (use a delay string like "1h30" for type="delay")
    """
    event = json.loads(event_json)
    id_event = event["data"].get("id_event")

    if id_event not in recommendation_catalog:
        return [json.dumps({"error": f"No recommendations defined for event_id {id_event}"})]

    recos = recommendation_catalog[id_event]

    # When no threshold is provided, skip filtering and return all recommendations sorted
    if threshold_value is None:
        filtered = list(recos)
    else:
        filtered = []
        for reco_json in recos:
            reco = json.loads(reco_json)
            kpis = reco["data"]["kpis"]
            passengers = int(kpis.get("nb_impacted_passengers", 0))
            cost = int(kpis.get("cost", 0))
            total_cost = int(kpis.get("total_cost", 0))
            delay_minutes = parse_delay_to_minutes(kpis.get("delay", "0min"))

            if type == "passengers" and passengers <= threshold_value:
                filtered.append(reco_json)
            elif type == "delay":
                if delay_minutes <= parse_delay_to_minutes(threshold_value):
                    filtered.append(reco_json)
            elif type == "cost" and cost <= threshold_value:
                filtered.append(reco_json)
            elif type == "total_cost" and total_cost <= threshold_value:
                filtered.append(reco_json)

    def _key(reco_json):
        reco = json.loads(reco_json)
        kpis = reco["data"]["kpis"]
        if type == "passengers":
            return int(kpis.get("nb_impacted_passengers", 0))
        if type == "delay":
            return parse_delay_to_minutes(kpis.get("delay", "0min"))
        if type == "cost":
            return int(kpis.get("cost", 0))
        if type == "total_cost":
            return int(kpis.get("total_cost", 0))
        return 0

    if type not in ("passengers", "delay", "cost", "total_cost"):
        return [json.dumps({"error": "type must be 'passengers', 'delay', 'cost', or 'total_cost'"})]

    return sorted(filtered, key=_key)


def SNCF_risk(event_json, context_json, recommendation_catalog, type):
    """
    Returns all recommendations sorted by a KPI ascending (no threshold filtering).
    """
    event = json.loads(event_json)
    id_event = event["data"].get("id_event")

    if id_event not in recommendation_catalog:
        return [json.dumps({"error": f"No recommendations defined for event_id {id_event}"})]

    recos = recommendation_catalog[id_event]

    kpi_keys = {
        "passengers": lambda r: int(json.loads(r)["data"]["kpis"].get("nb_impacted_passengers", 0)),
        "delay": lambda r: parse_delay_to_minutes(json.loads(r)["data"]["kpis"].get("delay", "0min")),
        "cost": lambda r: int(json.loads(r)["data"]["kpis"].get("cost", 0)),
        "total_cost": lambda r: int(json.loads(r)["data"]["kpis"].get("total_cost", 0)),
    }

    if type not in kpi_keys:
        return [json.dumps({"error": "type must be 'passengers', 'delay', 'cost', or 'total_cost'"})]

    return sorted(recos, key=kpi_keys[type])


def SNCF_risk_tie_break(event_json, context_json, recommendation_catalog, type, tie_breaker=None):
    """
    Orders recommendations by a primary KPI, using a secondary KPI to break ties.
    """
    event = json.loads(event_json)
    id_event = event["data"].get("id_event")

    if id_event not in recommendation_catalog:
        return [json.dumps({"error": f"No recommendations defined for event_id {id_event}"})]

    recos = recommendation_catalog[id_event]

    kpi_keys = {
        "passengers": lambda r: int(json.loads(r)["data"]["kpis"].get("nb_impacted_passengers", 0)),
        "delay": lambda r: parse_delay_to_minutes(json.loads(r)["data"]["kpis"].get("delay", "0min")),
        "cost": lambda r: int(json.loads(r)["data"]["kpis"].get("cost", 0)),
        "total_cost": lambda r: int(json.loads(r)["data"]["kpis"].get("total_cost", 0)),
    }

    if type not in kpi_keys:
        return [json.dumps({"error": "Invalid type"})]

    if tie_breaker is None:
        return sorted(recos, key=kpi_keys[type])

    if tie_breaker not in kpi_keys:
        return [json.dumps({"error": "Invalid tie_breaker"})]

    return sorted(recos, key=lambda r: (kpi_keys[type](r), kpi_keys[tie_breaker](r)))
