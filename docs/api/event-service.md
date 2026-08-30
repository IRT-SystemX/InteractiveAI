# Event Service API

The Event Service receives incoming messages, categorizes them, prioritizes tasks, and forwards notifications to the HMI frontend. It also maintains the system timeline.

**Base path:** `/cab_event/api/v1`

> **Authentication required** — All requests must include a bearer token in the `Authorization` header. See [Authentication](./authentication.md) for how to obtain one.
---

## Send an event

```http
POST http://{Platform_Server}/cab_event/api/v1/events
Content-Type: application/json
```

### Generic payload

| Field | Type | Required | Description |
|---|---|---|---|
| `use_case` | string | ✅ | Identifier for the application domain / use case (PowerGrid, Railway, ATM) |
| `title` | string | ✅ | Short title of the event |
| `description` | string | ✅ | Human-readable description of the event |
| `criticality` | string/int | ✅ | Severity level of the event (HIGH, MEDIUM, LOW) |
| `start_date` | datetime | ✅ | When the event started (ISO 8601) |
| `end_date` | datetime | ❌ | When the event ended — omit if unknown |
| `parent_event_id` | string | ❌ | ID of the parent event, if this event is a consequence of another |
| `data` | object | ❌ | Use-case-specific payload (see below) |

### Use-case-specific data (`data` field)

The `data` field is a free-form object used to pass domain-specific information. This data can be consumed by use-case-specific HMI components.

**Example — Power grid use case:**
```json
{
  "use_case": "power_grid",
  "title": "Line overload detected",
  "description": "Transmission line L42 is operating above rated capacity.",
  "criticality": "HIGH",
  "start_date": "2024-03-15T10:23:00Z",
  "data": {
    "line_id": "L42",
    "load_percentage": 112.5,
    "substation": "SUB-07"
  }
}
```

**Example — Railway  use case:**
```json
{
  "use_case": "Railway",
  "criticality": "HIGH",
  "title": "Passenger taken ill in Poitiers",
  "description": "Passenger taken ill in TGV AB001. Emergency services intervention in the Poitiers station. Impossible to access the Poitiers station. Estimated time of service traffic resumption: 12:00.",
  "start_date": "2024-03-15T10:00:00",
  "end_date": "2024-03-15T12:00:00",
  "data": {
    "id_event": "1",
    "event_type": "PASSENGER",
    "id_train": "AB001",
    "agent_id": "1",
    "delay": 0
  }
}
```
> `event_type` can be `PASSENGER`, `INFRASTRUCTURE`, `IMPACT`, or `HARDWARE`.
> 
**Example — ATM use case:**
```json
{
  "use_case": "ATM",
  "criticality": "HIGH",
  "title": "Plane in unauthorized sector",
  "description": "Aircraft AF1234 has entered sector TMA-NW without clearance. The aircraft is currently at FL320, deviating from its assigned route. Immediate coordination required with adjacent sector control.",
  "start_date": "2024-03-15T10:00:00",
  "end_date": "2024-03-15T10:30:00",
  "data": {
    "system": "none",
    "event_type": "sectorization",
    "id_plane": "1"
  }
}
```

### Response

On success, the API returns the created event object including its generated `id`.

---

## Postman collection

[Event-service.postman_collection.json](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Event-service.postman_collection.json)
