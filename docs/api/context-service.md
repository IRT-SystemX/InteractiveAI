# Context Service API

The Context Service collects and analyzes data related to the current operating environment: external conditions, controlled-system state, operator cognitive load, and mission parameters. The HMI module polls it continuously to display real-time context to the operator.

**Base path:** `/cab_context/api/v1`

> **Authentication required** — All requests must include a bearer token in the `Authorization` header. See [Authentication](./authentication.md) for how to obtain one.
---

## Send a context update

```http
POST http://{Platform_Server}/cab_context/api/v1/contexts
Content-Type: application/json
```

### Generic payload

| Field | Type | Required | Description |
|---|---|---|---|
| `use_case` | string | ✅ | Identifier for the application domain / use case |
| `date` | datetime | ✅ | Timestamp of the context snapshot (ISO 8601) |
| `data` | object | ❌ | Use-case-specific context information (see below) |

### Use-case-specific data (`data` field)

As with events, the `data` field carries domain-specific context that the HMI uses to render its context view.

**Example — Power grid use case:**
```json
{
  "use_case": "Powergrid",
  "date": "2024-03-15T10:23:00Z",
  "data": {
    "grid_load_percent": 87.3,
    "weather": "storm",
    "operator_shift": "night",
    "active_incidents": 2
  }
}
```

**Example — Railway use case:**
```json
{
  "use_case": "Railway",
  "date": "2024-03-15T10:00:00",
  "data": {
    "trains": [
      {
        "id_train": "AB001",
        "nb_passengers_onboard": "459",
        "trip": "Paris/Bordeaux",
        "stops": "Angoulême/Bordeaux",
        "failure": false
      }
    ]
  }
}
```
> The `trains` array accepts multiple train objects. Optional fields include `nb_passengers_connection`, `latitude`, `longitude`, and `speed` — omit them if not available.

**Example — ATM use case:**
```json
{
  "use_case": "ATM",
  "date": "2024-03-15T10:00:00",
  "data": {
    "ApDest": "LFBO",
    "Current_airspeed": 450,
    "Latitude": 43.6295,
    "Longitude": 1.3637,
    "wpList": ["TOU", "LESDO", "LFBO"]
  }
}
```

> `wpList` is the list of remaining waypoints for the aircraft. `ApDest` is the destination airport (ICAO code).
---

## Retrieve current context

Called by the HMI module to get the context at a given point in time. The platform automatically filters results to the running use case of the connected operator.

```http
GET http://{Platform_Server}/cab_context/api/v1/contexts/{date}
```

| Parameter | Location | Description |
|---|---|---|
| `date` | Path | ISO 8601 timestamp — returns the context closest to this date |

---

## Postman collection

[Context-service.postman_collection.json](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Context-service.postman_collection.json)
