# How to

Check the example code provided below to get an idea of how to use this agent 
in Grid2Op.

```python
import sys

import numpy as np

sys.path.append("../")
import grid2op
from loguru import logger
import os
import sys
from lightsim2grid import LightSimBackend

def search_chronic_num_from_name(scenario_name, env):
    found_id = None
    # Search scenario with provided name
    for id, sp in enumerate(env.chronics_handler.real_data.subpaths):
        sp_end = os.path.basename(sp)
        if sp_end == scenario_name:
            found_id = id
    return found_id

####### config
grid2op_env_path='/home/rozierale/Work/Rte/L2RPN/L2RPN_Codalab_Competition_Bundle-main/competition_codalab/L2RPN_icaps2021/input_data_test'
agent_seed= 1227139268
env_seed=2118338672
scenario_name='jan_28_1' # scenario to play amongst interesting ones: jan_28_1, mar_07_1, nov_34_1, sep_09_2

agent_path='../XD_silly_repo'
from XD_silly_repo.submission import make_agent

#######

def main():

    ###########
    # load grid2op environment
    env = grid2op.make(grid2op_env_path, backend=LightSimBackend())

    # set to scenario of interest and seed
    id_scenario = search_chronic_num_from_name(scenario_name, env)

    env.set_id(id_scenario)  # Load scenario jan_28_1
    env.seed(env_seed)

    # reset the env to apply the seed and start to the desired scenario
    obs = env.reset()
    params = env.get_params_for_runner()
    params['verbose'] = True
    assert env.chronics_handler.get_name() == scenario_name

    # load agent
    submission_location = os.path.join(agent_path, "submission")
    sys.path.append(agent_path)  # add agent's code and modules to python path

    #agent = make_agent(env, submission_location, n_actions=3, take_action_index=2)
    agent = make_agent(env, submission_location)
    # seed and reset the agent
    if agent_seed is not None:
        agent.seed(agent_seed)
    agent.reset(obs)

    #############
    # let's run our agent on a scenario !

    logger.info("Starting sim...")

    # Option 1: Uncomment this if you want to run the agent on a whole scenario without stopping
    # runner = Runner(**params, agentClass=None, agentInstance=agent)
    # runner.run(nb_episode=1, episode_id=[id_scenario], path_save="logs/xd_silly_n_actions_take_3rd", env_seeds=[env_seed], agent_seeds=[agent_seed])

    # Option 2 : Manually Run the scenario

    done = False
    step = 0
    while not done:
        # here you loop on the time steps: at each step your agent receive an observation
        # takes an action
        # and the environment computes the next observation that will be used at the next step.


        # Legacy way to get an action from the agent (single action - no multiple recommandations here)
        #action = agent.act(obs, reward, done)

        # Get several recommandations (=actions) from the agent, sorted by (simulated) efficiency
        # WARNING: The agent runs simulations with Grid2op backend under the hood
        recos = agent.make_recommandations(obs, n_actions=3)
        best_action, max_forecasted_rho_0 = recos[0]
        slightly_worse_action, max_forecasted_rho_1 = recos[1]
        even_worse_action, max_forecasted_rho_2 = recos[2]
        obs, reward, done, info = env.step(best_action)

        # Print ma
        print(np.max(obs.rho))
        # PSEUDO-CODE: CAN DO SECURITY ANALYSIS HERE
        # PSEUDO-CODE: COMPUTE EVENTS and send to CAB
        # PSEUDO-CODE: DO some plot
        step += 1

if __name__ == '__main__':
    main()
```