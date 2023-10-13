from resources.sncf.hypervisor import Hypervisor
from .base_recommendation import BaseRecommendation
from flask import current_app
import os


class SNCFManager(BaseRecommendation):
    def __init__(self) -> None:
        super().__init__()
        self.root_path = current_app.config["ROOT_PATH"]
        self.hypervisor_path = os.path.join(
            self.root_path, "resources/sncf/hypervisor.pth"
        )
        self.hypervisor = Hypervisor()
        self.hypervisor.load(self.hypervisor_path)

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        raw_position_agents = context_data.get("position_agents")
        raw_list_of_target = context_data.get("list_of_target")
        direction_agents = context_data.get("direction_agents")

        event_data = request_data.get("event", {})

        malfunction_agent = event_data.get("agent_id")
        malfunction_position = tuple(event_data.get("agent_position"))
        malfunction_delay = event_data.get("delay")

        position_agents = [
            tuple(value) for value in raw_position_agents.values()
        ]

        list_of_target = [
            [tuple(target) for target in agent_targets]
            for agent_targets in raw_list_of_target.values()
        ]

        """
        ai_actions, ai_description = self.hypervisor.recommend(position_agents,
                                                   direction_agents,
                                                   list_of_target,
                                                   malfunction_agent,
                                                   malfunction_position,
                                                   malfunction_delay)
        ai_recommendation = {
            "title": "Modification de plan de transport",
            "description": ai_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [{"transportation_plan":ai_actions}]
            }
        """

        fake_transport_plan = {
            "simulation_name": "bordeaux_tours_sim",
            "targets_list": [
                {
                    "agent_id": "0",
                    "targets": [],
                },
                {
                    "agent_id": "1",
                    "targets": [
                        {
                            "passengers": 0,
                            "target_id": 10,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 16,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 20,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 22,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 2,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 28,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 33,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 34,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 40,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 44,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 48,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 70,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 74,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 80,
                            "target_type": "STATION",
                        }
                    ],
                },
                {
                    "agent_id": "2",
                    "targets": [
                        {
                            "passengers": 0,
                            "target_id": 10,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 16,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 20,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 22,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 2,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 28,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 33,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 34,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 40,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 44,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 48,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 70,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 73,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 78,
                            "target_type": "STATION",
                        },
                        {
                            "passengers": 0,
                            "target_id": 0,
                            "target_type": "STATION",
                        }
                    ],
                },
            ],
        }

        fake_description = "Train 7652 : Annuler l'arrêt à la gare de Poitiers, passer par la LGV, arrêt suivant Angoulême.\n\nTrain 5440 : Annuler l'arrêt à la gare de Poitiers, passer par la LGV, arrêt suivant Angoulême."

        fake_recommendation = {
            "title": "Annuler l'arrêt à Poitiers",
            "description": fake_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [fake_transport_plan],
        }

        recommendation = [fake_recommendation]

        return recommendation
