from pandas import DataFrame
from numpy import array, float32, zeros
from numpy.typing import NDArray
from numpy.random import choice, randint

from gymnasium import Env
from gymnasium.spaces import Box, Dict

from actors import Ship, VesselCategory, Geopoint, VesselMoveStatus
from route_metrics import ice_integral_coefficient_on_step


class WaterWorldGeo(Env):
    def __init__(self, config: dict) -> None:
        super().__init__()
        # (1, 32)
        self.max_episode_steps = config.get('max_episode_steps')
        self.neighbors_shape = config.get('neighbors_shape')
        self.serialized_neighbors = config.get('serialized_neighbors')
        self.grid: NDArray = config.get('grid')

        self.routes: DataFrame = config.get('routes')
        self.date_start = config.get('date_start')

        self._tick = config.get('tick')

        self.action_space = Box(low=-1, high=1, shape=(2, ))
        self.observation_space = Dict({
            'angle': Box(low=-1, high=0, shape=(1, )),
            'compas': Box(low=-1, high=1, shape=(2, )),
            'slide_circle': Box(low=0, high=25, shape=self.neighbors_shape),
            'velocity': Box(low=0, high=25, shape=(1, )),
        })

    def _get_slide_circle(self):
        _, neighbors = self.serialized_neighbors.kneighbors([(
            self.ship.location_point.latitude,
            self.ship.location_point.longitude
        )])
        date = int(self.ship.total_time // (24 * 7) + self.date_start)
        new_slide_circle = ice_integral_coefficient_on_step(neighbors, self.grid.values, date)
        if self.observation_space['slide_circle'].shape == new_slide_circle.shape:
            self._last_slide_circle = new_slide_circle
        else:
            self._steps = self.max_episode_steps
        return self._last_slide_circle
    
    def _get_new_route(self) -> NDArray:
        # 4 values, ship_geo + waypoint_geo
        ship_lat, ship_lng, waypoint_lat, waypoint_lng = self.routes.sample(n=1).values[0]
        return Geopoint(ship_lat, ship_lng), Geopoint(waypoint_lat, waypoint_lng)
    
    def _init_geo_points(self):
        geo_ship, geo_waypoint = self._get_new_route()
        max_speed = randint(14, 20)
        self.ship = Ship(
            name='test',
            category=choice(list(VesselCategory)),
            location_point=geo_ship,
            route_request=geo_waypoint,
            status=VesselMoveStatus.waiting,
            max_speed=max_speed,
            avg_speed=0.0,
            curr_speed=0.0,
            tick=self._tick,
        )
    
    def _get_angle(self, action):
        x, y = action
        return self.ship._get_angle(x, y)

    def _get_compas(self):
        return self.ship._get_compas()

    def _is_term(self):
        return self.ship.get_port_distance() <= 10

    def _is_trunc(self):
        return any([
            self._steps >= self.max_episode_steps,
            self.ship.curr_speed is None,
            int(self.ship.total_time // (24 * 7) + self.date_start) >= 14
        ])
    
    def reset(self, *, seed=None, options=None):
        self._steps = 0
        self._last_slide_circle = zeros(self.observation_space['slide_circle'].shape)
        while True:
            self._init_geo_points()
            # чтобы понять начальную скороть
            slide_circle = self._get_slide_circle()
            self.ship._update_speed(slide_circle.mean())
            if self.ship.curr_speed:
                break
        return self.obs, {}

    def step(self, action):
        # каждый шаг это +0.01 суммарно по всем координатам, время пути считается в ship
        self._steps += 1
        self.ship.step(action)
        obs = self.obs
        self.ship._update_speed(obs['slide_circle'].mean())
        term, trunc = self._is_term(), self._is_trunc()
        reward = self.ship._get_angle()

        if term:
            reward = -self.ship.total_time
        if trunc:
            reward = -self.max_episode_steps
        return obs, reward, term, trunc, {}

    @property
    def obs(self):
        return {
            'angle': array([self.ship._get_angle()], dtype=float32),
            'compas': self.ship._get_compas().astype(float32),
            'slide_circle': self._get_slide_circle().astype(float32),
            'velocity': array([self.ship.curr_speed], dtype=float32),
        }