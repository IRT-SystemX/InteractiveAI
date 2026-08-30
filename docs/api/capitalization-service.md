# Capitalization Service API

The Capitalization Service stores operator feedback on recommendations — whether a recommendation was accepted or rejected. This data is used to improve AI models over time.

This API is called automatically by the HMI module when the operator makes a decision. It is documented here for reference.

**Base path:** `/cab_capitalization/api/v1`

---

## Store feedback

```http
POST http://{Platform_Server}/cab_capitalization/api/v1/feedbacks
Content-Type: application/json
```

### Feedback object

| Field | Type | Description |
|---|---|---|
| `event_id` | string | ID of the event that triggered the recommendation request |
| `context_id` | string | ID of the context at the time of the decision |
| `date` | datetime | Timestamp of the feedback (ISO 8601) |
| `feedback` | boolean | `true` if the recommendation was chosen, `false` if rejected |
| `recommendation` | object | The full recommendation object that was accepted or rejected |

### Example

```json
{
  "event_id": "evt_00312",
  "context_id": "ctx_00178",
  "date": "2024-03-15T10:31:00Z",
  "feedback": true,
  "recommendation": {
    "title": "Reroute traffic via L45",
    "description": "Redirect load from L42 to L45.",
    "agent_type": "AI",
    "actions": [
      { "type": "reroute", "line_from": "L42", "line_to": "L45", "load_percent": 70 }
    ]
  }
}
```

---

## Postman collection

[Capitalisation-service.postman_collection.json](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Capitalisation-service.postman_collection.json)
