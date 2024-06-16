from numpy import array, float32, zeros

from collections import defaultdict
from gymnasium.spaces import Discrete, Dict, Box

from envs.waterworld_geo import WaterWorldGeo
from envs.actors import ShipTimed, IceBreaker

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.utils.annotations import override


class WaterWorldGeoDiscrete(WaterWorldGeo):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._time_tick = config.get('time_tick')
    
    def reset(self, *, seed=None, options = None):
        self._steps = 0
        self._last_slide_circle = zeros(self.observation_space['slide_circle'].shape)
        self.ship: ShipTimed = options.get('ship')

        return self.obs, {}

    def _is_term(self):
        distance = self.ship.get_port_distance()
        if distance:
            return distance <= 10
        return False

    def _is_trunc(self):
        return any([
            self.ship.curr_speed is None,
            self.ship.location_point.latitude > 90, 
            self.ship.location_point.latitude < -90,
            self.ship.location_point.longitude > 200,
            self.ship.location_point.longitude < -200,
            int(self.ship.total_time // (24 * 7) + self.date_start) >= 14
        ])

    @property
    def obs(self):
        return {
            'angle': array([self.ship._get_angle()], dtype=float32),
            'compas': self.ship._get_compas().astype(float32),
            'slide_circle': self._get_slide_circle().astype(float32),
            'velocity': array([self.ship.curr_speed], dtype=float32),
            'ice_arc': array([self.ship.category.value], dtype=float32),
        }

from copy import deepcopy

class WaterWorldMultiEnv(MultiAgentEnv):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self._steps = 0
        self.max_episode_steps = config.get('max_episode_steps')
        self.neighbors_shape = config.get('neighbors_shape')

        self._time_tick = config.get('time_tick')
        self._ice_breaker_count = config.get('ice_breaker_counts')
        self._ships_count = config.get('ships_count')

        self._ships_list = config.get('ships_list')

        self.envs: list[WaterWorldGeoDiscrete] = [
            WaterWorldGeoDiscrete(config) for _ in range(self._ships_count + self._ice_breaker_count)
        ]
        # только ледоколы
        self._ice_breakers = self.envs[-self._ice_breaker_count:]
        # 
        self.terminateds = set()
        self.truncateds = set()
        self.observation_space = Dict({
            i: Dict({
                'angle': Box(low=-1, high=0, shape=(1, )),
                'compas': Box(low=-1, high=1, shape=(2, )),
                'slide_circle': Box(low=0, high=25, shape=self.neighbors_shape),
                'velocity': Box(low=0, high=25, shape=(1, )),
                'ice_arc': Box(low=0, high=12, shape=(1, )),
                'cordes': Box(low=-200, high=200, shape=(2, )),
                'ice_breaker_cords': Box(low=-200, high=200, shape=(self._ice_breaker_count * 2, )),
            }) for i, _ in enumerate(self.envs)
        })
        self._obs_space_in_preferred_format = True
        # up, down, left, right, waiting, connect, disconnect
        self.action_space = Dict({
            i: Discrete(n=7) for i, _ in enumerate(self.envs)
        })
        self._action_space_in_preferred_format = True
        self._agent_ids = set(range(len(self.envs)))

    def _get_ice_breaker_cordes(self):
        return array([
            [ice_breaker.ship.location_point.latitude, ice_breaker.ship.location_point.longitude]
            for ice_breaker in self._ice_breakers
        ], dtype=float32).flatten()

    def _get_agent_cordes(self, agent_ids: int):
        location_point = self.envs[agent_ids].ship.location_point
        return array([
            location_point.latitude,
            location_point.longitude,
        ], dtype=float32)

    @override(MultiAgentEnv)
    def reset(self, *, seed=None, options=None):
        self._steps = 0
        self._caravans = defaultdict(list)
        self._obs, self._rew, self._term, self._trunc, self._info = {}, {}, {}, {}, {}
        self.truncateds = set()
        self.truncateds = set()
        # flatten array for key 'ice_breaker_cords'
        for i, ice_breaker in enumerate(self._ice_breakers):
            ice_index = i + self._ships_count
            local_options = {'ship': deepcopy(self._ships_list[ice_index])}
            self._obs[ice_index], self._info[ice_index] = ice_breaker.reset(seed=seed, options=local_options)
            self._obs[ice_index]['cordes'] = self._get_agent_cordes(ice_index)

        ice_breaker_cordes = self._get_ice_breaker_cordes()

        for i, env in enumerate(self.envs):
            local_options = {'ship' : deepcopy(self._ships_list[i])}
            self._obs[i], self._info[i] = env.reset(seed=seed, options=local_options)
            self._obs[i]['cordes'] = self._get_agent_cordes(i)
            self._obs[i]['ice_breaker_cords'] = ice_breaker_cordes

        self._term['__all__'] = False
        self._trunc['__all__'] = False

        return self._obs, self._info

    @override(MultiAgentEnv)
    def step(self, action_dict: dict):
        self._steps += 1
        ice_breaker_cordes = self._get_ice_breaker_cordes()
        for i, action in action_dict.items():
            if self._term.get(i, False) or self._trunc.get(i, False):
                continue
            env = self.envs[i]
            if action == 4:
                pass
            elif action == 5:
                nearest_id, nearest_ice_breaker = self._get_nearest_ice_breaker(env.ship)
                if nearest_id:
                    caravan_list = self._caravans[nearest_id]
                    if len(caravan_list) < 2 and env.ship not in caravan_list:
                        self._caravans[nearest_id].append(env.ship)
            elif action == 6:
                nearest_id, nearest_ice_breaker = self._get_nearest_ice_breaker(env.ship)
                if nearest_id and env.ship in self._caravans[nearest_id]:
                    self._caravans[nearest_id].remove(env.ship)
            self._obs[i], self._rew[i], self._term[i], self._trunc[i], self._info[i] = (
                env.step(action)
            )
            env.ship._update_speed(
                self._obs[i]['slide_circle'].mean()
            )
            self._obs[i]['cordes'] = self._get_agent_cordes(i)
            self._obs[i]['ice_breaker_cords'] = ice_breaker_cordes
            if self._term[i]:
                self.terminateds.add(i)
            if self._trunc[i]:
                self.truncateds.add(i)
            
        self._update_caravans()
        self._term['__all__'] = len(self.terminateds) > 0
        self._trunc['__all__'] = len(self.truncateds) > 0 or self._steps >= self.max_episode_steps
        
        if self._term['__all__'] or self._trunc['__all__']:
            for key in self._rew:
                if not self._term[key]:
                    self._rew[key] = -self.envs[i].ship.total_time

        return self._obs, self._rew, self._term, self._trunc, self._info

    def _get_nearest_ice_breaker(self, ship: ShipTimed):
        def get_distance(ship1: ShipTimed, ship2: ShipTimed):
            return ShipTimed._get_distance(
                ship1.location_point,
                ship2.location_point
            )
        distances = {}
        for i, ice_breaker_env in enumerate(self._ice_breakers):
            distances[i] = get_distance(ship, ice_breaker_env.ship)
        try:
            ice_breaker_id = min(distances.keys(), key=lambda key: distances[key])
            if distances[ice_breaker_id] <= 20:
                return ice_breaker_id, self._ice_breakers[ice_breaker_id]
        except:
            pass
        return None, None
    
    def _update_caravans(self):
        for caravan_id, ships_list in self._caravans.items():
            ice_breaker = self._ice_breakers[caravan_id].ship
            if len(ships_list) == 0:
                slowest_speed = ice_breaker.avg_speed
            else:
                slowest_ship = min(ships_list, key=lambda ship: ship.avg_speed)
                slowest_speed = slowest_ship.avg_speed

            ice_breaker.avg_speed = slowest_speed
            for ship in ships_list:
                ship.avg_speed = slowest_speed
