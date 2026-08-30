# InteractiveAI Platform — Overview

InteractiveAI is an open-source framework designed for industries that need to monitor and manage complex networks. It integrates human-machine interactions and human expertise to optimize AI performance, and streamlines the integration of advanced AI modules for demanding operational environments.

## Architecture

The platform follows a 3-tier architecture:

| Layer | Role |
|---|---|
| **Presentation (Frontend)** | Browser rendering and user interaction (HMI module) |
| **Services** | Business logic, AI modules, and application rules |
| **Data** | Persistent storage — databases, files, knowledge base, and ontology |

An HTTP **Gateway** sits at the entry point of the services layer and routes incoming requests to the appropriate service based on the API called.

## Services

Services are split into two categories:

### Support Services
Pure software services (no AI) that underpin the supervision feature:

- **Event Service** — Ingests incoming messages, categorizes and prioritizes events, sends notifications to the frontend, and maintains the timeline.
- **Context Service** — Collects and analyzes internal and external context data (environment, operator cognitive load, mission parameters) and keeps the current context up to date.
- **Historic Service** — Tracks all events and operator actions in a log database.

### AI / Business Services

- **Recommendation Service** — Handles requests for AI-generated and ontology-based recommendations in response to events.
- **Knowledge Acquisition Service** — Manages the knowledge base (implicitly integrated into the Recommendation Service).
- **Capitalization Service** — Collects and stores operator feedback (chosen/rejected recommendations) for future model improvement.

## Integration Points for External Systems

External systems (simulators, data sources) only need to call **two** APIs to communicate with the platform:

1. **Event API** — to push events into the platform
2. **Context API** — to push context updates

All other APIs are consumed internally by the platform's services and HMI module.

When the operator selects a recommendation, the platform will call back an endpoint on the simulator side:
```
POST http://{Simulator_server}/api/v1/recommendations
```
You must implement this endpoint in your simulator to receive the selected actions.

## Source Code

- Platform repository: [AINETUS/InteractiveAI](https://github.com/ainetus/InteractiveAI)
- Postman collections: [`docs/postman_collections/`](https://github.com/IRT-SystemX/InteractiveAI/tree/main/docs/postman_collections)
