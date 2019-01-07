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

    nb_cars = -1
    def __init__(self,road,T, leader, s0, a = 1, vehicle_type = 0, b = 1.5):
        """Class modelizing a car
        road
        T : desired time headway (security time) [s]
        leader : vehicle ahead
        s0 = minimal distance (bumper-to-bumper) to the leader [m]
        vehicle_type = 0 for a car, 1 for a truck
        b = comfortable deceleration of the driver, b > 0 [m/s-2]
        """

        # We check input paramaters have the expected types

        if not (type(road) is Road and type(T) in (int,float) and (type(leader) is Vehicle or leader == None)
        and type(s0) in (int,float) and type(a) in (int,float) and type(vehicle_type) is int and type(b) in (int,float)):
            raise TypeError("Types of entered parameters are incorrect")

        Vehicle.nb_cars += 1
        self.name = Vehicle.nb_cars
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)
        self.T = T

        self.s0 = s0
        self.x = 0 # Abscissa of the vehicle on the road
        self.v = 0 # Speed of the vehicule
        self.v_old = 0 # Speed of the vehicle at the precedent time instant
        self.a = a # Acceleration
        self.b = b

        if vehicle_type == 0: # It's a car
            self.b_max = 8 # Maximum vehicle deceleration (in case of danger ahead)
        elif vehicle_type == 1 : # It's a truck
            self.b_max = 4
        else:
            Vehicle.nb_cars -= 1
            raise TypeError("Non existing vehicle. 0 = car, 1 = truck")

        self.leader = leader
        self.delta = 4

    def spacing_with_leader(self):
        if self.leader == None:
            return inf
        else :
            return self.leader.x - self.x

    def acceleration(self, v):
        """Calculate the acceleration of the vehicule
        s : actual gap [m]
        v : actual speed [m/s]
        vl : actual speed of the leader [m/s]

        a_free : free road behavior (no vehicle ahead)
        a_int : interaction term
        """
        if self.leader is not None:
            vl = self.leader.v
        else:
            vl = self.v

        s = self.spacing_with_leader()

        a_free = self.a * (1-(v/self.v0)**self.delta)
        a_int = - self.a * ( (self.s0 + v*self.T + max(0,(v * (vl-v)) / (2*(self.a*self.b)**0.5))) /s )**2

        return a_free + a_int
