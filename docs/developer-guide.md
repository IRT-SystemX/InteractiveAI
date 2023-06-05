# Development Guide - Cab Assistant Platform

Welcome to the development guide for the Cab Assistant Platform. This guide provides an overview of the development process, including setting up the environment, running the application, and contributing to the project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up the Environment](#setting-up-the-environment)
3. [Running the Application](#running-the-application)
4. [Contributing](#contributing)

## 1. Prerequisites<a name="prerequisites"></a>

Before getting started with the development process, ensure that you have the following prerequisites:

- [Git (version 2.40.1)](https://git-scm.com/)
- [Docker (version 24.0.2)](https://www.docker.com/)
- [Docker Compose (version 1.25.0)](https://www.docker.com/) 

## 2. Setting Up the Environment<a name="setting-up-the-environment"></a>

To set up the development environment, follow these steps:

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


## 3. Running the Application<a name="running-the-application"></a>

The Cab Assistant Platform can be run in different modes depending on your development needs.

### Running Recommendation Service (Dev Mode)

To run the Recommendation Service on your local machine:

1. Navigate to Recommendation Service.
```sh
cd cab-assistant-platform/config/recommendation-service/

```

2. Start the Recommendation Service using `docker-compose.bash`:

```sh
./docker-compose.bash

```

### Running All Services (Dev Mode)

To run all services on the dev server:

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

## Contributing

Contributions to the Cab Assistant Platform are welcome! To contribute please make sure to use [developer guide](docs/developer-guide.md)

1. Create a gitlab issue and use it to create your branch from develop branch
2. Fetch new created branch `git fetch`.
3. Checkout you branch `git checkout 1-your-branch'`.
4. Commit your changes: `git commit -am 'Add your feature'`.
5. Push to the branch: `git push origin 1-your-branch`.
6. Create a pull request, explaining your changes and their purpose.


## Test CAB

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


## Troubleshooting

Are you having issues with setting up your environment? Here are some tips that might help.

### EoL Sequence Configuration errors.

Some users may encounter issues if their system is automatically converting end of line sequence from LF to CRLF.
If the problem is related to git configuration, [here is a link that can help. ](https://medium.com/@csmunuku/windows-and-linux-eol-sequence-configure-vs-code-and-git-37be98ef71df)


### Always unauthorized

Sometimes we have issues setting up .env file with the correct value.
The .env should contain:

```env
HOST_IP=<IP_Address>
```

If the IP_Address is not your network IP address, please set it manually and run the system using native docker-compose commands.