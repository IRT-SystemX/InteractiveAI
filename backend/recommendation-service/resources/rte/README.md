git clone --recursive https://git.irt-systemx.fr/cab/grid2op/rtegrid2op_poc_simulator.git --branch multiaction_agent
mkdir rtegrid2op_poc_simulator/env_ICAPS_input_data_test
unzip env_ICAPS_input_data_test.zip -d rtegrid2op_poc_simulator/env_ICAPS_input_data_test
mkdir rtegrid2op_poc_simulator/XD_silly_repo
unzip XD_silly_repo.zip -d rtegrid2op_poc_simulator/XD_silly_repo
cd rtegrid2op_poc_simulator
git clone https://github.com/rte-france/Grid2Op