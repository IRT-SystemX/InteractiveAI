import json
import uuid

import pytest
from settings import logger
from api.models import ContextModel, db
from datetime import datetime

RTE_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODQzMzMyNjEsImlhdCI6MTY4MzcyODQ2MSwianRpIjoiNzE2YjAyZDQtMjliYS00MWJkLTg1YjItODAwNGNlYzFhMDMzIiwiaXNzIjoiaHR0cDovLzE5Mi4xNjguMjExLjk1OjMyMDAvcmVhbG1zL2RldiIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJydGVfdXNlciIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9wZmFiLWNsaWVudCIsInNlc3Npb25fc3RhdGUiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJzaWQiOiI4OTc2YjEyNS0zOWE4LTRiZGYtYjUyMy03ZTBkY2JjZGQzYjQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImdyb3VwcyI6IkRpc3BhdGNoZXI7UmVhZE9ubHk7U3VwZXJ2aXNvciIsInByZWZlcnJlZF91c2VybmFtZSI6InJ0ZV91c2VyIiwiZ2l2ZW5fbmFtZSI6IiIsImVudGl0aWVzSWQiOiJSVEUiLCJmYW1pbHlfbmFtZSI6IiJ9.j-_kiNnn5jQtUBMZ-oaeWVVfZLM1dWLFjRYKfL9pkpklG-CAVl1CuUQE969YkaPZLD4TtXaiNy02LhkIWmSwQuks2lH5_dtUlCBlpIouD1liDxg1g_oXn_m3vKwzDQ03KeeVC03BCMJR8gDTED80U-vjXT33-BngpjMP2rFMZRiZIJO_BB4GnIf55dnazWj8jbp0MVZYS9fuNeuLLrRgMevGDn5s-AlznmWLce1K6P882StmhI0unRXVOTRae8xRvDkk0BJ545K9FtLoZtgOeyEw7JrvElkPMqWKOy3R5hmpJENZSV1zCMBdXusVi7GTyn4denCqA7yYerWi_yaITg"
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
