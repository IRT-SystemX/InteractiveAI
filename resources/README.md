# RTE grid2op POC simulator

This POC use Grid2Op platform to perform it simulation.

Grid2Op is a platform, built with modularity in mind, that allows to perform powergrid operation.
And that's what it stands for: Grid To Operate.
Grid2Op acts as a replacement of [pypownet](https://github.com/MarvinLer/pypownet) 
as a library used for the Learning To Run Power Network [L2RPN](https://l2rpn.chalearn.org/). 

This framework allows to perform most kind of powergrid operations, from modifying the setpoint of generators,
to load shedding, performing maintenance operations or modifying the *topology* of a powergrid
to solve security issues.

For further explanation on Grid2Op, the official documentation of Grid2Op is available at [https://grid2op.readthedocs.io/](https://grid2op.readthedocs.io/).
And it can also be found here [Grid2Op/README.md](Grid2Op/README.md).

*   [1 Installation](#1-installation)
    *   [1.1 Requirements](#11-requirements)
    *   [1.2 Setup a Virtualenv (optional)](#12-setup-a-virtualenv-optional)
    *   [1.3 Installation of the simulator layer](#13-installation-of-the-simulator-layer)
        *   [1.3.1 CASE 1 : Console Simulator](#131-case-1--console-simulator)
        *   [1.3.2 CASE 2 : Web App Simulator](#132-case-2--web-app-simulator)
*   [2 Run the simulator](#2-run-the-simulator)
    *   [2.1 CASE 1 : Console Simulator](#21-case-1--console-simulator)
        *   [Configurate the simulator settings](#configurate-the-simulator-settings)
        *   [Run the simulator in your terminal](#run-the-simulator-in-your-terminal)
    *   [2.2 CASE 2 : Web App Simulator](#22-case-2--web-app-simulator)
        *   [To launch the simulator app](#to-launch-the-simulator-app)
        *   [Run the simulator in your terminal (optional)](#run-the-simulator-in-your-terminal-optional)
    *   [2.3 Credentials required to run the simulation](#23-credentials-required-to-run-the-simulation)
*   [3 Project Structure](#3-project-structure)
    *   [3.1 Main Directories](#31-main-directories)
    *   [3.2 Important Files](#32-important-files)


# 1 Installation
## 1.1 Requirements:
* Python >= 3.6
* Docker and Docker Compose

## 1.2 Setup a Virtualenv (optional)
### Create a virtual environment 
```commandline
cd my-project-folder
pip3 install -U virtualenv
python3 -m virtualenv venv_grid2op
```

### Enter the virtual environment
```commandline
source venv_grid2op/bin/activate
```

## 1.3 Installation of the simulator layer

### 1.3.1 CASE 1 : Console Simulator

1. Install dependencies for the console simulator:

```commandline
cd rte
pip install -r requirements-consol.txt
```

2. Install API-specific dependencies:

```commandline
pip install -r requirements-api.txt
```

3. For the Docker environment, use the provided docker-compose.yml and Dockerfile.

### 1.3.2 CASE 2 : Web App Simulator

1. Install dependencies for the console simulator:

```commandline
cd rte
pip install -r requirements-app.txt
```

3. For the Docker environment, use the provided docker-compose.yml and Dockerfile.
```
cd rte
docker-compose up -d --build
```

# 2 Run the simulator

## 2.1 CASE 1 : Console Simulator

### Configurate the simulator settings
* Define your simulation configuration in the file: [`/rtegrid2op_poc_simulator/config/CONFIG.toml`](/rtegrid2op_poc_simulator/config/CONFIG.toml)
* Define CAB connection settings in the file: [`/rtegrid2op_poc_simulator/config/API_RTE_CAB.toml`](/rtegrid2op_poc_simulator/config/API_RTE_CAB.toml)

### Run the simulator in your terminal
```commandline
cd rte
python rte_poc_simulator_consol.py
```

## 2.2 CASE 2 : Web App Simulator

### To launch the simulator app
Open a web browser and navigate to the URL returned by Docker after running the containers. 
This URL will typically be `http://localhost:5100` unless you've configured a different port.

Note: If you're running Docker on a remote machine or using Docker Toolbox on Windows, 
you may need to replace 'localhost' with the appropriate IP address.

### Run the simulator in your terminal (optional)
```commandline
cd rte
python rte_poc_simulator_app.py
```

## 2.3 Credentials required to run the simulation

To run the simulation, you will need the following credentials:

**CAB credentials:**
   - Username: `publisher_test`
   - Password: `test`

These credentials are created by the CAB platform. The RTE's simulator only requests access to the CAB platform server using these credentials.


# 3 Project Structure

## 3.1 Main Directories

- `/Resources`: Contains resources needed for the simulator.
- `/app`: Contains the web application code for the simulator.
- `/config`: Contains configuration files for the simulator.

## 3.2 Important Files

- `rte_poc_simulator_consol.py`: Main script to run the simulator in console mode.
- `rte_poc_simulator_app.py`: Main script to run the simulator in web application mode.
- `requirements-consol.txt`: List of dependencies for the console mode simulator.
- `requirements-app.txt`: List of dependencies for the web application mode simulator.
- `docker-compose.yml`: Configuration for the Docker environment.
- `Dockerfile.app` and `Dockerfile.api`: Dockerfile files to build Docker images.