import _pickle as cPickle
import copy
import functools
import os
from copy import deepcopy
from typing import Tuple, List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from grid2op.Agent import BaseAgent
from loguru import logger


class unitary_action_network(nn.Module):
    def __init__(self, params_dict, scalar_dict):
        super(unitary_action_network, self).__init__()

        mean = scalar_dict["mean"]
        std = scalar_dict["std"]

        self.zero_std = np.where(std == 0.0)[0]
        self.mean = np.array([mean[i] for i in range(len(mean)) if i not in self.zero_std])
        self.std = np.array([std[i] for i in range(len(std)) if i not in self.zero_std])

        self.month_embedding = nn.Embedding(12, 64, _weight=torch.Tensor(params_dict['emb_month.w_0']))
        self.hour_embedding = nn.Embedding(24, 64, _weight=torch.Tensor(params_dict['emb_hour.w_0']))

        self.fc1 = nn.Linear(267, 512)
        self.fc1.weight.data = torch.Tensor(params_dict['fc1.w_0']).T
        self.fc1.bias.data = torch.Tensor(params_dict['fc1.b_0'])

        self.fc2 = nn.Linear(512, 512)
        self.fc2.weight.data = torch.Tensor(params_dict['fc2.w_0']).T
        self.fc2.bias.data = torch.Tensor(params_dict['fc2.b_0'])

        self.fc3 = nn.Linear(512, 512)
        self.fc3.weight.data = torch.Tensor(params_dict['fc3.w_0']).T
        self.fc3.bias.data = torch.Tensor(params_dict['fc3.b_0'])

        self.fc4 = nn.Linear(512, 512)
        self.fc4.weight.data = torch.Tensor(params_dict['fc4.w_0']).T
        self.fc4.bias.data = torch.Tensor(params_dict['fc4.b_0'])

        self.fc5 = nn.Linear(512, 512)
        self.fc5.weight.data = torch.Tensor(params_dict['fc5.w_0']).T
        self.fc5.bias.data = torch.Tensor(params_dict['fc5.b_0'])

        self.fc6 = nn.Linear(512, 500)
        self.fc6.weight.data = torch.Tensor(params_dict['fc6.w_0']).T
        self.fc6.bias.data = torch.Tensor(params_dict['fc6.b_0'])

    def feature_process(self, raw_obs):
        obs = raw_obs.to_dict()

        loads = []
        for key in ['q', 'v']:
            loads.append(obs['loads'][key])
        loads = np.concatenate(loads)

        prods = []
        for key in ['q', 'v']:
            prods.append(obs['prods'][key])
        prods = np.concatenate(prods)

        features = np.concatenate([loads, prods])
        features = np.array([features[i] for i in range(len(features)) if i not in self.zero_std])
        norm_features = (features - self.mean) / self.std

        rho = obs['rho']

        time_info = np.array([raw_obs.month - 1, raw_obs.hour_of_day])

        return np.concatenate([norm_features, rho, time_info]).tolist()

    def forward(self, raw_obs):

        obs_vec = np.array(self.feature_process(raw_obs)).reshape([1, -1])
        dense_input = torch.tensor(obs_vec[:, :-2], dtype=torch.float32)
        month = torch.tensor(obs_vec[:, -2], dtype=torch.int32)
        hour = torch.tensor(obs_vec[:, -1], dtype=torch.int32)

        month_emb = self.month_embedding(month)
        hour_emb = self.hour_embedding(hour)
        obs_emb = torch.cat([dense_input, month_emb, hour_emb], axis=1)

        x = F.relu(self.fc1(obs_emb))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        predicts = self.fc6(x)

        return predicts.detach().cpu().numpy()


class PowerNetAgent(BaseAgent):
    def __init__(self, env, submission_path, n_actions=1, take_action_index=0):
        BaseAgent.__init__(self, action_space=env.action_space)
        # global action
        self.sub_topo_dict = {}
        self.simulate_times = 0
        self.alive_step = 0
        self.action_space = env.action_space
        self.n_actions = n_actions
        self.take_action_index = take_action_index
        logger.info(f"Pooling {n_actions} actions from our Reinforcement core")
        # construct action_to_sub_topo
        offset = 59
        self.action_to_sub_topo = {}
        for sub_id, sub_elem_num in enumerate(self.action_space.sub_info):
            self.action_to_sub_topo[sub_id] = (offset, offset + sub_elem_num)
            offset += sub_elem_num

        # ============================= load baidu unitary action 500 =======================
        unitary_actions_vec = np.load(os.path.join(submission_path, "unitary_action.npz"), 'r')["actions"]
        self.unitary_actions = [self.action_space.from_vect(action) for action in list(unitary_actions_vec)]

        params_dict = np.load(os.path.join(submission_path, 'unitary_action_network.npz'))
        scalar_dict = np.load(os.path.join(submission_path, 'unitary_action_scalar.npz'))
        self.unitary_es_agent = unitary_action_network(params_dict, scalar_dict)

        # construct action_to_sub_id
        self.action_to_sub_id = {}
        for act_idx, action in enumerate(self.unitary_actions):
            act_dict = action.impact_on_objects()
            if act_dict["redispatch"]['changed']:
                self.action_to_sub_id[act_idx] = "redispatch"
            elif act_dict["topology"]['changed']:
                self.action_to_sub_id[act_idx] = act_dict["topology"]["assigned_bus"][0]['substation']

        # ============================= load alarm action =======================
        self.alarms_lines_area = env.alarms_lines_area
        self.alarms_area_names = env.alarms_area_names
        self.alarm_overflow_flag = False
        self.alarm_cool_down = False
        self.alarm_cool_time = 3  # needed to be finetuned
        self.alarm_count = 0

        # ============================= load redispatch action 80 =======================
        self.redispatch_cnt = 0
        self.max_redispatch_cnt = 3  # needed to be finetuned

        act_matrix = cPickle.load(open(os.path.join(submission_path, 'redispatch_action.pkl'), 'rb'))['act_matrix']
        self.redispatch_actions = [self.action_space.from_vect(act_matrix[i, :]) for i in range(len(act_matrix))]

    # def act_without_alarm(self, observation):
    #    return recommandation(observation, n_actions=1)
    def act_without_alarm(self, observation):  # recommandation(self, observation, n_actions)
        # if there is a disconnected line, then try to reconnect it
        action = self.reconnect_action(observation)
        if action is not None:
            return action

        # if there is no disconnected line, try to reset topology and redispatch
        if np.all(observation.topo_vect != -1):
            self.redispatch_cnt = 0

            self.sub_topo_dict = self.calc_sub_topo_dict(observation)
            # try to reset the topology to the orginal state
            action = self.reset_topology(observation)
            if action is not None:
                return action

            # # try to reset the redispatch to the orginal state
            # action = self.reset_redispatch(observation)
            # if action is not None:
            #     return action

        # if there is a overflow line, then try to fix it
        if np.any(observation.rho > 1.0):
            # if (observation.line_status[45] == False or observation.line_status[56] == False):
            #     action, least_overflow_1 = self.unitary_actions_simulate_seq(observation)
            # else:
            #     action, least_overflow_1 = self.unitary_actions_simulate(observation)
            if self.n_actions == 1:
                action, least_overflow_1 = self.build_unitary_actions_with_seq_simulation(observation)
            else:
                actions = self.make_recommandations(observation, n_actions=self.n_actions)
                # Simulate everything
                logger.debug(f'== Pooled {len(actions)} actions from our Reinforcment core ==')
                if got_redispatching([a[0] for a in actions]):
                    logger.debug('Got redispatching !')
                for a, max_rho in actions:
                    logger.debug(f"Max rho (simulated): {max_rho}")
                    logger.debug(a)
                idx = self.take_action_index if self.take_action_index < len(actions) else len(actions)-1
                action, least_overflow_1 = actions[idx]  # Get first action, theoretically the most efficient
            # if the action has not solved the overflow
            if least_overflow_1 > 1.0:
                self.alarm_overflow_flag = True
        else:
            action = self.action_space({})
        # If lines 45 or 56 are disconnected, add redispatching to the action
        if (observation.line_status[45] == False or observation.line_status[56] == False):

            if action != self.action_space({}) \
                    and self.redispatch_cnt < self.max_redispatch_cnt \
                    and action.impact_on_objects()['topology']['changed']:
                action, least_overflow_2 = self.add_redispatching_to_action_if_possible(observation, action)

            if observation.attention_budget[0] >= 2:
                self.alarm_overflow_flag = True

        return action

    def act(self, observation, reward, done):
        # if not observation.month == 12:
        #     return self.action_space({}) 

        self.alive_step += 1
        self.alarm_overflow_flag = False

        if not self.alarm_cool_down:
            self.alarm_count += 1
            if self.alarm_count >= self.alarm_cool_time:
                self.alarm_cool_down = True
                self.alarm_count = 0

        action = self.act_without_alarm(observation)

        if np.any(observation.rho > 1.0) or np.any(observation.line_status == False):

            if observation.attention_budget[0] >= 2:
                self.alarm_overflow_flag = True

        if self.alarm_overflow_flag and not observation.is_alarm_illegal and self.alarm_cool_down:
            zones_alert = self.get_region_alert(observation)
            action.raise_alarm = zones_alert
            self.alarm_cool_down = False
            self.alarm_count = 0

        # if this action will cause game over, the try disconnected action
        sim_obs, sim_reward, sim_done, sim_inf = observation.simulate(action)
        observation._obs_env._reset_to_orig_state()

        if sim_done:
            for dis_line in range(59):  # from the left to the right
                try:
                    dis_action = self.action_space.disconnect_powerline(dis_line)
                    dis_obs, dis_reward, dis_done, dis_inf = observation.simulate(dis_action)
                    observation._obs_env._reset_to_orig_state()

                    if not dis_done:
                        return dis_action

                except BaseException:
                    print('disconnect_action error')
                    continue

        return action

    def calc_sub_topo_dict(self, observation):
        offset = 0
        sub_topo_dict = {}

        for sub_id, sub_elem_num in enumerate(observation.sub_info):
            sub_topo = observation.topo_vect[offset:offset + sub_elem_num]
            offset += sub_elem_num
            sub_topo_dict[sub_id] = sub_topo

        return sub_topo_dict

    def reconnect_action(self, observation):
        # reconnect the line if the line will not cause overflow
        # return a reconnect action or None
        disconnected_lines = np.where(observation.line_status == False)[0].tolist()

        for line_id in disconnected_lines:  # from the left to the right
            if observation.time_before_cooldown_line[line_id] == 0:
                action = self.action_space({"set_line_status": [(line_id, +1)]})

                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
                    observation._obs_env._reset_to_orig_state()
                    if np.max(observation.rho) < 1.0 and np.max(obs_simulate.rho) >= 1.0:
                        continue

                except BaseException:
                    print('reconnect_action error')
                    continue

                finally:
                    self.simulate_times += 1

                return action

        return None

    def reset_topology(self, observation):
        # if there is no overflow then try to reset the topology
        if np.max(observation.rho) < 0.95:

            for sub_id, sub_elem_num in enumerate(observation.sub_info):
                sub_topo = self.sub_topo_dict[sub_id]

                if sub_id == 28:
                    sub_28_topo = np.array([2.0, 1.0, 2.0, 1.0, 1.0]).astype(np.int32)

                    if not np.all(sub_topo.astype(np.int32) == sub_28_topo.astype(np.int32)) \
                            and observation.time_before_cooldown_sub[sub_id] == 0:

                        act = self.action_space({
                            "set_bus": {
                                "substations_id": [(sub_id, sub_28_topo.astype(np.int32).tolist())]
                            }
                        })

                        try:
                            obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(act)
                            observation._obs_env._reset_to_orig_state()
                            if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                                return None
                            if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                                if np.max(obs_simulate.rho) < 0.95:
                                    return act

                        except BaseException:
                            print('reset_topology error')
                            continue

                        finally:
                            self.simulate_times += 1

                    continue

                if np.any(sub_topo == 2) and observation.time_before_cooldown_sub[sub_id] == 0:
                    sub_topo = np.where(sub_topo == 2, 1, sub_topo)  # bus 2 to bus 1
                    sub_topo = np.where(sub_topo == -1, 0, sub_topo)  # don't do action in bus=-1
                    reconfig_sub = self.action_space({
                        "set_bus": {
                            "substations_id": [(sub_id, sub_topo.astype(np.int32).tolist())]
                        }
                    })

                    try:
                        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(reconfig_sub)
                        observation._obs_env._reset_to_orig_state()
                        if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                            return None
                        if not done_simulate:
                            if not np.any(obs_simulate.topo_vect != observation.topo_vect):  # have some impact
                                return None
                        if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                            if np.max(obs_simulate.rho) < 0.95:
                                return reconfig_sub

                    except BaseException:
                        print('reset_topology error')
                        return None

                    finally:
                        self.simulate_times += 1

        elif np.max(observation.rho) >= 1.0:
            sub_id = 28
            sub_topo = self.sub_topo_dict[sub_id]
            if np.any(sub_topo == 2) and observation.time_before_cooldown_sub[sub_id] == 0:
                sub_28_topo = np.array([1.0, 1.0, 1.0, 1.0, 1.0]).astype(int)
                act = self.action_space({
                    "set_bus": {
                        "substations_id": [(sub_id, sub_28_topo.astype(int))]
                    }
                })

                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(act)
                    observation._obs_env._reset_to_orig_state()
                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        return None
                    if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                        if np.max(obs_simulate.rho) < 0.99:
                            return act

                except BaseException:
                    print('reset_topology error')
                    return None

        return None

    def reset_redispatch(self, observation):
        # if there is no overflow then try to reset the redispatch
        if np.max(observation.rho) < 1.0:
            # reset redispatch
            if not np.all(observation.target_dispatch == 0.0):
                gen_ids = np.where(observation.gen_redispatchable)[0]
                gen_ramp = observation.gen_max_ramp_up[gen_ids]
                changed_idx = np.where(observation.target_dispatch[gen_ids] != 0.0)[0]
                redispatchs = []
                for idx in changed_idx:
                    target_value = observation.target_dispatch[gen_ids][idx]
                    value = min(abs(target_value), gen_ramp[idx])
                    value = -1 * target_value / abs(target_value) * value
                    redispatchs.append((gen_ids[idx], value))
                action = self.action_space({"redispatch": redispatchs})

                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
                    observation._obs_env._reset_to_orig_state()
                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        return None
                    if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                        if np.max(obs_simulate.rho) < 1.0:
                            return action

                except BaseException:
                    print('reset_redispatch error')
                    return None

                finally:
                    self.simulate_times += 1

    def get_action_from_index(self, observation, idx):
        # this function is used to get a legal action from the action space
        action = self.unitary_actions[idx]
        sub_id = self.action_to_sub_id[idx]
        if sub_id != "redispatch":  # topology change action
            if observation.time_before_cooldown_sub[int(sub_id)] != 0:
                return None

            legal_action_vec = np.array(action.to_vect()).copy()
            sub_topo = self.sub_topo_dict[int(sub_id)]

            if np.any(sub_topo == -1):  # line disconnected
                start, end = self.action_to_sub_topo[int(sub_id)]
                action_topo = legal_action_vec[start:end].astype(np.int32)  # reference
                action_topo[np.where(sub_topo == -1)[0]] = 0  # done't change bus=-1
                legal_action_vec[start:end] = action_topo
                legal_action = self.action_space.from_vect(legal_action_vec)

            else:
                legal_action = action

        else:
            legal_action = action

        return legal_action

    def make_simulatable_obs(self, new_obs, old_obs):
        # make the simulated obs simulatable
        new_obs.action_helper = old_obs.action_helper
        new_obs._obs_env = old_obs._obs_env

        # direct copy
        new_obs._forecasted_inj = old_obs._forecasted_inj

        # if len(new_obs._forecasted_inj) > 2:
        #     new_obs._forecasted_inj = new_obs._forecasted_inj[1:]

        # linear extrapolation of the injection
        # new_injection = {k : 2 * old_obs._forecasted_inj[1][1]['injection'][k] - old_obs._forecasted_inj[0][1]['injection'][k] for k in old_obs._forecasted_inj[1][1]['injection']}
        # new_datetime = old_obs._forecasted_inj[1][0] + datetime.timedelta(minutes=5)
        # new_obs._forecasted_inj = [old_obs._forecasted_inj[1], (new_datetime, {'injection' : new_injection})]

        return new_obs

    def build_unitary_actions_with_seq_simulation(self, observation):
        # get a baseline by do nothing
        try:
            obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(self.action_space({}))
            observation._obs_env._reset_to_orig_state()

            least_overflow = 2.0
            if obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                least_overflow = float(np.max(obs_simulate.rho))

        except BaseException:
            least_overflow = 2.0

        finally:
            self.simulate_times += 1

        if least_overflow < 1.0:
            return self.action_space({}), least_overflow

        # candidate in format (max_rho, action_sequence, simulatable_obs, expanded_flag)
        line_overflow = observation.rho >= 1.0
        candidates = [(observation.rho.max(), [], observation, False)]

        def compare(a, b):
            penalty_factor = 0.1

            a_score = a[0] + penalty_factor * len(a[1])
            b_score = b[0] + penalty_factor * len(b[1])

            a_solve = a[0] < 1.0
            b_solve = b[0] < 1.0

            if not a_solve == b_solve:
                return -1 if a_solve else 1

            a_fix_line = np.all(np.logical_or(a[2].rho >= 1.0, line_overflow))
            b_fix_line = np.all(np.logical_or(b[2].rho >= 1.0, line_overflow))

            if a_fix_line == b_fix_line:
                if a_score == b_score:
                    return 0
                else:
                    return -1 if a_score < b_score else 1
            else:
                return -1 if a_fix_line else 1

        planning_horizon = 4 - observation.timestep_overflow.max()
        for depth in range(planning_horizon):
            new_candidates = []
            expand_num = 150 if depth == 0 else 50
            select_num = 50 if depth == 0 else 50

            for candidate in candidates:
                current_max_rho, current_actions, simulatable_obs, expanded_flag = candidate

                if current_max_rho < 1.0:  # already in control, do not simulate further
                    new_candidates.append(candidate)
                    continue

                if expanded_flag == True:  # the candidate is already expanded
                    new_candidates.append(candidate)
                    continue
                else:
                    new_candidates.append((current_max_rho, current_actions, simulatable_obs, True))  # mark as expanded

                predicted_rho = self.unitary_es_agent(simulatable_obs)[0, :]  # 500
                sorted_idx = np.argsort(predicted_rho).tolist()
                top_idx = sorted_idx[:expand_num]
                top_idx.sort()

                for idx in top_idx:
                    legal_action = self.get_action_from_index(simulatable_obs, idx)
                    if legal_action is None: continue
                    if legal_action in current_actions: continue

                    obs_simulate, reward_simulate, done_simulate, info_simulate = simulatable_obs.simulate(legal_action)
                    observation._obs_env._reset_to_orig_state()

                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        continue

                    if obs_simulate is not None and not any(np.isnan(obs_simulate.rho)) and not done_simulate:
                        overflow_value = float(np.max(obs_simulate.rho))
                        action_sequence = deepcopy(current_actions)
                        action_sequence.append(legal_action)
                        new_candidates.append((overflow_value, action_sequence,
                                               self.make_simulatable_obs(obs_simulate, simulatable_obs), False))

                    self.simulate_times += 1

            # new_candidates = sorted(new_candidates, key=lambda x: x[0])
            new_candidates = sorted(new_candidates, key=functools.cmp_to_key(compare))
            candidates = new_candidates[:select_num]  # only consider the top 30

            if candidates[0][0] < 1.0: break

        if len(candidates) > 0:
            best_candidate = candidates[0]

            if len(best_candidate[1]) == 0:
                return self.action_space({}), least_overflow

            if best_candidate[0] >= least_overflow:
                return self.action_space({}), least_overflow

            best_action = best_candidate[1][0]
            simulated_obs, _, _, _ = observation.simulate(best_action)
            rho = simulated_obs.rho.max()

            return best_action, rho
        else:
            return self.action_space({}), least_overflow

    def make_recommandations(self, observation, n_actions=3) -> List[Tuple]:
        """
        This function builds operational plans by ensuring a sufficient diversity of actions is retained.
        It will try to provide amongst recommandations at least one redispatch action, alongside with
        topological changes on distinct substations.
        It is NOT designed to provide the `n_recommandations` best actions, but to provide human player with
        interesting action choices.
        :param observation: A Grid2oOp.Observation
        :param n_actions: Number of actions to return
        :return: A list of Grid2Op.Action with their simulated max_rho
        """
        try:
            obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(self.action_space({}))
            observation._obs_env._reset_to_orig_state()

            least_overflow = 2.0
            if obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                least_overflow = float(np.max(obs_simulate.rho))

        except BaseException:
            least_overflow = 2.0

        finally:
            self.simulate_times += 1
        # No overflow: do nothing!
        if least_overflow < 1.0:
            return [(self.action_space({}), least_overflow)]

        self.sub_topo_dict = self.calc_sub_topo_dict(observation)

        # Candidate in format (max_rho, action_sequence, simulatable_obs, expanded_flag)
        line_overflow = observation.rho >= 1.0
        candidates = [(observation.rho.max(), [], observation, False)]

        def compare(a, b):
            penalty_factor = 0.1

            a_score = a[0] + penalty_factor * len(a[1])
            b_score = b[0] + penalty_factor * len(b[1])

            a_solve = a[0] < 1.0
            b_solve = b[0] < 1.0

            if not a_solve == b_solve:
                return -1 if a_solve else 1

            a_fix_line = np.all(np.logical_or(a[2].rho >= 1.0, line_overflow))
            b_fix_line = np.all(np.logical_or(b[2].rho >= 1.0, line_overflow))

            if a_fix_line == b_fix_line:
                if a_score == b_score:
                    return 0
                else:
                    return -1 if a_score < b_score else 1
            else:
                return -1 if a_fix_line else 1

        planning_horizon = 4 - observation.timestep_overflow.max()

        # We'll build candidate action sequences up to planning_horizon depth
        for depth in range(planning_horizon):
            new_candidates = []
            expand_num = 150 if depth == 0 else 50
            select_num = 50 if depth == 0 else 50

            for candidate in candidates:
                # Get candidate (max_rho, action_sequence, simulatable_obs, expanded_flag)
                current_max_rho, current_actions, simulatable_obs, expanded_flag = candidate

                if current_max_rho < 1.0:  # already in control, do not simulate further
                    new_candidates.append(candidate)
                    continue

                if expanded_flag == True:  # the candidate is already expanded
                    new_candidates.append(candidate)
                    continue
                else:
                    new_candidates.append((current_max_rho, current_actions, simulatable_obs, True))  # mark as expanded
                # Get forecasted rhos from our NeuralNet model
                predicted_rho = self.unitary_es_agent(simulatable_obs)[0, :]  # 500
                sorted_idx = np.argsort(predicted_rho).tolist()
                # Keep only expand_num actions
                top_idx = sorted_idx[:expand_num]
                top_idx.sort()  # WHY ??

                # For action in top 50 to 150 actions
                for idx in top_idx:
                    legal_action = self.get_action_from_index(simulatable_obs, idx)
                    if legal_action is None: continue
                    if legal_action in current_actions: continue

                    obs_simulate, reward_simulate, done_simulate, info_simulate = simulatable_obs.simulate(legal_action)
                    observation._obs_env._reset_to_orig_state()

                    # Drop invalid actions
                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        continue
                    # Add action seq to candidates
                    if obs_simulate is not None and not any(np.isnan(obs_simulate.rho)) and not done_simulate:
                        overflow_value = float(np.max(obs_simulate.rho))
                        action_sequence = deepcopy(current_actions)
                        action_sequence.append(legal_action)
                        new_candidates.append((overflow_value, action_sequence,
                                               self.make_simulatable_obs(obs_simulate, simulatable_obs), False))

                    self.simulate_times += 1

            new_candidates = sorted(new_candidates,
                                    key=functools.cmp_to_key(compare))  # sort action sequences by effectiveness
            candidates = new_candidates[:select_num]  # only consider the top candidates

            if candidates[0][0] < 1.0: break

        # Extract best candidate from all candidates.
        if len(candidates) > 0:
            return self.filter_candidates(candidates, observation, n_recommandations=n_actions)

        # No candidate...
        else:
            return [(self.action_space({}), least_overflow)]

    @staticmethod
    def filter_candidates(candidates, observation, n_recommandations):

        # Candidates are sorted by efficiency
        sub_ids = []
        actions = []
        best_action_to_add = None
        for c in candidates:
            # Empty actions !
            if len(c[1]) == 0:
                continue
            action = c[1][0]

            # Return when we have enough actions
            if len(actions) == n_recommandations:
                break

            # Try to fill the last free action slot with a redispatching action
            if len(actions) == n_recommandations - 1 and not got_redispatching(actions) and not is_redispacthing(
                    action):
                if best_action_to_add is None and get_sub_id_in_action(action) not in sub_ids:
                    best_action_to_add = action
                continue

            # Filling actions with action
            else:
                # Redispatch
                if is_redispacthing(action):
                    actions.append(action)
                # Topological
                else:
                    sub_id = get_sub_id_in_action(action)
                    # Already got an action on this sub_id
                    if sub_id in sub_ids:
                        continue
                    sub_ids.append(sub_id)
                    actions.append(action)
        # Fill remaining actions with a saved action
        if best_action_to_add is None:
            if len(candidates[0][1])>0:
                best_action_to_add = candidates[0][1][0]
            else:
                n_recommandations = 0  # pas trouve de recommandation a faire
        if len(actions) < n_recommandations:
            actions += [best_action_to_add] * (n_recommandations - len(actions))

        out = []
        for action in actions:
            obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
            rho = obs_simulate.rho.max()
            out.append((action, rho))
        return out

    def add_redispatching_to_action_if_possible(self, observation, action):
        """
        Add redispatching to a given action
        """
        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
        observation._obs_env._reset_to_orig_state()

        origin_rho = 10.0
        if not done_simulate:
            origin_rho = obs_simulate.rho.max()

        least_rho = origin_rho
        best_action = None
        for redispatch_action in self.redispatch_actions:
            try:
                redispatch_action = copy.deepcopy(redispatch_action)
                redispatch_action._curtail = np.zeros(22)
                action = copy.deepcopy(action)
                action._redispatch = np.zeros(22)

                combine_action = self.action_space.from_vect(action.to_vect() + redispatch_action.to_vect())

                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(combine_action)
                observation._obs_env._reset_to_orig_state()

            except BaseException:
                print('redispatch_action error')
                continue

            max_rho = 10.0
            if not done_simulate:
                max_rho = obs_simulate.rho.max()
            if max_rho < least_rho:
                least_rho = max_rho
                best_action = combine_action

        if least_rho < origin_rho:
            action = best_action
            self.redispatch_cnt += 1

        return action, least_rho

    def get_region_alert(self, observation):
        # extract the zones they belong too
        zones_these_lines = set()
        zone_for_each_lines = self.alarms_lines_area

        lines_overloaded = np.where(observation.rho >= 1)[0].tolist()  # obs.rho>0.6
        # print(lines_overloaded)
        for line_id in lines_overloaded:
            line_name = observation.name_line[line_id]
            for zone_name in zone_for_each_lines[line_name]:
                zones_these_lines.add(zone_name)

        zones_these_lines = list(zones_these_lines)
        zones_ids_these_lines = [self.alarms_area_names.index(zone) for zone in zones_these_lines]
        return zones_ids_these_lines


def make_agent(env, submission_path, n_actions=3, take_action_index=2):
    # my_agent = MyAgent(env.action_space,  env.alarms_lines_area, env.alarms_area_names, submission_path)
    my_agent = PowerNetAgent(env, submission_path, n_actions,take_action_index)
    return my_agent


def is_redispacthing(action):
    return action.impact_on_objects()["redispatch"]['changed']


def got_redispatching(actions):
    return any(is_redispacthing(a) for a in actions)


def get_sub_id_in_action(action):
    impact = action.impact_on_objects()
    if impact["topology"]['changed']:
        return impact["topology"]["assigned_bus"][0]['substation']
    else:
        return None
