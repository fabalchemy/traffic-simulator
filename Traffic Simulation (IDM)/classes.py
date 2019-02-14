"""Traffic Simulation (IDM)
Necessary classes for the simulation"""

from math import inf, acos, cos, sqrt, fabs

# Often used Exceptions :
NotRoadError = TypeError("Input road is not Road type")
NotVehicleError = TypeError("Input vehicle is not Vehicle type")
NotCrossError = TypeError("Input cross is not Cross type")
NotLinkedRoad = ValueError("Input road is not linked to this cross")
NotLinkedCross = ValueError("Input cross is not linked to this road")

class Road:
    """Class modelizing a road between two crosses"""

    def __init__(self, name, cross1, cross2, speed_limit):
        self.name = name
        self.cross1 = cross1
        self.cross2 = cross2
        self.lenght = Road.distance(cross1, cross2)
        self.speed_limit = speed_limit

        cross1.roads.append(self)
        cross2.roads.append(self)

        self.vehicle_list_12 = list()
        self.vehicle_list_21 = list()

    def distance(cross1,cross2):
        """Euclidean distance between two crosses"""
        x1,y1 = cross1.coords
        x2,y2 = cross2.coords

        return float(((x2-x1)**2 + (y2-y1)**2)**0.5)

    def incoming_veh(self,vehicle,origin_cross,x = 0):
        """Incoming vehicle on the road from the origin_cross
        x = the abscissa on this road when arriving (useful when vehicles arrive from another road with a certain speed)"""

        #input paramaters check :
        if type(vehicle) is not Vehicle:
            raise notVehicleError
        if type(origin_cross) is not Cross: #Does it work for classes heriting from Cross ?
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise NotLinkedCross
        if x > self.lenght:
            raise ValueError("Incoming abscissa is too high")

        #Then we add the vehicle at the beginning of the road, in the corresponding direction
        if origin_cross == self.cross1:
            self.vehicle_list_12 = self.vehicle_list_12.append(vehicle)
        else:
            self.vehicle_list_21 = self.vehicle_list_21.append(vehicle)

        vehicle.x = x

    def outgoing_veh(self,vehicle, destination_cross):
        """Outgoing vehicle of the road"""

        #input paramaters check :
        if type(vehicle) is not Vehicle:
            raise notVehicleError
        if vehicle in self.vehicle_list_12:
            destination_cross.transfer_vehicle(self.vehicle_list_12.pop(0), vehicle.x - self.lenght)
        elif vehicle in self.vehicle_list_21:
            return destination_cross.transfer_vehicle(self.vehicle_list_21.pop(0), vehicle.x - self.lenght)
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
            return self.vehicle_list_21[-1]
        else:
            return self.vehicle_list_12[-1]

class Cross:
    """Class modelizing a cross"""
    def __init__(self, coords, cross_dispatch_matrix = list()):
        """(cartesian) coords : (x,y)
        cross_dispatch_matrix : list of lists of vehicles dispatch on other roads
            (L[x] = entry, L[x][y] exit)"""

        # Check valid coords
        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("Types of entered parameters are incorrect")
        if cross_type not in ["trafficLight", "generator", "simpleCross"]:
            raise ValueError("Incorrect cross type")
        self.coords = coords

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

        def input_road(self,road):
            """Add the new road connected to the cross to self.roads"""
            if type(road) is not Road:
                raise NotRoadError

            if len(self.roads) >= 4:
                print("Cannot add a new road on this cross, crosses cannot be linked with more than 4 roads")
            else:
                self.roads.append(road)

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

        def define_priority_axis(self, axis):
            """Define the priority axis of this cross"""
            AxisError = TypeError("axis must be a tuple of 2 roads")
            if (type(axis) is not tuple):
                raise TypeError("Input axis is not a tuple")
            if len(axis) != 2 or (type(axis[0]) is not Road) or (type(axis[1]) is not Road):
                raise ValueError("Input axis must be a tuple of 2 roads")

            self.priority_axis = axis

        def transfer_vehicle(self,vehicle,x):
            """Pick up the vehicle from the road to put it at the beginning of the next road"""
            if type(vehicle) is not Vehicle:
                raise NotVehicleError
            if road not in self.roads:
                raise NotLinkedRoad

            road.incoming_veh(x)



class TrafficLight(Cross):
    """Traffic light, a type of cross"""

    def __init__(self, coords, matrix):
        """Traffic light, defined by:
        - (x,y) cartesian coordinates
        - in/out light command matrix"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and type(coords[1]) in (int,float)):
            raise TypeError("Input coordinates are incorrect (expected (x,y))")
        self.coords = coords

        #Traffic light color = 0 for green, 1 for red
        self.color = 0


class Vehicle:
    """Vehicle"""

    map_veh_list = list() #List of real vehicles (SlowDownAtCross and TrafficLight are not counted in)
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
        if type(road) is not Road:
            raise NotRoadError
        if type(T) not in (int,float):
            raise TypeError("Input T is not int/float type")
        if not (type(leader) is Vehicle or leader == None):
            raise TypeError("Input leader is not Vehicle/None type")
        if type(s0) not in (int,float):
            raise TypeError("Input s0 is not int/float")
        if type(a) not in (int,float):
            raise TypeError("Input a is not int/float")
        if type(vehicle_type) is not int:
            raise TypeError("Input vehicle_type is not int")
        if type(b) not in (int,float):
            raise TypeError("Input b is not int/float")


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

    def change_leader(self, vehicle):
        """To change the leader of a vehicle, from outside the class"""
        if type(vehicle) is not Vehicle:
            raise NotVehicleError
        self.leader = vehicle

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

class SlowDownAtCross(Vehicle): # To rename
    """We use a stopped or slow vehicle to slow down the vehicle arriving to a cross and quitting the priority axis (and then turning)
    We use a stopped vehicle to stop the vehicle arriving to a cross, because it doesn't have the required space to cross the road
    We use a slow vehicle (or stopped further away) to slow down the vehicle going to cross the road, because it cannot turn the corner at a full speed"""

    """Warning : think a way to delete the object when it is no more useful"""

    def __init__(self, road, cross):

        if type(road) is not Road:
            raise NotRoadError
        self.road = road

        if type(cross) not in (Cross, TrafficLight, SimpleCross):
            raise TypeError("cross must be a Cross (TrafficLight, SimpleCross)")

        change_leader(road.leader(cross), self) # If cross is not linked to the road, an exception is thrown by Road.leader()

        #To stop a vehicle if it cannot cross the road because of a vehicle arriving in the other way
        self.x = lenght(road) + 2
        self.v = 0
