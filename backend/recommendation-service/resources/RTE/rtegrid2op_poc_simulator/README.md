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
    *   [1.3 Install Grid2Op from source](#13-install-grid2op-from-source)
    *   [1.4 Install Grid2Op for contributors (optional)](#14-install-grid2op-for-contributors-optional)
    *   [1.5 Install RTE simulator layer](#15-install-rte-simulator-layer)
*   [2 Getting Started](#2-getting-started)
    *   [2.1 Configurate the simulator settings](#21-configurate-the-simulator-settings)
    *   [2.2 Run the simulator](#22-run-the-simulator)


# 1 Installation
## 1.1 Requirements:
*   Python >= 3.6

## 1.2 Setup a Virtualenv (optional)
### Create a virtual environment 
```commandline
cd my-project-folder
pip3 install -U virtualenv
python3 -m virtualenv venv_grid2op
```

### Enter virtual environment
```commandline
source venv_grid2op/bin/activate
```

## 1.3 Install Grid2Op from source
```commandline
git clone https://git.irt-systemx.fr/cab/grid2op/rtegrid2op_poc_simulator.git
cd rtegrid2op_poc_simulator/Grid2Op
pip3 install -U .
cd ..
```

## 1.4 Install Grid2Op for contributors (optional)
```commandline
git clone https://git.irt-systemx.fr/cab/grid2op/rtegrid2op_poc_simulator.git
cd rtegrid2op_poc_simulator/Grid2Op
pip3 install -e .
pip3 install -e .[optional]
pip3 install -e .[docs]
```

## 1.5 Install RTE Simulator layer
```commandline
cd rtegrid2op_poc_simulator
pip install -r requirements.txt
```


# 2 Getting Started
## 2.1 Configurate the simulator settings
*   Define your simulation configuration in CONFIG.toml file.
*   Define CAB connexion setting in API_RTE_CAB.toml file.

## 2.2 Run the simulator
```commandline
cd rtegrid2op_poc_simulator
python assistantManager.py
```