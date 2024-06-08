from typing import List, Dict, Tuple

import numpy as np
from bresenham import bresenham


def route_steps_on_edge(x_start: float, y_start: float, x_end: float, y_end: float) -> List[Tuple[float, float]]:
    """
    Return list with grid points based on bresenham algorithm:
        1. A distance vector is laid out along a straight line between points A and B.
        2. Next, the vector is placed on grip of floats - those squares that intersect the straight line are returned in the array.
    """
    x_start, y_start, x_end, y_end = int(100*x_start), int(100*y_start), int(100*x_end), int(100*y_end)
    quadrants = [(i[0]/100, i[1]/100) for i in list(bresenham(x_start, y_start, x_end, y_end))]
    return quadrants

def get_closest_grid_points_on_route_step(neigbors, quadrants: List[Tuple[float, float]]) -> List[List[int]]:
    """
    Return array with 4 closest points in grid by its index in source grid
    """
    _, closest_quadrants = neigbors.kneighbors(quadrants)
    return closest_quadrants.tolist()

def ice_integral_coefficient_on_step(neighbors_on_step: List[int], grid: np.array, date_num_col) -> List[float]:
    ice_metric_on_step = []
    for candidate in neighbors_on_step:
        ice_metric_on_step.append(grid[candidate, date_num_col])
    return bugfix_on_ice(ice_metric_on_step)

def speed_on_step(vessel_category: int, ice_metrics: List[float], limits) -> List[float]:
    # TODO: place here speed_limitations from actors
    ...

def ice_metrics_on_route(closest_quadrants: List[List[int]], grid: np.array, date_num_col: int) -> Tuple[np.array, set]:
    ice_metric = []
    for neighbors_on_step in closest_quadrants:
        ice_metric.append(ice_integral_coefficient_on_step(neighbors_on_step, grid, date_num_col))
    ice_metric = np.array(ice_metric)
    return ice_metric.min(axis=1), set(ice_metric.min(axis=1))

def bugfix_on_ice(ice_metric):
    ice_metric = np.array(ice_metric)
    res = np.where(ice_metric<=0, ice_metric[ice_metric>0].mean(), ice_metric)
    if np.isnan(res).all():
        return np.array([10.0]*len(ice_metric))
    return res
