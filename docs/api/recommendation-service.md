# Recommendation Service API

The Recommendation Service is called by the HMI module when an operator requests help. It returns a list of recommendations combining AI-generated solutions and ontology-based solutions.

> **Note:** This API is called internally by the platform. External integrators interact with recommendations indirectly — by receiving the selected recommendation's actions at their simulator callback endpoint (`POST http://{Simulator_server}/api/v1/recommendations`).

**Base path:** `/cab_recommendation/api/v1`

---

## Get recommendations

```http
POST http://{Platform_Server}/cab_recommendation/api/v1/recommendation
Content-Type: application/json
```

### Request body

| Field | Type | Description |
|---|---|---|
| `event` | object | The current event object |
| `context` | object | The current context object |

### Response

Returns an array of recommendation objects.

### Recommendation object

| Field | Type | Description |
|---|---|---|
| `title` | string | Short label displayed on the HMI |
| `description` | string | Detailed explanation of the recommendation |
| `kpis` | array | *(Optional)* List of KPI objects for comparing recommendations side-by-side |
| `agent_type` | string | Source of the recommendation — `AI` or `onto` (ontology) |
| `actions` | array | List of actions to send to the simulator when this recommendation is chosen |

### Example response

```json
[
  {
    "title": "Reroute traffic via L45",
    "description": "Redirect load from L42 to L45 to bring L42 below rated capacity.",
    "agent_type": "AI",
    "kpis": [
      { "name": "Load reduction on L42", "value": "18%", "unit": "%" },
      { "name": "Estimated time to restore", "value": "5", "unit": "min" }
    ],
    "actions": [
      { "type": "reroute", "line_from": "L42", "line_to": "L45", "load_percent": 70 }
    ]
  },
  {
    "title": "Reduce generation at G3",
    "description": "Lower output at generator G3 to reduce grid stress.",
    "agent_type": "onto",
    "kpis": [
      { "name": "Load reduction on L42", "value": "12%", "unit": "%" }
    ],
    "actions": [
      { "type": "set_generation", "generator": "G3", "output_mw": 80 }
    ]
  }
]
```

### Simulator callback

When the operator selects a recommendation, the platform forwards its `actions` array to your simulator:

```http
POST http://{Simulator_server}/api/v1/recommendations
Content-Type: application/json

{ "actions": [ ... ] }
```

You must implement this endpoint in your simulator.

---

## Postman collection

[Recommendation-service.postman_collection.json](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Recommendation-service.postman_collection.json)
