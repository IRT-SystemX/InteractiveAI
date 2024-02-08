import json
import uuid

import pytest
from settings import logger
from api.models import ContextModel, db
from datetime import datetime

RTE_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQzMzMyNjEsImlhdCI6MTY4MzcyODQ2MSwianRpIjoiNzE2YjAyZDQtMjliYS00MWJkLTg1YjItODAwNGNlYzFhMDMzIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJydGVfdXNlciIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9wZmFiLWNsaWVudCIsInNlc3Npb25fc3RhdGUiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJzaWQiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImdyb3VwcyI6IkRpc3BhdGNoZXI7UmVhZE9ubHk7U3VwZXJ2aXNvciIsInByZWZlcnJlZF91c2VybmFtZSI6InJ0ZV91c2VyIiwiZ2l2ZW5fbmFtZSI6IiIsImVudGl0aWVzSWQiOiJSVEUiLCJmYW1pbHlfbmFtZSI6IiJ9.j-_kiNnn5jQtUBMZ-oaeWVVfZLM1dWLFjRYKfL9pkpklG-CAVl1CuUQE969YkaPZLD4TtXaiNy02LhkIWmSwQuks2lH5_dtUlCBlpIouD1liDxg1g_oXn_m3vKwzDQ03KeeVC03BCMJR8gDTED80U-vjXT33-BngpjMP2rFMZRiZIJO_BB4GnIf55dnazWj8jbp0MVZYS9fuNeuLLrRgMevGDn5s-AlznmWLce1K6P882StmhI0unRXVOTRae8xRvDkk0BJ545K9FtLoZtgOeyEw7JrvElkPMqWKOy3R5hmpJENZSV1zCMBdXusVi7GTyn4denCqA7yYerWi_yaITg"
DA_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQ0MDEyMTksImlhdCI6MTY4Mzc5NjQxOSwianRpIjoiYTI4NzM0ZjYtZjVjOC00MTMwLThmYjctNTczZDc1YzM5ZDhjIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJkYV91c2VyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoib3BmYWItY2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6ImJkM2I4NjEwLTFkMDUtNGJkZC05MTZiLTYxZGNmZTZkNWU3MiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6ImJkM2I4NjEwLTFkMDUtNGJkZC05MTZiLTYxZGNmZTZkNWU3MiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZ3JvdXBzIjoiUlRFO0FETUlOO1JlYWRPbmx5IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZGFfdXNlciIsImVudGl0aWVzSWQiOiJEQSJ9.RKl9ndaXW_EdMW81YRBxuwQhcRaZwvlfSG1H0ms1ElySp-XGnunvdNuj6VLwB56_wjdijPUnqOrKAsYMxa9lGipUzeAIdbPFojO1Et1IxGQSyqxJTX9ngpSQi3btJM3eP1bQ3bHSLNKIdSpZrCdhhxP8-s6vHa__7RcIMxSBvYjX-tT97qQBubqqHdSouAJP1RZYn1_G8T6Pzs1hK2RXseMRYvBUAtXD24-Lk9IaRB9GUO5P9MCb_VldqUEPAWM5rVkjxrojAUB0OM1NGcge1jiQotHyeqBPnB5oHD_2LdygbsuO5i1t4Z5y4Q2JxyMzrR4nyh3lrSjhUf60cfFpEA"
SNCF_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQ0MDE2OTAsImlhdCI6MTY4Mzc5Njg5MCwianRpIjoiN2MzZTQ2YzUtYTliOC00ZTRmLWFmYjAtZjBlODU5Y2U3YzA1IiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJzbmNmX3VzZXIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJvcGZhYi1jbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiM2MwNzRmNTMtODMxNy00NTE5LTk1MGMtOWZlOTE1ZjVjY2QwIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJlbWFpbCBwcm9maWxlIiwic2lkIjoiM2MwNzRmNTMtODMxNy00NTE5LTk1MGMtOWZlOTE1ZjVjY2QwIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzbmNmX3VzZXIiLCJlbnRpdGllc0lkIjoiU05DRiJ9.LZzZGg8Gu73_8HKzAPZJdR1E_e_NPyt-Q_d0lV7YzL2zjO0_q5-F08QG8nZYBoIAK_2C10Ho7qABHNTBeIR0Oe9NQnvyRn85YGLlx1k495e9p2-ZGNAh-JBbZ20ohEoghEbRAmR304gr_fKqVBM5QoxZrYdApMRbMfGuR_vGlUaQwnuG_p5uHu0wU_3SFItOtg1cSEWgviKnEt5gNuQ3D8zWAN1YtYivpqraYwQRdbENjXtxJCWsIgK-nclAWilan3vEGHGLBhZ8FCYw0U670YnlXOoe2wnFXEwt20maJzidPXA7XhEjbmUo9J-yEgEnjWspvcQhNwgsisx8P2Jyqw"
ORANGE_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQ3NjY4NTksImlhdCI6MTY4NDE2MjA1OSwianRpIjoiNDE4ZGVlMmItYWFjNi00NTJlLWE5MGYtMzIyNzhlMzRhMjJiIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJvcmFuZ2VfdXNlciIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9wZmFiLWNsaWVudCIsInNlc3Npb25fc3RhdGUiOiI1Mjk3ODA1ZC1mYzczLTRkOTQtOTdmYy0wYzVhNTJjNDE0NDAiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJzaWQiOiI1Mjk3ODA1ZC1mYzczLTRkOTQtOTdmYy0wYzVhNTJjNDE0NDAiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImdyb3VwcyI6IlJURTtBRE1JTjtSZWFkT25seSIsInByZWZlcnJlZF91c2VybmFtZSI6Im9yYW5nZV91c2VyIiwiZW50aXRpZXNJZCI6Ik9SQU5HRSJ9.KriZd2FZT39Yi8LD2lnVGJad9nEZ00W7rQzcTaFBbGjh9AnfgC6bEwmH20u0d61ldHA0KcH9_NC8LolNhRDjGqA6QDy8l-nA67VUK-CT_9uj9bW9oo8LVHCKn-pcK2t6LlPFexQjSeb0-rK9_jA-O-7rAdXQVEhYc1shxJYTNhNqtwmEBE_QApmDTocoIBPA6jUzqGWh0wUMswmKVPAUU1yWDBUBVDsRCcKVRAO2p-P64CxyXC0R1RRSGZ1i4jexggjeIfyrARXkJrjcAMYAu4HBi8k91vDd6KBiJs45TVm9_5rrW25ZASWTPUO4fuuaz3k47DTUGQBNstO483ZrkA"
PUBLISHER_TEST_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2OTk5Nzk0NTEsImlhdCI6MTY5OTM3NDY1MSwianRpIjoiMjg5YTg5MDUtOTQ0YS00MGIwLWJkYTYtNzU5ODkzZWVmODFmIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvYXV0aC9yZWFsbXMvZGV2IiwiYXVkIjoiYWNjb3VudCIsInN1YiI6InB1Ymxpc2hlcl90ZXN0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoib3BmYWItY2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6ImI1ZjUwZTc0LTYwOWEtNGI5MC1iMDhkLTFjNDQwM2MyMGMzYSIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6ImI1ZjUwZTc0LTYwOWEtNGI5MC1iMDhkLTFjNDQwM2MyMGMzYSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZ3JvdXBzIjoiRGlzcGF0Y2hlcjtSZWFkT25seTtTdXBlcnZpc29yIiwicHJlZmVycmVkX3VzZXJuYW1lIjoicHVibGlzaGVyX3Rlc3QiLCJnaXZlbl9uYW1lIjoiIiwiZmFtaWx5X25hbWUiOiIifQ.RddLBhlhPMZst7TIRe10goMEZCriUchF9qNLBG889dnRP_YRh_bc-63cPeDbPG-YmeiXiQGJ3CJ9xGvc7uQl7iKLtCrBtTqn0A1IKOWmCrfaQ_czTyNKz5mrlU9HmzpO6H534Wjrx4uylwwhXrjuO7c06wZvn03tpNrBdoIVvCQqyInfY_QDoOttXU6-dj8S6aZavAsPDSNSrfzgiP33VT5Y0atoiHZ4gNvIeRAFIl6VrbAAQ7YkVDwzHAMPcA4QC4_k6t_m9t8KJ5otdzicDS6QJLV9hKUGzFPKJN60FSmscE9Gs7Uud_EGT-9GA_i53-1Pzxq6EWr-BkQ28kQDFQ"


def test_get_all_rte_contexts(client, create_usecases, create_contexts, rte_auth_mocker):
    headers = {"Authorization": f"Bearer {RTE_BEARER_TOKEN}"}
    response = client.get("/api/v1/contexts", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1


def test_add_rte_context(client, create_usecases, rte_auth_mocker):
    context_data = {
        "date": "2022-12-01T16:08:29.060050",
        "data": {"observation": {"rho": 11}, "topology": "iii"},
        "use_case": "RTE",
    }
    headers = {"Authorization": f"Bearer {RTE_BEARER_TOKEN}"}
    response = client.post(
        "/api/v1/contexts", headers=headers, json=context_data
    )
    assert response.status_code == 201


def test_add_da_context(client, create_usecases, da_auth_mocker):
    context_data = {
        "data": {
            "ApDest": {
                "apcity": "LE BOURGET",
                "apid": "LFPB",
                "aplat": 48.969,
                "aplon": 2.441,
                "apname": "LE BOURGET Airport"
            },
            "Current_airspeed": 202.8167266845703,
            "Latitude": 48.45396423339844,
            "Longitude": 3.3079421520233154,
            "wpList": [
                {
                    "wpid": "PG102",
                    "wpidx": 1,
                    "wplat": 48.720722,
                    "wplon": 2.590194
                },
                {
                    "wpid": "PG518",
                    "wpidx": 2,
                    "wplat": 48.816667,
                    "wplon": 2.489056
                },
                {
                    "wpid": "PG515",
                    "wpidx": 3,
                    "wplat": 48.916222,
                    "wplon": 2.459417
                }
            ]
        },
        "date": "2023-12-05T08:51:49.341641",
        "use_case": "DA"
    }
    headers = {"Authorization": f"Bearer {DA_BEARER_TOKEN}"}
    response = client.post(
        "/api/v1/contexts", headers=headers, json=context_data
    )
    logger.info(response.text)
    assert response.status_code == 201


def test_add_sncf_context(client, create_usecases, sncf_auth_mocker):
    context_data = {
        "date": "2022-12-01T16:08:29.060050",
        "data": {
            "trains": [
                {
                    "id_train": "12345",
                    "nb_passengers_onboard": 200,
                    "nb_passengers_connection": 13,
                    "latitude": "45.8574215",
                    "longitude": "4.4819996",
                    "speed": 300,
                    "failure": False,
                }
            ]
        },
        "use_case": "SNCF",
    }

    headers = {"Authorization": f"Bearer {SNCF_BEARER_TOKEN}"}
    response = client.post(
        "/api/v1/contexts", headers=headers, json=context_data
    )
    logger.info(response.text)
    assert response.status_code == 201


def test_add_orange_context(client, create_usecases, orange_auth_mocker):
    context_data = {
        "date": "2022-11-01T16:08:29.060050",
        "data": {
            "applications": [
                {
                    "application_id": "1",
                    "KPI": {
                        "nb_req": 2000,
                        "nb_err": 100,
                        "nb_pl": 100,
                        "delay_avg": 1,
                    },
                    "Horodatage": "date",
                    "KPI_composite": {"ratio_pl": "", "ratio_err": ""},
                }
            ]
        },
        "use_case": "ORANGE",
    }
    headers = {"Authorization": f"Bearer {SNCF_BEARER_TOKEN}"}
    response = client.post(
        "/api/v1/contexts", headers=headers, json=context_data
    )
    logger.info(response.text)
    assert response.status_code == 201


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_get_with_use_case(
    client, create_usecases, create_contexts, publisher_test_auth_mocker
):
    headers = {"Authorization": f"Bearer {PUBLISHER_TEST_BEARER_TOKEN}"}
    response = client.get("/api/v1/contexts?use_case=RTE", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["date"] == "2022-11-07T16:06:00.741655"


def test_get_with_use_case_and_date(
    client, create_usecases, create_contexts
):
    headers = {"Authorization": f"Bearer {PUBLISHER_TEST_BEARER_TOKEN}"}
    response = client.get(
        "/api/v1/contexts?use_case=RTE&date=2022-11-07T16:06:00.741655",
        headers=headers,
    )
    logger.error(response.json)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["date"] == "2022-11-07T16:06:00.741655"
