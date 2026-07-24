# backend/recommendation-service/resources/Railway/manager.py
import json
from api.manager.base_manager import BaseRecommendationManager
from .mockRecommendations.mockRecommendations import RECOMMENDATION_CATALOG
from .sncf_recommender import SNCF_RECO3, SNCF_deontic, SNCF_risk, SNCF_risk_tie_break

import logging

logger = logging.getLogger(__name__)


class RailwayManager(BaseRecommendationManager):
    def __init__(self):
        super().__init__()

    def _transform_recommendation(self, reco_json):
        """Transform a recommendation from catalog format to API output format."""
        reco = json.loads(reco_json)
        return {
            "title": reco["data"]["title"],
            "description": reco["data"]["description"],
            "use_case": reco["data"]["use_case"],
            "agent_type": reco["data"]["agent_type"],
            "actions": [{}],
            "kpis": reco["data"]["kpis"],
        }

    def get_recommendation(self, request_data):
        """
        Return recommendations for a Railway event.

        Supports four modes controlled by request_data["event"]["mode"]:

        - "basic" (default): best-first ordering via SNCF_RECO3
        - "deontic": filter by KPI threshold, then sort ascending via SNCF_deontic
            requires: sort_type ("passengers"|"delay"|"cost"|"total_cost")
                      threshold_value (int, or delay string e.g. "1h30" for delay)
        - "risk": sort all recommendations by KPI ascending via SNCF_risk
            requires: sort_type
        - "risk_tie_break": sort by primary KPI, break ties with secondary via SNCF_risk_tie_break
            requires: sort_type
            optional: tie_breaker (same values as sort_type)
        """
        event_data = request_data.get("event", {})
        context_data = request_data.get("context", {})

        # Ensure id_event has a fallback so catalog lookup always has a key
        event_for_sncf = {**event_data, "id_event": str(event_data.get("id_event", "1"))}

        # Wrap into the structure expected by SNCF functions
        event_json = json.dumps({"data": event_for_sncf})
        context_json = json.dumps({"data": context_data})

        mode = event_data.get("mode", "deontic")
        logger.info(f"Railway recommendation — event_id: {event_for_sncf['id_event']}, mode: {mode}")

        if mode == "deontic":
            sort_type = event_data.get("sort_type", "cost")
            threshold_value = event_data.get("threshold_value")
            recommendations = SNCF_deontic(
                event_json, context_json, RECOMMENDATION_CATALOG,
                type=sort_type, threshold_value=threshold_value,
            )
        elif mode == "risk":
            sort_type = event_data.get("sort_type", "cost")
            recommendations = SNCF_risk(
                event_json, context_json, RECOMMENDATION_CATALOG,
                type=sort_type,
            )
        elif mode == "risk_tie_break":
            sort_type = event_data.get("sort_type", "cost")
            tie_breaker = event_data.get("tie_breaker")
            recommendations = SNCF_risk_tie_break(
                event_json, context_json, RECOMMENDATION_CATALOG,
                type=sort_type, tie_breaker=tie_breaker,
            )
        else:  # "basic" or any unrecognised mode
            recommendations = SNCF_RECO3(event_json, context_json, RECOMMENDATION_CATALOG)

        # Surface catalog errors as an empty list rather than crashing downstream
        if recommendations and isinstance(recommendations[0], dict) and "error" in recommendations[0]:
            logger.error(f"Recommendation error: {recommendations[0]['error']}")
            return []

        return [self._transform_recommendation(reco) for reco in recommendations]
