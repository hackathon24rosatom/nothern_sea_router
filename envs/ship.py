from numpy import array


class Ship:
    def __init__(self, velocity, lat, lng):
        self.velocity = velocity
        self.lat = lat
        self.lng = lng

        self._xvec = 0
        self._yvec = 0
        self._numpy_velocity = array([self.velocity])

    def update(self, action):
        if action == 0:
            self.lat += 1
            self._xvec = 1
            self._yvec = 0
        elif action == 1:
            self.lat -= 1
            self._xvec = -1
            self._yvec = 0
        elif action == 2:
            self.lng += 1
            self._xvec = 0
            self._yvec = 1
        else:
            self.lng -= 1
            self._xvec = 0
            self._yvec = -1
    
    @property
    def geo(self):
        return self.lat, self.lng
    
    @property
    def int_geo(self):
        return round(self.lat), round(self.lng)
    
    @property
    def numyp_geo(self):
        return array([self.lat, self.lng])
    
    @property
    def vec_xy(self):
        return self._xvec, self._yvec
    
    @property
    def numpy_velocity(self):
        return self._numpy_velocity
