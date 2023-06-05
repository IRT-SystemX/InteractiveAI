# CAB Assistant Platform
![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=for-the-badge&logo=angular&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
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

Cockpit and Bidirectional Assistant (CAB) platform provides support in augmented decision-making for complex steering systems.

The platform make use of the project OperatorFabric for notification management and authentication.

<!-- GETTING STARTED -->
## Getting Started
Before starting cab-platform you need a running version of [OperatorFabric](https://github.com/opfab/operatorfabric-core)

### Prerequisites

* Docker
* OperatorFabric

### Setting Up the Environment

1. Clone the repo of OperatorFabric
```sh
git clone https://github.com/opfab/operatorfabric-core
```

2. Clone the repo of cab assistant
```sh
git clone https://git.irt-systemx.fr/cab/cab-assistant-platform.git
```

3. Set new configuration to OperatorFabric
```sh
cd cab-assistant-platform
./config_of.sh
```
4. Download recommendation-service resources and copy them into `backend/recommendation-service/resources`


**Note** config_of.sh will copy the folder of-config in cab-assistant-platform to operatorfabric-core/config/

## Usage

- Development Mode:
  - Run the Recommendation Service independently for local development.
  - Run all services together on the dev server for comprehensive testing.

### Running All Services (Dev Mode)

1. Run OperatorFabric
```sh
cd ../operatorfabric-core/config/cab-docker
./docker-compose.bash
```

2. Run Cab-assistant
```sh
cd ../../../cab-assistant-platform/config/dev/cab
./docker-compose.bash
```

3. Load resources into OperatorFabric
```sh
cd resources
./loadTestConf.sh
```

### Default ports

This project is based on a microservice architecture. Every service run on a specific port. Some of th default ports are as fellow:
* Frontend: 3200
* Context Service: 5100
* Event Service: 5000
* Historic Service: 5200

### Authentication data

The system use the authentication data of OperatorFabric.
OperatorFabric use keycloak to manage users  authentication data. You can check it on port 89.
You can find authentication data in OperatorFabric repository under config/docker/users-docker.yml and config/keycloak

Some examples of credentials:

| username         | password |
| ---------------- | -------- |
| `admin`          | `test`   |
| `publisher_test` | `test`   |
| `da_user`        | `test`   |
| `sncf_user`      | `test`   |
| `orange_user`    | `test`   |
| `rte_user`       | `test`   |


By default, the system allows the user to be connected only from a single machine. Which means if you try to connect using the same credentials from another machine, you will be disconnected on the first machine. 

# Development

Contributions to the Cab Assistant Platform are welcome! To contribute, please make sure to use [developer guide](docs/developer-guide.md)

# Docs
A postman collection is under docs/postman_collections.
You can also check the openapi through the URL http://localhost:[Service port]/docs