import json

import pytest

from settings import logger

RTE_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQzMzMyNjEsImlhdCI6MTY4MzcyODQ2MSwianRpIjoiNzE2YjAyZDQtMjliYS00MWJkLTg1YjItODAwNGNlYzFhMDMzIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJydGVfdXNlciIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9wZmFiLWNsaWVudCIsInNlc3Npb25fc3RhdGUiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJzaWQiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImdyb3VwcyI6IkRpc3BhdGNoZXI7UmVhZE9ubHk7U3VwZXJ2aXNvciIsInByZWZlcnJlZF91c2VybmFtZSI6InJ0ZV91c2VyIiwiZ2l2ZW5fbmFtZSI6IiIsImVudGl0aWVzSWQiOiJSVEUiLCJmYW1pbHlfbmFtZSI6IiJ9.j-_kiNnn5jQtUBMZ-oaeWVVfZLM1dWLFjRYKfL9pkpklG-CAVl1CuUQE969YkaPZLD4TtXaiNy02LhkIWmSwQuks2lH5_dtUlCBlpIouD1liDxg1g_oXn_m3vKwzDQ03KeeVC03BCMJR8gDTED80U-vjXT33-BngpjMP2rFMZRiZIJO_BB4GnIf55dnazWj8jbp0MVZYS9fuNeuLLrRgMevGDn5s-AlznmWLce1K6P882StmhI0unRXVOTRae8xRvDkk0BJ545K9FtLoZtgOeyEw7JrvElkPMqWKOy3R5hmpJENZSV1zCMBdXusVi7GTyn4denCqA7yYerWi_yaITg"
DA_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQ0MDEyMTksImlhdCI6MTY4Mzc5NjQxOSwianRpIjoiYTI4NzM0ZjYtZjVjOC00MTMwLThmYjctNTczZDc1YzM5ZDhjIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJkYV91c2VyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoib3BmYWItY2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6ImJkM2I4NjEwLTFkMDUtNGJkZC05MTZiLTYxZGNmZTZkNWU3MiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6ImJkM2I4NjEwLTFkMDUtNGJkZC05MTZiLTYxZGNmZTZkNWU3MiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZ3JvdXBzIjoiUlRFO0FETUlOO1JlYWRPbmx5IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZGFfdXNlciIsImVudGl0aWVzSWQiOiJEQSJ9.RKl9ndaXW_EdMW81YRBxuwQhcRaZwvlfSG1H0ms1ElySp-XGnunvdNuj6VLwB56_wjdijPUnqOrKAsYMxa9lGipUzeAIdbPFojO1Et1IxGQSyqxJTX9ngpSQi3btJM3eP1bQ3bHSLNKIdSpZrCdhhxP8-s6vHa__7RcIMxSBvYjX-tT97qQBubqqHdSouAJP1RZYn1_G8T6Pzs1hK2RXseMRYvBUAtXD24-Lk9IaRB9GUO5P9MCb_VldqUEPAWM5rVkjxrojAUB0OM1NGcge1jiQotHyeqBPnB5oHD_2LdygbsuO5i1t4Z5y4Q2JxyMzrR4nyh3lrSjhUf60cfFpEA"
SNCF_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQ0MDE2OTAsImlhdCI6MTY4Mzc5Njg5MCwianRpIjoiN2MzZTQ2YzUtYTliOC00ZTRmLWFmYjAtZjBlODU5Y2U3YzA1IiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJzbmNmX3VzZXIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJvcGZhYi1jbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiM2MwNzRmNTMtODMxNy00NTE5LTk1MGMtOWZlOTE1ZjVjY2QwIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwic2lkIjoiM2MwNzRmNTMtODMxNy00NTE5LTk1MGMtOWZlOTE1ZjVjY2QwIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzbmNmX3VzZXIiLCJlbnRpdGllc0lkIjoiU05DRiJ9.LZzZGg8Gu73_8HKzAPZJdR1E_e_NPyt-Q_d0lV7YzL2zjO0_q5-F08QG8nZYBoIAK_2C10Ho7qABHNTBeIR0Oe9NQnvyRn85YGLlx1k495e9p2-ZGNAh-JBbZ20ohEoghEbRAmR304gr_fKqVBM5QoxZrYdApMRbMfGuR_vGlUaQwnuG_p5uHu0wU_3SFItOtg1cSEWgviKnEt5gNuQ3D8zWAN1YtYivpqraYwQRdbENjXtxJCWsIgK-nclAWilan3vEGHGLBhZ8FCYw0U670YnlXOoe2wnFXEwt20maJzidPXA7XhEjbmUo9J-yEgEnjWspvcQhNwgsisx8P2Jyqw"


def test_get_all_rte_events(
    client, create_usecases, rte_auth_mocker, create_events
):
    headers = {"Authorization": f"Bearer {RTE_BEARER_TOKEN}"}
    response = client.get("/api/v1/events", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1


def test_get_events_for_use_case(
    client, create_usecases, rte_auth_mocker, create_events
):
    headers = {"Authorization": f"Bearer {RTE_BEARER_TOKEN}"}
    response = client.get("/api/v1/events?use_case=RTE", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["use_case"] == "RTE"


def test_add_rte_event(
    client, create_usecases, rte_auth_mocker, mock_of_create_cards_request
):
    event_data = {
        "criticality": "MEDIUM", 
        "title": "Risque sur al\u00e9a N-1 sur la ligne 44_45_126", 
        "description": "Lignes impact\u00e9es 44_48_133, charge max 149.5%", 
        "data": {
            "event_type": "anticipation", 
            "line": "44_45_126", 
            "flux": 149.5, 
            "kpis": {
                "max_overload": "", 
                "renewable_energy_share": 0.5082022502483139, 
                "total_consumption": 1177.619999885559, 
                "distance_from_reference_topology": 0.0,
                "curtailment_volume": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                "redispatching_volume": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            },
        }, 
        "use_case": "RTE", 
        "is_active": False,
    }
    headers = {"Authorization": f"Bearer {RTE_BEARER_TOKEN}"}
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    assert response.status_code == 201


def test_update_rte_event_if_exist(
    client, create_usecases, rte_auth_mocker, mock_of_create_cards_request
):

    event_data = {
        "criticality": "MEDIUM", 
        "title": "Risque sur al\u00e9a N-1 sur la ligne 44_45_126", 
        "description": "Lignes impact\u00e9es 44_48_133, charge max 149.5%", 
        "data": {
            "event_type": "anticipation", 
            "line": "44_45_126", 
            "flux": 149.5, 
            "kpis": {
                "max_overload": "", 
                "renewable_energy_share": 0.5082022502483139, 
                "total_consumption": 1177.619999885559, 
                "distance_from_reference_topology": 0.0,
                "curtailment_volume": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                "redispatching_volume": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            },
        }, 
        "use_case": "RTE", 
        "is_active": False,
    }
    headers = {"Authorization": f"Bearer {SNCF_BEARER_TOKEN}"}

    # Create intial event
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["criticality"] == "ROUTINE"

    # Create with same id_train
    event_data["criticality"] = "HIGH"
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    assert response.status_code == 201

    # Verify their is only one event
    response = client.get("/api/v1/events", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["criticality"] == "HIGH"


def test_add_da_event(
    client, create_usecases, da_auth_mocker, mock_of_create_cards_request
):
    event_data = {
        "criticality": "HIGH",
        "title": "90 PRESS: CABIN ALT TOO HI",
        "description": "Cabin altitude exceeding: 8,300 ft, OR 14,200 ft when high airfield operation is active.",
        "data": {
            "system": "AIR CONDITIONING AND PRESSURIZATION",
            "event_type": "90 PRESS: CABIN ALT TOO HI",
            "id_plane" : "1"
        },
        "use_case": "DA",
    }
    headers = {"Authorization": f"Bearer {DA_BEARER_TOKEN}"}
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    logger.info(response.text)
    logger.error(response.text)
    print(response.text)
    assert response.status_code == 201


def test_add_sncf_event(
    client, create_usecases, sncf_auth_mocker, mock_of_create_cards_request
):
    event_data = {
        "title": "PASSENGER - TGV 8404",
        "criticality": "MEDIUM",
        "data": {
            "agent_id": "0",
            "agent_position": [220, 2],
            "delay": 55,
            "event_type": "PASSENGER",
            "id_train": "8404",
            "malfunction_stop_position": [94, 2],
            "num_rame": "18",
            "tmp_rame": "27",
        },
        "start_date": "2023-04-11T06:20:12",
        "description": "0 is having PASSENGER malfunction",
        "is_active": True,
        "use_case": "SNCF",
    }

    headers = {"Authorization": f"Bearer {SNCF_BEARER_TOKEN}"}
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    logger.info(response.text)
    assert response.status_code == 201


def test_update_sncf_event_if_exist(
    client, create_usecases, sncf_auth_mocker, mock_of_create_cards_request
):

    event_data = {
        "title": "PASSENGER - TGV 8404",
        "criticality": "MEDIUM",
        "data": {
            "agent_id": "0",
            "agent_position": [220, 2],
            "delay": 55,
            "event_type": "PASSENGER",
            "id_train": "8404",
            "malfunction_stop_position": [94, 2],
            "num_rame": "18",
            "tmp_rame": "27",
        },
        "start_date": "2023-04-11T06:20:12",
        "description": "0 is having PASSENGER malfunction",
        "is_active": True,
        "use_case": "SNCF",
    }

    headers = {"Authorization": f"Bearer {SNCF_BEARER_TOKEN}"}

    # Create intial event
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["criticality"] == "MEDIUM"

    # Create with same id_train
    event_data["criticality"] = "HIGH"
    response = client.post("/api/v1/events", headers=headers, json=event_data)
    assert response.status_code == 201

    # Verify their is only one event
    response = client.get("/api/v1/events", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["criticality"] == "HIGH"


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
