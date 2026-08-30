# InteractiveAI

InteractiveAI is an open-source platform for monitoring and managing complex industrial networks. It integrates human-machine interaction and human expertise to optimize AI performance in demanding operational environments.

## Documentation

- [Platform Overview](./overview.md) — Architecture, services, and integration model
- [Getting Started](./getting-started.md) — How to connect your system to the platform

### API Reference

| Service | Description |
|---|---|
| [Event Service](./api/event-service.md) | Push events into the platform |
| [Context Service](./api/context-service.md) | Push context updates to the platform |
| [Historic Service](./api/historic-service.md) | Event and action log; report generation |
| [Recommendation Service](./api/recommendation-service.md) | AI and ontology-based recommendations |
| [Capitalization Service](./api/capitalization-service.md) | Operator feedback storage |

## Quick start

External systems only need to call two APIs:

```http
# 1. Send an event
POST http://{Platform_Server}/cab_event/api/v1/events

# 2. Send a context update
POST http://{Platform_Server}/cab_context/api/v1/contexts
```

See [Getting Started](./getting-started.md) for full details, including the simulator callback endpoint you need to implement.

## Source

Based on the [IRT-SystemX/InteractiveAI](https://github.com/ainetus/InteractiveAI) platform.
