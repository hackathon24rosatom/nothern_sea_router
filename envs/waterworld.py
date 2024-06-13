from numpy import array, float32, zeros
from numpy.typing import NDArray
from numpy.random import randint
from numpy.lib.stride_tricks import sliding_window_view
from math import acos, pi

from gymnasium import Env
from gymnasium.spaces import Box, Dict, Discrete

from envs.ship import Ship


class WaterWorld(Env):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self.water_map: NDArray = config.get('water_map')
        self.map_shape = config.get('map_shape')
        self.window_shape = config.get('window_shape')
        self.max_episode_steps = config.get('max_episode_steps')

        self._watermap_with_borders, self._sliding_window_view = self._get_sliding_view(
            water_map=self.water_map,
            window_shape=self.window_shape
        )

        self._xshift = abs(self.water_map.shape[0] - self._watermap_with_borders.shape[0]) // 2
        self._yshift = abs(self.water_map.shape[1] - self._watermap_with_borders.shape[1]) // 2
        # self._xmax = self._sliding_window_view.shape[0] - 1
        # self._ymax = self._sliding_window_view.shape[1] - 1

        self._distance_scaler = array(self.water_map.shape)
        
        # self.action_space = Box(low=-1, high=1, shape=(2, ), dtype=float32)
        self.action_space = Discrete(n=4)
        self.observation_space = Dict({
            'velocity': Box(low=0, high=1, shape=(1, ), dtype=float32),
            # 'geo': Box(low=0, high=self.water_map.shape[0], shape=(2, ), dtype=float32),
            # 'way_point': Box(low=0, high=self.water_map.shape[0], shape=(2, ), dtype=float32),
            'slide_window': Box(low=0, high=1, shape=self.window_shape, dtype=float32),
            'angle': Box(low=-1, high=0, shape=(1, ), dtype=float32),
            # 'distance': Box(low=-1, high=1, shape=(2, ), dtype=float32),
            'compas': Box(low=-1, high=1, shape=(2, ), dtype=float32),
        })

    @staticmethod
    def _get_sliding_view(water_map: NDArray, window_shape):
        # use window shape 1, 3, 5...
        border_window = tuple(map(lambda x: x // 2 + 1, window_shape))
        watermap_with_borders = zeros(shape=(
            water_map.shape[0] + 2 * border_window[0],
            water_map.shape[1] + 2 * border_window[1],
        ))
        watermap_with_borders[
            border_window[0]: -border_window[0],
            border_window[1]: -border_window[1],
        ] = water_map

        return (
            watermap_with_borders,
            sliding_window_view(watermap_with_borders, window_shape=window_shape),
        )
    
    def _get_ice_value(self):
        # TODO надо заменить
        geo_x, geo_y = self.ship.geo
        return self._watermap_with_borders[(geo_x + self._xshift, geo_y + self._yshift)]

    def _get_window_view(self):
        return self._sliding_window_view[tuple(map(lambda x: x + 1, self.ship.int_geo))]

    def _init_ship(self):
        while True:
            lat = randint(low=0, high=self.water_map.shape[0])
            lng = randint(low=0, high=self.water_map.shape[1])

            if self._watermap_with_borders[(lat + self._xshift, lng + self._yshift)] != 0:
                break
        return Ship(
            velocity=1.,
            lat=lat,
            lng=lng,
        )

    def _init_waypoint(self):
        while True:
            lat = randint(low=0, high=self.water_map.shape[0])
            lng = randint(low=0, high=self.water_map.shape[1])

            if (
                self._watermap_with_borders[(lat + self._xshift, lng + self._yshift)] != 0 and
                lat != self.ship.lat and lng != self.ship.lng
            ):
                break
        return (lat, lng)

    def _get_angle(self):
        if self._last_action is None:
            return 0.
        geo_x, geo_y = self.ship.geo
        way_point_x_vec = geo_x - self.way_point[0]
        way_point_y_vec = geo_y - self.way_point[1]
        sum_wayp = sum(map(abs, [way_point_x_vec, way_point_y_vec]))
        if sum_wayp == 0:
            return 0.
        
        ship_x_vec, ship_y_vec = self.ship.vec_xy
        s = (way_point_x_vec * ship_x_vec + way_point_y_vec * ship_y_vec)
        l = (
            (way_point_x_vec ** 2 + way_point_y_vec ** 2) ** (1/2) *
            (ship_x_vec ** 2 + ship_y_vec ** 2) ** (1/2)
        )
        return acos(round(s / l, 5)) / pi - 1


    def _get_compas(self):
        geo_x, geo_y = self.ship.geo
        way_point_x_vec = geo_x - self.way_point[0]
        way_point_y_vec = geo_y - self.way_point[1]

        sum_wayp = sum(map(abs, [way_point_x_vec, way_point_y_vec])) or 1

        return array([way_point_x_vec, way_point_y_vec]) / sum_wayp
    
    def _get_distance(self):
        geo_x, geo_y = self.ship.geo
        way_point_x, way_point_y = self.way_point

        return array([way_point_x - geo_x, way_point_y - geo_y]) / self._distance_scaler

    def _is_term(self):
        # TODO
        geo_x, geo_y = self.ship.geo
        way_point_x, way_point_y = self.way_point

        return ((geo_x - way_point_x) ** 2 + (geo_y - way_point_y) ** 2) ** (1/2) <= 0.2

    def _is_trunc(self):
        geo_x, geo_y = self.ship.geo
        return any([
            self._steps >= self.max_episode_steps,
            self._get_ice_value() == 0,
            geo_x < 0,
            geo_x > self.water_map.shape[0],
            geo_y < 0,
            geo_y > self.water_map.shape[1],
        ])

    @staticmethod
    def _generate_rnd_map(map_shape, map_stack_count=1):
        map_generator = lambda shape: randint(low=0, high=4, size=map_shape).astype(bool)

        new_map = sum([map_generator(map_shape)] * map_stack_count).astype(int)

        return new_map

    @property
    def obs(self):
        return {
            'velocity': self.ship.numpy_velocity,
            # 'geo': self.ship.numyp_geo,
            # 'way_point': self._numpy_way_point,
            'slide_window': self._get_window_view(),
            'angle': array([self._get_angle()]),
            'compas': self._get_compas(),
        }

    def reset(self, *, seed=None, options=None):
        new_map = self._generate_rnd_map(self.map_shape)
        self.water_map = new_map
        self._watermap_with_borders, self._sliding_window_view = self._get_sliding_view(
            water_map=self.water_map,
            window_shape=self.window_shape
        )
        # self._xshift = abs(self.water_map.shape[0] - self._watermap_with_borders.shape[0]) // 2
        # self._yshift = abs(self.water_map.shape[1] - self._watermap_with_borders.shape[1]) // 2

        self.ship = self._init_ship()
        self.way_point = self._init_waypoint()
        self._numpy_way_point = array(list(self.way_point))
        self._steps = 0
        self._last_action = None
        self._reward = 0

        return self.obs, {}

    def step(self, action: int):
        self._steps += 1
        self._last_action = action
        self.ship.update(action)
        # ice_value = self._get_ice_value()

        term, trunc = self._is_term(), self._is_trunc()
        reward = self._get_angle()

        if term:
            reward = 100

        if trunc:
            reward = -100
            # reward = sum(map(lambda x: x ** 2, self._get_distance())) ** (1/2)
        
        return self.obs, reward, term, trunc, {}
