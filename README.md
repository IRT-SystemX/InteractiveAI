# InteractiveAI Assistant Platform
**An interactive AI Assistant Platform for Real Time operations**

_Frontend_ 
​ [![Node](https://img.shields.io/badge/Node-339933?style=plastic&logo=nodedotjs&logoColor=fff)](https://nodejs.org) [![Vue](https://img.shields.io/badge/Vue-35495E?style=plastic&logo=vuedotjs&logoColor=fff)](https://vuejs.org) [![Vite](https://img.shields.io/badge/Vite-%23646CFF.svg?style=plastic&logo=vite&logoColor=fff)](https://vitejs.dev) [![TypeScript](https://img.shields.io/badge/Typescript-%23007ACC.svg?style=plastic&logo=typescript&logoColor=fff)](https://www.typescriptlang.org) [![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=plastic&logo=Leaflet&logoColor=fff)](https://leafletjs.com) [![Axios](https://img.shields.io/badge/Axios-671ddf?&style=plastic&logo=axios&logoColor=fff)](https://axios-http.com)

_Backend_ 
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=plastic&logo=flask&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=plastic&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=plastic&logo=docker&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=plastic&logo=postman&logoColor=white)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#setting-up-the-environment">Setting Up the Environment</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#docs">Docs</a></li>

  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

InteractiveAI platform provides support in augmented decision-making for complex steering systems.
It is a prototype of a bi-directional virtual assistant, open in terms of industrial applications, in which it will be possible to evaluate the forms of exchange between the expert and an AI that learns continuously, both from the information flows received and the decisions made by the human. The platform will help and assist the operator of a complex operation to resolve incidents/faults in his industrial environment.

As it is designed, the platform is generic, it can be used for different use cases. As an example, the use case of managing **power line** overloads at **PowerGrid** (Réseau de Transport d'Electricité français) is provided. To install and run the PowerGrid simulator, please refer to the detailed guide available in the file PowerGrid simulator's [README](/usecases_examples/PowerGrid/README.md). This guide provides specific instructions for setting up and running the PowerGrid use case.

The platform uses the project **OperatorFabric** for notification management.


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- [Git (version 2.40.1)](https://git-scm.com/)
- [Docker Engine (version 27)](https://www.docker.com/)
- [Docker Compose V2](https://www.docker.com/) 


### Setting Up the Environment

Clone the repo of the assistant

```sh
git clone [repo-url]
```

## Usage

InteractiveAI offers versatile deployment options, leveraging either Docker or Kubernetes. The primary method entails initiating InteractiveAI via Docker to launch all services concurrently. However, recognizing potential resource strain in this mode, we've introduced alternative configurations. These configurations enable selective startup of essential services with minimal dependencies, catering to streamlined versions of certain APIs.
Below are the steps to start all services. For other methods, please consult the developer guide.

### Running All Services (Dev Mode)

1. **Set-up environment variables**

Configuration is read from a gitignored `.secrets` file that `docker-compose.sh` sources.
Copy the template and fill in your values:

```sh
cd config/dev/cab-standalone
cp .secrets.example .secrets
# then edit .secrets
```

Key variables (see `.secrets.example` for all options and per-environment values):

- `VITE_POWERGRID_SIMU` — the frontend's simulator endpoint. Use the same-origin proxy
  value `/powergrid-simu` (avoids CORS); set it to `false` to disable the PowerGrid UI.
  `VITE_RAILWAY_SIMU` / `VITE_ATM_SIMU` are the equivalents for the other use cases.
- `POWERGRID_SIMU_UPSTREAM` — where nginx actually forwards `/powergrid-simu/`. This is the
  only value that changes per environment:
  - Local dev : `http://host.docker.internal:5122/` (simulator container on the host)
  - LAN       : `http://192.168.208.61:5100/`
  - Public/k8s: handled by `nginx-kubernetes.conf` via the helm chart (not this variable)
- `RL_AGENT_API_URL` / `RL_AGENT_API_TOKEN` — the deep expert agent that powers PowerGrid
  recommendations (see [The PowerGrid expert agent API](#the-powergrid-expert-agent-api) below to
  install it). A token is required in every mode:
  - Local dev : `http://host.docker.internal:5123/api/v1/recommendation` (agent on the host)
  - Server    : `http://192.168.208.61:5000/api/v1/recommendation`
  - Public    : `https://interactiveagent.passerelle.irt-systemx.fr/api/v1/recommendation`

> **_NOTE:_** `host.docker.internal` lets the containers reach services (simulator, expert agent)
> running on the host — this is how local dev connects to them. Make sure those host services
> listen on `0.0.0.0` (not only `127.0.0.1`) so the containers can reach them.
>
> **_NOTE:_** For the simulator itself, you can use the example we provide — follow the tutorial
> in [InteractiveAI/usecases_examples/PowerGrid/](/usecases_examples/PowerGrid/README.md).
>
> 
2. **Run InteractiveAI assistant**
```sh
cd config/dev/cab-standalone
./docker-compose.sh
```
> **_NOTE:_** You will see the word cab on most files in the project. Note that it was the initial project name of InteractiveAI. Might be updated later. 

3. **Setting up Keycloak `Frontend URL`**  
    * Access Keycloak Interface: 
      - Ensure that your Keycloak instance is running and accessible.
      - Open a web browser and navigate to the Keycloak admin console, typically available at `http://localhost:89/auth/admin`.  
    * Login to Keycloak Admin Console: 
      - Log in to the Keycloak admin console using your administrator credentials (`admin:admin` by default)
    * Configure frontendUrl:
      - On the Keycloak admin console, locate and click on the "Realm Settings" section.
      - In the Frontend URL field, add the URL of InteractiveAI frontend. If your frontend is hosted locally for development purposes, you might add `http://localhost:3200/`.
      - After adding the frontend URL, save the changes.
    * Configure Valid Redirect URIs:
      - On the Keycloak admin console, locate and click on the "Clients" section.
      - Select the client (opfab-client).  
      - Within the client settings, look for the "Valid Redirect URIs" field.
      - Add the URL of the frontend with /*, if it's local deployment: `http://localhost:3200/*`.
      - After adding the Valid Redirect URIs, save the changes to update the client settings.


4. **Load resources**

**WARNING:** You need to restart the frontend after updating the URL on keycloak do it before loading the resources. 
```sh
docker restart frontend
```

```sh
cd resources
./loadTestConf.sh
```

5. If you encounter CORS errors (which can happen if you start the platform in a non-HTTPS environment), you can start your browser with security mode disabled.

```sh
your-chromium-browser --disable-web-security --user-data-dir="[some directory here]" # replace your-chromium-browser with your browser
```

> **_NOTE:_** If you encounter any issues, please refer to our [troubleshooting guide](docs/troubleshooting.md).

### The PowerGrid expert agent API

PowerGrid recommendations are produced by a separate service — the **deep expert agent**. The
`cab_recommendation` service calls it at `RL_AGENT_API_URL`, so it must be running (and reachable)
for recommendations to appear in InteractiveAI.

1. Clone the agent repository and check out the API branch:

```sh
git clone https://github.com/ainetus/T2.1_deep_expert.git
cd T2.1_deep_expert
git checkout feat/api-auth-compose
```

2. Start it by following that repository's README (the `feat/api-auth-compose` branch ships a
   Docker Compose and adds token authentication). For local development:
   - expose it on port **5123**, and
   - make it listen on `0.0.0.0` (not only `127.0.0.1`) so the InteractiveAI containers can reach
     it through `host.docker.internal`.

3. Point InteractiveAI at it in `config/dev/cab-standalone/.secrets`, with a token that matches
   the one the agent expects:

```sh
export RL_AGENT_API_URL=http://host.docker.internal:5123/api/v1/recommendation
export RL_AGENT_API_TOKEN=<token configured in the expert agent>
```

Then (re)run `./docker-compose.sh` so `cab_recommendation` picks up the values. For the LAN and
public deployments, use the corresponding `RL_AGENT_API_URL` from step 1 of
[Running All Services](#running-all-services-dev-mode) instead.

### Default ports

This project is based on a microservice architecture. Every service run on a specific port. Some of the default ports are as fellow:
* Frontend: 3200
* Context Service: 5100
* Event Service: 5000
* Historic Service: 5200
* Keycloak: 89

Companion services for the PowerGrid use case run on the host (local dev) and are reached by the
containers via `host.docker.internal`:
* PowerGrid simulator (provided example): 5122
* PowerGrid expert agent API: 5123

### Authentication data

For a development environment, the system uses predefined initial data for Keycloak setup.
You can find authentication data under config/dev/cab-keycloak

Some examples of credentials:

| username         | password |
| ---------------- | -------- |
| `admin`          | `test`   |
| `powergrid_user` | `test`   |
| `railway_user`   | `test`   |
| `atm_user`       | `test`   |


By default, the system allows the user to be connected only from a single machine. Which means if you try to connect using the same credentials from another machine, you will be disconnected on the first machine. 

# Development

Contributions to the InteractiveAI Assistant Platform are welcome! To contribute, please make sure to use [developer guide](docs/developer-guide.md)

# Docs
A postman collection is under docs/postman_collections.
You can also check the openapi through the URL http://localhost:[Service port]/docs
