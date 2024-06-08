import numpy as np
from geopy.distance import great_circle


class Route_parameters:
    def __init__(self, speed_array, start_point, end_point):
        """
        Initializes a Route_parameters object.

        Args:
            speed_array (List[List[float]]): A list of lists containing the speeds for each point in the route.
            start_point (Tuple[float, float]): The starting point of the route.
            end_point (Tuple[float, float]): The ending point of the route.

        Returns:
            None
        """
        self.speed_array = np.array(speed_array)
        self.start_point = np.array(start_point)
        self.end_point = np.array(end_point)

    # Define the get_distance method by great_circle
    def get_distance(self):
        """
        Calculate the distance between the start and end points.

        Returns:
            float: The distance between the start and end points in miles.
        """
        # For example, you can calculate the distance between the start and end points
        k_miles = 0.539957
        distance = great_circle(self.start_point,self.end_point).km * k_miles
        return distance
    
    def min_speed(self):
        """
        Finds the minimum value in each column of the 2D array.

        Returns:
            numpy.ndarray: A 1D array of minimum values from each column.
        """
        min_numbers = []
        try:
            num_arrays = self.speed_array.shape[1]
            for i in range(num_arrays):
                min_value = float('inf')  # Initialize with a large value
                for array in self.speed_array:
                    if array[i] < min_value:
                        min_value = array[i]
                min_numbers.append(min_value)
            return np.array(min_numbers)
        except IndexError:
            return self.speed_array
    
    def get_time(self):
        distance = self.get_distance()
        min_speed = self.min_speed()
        min_speed = np.average(min_speed) # just a average
        time = distance / min_speed
        return time