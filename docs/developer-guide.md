# Development Guide - InteractiveAI Assistant Platform

Welcome to the development guide for the InteractiveAI Assistant Platform. This guide provides an overview of the development process, including setting up the environment, running the application, and contributing to the project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Running the Application](#running-the-application)
3. [Contributing](#contributing)
4. [Unittest](#Unittest)


## 1. Prerequisites<a name="prerequisites"></a>

Before getting started with the development process, ensure that you have the following prerequisites:

- [Git (version 2.40.1)](https://git-scm.com/)
- [Docker (version 24.0.2)](https://www.docker.com/)
- [Docker Compose (version 1.25.0)](https://www.docker.com/) 

## 3. Running the Application<a name="running-the-application"></a>

The InteractiveAI Assistant Platform can be run in different modes, depending on your development needs. The initial setup mentioned in the README file remains mandatory anyway. If you encounter any issues, please refer to our [troubleshooting guide](docs/troubleshooting.md).

### Running Recommendation Service (Dev Mode using docker)

To run the Recommendation Service on your local machine using docker:

1. Navigate to Recommendation Service.
```sh
cd cab-assistant-platform/config/recommendation-service/

```

2. Start the Recommendation Service using `docker-compose.bash`:

```sh
./docker-compose.bash

```

### Running Recommendation Service (Test Mode using python virtualenv)

To run the Recommendation Service on your local machine:

1. Create a python virtual env. For linux you can use these commands:

```sh
python3 -m venv <name_of_virtualenv>
source <name_of_virtualenv>/bin/activate
```

2. Install python requirements.txt

```sh
cd backend/recommendation-service
pip install -r requirements.txt
```

3. If you usecase uses Owlready2, Install Java

4. Start the web service
   * Option 1:
      Update envirement variables as felow:
         FLASK_APP="app:create_app('test')"
         FLASK_ENV="development"
         AUTH_DISABLED="True"
         DEFAULT_USE_CASE=YOUR_USE_CASE ("SNCF", "RTE", "DA")
      then start service using command:
```sh
python -m flask run --host=0.0.0.0 --reload
```

   * Option 2:
      Update start_service.bash and use it to run service

### Specific Configuration for the RTE Use Case

For the RTE use case, the recommendation service utilizes the resources `XD_silly_repo` and `env_icaps_input_data_test`. 
- `env_icaps_input_data_test` is a grid2op compliant scenarios' collection package.
- `XD_silly_repo` is a compliant a grid2op compliant RL agent package.

If you wish to modify these, you must add your replacement folders in [`backend/recommendation-service/resources/RTE/rtegrid2op_poc_simulator`](../backend/recommendation-service/resources/RTE/rtegrid2op_poc_simulator) and update there in the file `CONFIG_RTE.toml` the followings parameter to match your new folders:

For the scenario collection integration:
- `env_name`: Name of the scenario folder. By default, it is set to `"env_icaps_input_data_test"` at the moment.
- `env_seed`: Seed to initialize the grid2op environment. By default, it is set to `2118338672` at the moment.
- `scenario_name`: Name of the scenario to be executed. By default, it is set to `'jan_28_1'` at the moment.

For the RL agent integration:
- `assistant_name`: Name of the RL agent folder. By default, it is set to `"XD_silly_repo"` at the moment.
- `assistant_seed`: Seed to initialize the RL agent. By default it is set to `1227139268` at the moment.

It is recommended to rebuild and restart the recommendation service for these changes to take effect.

### Running All Services (Dev Mode)

To run all services on the dev server you can check the steps in the main README file

## Contributing

Contributions to the InteractiveAI Assistant Platform are welcome! To contribute please make sure to use [developer guide](docs/developer-guide.md)

1. Create a gitlab issue and use it to create your branch from develop branch
2. Fetch new created branch `git fetch`.
3. Checkout you branch `git checkout 1-your-branch'`.
4. Commit your changes: `git commit -am 'Add your feature'`.
5. Push to the branch: `git push origin 1-your-branch`.
6. Create a pull request, explaining your changes and their purpose.

### Frontend

You can find more informations on how to contribute, modify and create new use cases in the specific [frontend README](../frontend/README.md)


## Unittest

Every service have it's unittest with it. Here is an example of how you can run a service unittest.

### Run recommendation-service unittest

1. Create a python virtual env. For linux you can use these commands:

```sh
python3 -m venv <name_of_virtualenv>
source <name_of_virtualenv>/bin/activate
```

2. Install requirements.txt.

```sh
pip install -r requirements.txt
```

3. Run unittest and create a coverage report

```sh
pytest --cov=. --cov-report=html
```
