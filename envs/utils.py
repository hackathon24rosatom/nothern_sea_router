import os
import dill
import numpy as np
from sklearn.neighbors import NearestNeighbors


def find_and_serialize_neighbors(grid: np.array, static_folder: str, file_name: str = "neighbors"):
    nbrs = NearestNeighbors(n_neighbors=32, algorithm='ball_tree').fit(grid)
    file_path = os.path.join(os.getcwd(), static_folder, file_name)
    with open(file_path, 'wb') as file:
        dill.dump(nbrs, file)

def load_serialized_neighbors(static_folder: str, file_name: str = "neighbors"):
    file_path = os.path.join(static_folder, file_name)
    with open(file_path, 'rb') as file:
        neighbors = dill.load(file)
    return neighbors

