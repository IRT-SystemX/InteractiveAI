# Getting Started

This guide explains how to connect an external system (e.g. a simulator or data source) to the InteractiveAI platform.

## Prerequisites

- A running instance of the InteractiveAI platform. Replace `{Platform_Server}` in all API calls with your server's host and port (e.g. `localhost:8080`).
- HTTP client of your choice (curl, Postman, your application's HTTP library).

## Authentication

All API calls require a bearer token. Obtain one first, then include it in every request:

```http
POST http://{Platform_Server}:3200/auth/token
Content-Type: application/x-www-form-urlencoded

username=publisher_test&password=test&grant_type=password&clientId=opfab-client
```

Then add the token to all subsequent requests:

```http
Authorization: Bearer <access_token>
```

See [Authentication](./api/authentication.md) for the full details and a Python example.

## What you need to implement

### 1. Send events to the platform

Whenever a notable event occurs in your system, push it to the platform:

```http
POST http://{Platform_Server}/cab_event/api/v1/events
Content-Type: application/json
```

See [Event Service API](./api/event-service.md) for the full payload schema and examples.

### 2. Send context updates to the platform

Keep the platform informed of the current operating context:

```http
POST http://{Platform_Server}/cab_context/api/v1/contexts
Content-Type: application/json
```

See [Context Service API](./api/context-service.md) for the full payload schema and examples.

### 3. Implement a recommendations endpoint (optional but recommended)

When an operator selects a recommendation, the platform will call back your simulator with the list of actions to execute. You must expose this endpoint on your side:

```http
POST http://{Simulator_server}/api/v1/recommendations
```

The body will contain the actions array from the chosen recommendation (see [Recommendation Service](./api/recommendation-service.md)).

## API summary

| Service | Endpoint | Who calls it |
|---|---|---|
| Event | `POST /cab_event/api/v1/events` | **Your system** |
| Context | `POST /cab_context/api/v1/contexts` | **Your system** |
| Context (read) | `GET /cab_context/api/v1/contexts/$date` | HMI (internal) |
| Historic | `POST /api/v1/traces` | Internal |
| Historic (read) | `GET /api/v1/traces/$start_date/&end_date` | Internal |
| Recommendation | `POST /cab_recommendation/api/v1/recommendation` | Internal (HMI) |
| Capitalization | `POST /cab_capitalization/api/v1/feedbacks` | Internal (HMI) |
| **Simulator callback** | `POST http://{Simulator_server}/api/v1/recommendations` | **Platform → Your system** |

## Postman collections

Ready-to-use Postman collections are available for each service:

- [Event Service](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Event-service.postman_collection.json)
- [Context Service](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Context-service.postman_collection.json)
- [Historic Service](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Historic-service.postman_collection.json)
- [Recommendation Service](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Recommendation-service.postman_collection.json)
- [Capitalisation Service](https://github.com/IRT-SystemX/InteractiveAI/blob/main/docs/postman_collections/Capitalisation-service.postman_collection.json)
