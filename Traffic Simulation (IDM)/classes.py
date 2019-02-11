"""Traffic Simulation (IDM)
Necessary classes for the simulation"""

from math import inf, acos, cos, sqrt, fabs

class Road:
    """Class modelizing a road between two crosses"""

    notVehicleError = TypeError("The object added to the road must be a Vehicle")
    notCrossError = TypeError("Input cross is not type Cross")
    crossNotOnRoad = ValueError("This road is not linked to the input cross")

    def __init__(self, name, cross1, cross2, speed_limit):
        self.name = name
        self.cross1 = cross1
        self.cross2 = cross2
        self.lenght = Road.distance(cross1, cross2)
        self.speed_limit = speed_limit

        cross1.roads.append(self)
        cross2.roads.append(self)

        self.vehicles_list_12 = list()
        self.vehicles_list_21 = list()

    def distance(cross1,cross2):
        """Euclidean distance between two crosses"""
        x1,y1 = cross1.coords
        x2,y2 = cross2.coords

        return float(((x2-x1)**2 + (y2-y1)**2)**0.5)

    def incoming_veh(self,vehicle,origin_cross):
        """Incoming vehicle on the road from the origin_cross"""

        #input paramaters check :
        if type(vehicle) is not Vehicle:
            raise notVehicleError
        if type(origin_cross) is not Cross: #Does it work for classes heriting from Cross ?
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        #Then we add the vehicle at the beginning of the road, in the corresponding direction
        if origin_cross == self.cross1:
            self.vehicles_list_12 = self.vehicles_list_12.append(vehicle)
        else:
            self.vehicles_list_21 = self.vehicles_list_21.append(vehicle)

    def outcoming_veh(self,vehicle, destination_cross):
        """Outcoming vehicle of the road"""

        #input paramaters check :
        if type(vehicle) is not Vehicle:
            raise notVehicleError

        if vehicle in self.vehicles_list_12:
            return self.vehicles_list_12.pop(0)
        elif vehicle in self.vehicles_list_21:
            return self.vehicles_list_21.pop(0)
        else:
            raise ValueError("Vehicle not on this road")



    def leader(self,destination_cross):
        """Return the first vehicle to arrive on the destination cross by this road"""

        #input parameters check
        if type(destination_cross) is not Cross:
            raise notCrossError
        if destination_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        if destination_cross is self.cross1: # return the first vehicle arriving to the destination cross from this road
            return self.vehicles_list_21[-1]
        else:
            return self.vehicles_list_12[-1]

class Cross:
    """Class modelizing a cross"""
    def __init__(self, coords, cross_type, cross_dispatch_matrix = list()):
        """(cartesian) coords : (x,y)
        cross_type : ['trafficLight', 'generator', 'simpleCross']
        cross_dispatch_matrix : list of lists of vehicles dispatch on other roads
            (L[x] = entry, L[x][y] exit)"""

        # Check valid coords
        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("Types of entered parameters are incorrect")
        if cross_type not in ["trafficLight", "generator", "simpleCross"]:
            raise ValueError("Incorrect cross type")
        self.coords = coords

        # Check cross_type
        if type(cross_type) is not str:
            raise TypeError("String type expected for cross_type")
        if cross_type not in ['trafficLight', 'generator', 'simpleCross']:
            raise ValueError("Input cross_type is invalid")
        self.cross_type = cross_type

        # Check cross_dispatch_matrix
        if type(cross_dispatch_matrix) is not list:
            raise TypeError("cross_dispatch_matrix must be list type")

        # Check cross_dispatch_matrix is list of lists of the same lenght (same number of incoming and outgoing roads)
        roads_nb = len(cross_dispatch_matrix)
        for road in range(roads_nb):
            if type(cross_dispatch_matrix[road]) is not list:
                raise TypeError("cross_dispatch_matrix must be a list of lists")
            if len(cross_dispatch_matrix[road]) != roads_nb:
                raise ValueError("cross_dispatch_matrix must have the same number of incoming and outgoing roads")

            # By our own choice, cars cannot turn back when arriving to a cross
            # This involves for all incoming road, cross_dispatch_matrix[i][i] must equal 0
            if cross_dispatch_matrix[road][road] != 0:
                raise ValueError("Vehicles cannot turn back at a cross. This involves cross_dispatch_matrix[road i][road i] must be 0 for every road.")





        self.cross_dispatch_matrix = cross_dispatch_matrix

        self.roads = list()

        def sort_linked_roads(self):
            """Sort the roads from the 1st by their angle around the cross
            By computing scalar and vectorial products"""

            vector_list = list()
            for road in self.roads:
                sense = 1
                if road.cross2 == self:
                    sense = -1
                vector_list = (road, sense*(road.cross2.coords[0] - self.coords[0]), sense*(road.cross2.coords[1] - self.coords[1]))

            angle_list = list()
            for (road,x,y) in vector_list:
                angle_list.append((angle(angle_list[0][1],angle_list[0][2], x,y)), road)

            sort(angle_list)

            return [x[1] for x in angle_list]


        def angle(x1,y1,x2,y2):
            return acos((x1*x2 + y1*y2)/ (sqrt(x1*x1 + y1*y1) * sqrt(x2*x2 + y2*y2))) * -(x1*y2 - x2*y1) / fabs(x1*y2 - x2*y1)
            #minus put because of the reversed sense of y-axis on Tkinter




class TrafficLight(Cross):
    """Traffic light, a type of cross"""

    def __init__(self, coords, matrix):
        """Traffic light, defined by:
        - (x,y) cartesian coordinates
        - in/out light command matrix"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and type(coords[1]) in (int,float)):
            raise TypeError("Input coordinates are incorrect")
        self.coords = coords

        #Traffic light color = 0 for green, 1 for red
        self.color = 0






class Vehicle:
    """Vehicle"""

    map_veh_list = list()
    def __init__(self,road,origin_cross,T, leader, s0, a = 1, vehicle_type = 0, b = 1.5):
        """Class modelizing a car:
        road
        origin_cross : Cross by where the car enter on the road
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
            raise TypeError("Non existing vehicle. 0 = car, 1 = truck")

        self.b = b
        self.delta = 4

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

        self.x = 0 # Position of the vehicle on the road
        self.v = 0 # Speed of the vehicule
        self.v_old = 0 # Speed of the vehicle at the precedent time instant

        map_veh_list += self

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
