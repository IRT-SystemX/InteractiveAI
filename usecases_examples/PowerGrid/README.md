# PowerGrid grid2op POC simulator

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

- [PowerGrid grid2op POC simulator](#powergrid-grid2op-poc-simulator)
- [1 Installation](#1-installation)
  - [1.1 Requirements:](#11-requirements)
  - [1.2 Setup a Virtualenv (optional)](#12-setup-a-virtualenv-optional)
    - [Create a virtual environment](#create-a-virtual-environment)
    - [Enter the virtual environment](#enter-the-virtual-environment)
  - [1.3 Installation of the simulator layer](#13-installation-of-the-simulator-layer)
- [2 Run the simulator](#2-run-the-simulator)
  - [2.1 Local deployment](#21-local-deployment)
  - [2.2 Server deployment](#22-server-deployment)
  - [2.3 Run directly, without Docker (optional)](#23-run-directly-without-docker-optional)
  - [2.4 Credentials required to run the simulation](#24-credentials-required-to-run-the-simulation)
- [3 Project Structure](#3-project-structure)
  - [3.1 Main Directories](#31-main-directories)
  - [3.2 Important Files](#32-important-files)


# 1 Installation
## 1.1 Requirements:
* Python >= 3.6
* Docker and Docker Compose

## 1.2 Setup a Virtualenv (optional)
Follow this section only if you want to run the simulator directly on your host, without Docker
(see [2.3](#23-run-directly-without-docker-optional)). With Docker you can skip this section.

### Create a virtual environment 
```commandline
cd usecases_examples/PowerGrid
python3 -m venv venv_grid2op
```

### Enter the virtual environment
- On Linux based systems:
```commandline
source venv_grid2op/bin/activate
```

- On Windows based systems:
```commandline
source venv_grid2op/scripts/activate
```

## 1.3 Installation of the simulator layer
This step is only required to run the simulator directly on your host (without Docker).
When using Docker, dependencies are installed inside the image automatically.

```commandline
cd InteractiveAI/usecases_examples/PowerGrid
pip install -r requirements-app.txt
```

# 2 Run the simulator

The simulator is a web application. Two Docker Compose files are provided:

| File                       | Use                 | Simulator UI               | InteractiveAI                                |
| -------------------------- | ------------------- | -------------------------- | -------------------------------------------- |
| `docker-compose.local.yml` | Local development   | http://localhost:5122      | on the same host, via `host.docker.internal` |
| `docker-compose.yml`       | Server / production | http://SERVER_ADDRESS:5100 | a remote/public URL                          |

## 2.1 Local deployment

Use this when InteractiveAI is running on the **same machine** as the simulator.

```commandline
cd InteractiveAI/usecases_examples/PowerGrid
docker compose -f docker-compose.local.yml up -d --build
```

Then open http://localhost:5122 in your browser.

In the login page, select the InteractiveAI server
`http://host.docker.internal:3200/`.

Because the code is bind-mounted in this mode, changes to templates/code are picked up on a browser refresh, without rebuilding the image.

## 2.2 Server deployment

Use this to deploy the simulator on a server, connecting to a **remote/public** InteractiveAI
instance (e.g. `https://demo.interactiveai.irt-systemx.fr/`).

```commandline
cd InteractiveAI/usecases_examples/PowerGrid
docker compose up -d --build
```

Then open http://SERVER_ADDRESS:5100/ (with **SERVER_ADDRESS** the address of your remote
machine), and select the public InteractiveAI URL in the login page. The list of available
InteractiveAI servers is defined in
[`config/API_POWERGRID_CAB.toml`](/usecases_examples/PowerGrid/config/API_POWERGRID_CAB.toml);
you can also add one directly from the login page.

The code is bind-mounted in this mode too, so edits to code/templates take effect after a
container restart, without rebuilding the image.

## 2.3 Run directly, without Docker (optional)

After completing the installation steps in [section 1](#1-installation):

```commandline
cd InteractiveAI/usecases_examples/PowerGrid
python PowerGrid_poc_simulator_app.py
```

## 2.4 Credentials required to run the simulation

To run the simulation, you will need the following credentials:

**InteractiveAI credentials:**
   - Username: `publisher_test`
   - Password: `test`

These credentials are created by the InteractiveAI platform. The PowerGrid's simulator only requests access to the InteractiveAI platform server using these credentials.


# 3 Project Structure

## 3.1 Main Directories

- `/Resources`: Contains resources needed for the simulator.
- `/app`: Contains the web application code for the simulator.
- `/config`: Contains configuration files for the simulator.

## 3.2 Important Files

- `PowerGrid_poc_simulator_app.py`: Main script to run the simulator in web application mode.
- `requirements-app.txt`: List of dependencies for the web application mode simulator.
- `docker-compose.local.yml`: Docker Compose file for local development (simulator UI on port 5122).
- `docker-compose.yml`: Docker Compose file for server deployment (simulator UI on port 5100).
- `Dockerfile.app`: Dockerfile used to build the simulator Docker image.
