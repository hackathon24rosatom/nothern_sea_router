import numpy as np
from geopy.distance import great_circle


class Speedy:
    def __init__(self, speed_array, start_point, end_point):
        self.array = speed_array
        self.start_point = start_point
        self.end_point = end_point

    # Define the get_distance method by great_circle
    def get_distance(self):
        # Perform operations on the array
        # For example, you can calculate the distance between the start and end points
        k_miles = 0.539957
        distance = great_circle(np.array(self.start_point),np.array(self.end_point)).km * k_miles
        return distance
    
    def min_speed(self):
        min_numbers = []
        num_arrays = self.array.shape[1]
        
        for i in range(num_arrays):
            min_value = float('inf')  # Initialize with a large value
            
            for array in self.array:
                if array[i] < min_value:
                    min_value = array[i]
            
            min_numbers.append(min_value)
        
        return min_numbers
        
    
    def get_time(self):
        distance = self.get_distance()
        min_numbers = self.min_speed()
        time = distance / min_numbers # this is shit yet
        return time