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
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>

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
  ```sh
  git clone https://github.com/opfab/operatorfabric-core
  cd config/docker
  docker-compose up -d
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://git.irt-systemx.fr/cab/cab-assistant-platform.git
   ```
2. Load resources into OperatorFabric
   ```sh
   cd resources
   ./loadTestConf.sh
   ```
3. Run using docker:
   ```sh
   docker-compose up -d
   ```

## Usage
This project is based on a microservice architecture. Every service run on a specific port. Default ports are as fellow:
* Frontend: 3200
* Context Service: 5100
* Event Service: 5000
* Historic Service: 5200

### Authentication data

The system use the authentication data of OperatorFabric.
OperatorFabric use keycloak to manage users  authentication data. You can check it on port 89.
You can find authentication data in OperatorFabric repository under config/docker/users-docker.yml and config/keycloak

Some examples of users logins/passwords:
* operator1_fr/ test
* publisher_test/ test

# Docs
A postman collection is under docs/postman_collections.
You can also check the openapi through the URL http://localhost:[Service port]/docs