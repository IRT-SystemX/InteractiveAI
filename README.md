# InteractiveAI Assistant Platform
**An interactive AI Assistant Platform for Real Time operations**

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
git clone https://github.com/AI4REALNET/InteractiveAI.git
```

## Usage

InteractiveAI offers versatile deployment options, leveraging either Docker or Kubernetes. The primary method entails initiating InteractiveAI via Docker to launch all services concurrently. However, recognizing potential resource strain in this mode, we've introduced alternative configurations. These configurations enable selective startup of essential services with minimal dependencies, catering to streamlined versions of certain APIs.
Below are the steps to start all services. For other methods, please consult the developer guide.

### Running All Services (Dev Mode)

1. **Set-up environement variables**
   

`VITE_POWERGRID_SIMU`, `VITE_RAILWAY_SIMU` , `VITE_ATM_SIMU` are the simulators' endpoints.
Put for each UC the corresponding IP address.

Examples: 

```sh
export VITE_POWERGRID_SIMU=http://[Service url]:[Service port]
export VITE_RAILWAY_SIMU=http://[Service url]:[Service port]
export VITE_ATM_SIMU=http://[Service url]:[Service port]
```
> **_NOTE:_** For this step, you should already have a running simulator. If not, you can use the simulator we provided as an example. For this, please follow the tutorial provided in InteractiveAI/usecases_examples/PowerGrid/ then set the VITE_POWERGRID_SIMU variable to http://YOUR_SERVER_ADDRESS:5100/
>
> 
2. **Run InteractiveAI assistant**
```sh
cd config/dev/cab-standalone
./docker-compose.sh
```
> **_NOTE:_** You will see the word cab (Cockpit Assistant Bidirectionnel) on most files in the project. Note that it was the initial project name of InteractiveAI. Might be updated later. 

3. **Setting up Keycloak `Frontend URL`**  
    * Access Keycloak Interface: 
      - Ensure that your Keycloak instance is running and accessible.
      - Open a web browser and navigate to the Keycloak admin console, typically available at `http://localhost:89/auth/admin`.  
    * Login to Keycloak Admin Console: 
      - Log in to the Keycloak admin console using your administrator credentials (`admin:admin` by default)
    * Configure frontendUrl:
      - On the Keycloak admin console, locate and click on the "Realm Settings" section.
      - In the Frontend URL setting, add the URL of your Assistant Platform frontend as a valid redirect URI. This URL is typically where your frontend application is hosted. For example, if your frontend is hosted locally for development purposes, you might add `http://localhost:3200/*`.
      - After adding the frontend URL, save the changes to update the client settings.
    * Configure Valid Redirect URIs:
      - On the Keycloak admin console, locate and click on the "Clients" section.
      - Select the client representing your Assistant Platform application.  
      - Within the client settings, look for the "Valid Redirect URIs" or similar configuration field.
      - Add the URL of your Assistant Platform frontend, it should match the one used in the frontendUrl setting.
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

5. If you encounter CORS errors (which can happen if you start tha platform in a non-HTTPS environment), you can start your browser with security mode disabled.

```sh
your-chromium-browser --disable-web-security --user-data-dir="[some directory here]" # replace your-chromium-browser with your browser
```

> **_NOTE:_** If you encounter any issues, please refer to our [troubleshooting guide](docs/troubleshooting.md).

### Default ports

This project is based on a microservice architecture. Every service run on a specific port. Some of th default ports are as fellow:
* Frontend: 3200
* Context Service: 5100
* Event Service: 5000
* Historic Service: 5200
* Keycloak: 89

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
