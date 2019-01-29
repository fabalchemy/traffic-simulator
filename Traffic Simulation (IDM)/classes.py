"""Traffic Simulation (IDM)
Necessary classes for the simulation"""

from math import inf

class Road:
    """Class modelizing a road between two crosses"""

    def __init__(self, name, cross1, cross2, speed_limit):
        self.name = name
        self.cross1 = cross1
        self.cross2 = cross2
        self.lenght = Road.distance(cross1, cross2)
        self.speed_limit = speed_limit

    def distance(cross1,cross2):
        """Euclidean distance between two crosses"""
        x1,y1 = cross1.coords
        x2,y2 = cross2.coords

        return ((x2-x1)**2 + (y2-y1)**2)**0.5

class Cross:
    """Class modelizing a cross"""
    def __init__(self, coords, is_generator = False):
        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float) and type(is_generator) is bool):
            raise TypeError("Types of entered parameters are incorrect")
        self.coords = coords
        self.is_generator = is_generator


class Vehicle:
    """Vehicle"""

    nb_vehicle = 0
    def __init__(self,road,T, leader, s0, a = 1, vehicle_type = 0, b = 1.5):
        """Class modelizing a car
        road
        T : desired time headway (security time) [s]
        leader : vehicle ahead
        s0 = minimal distance (bumper-to-bumper) to the leader [m]
        vehicle_type = 0 for a car, 1 for a truck
        b = comfortable deceleration of the driver, b > 0 [m/s²]
        """

        # We check input paramaters have the expected types
        if not (type(road) is Road and type(T) in (int,float) and (type(leader) is Vehicle or leader == None)
        and type(s0) in (int,float) and type(a) in (int,float) and type(vehicle_type) is int and type(b) in (int,float)):
            raise TypeError("There is a problem with the given parameters")

        # TODO: Be more specific about that problem

        Vehicle.nb_vehicle += 1
        self.road = road
        self.T = T
        self.leader = leader
        self.s0 = s0
        self.a = a # Acceleration

        if vehicle_type == 0: # It's a car
            self.b_max = 8 # Maximum vehicle deceleration (in case of danger ahead)
        elif vehicle_type == 1 : # It's a truck
            self.b_max = 4
        else:
            Vehicle.nb_vehicle -= 1
            raise TypeError("Non existing vehicle. 0 = car, 1 = truck")

        self.b = b
        self.delta = 4

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

        self.x = 0 # Position of the vehicle on the road
        self.v = 0 # Speed of the vehicule
        self.v_old = 0 # Speed of the vehicle at the precedent time instant

    def spacing_with_leader(self):
        """Return the spacing between the car and its leader
        If there is no leader, the distance is infinite"""
        if self.leader == None:
            return 1000
        else :
            return self.leader.x - self.x

    def speed_of_leader(self):
        """Return the speed of the leader, if it exists
        Otherwise, return the speed of the car to cancel the interaction acceleration"""
        if self.leader == None:
             return self.v
        else:
            return self.leader.v

    def a_free(self, v):
        """Return the freeway acceleration (with no car ahead)"""
        if v <= self.v0 :
            return self.a * (1 - (v/self.v0)**self.delta)
        else:
            return -self.b * (1 - (self.v0/v)**(self.a*self.delta/self.b))

    def z(self, v):
        """Acceleration term linked to distance to the leader"""
        s = self.spacing_with_leader()
        #delta_v = self.speed_of_leader() - v
        delta_v = v- self.speed_of_leader()
        return (self.s0 + max(0, v*self.T + v*delta_v/(2*(self.a*self.b)**0.5))) /s


    def acceleration_IDM(self):
        return self.a * (1 - (self.v/self.v0)**self.delta - ((self.s0 + max(0, self.v * self.T + (self.v * (self.v-self.speed_of_leader())/2*(self.a*self.b)**0.5)))/self.spacing_with_leader())**2)


    def acceleration(self):
        """Return the global acceleration"""
        v = self.v
        z = self.z(v)
        a = self.a
        a_free = self.a_free(v)
        if v <= self.v0:
            if z >= 1:
                return max(-self.b_max, a * (1 - z**2))
            else:
                return max(-self.b_max,a_free * (1 - z**(2*a / a_free)))

        else:
            if z >= 1:
                return max(-self.b_max, a_free + a * (1 - z**2))
            else:
                return max(-self.b_max,a_free)
