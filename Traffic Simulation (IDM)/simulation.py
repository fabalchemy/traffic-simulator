# coding = utf-8
"""Classes necessary to run the mathematical simulation"""

from math import inf, acos, cos, sqrt, fabs
from random import random,randint
from operator import attrgetter

# Often used Exceptions :
NotRoadError = TypeError("Input road is not Road type")
NotVehicleError = TypeError("Input vehicle is not Vehicle type")
NotCrossError = TypeError("Input cross is not Cross type")
NotLinkedRoad = ValueError("Input road is not linked to this cross")
NotLinkedCross = ValueError("Input cross is not linked to this road")

# Lists
generator_list = G = []
cross_list = C = []
road_list = R = []
vehicle_list = V = []
vehicle_to_delete = []

def angle(x,y):
    """Give the oriented angle [-3.14 ; +3.14] between the vector (x,y) and the horizontal axis (1,0)"""
    # The y-axis is "reversed" in Tkinter !
    # We use vector product to find the orientation of the vectors
    sign = 1 if y >= 0 else -1
    # We use scalar product to find the angle and multiply it by the orientation
    return acos((x) / sqrt(x*x + y*y)) * sign

class Road:
    """Class representing a road, which is a line segment between two intersections"""

    def __init__(self, cross1, cross2, speed_limit, id = None):
        """Initialize a Road object connected to two Intersections, with a speed_limit"""
        if not isinstance(cross1, Cross):
            raise NotCrossError
        if not isinstance(cross2, Cross):
            raise NotCrossError
        if type(speed_limit) not in (int,float):
            raise TypeError("speed_limit is not int/float")

        self.cross1 = cross1
        self.cross2 = cross2
        self.speed_limit = speed_limit
        self.id = id

        x1,y1 = cross1.coords
        x2,y2 = cross2.coords
        self.length = float(((x2-x1)**2 + (y2-y1)**2)**0.5)
        self.angle = angle(x2-x1, y2-y1)
        print("Road : ", self.id, "angle : ", self.angle)
        self.width = 5

        cross1.add_road(self)
        cross2.add_road(self)

        self.vehicle_list_12 = list()
        self.vehicle_list_21 = list()

    def incoming_veh(self, vehicle, origin_cross, x = 0):
        """Incoming vehicle on the road from origin_cross
        x is the position of the vehicle on the road when arriving
        (useful when vehicles come from another road with a certain speed)"""

        # We check the paramaters
        if type(vehicle) is not Vehicle:
            raise notVehicleError
        if not isinstance(origin_cross, Cross):
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise NotLinkedCross
        if x > self.length:
            raise ValueError("Incoming abscissa is too high")

        vehicle.change_leader(self.last_vehicle(origin_cross))

        # We add the vehicle at the beginning of the road, in the corresponding direction
        if origin_cross == self.cross1:
            self.vehicle_list_12.append(vehicle)
            vehicle.destination_cross = self.cross2
        else:
            self.vehicle_list_21.append(vehicle)
            vehicle.destination_cross = self.cross1

        vehicle.x = x
        vehicle.road = self
        vehicle.origin_cross = origin_cross
        vehicle.v0 = self.speed_limit

        # We choose the next road
        vehicle.next_road = vehicle.destination_cross.choose_direction(self)

    def outgoing_veh(self, vehicle):
        """Outgoing vehicle of the road"""
        if vehicle != None:
            destination_cross = vehicle.destination_cross

            # We check the paramaters
            if type(vehicle) is not Vehicle:
                raise notVehicleError

            if vehicle.x > self.length:
                if vehicle in self.vehicle_list_12:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_12[0]
                        vehicle.destroy()
                        if len(self.vehicle_list_12)>0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_12.pop(0), vehicle.next_road, vehicle.x - self.length)
                        # if len(self.vehicle_list_12)>0:
                        #     destination_cross.new_leader(vehicle) # Alert vehicles arrving next to it that it's their new leader

                elif vehicle in self.vehicle_list_21:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_21[0]
                        vehicle.destroy()
                        if len(self.vehicle_list_21)>0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_21.pop(0), vehicle.next_road, vehicle.x - self.length)
                        # if len(self.vehicle_list_21)>0:
                        #     destination_cross.new_leader(vehicle) # Alert vehicles arrving next to it that it's their new leader

                else:
                    raise ValueError("Vehicle not on this road")

    def first_vehicle(self,destination_cross):
        """Return the first vehicle arriving on destination_cross from this road"""

        # We check the parameters
        if not isinstance(destination_cross, Cross):
            raise notCrossError
        if destination_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        if destination_cross is self.cross1:
            return self.vehicle_list_21[0] if len(self.vehicle_list_21) > 0 else None
        else:
            return self.vehicle_list_12[0] if len(self.vehicle_list_12) > 0 else None

    def last_vehicle(self, origin_cross):
        """Return the last vehicle arrived on the road from the origin_cross"""

        #input parameters check
        if not isinstance(origin_cross, Cross):
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        if origin_cross is self.cross1:
            return self.vehicle_list_12[-1] if len(self.vehicle_list_12) > 0 else None
        else:
            return self.vehicle_list_21[-1] if len(self.vehicle_list_21) > 0 else None

class Cross:
    """Class modelizing a cross"""

    def __init__(self, coords,id = None):
        """(cartesian) coords : (x,y)
        dispatch : list of lists of vehicles dispatch on other roads
            (L[x] = entry, L[x][y] exit)"""

        # Check coords
        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")


        self.id = id
        self.dispatch = None
        self.coords = coords
        self.roads = list()
        self.dispatch = None

    def add_road(self,road):
        """Add the new road connected to the cross to self.roads"""
        if type(road) is not Road:
            raise NotRoadError

        if len(self.roads) >= 4:
            print("Cannot add a new road on this cross, crosses cannot be linked with more than 4 roads")
            print("Cross ID: ",self.id)
        else:
            self.roads.append(road)

    def define_priority_axis(self, axis):
        """Define the priority axis of the cross
        axis : a tuple containing 2 roads"""
        AxisError = TypeError("axis must be a tuple of 2 roads")
        if (type(axis) is not tuple) and axis != None:
            raise TypeError("Input axis is not a tuple or NoneType")
        if axis != None and (len(axis) != 2 or (type(axis[0]) is not Road) or (type(axis[1]) is not Road)):
            raise ValueError("Input axis must be a tuple of 2 roads or None")

        self.priority_axis = axis

    def sort_roads(self):
        temp_list = []
        print([(road.id, road.angle) for road in self.roads])
        for road in self.roads:
            if road.cross1 == self:
                print("cas1, cross ={},road={}".format(self.id,road.id))
                temp_list.append((road, road.angle))
            else:
                print("cas2 cross ={},road={}".format(self.id,road.id))
                angle = road.angle%(2*3.1415) - 3.1415
                # angle = road.angle - 3.1415
                temp_list.append((road, angle))

        temp_list.sort(key = lambda item : item[1])
        print([(item[0].id, item[1]) for item in temp_list])
        self.roads = [item[0] for item in temp_list]

        if len(self.roads) > 2: # For 3 and 4-road crosses
            while not (self.priority_axis[0] in (self.roads[0], self.roads[2]) and self.priority_axis[1] in (self.roads[0], self.roads[2])):
                print("stuck here : cross =", self.id)
                self.roads.append(self.roads.pop(0))

    def transfer_vehicle(self, vehicle, next_road, x):
        """Pick up the vehicle from road to put it at the beginning of next_road"""
        if type(vehicle) is not Vehicle:
            raise NotVehicleError
        if next_road not in self.roads:
            raise NotLinkedRoad
        next_road.incoming_veh(vehicle,self, x)

    def choose_direction(self, origin_road):
        """Return the next road for a vehicle arriving on the cross
        Use the probability to go on each road (dispatch)"""

        if type(origin_road) is not Road:
            raise NotRoadError
        if origin_road not in self.roads:
            raise NotLinkedRoad

        if type(self) is GeneratorCross:
            return None

        if len(self.roads) == 2:
            if origin_road == self.roads[0]:
                return self.roads[1]
            else:
                return self.roads[0]

        proba = random()
        for j in range(len(self.roads)):
            if proba <= self.dispatch[self.roads.index(origin_road)][j]:
                return self.roads[j]

        raise ValueError("Cannot return the next road")

    def set_dispatch(self, dispatch):
        # Check dispatch
        if type(dispatch) is not list:
            raise TypeError("dispatch must be list type")
        # Check dispatch is list of lists of the same length (same number of incoming and outgoing roads)
        roads_nb = len(dispatch)
        for road in range(roads_nb):
            if type(dispatch[road]) is not list:
                raise TypeError("dispatch must be a list of lists")
            if len(dispatch[road]) != roads_nb:
                raise ValueError("dispatch must have the same number of incoming and outgoing roads")

        # By our own choice, cars cannot turn back when arriving to a cross
        # This involves that for all incoming road dispatch[i][i] must equal 0
            if dispatch[road][road] != 0:
                raise ValueError("Vehicles cannot turn back at a cross. This involves dispatch[road i][road i] must be 0 for every road.")


        for i in range(len(dispatch)):
            for j in range(1,len(dispatch)):
                dispatch[i][j] += dispatch[i][j-1]
            if dispatch[i][-1] != 1:
                raise ValueError("Frequencies sum must equal 1")

        self.dispatch = dispatch

    # def new_leader(self,vehicle):
    #     """When a car go out of a road, incoming on a new road,
    #     set this car as leader of the vehicles arriving at the cross and going on the same road"""
    #     for road in self.roads:
    #         if road is not vehicle.road:
    #             arriving_vehicle = road.first_vehicle(self)
    #             if arriving_vehicle != None and arriving_vehicle.next_road == vehicle.road:
    #                 arriving_vehicle.change_leader(vehicle)

    def decision_maker(self,veh):

        if type(veh.destination_cross) is not GeneratorCross and len(self.roads)>2:
            decision = False
            if veh.road in self.priority_axis:
                if veh.next_road in self.priority_axis:
                    if veh.leader != veh.next_road.last_vehicle(self):
                        veh.change_leader(veh.next_road.last_vehicle(self))
                    decision = True # Return decision but not change speed

                else:
                    veh.turn_speed() # TODO : can reduce speed later ?
                    if veh.next_road == self.roads[(self.roads.index(veh.road)+1)%len(self.roads)]: # Turning left
                        front_road = self.priority_axis[1] if veh.road == self.priority_axis[0] else self.priority_axis[0]
                        front_veh = front_road.first_vehicle(self)
                        if front_veh == None or veh.time_to_cross() < front_veh.time_to_cross():
                            decision = True
                        else:
                            if veh == veh.road.first_vehicle(self):
                                veh.change_leader(FakeLeader(veh.road.length))
                            # return False
                    else: # Turning right
                        decision = True

            else: # veh.road not in priority_axis
                veh.turn_speed()
                if veh.next_road == self.roads[(self.roads.index(veh.road)-1)%len(self.roads)]: # Turning right
                    left_veh = self.roads[(self.roads.index(veh.road)+1)%len(self.roads)].first_vehicle(self)
                    if left_veh == None or veh.time_to_cross() < left_veh.time_to_cross():
                        decision = True
                    else:
                        if veh == veh.road.first_vehicle(self):
                            veh.change_leader(FakeLeader(veh.road.length))
                        # return False
                elif veh.next_road == self.roads[(self.roads.index(veh.road)+1)%len(self.roads)]: # Turning left
                    right_veh = self.roads[(self.roads.index(veh.road)-1)%len(self.roads)].first_vehicle(self)
                    left_veh = self.roads[(self.roads.index(veh.road)+1)%len(self.roads)].first_vehicle(self)
                    if left_veh == None or veh.time_to_cross() < left_veh.time_to_cross():
                        if right_veh == None or veh.time_to_cross() < right_veh.time_to_cross():
                            if len(self.roads) == 4:
                                front_road = self.roads[(self.roads.index(veh.road)+2)%len(self.roads)]
                                front_veh = front_road.first_vehicle(self)
                                if front_veh == None or veh.time_to_cross() < front_veh.time_to_cross():
                                    decision = True
                            else:
                                decision = True
                        else:
                            if veh == veh.road.first_vehicle(self):
                                veh.change_leader(FakeLeader(veh.road.length))
                            # return False

            if decision:
                if veh.leader == None or type(veh.leader) is FakeLeader or veh.leader.road != veh.road:
                    veh.change_leader(veh.next_road.last_vehicle(self))

            # return decision


class GeneratorCross(Cross):
    """Generator cross, at the edges of the map, to add or delete vehicles on/of the map"""

    def __init__(self,coords,time_lapse):
        """coords : (x,y) coordinates
        time_lapse [s] : time between two vehicle income"""

        # Check coords
        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")
        # Check time_lapse
        if type(time_lapse) not in (int,float):
            raise TypeError("time_lapse is not int/float")

        self.coords = coords
        self.time_lapse = time_lapse
        self.roads = list()

    def generate(self, t):
        """Generate vehicles on the map"""
        road = self.roads[0]

        vehicle_ahead = self.roads[0].last_vehicle(self)

        if t % self.time_lapse == 0 and (vehicle_ahead == None or vehicle_ahead.x > (self.roads[0].speed_limit**2)/(2*vehicle_ahead.b_max) +vehicle_ahead.s0):
            leader = self.roads[0].last_vehicle(self)
            if (leader != None and leader.x >= leader.s0) or leader == None:
                # print(str(t) + " : new-vehicule !")

                new_vehicle = Vehicle(road, self)
                new_vehicle.leader = leader
                vehicle_list.append(new_vehicle)
                Cross.transfer_vehicle(self, new_vehicle, self.roads[0], 0)
                new_vehicle.v = self.roads[0].speed_limit
                return new_vehicle
        return None

class Vehicle:
    """Representation of a vehicle"""

    def __init__(self,road,origin_cross,T = 2, s0 = 5.5, a = 1, vehicle_type = "car", b = 1.5):
        """road : Road on which the car is summoned
        origin_cross : Cross by where the car enter on the road
        T : Desired time headway [s]
        leader : Vehicle ahead
        s0 = Minimal distance (bumper-to-bumper) with the leader [m]
        vehicle_type = car, truck
        b = comfortable deceleration of the driver, b > 0 [m/s²]
        """
        # We check input parameters have the expected types
        if type(road) is not Road:
            raise NotRoadError
        if type(T) not in (int,float):
            raise TypeError("Input T is not int/float type")
        if type(s0) not in (int,float):
            raise TypeError("Input s0 is not int/float")
        if type(a) not in (int,float):
            raise TypeError("Input a is not int/float")
        if type(vehicle_type) is not str:
            raise TypeError("Input vehicle_type is not str")
        if type(b) not in (int,float):
            raise TypeError("Input b is not int/float")

        self.road = road
        self.origin_cross = origin_cross
        self.destination_cross = None
        self.next_road = None
        self.T = T
        self.leader = None
        self.s0 = s0
        self.a = a # Acceleration

        self.rep = None # Index for graphic representation

        if vehicle_type == "car": # It's a car
            self.b_max = 8 # Maximum vehicle deceleration (in case of danger ahead)
            self.length = 4
            self.width = 2
        elif vehicle_type == "truck" : # It's a truck
            self.b_max = 4
            self.length = 16
            self.width = 2.5
        else:
            raise TypeError("Non existing vehicle, car or truck ?")

        self.b = b
        self.delta = 4

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

        self.x = 0 # Position of the vehicle on the road
        self.v = 0 # Speed of the vehicule

    def turn_speed(self):
        """Give the recommended speed when changing road
        f(0) = 0, f(PI/2) = 15/50, f(PI) = 1"""
        if self.next_road != None:
            angle = abs(self.next_road.angle - self.road.angle) % 3.1415
            if angle < 0.01:
                angle = 3.1415
            self.v0 = (0.08 *angle*angle + 0.06 * angle) * self.road.speed_limit
        # self.v0 = veh.road.speed_limit

    def time_to_cross(self):
        if self.v > 0.1:
            return (self.road.length - self.x)/self.v
        else:
            return 2 # Constant may be modified

    def destroy(self):
        print("DELETE")
        vehicle_to_delete.append(self)
        vehicle_list.remove(self)

    def change_leader(self, vehicle):
        """To change the leader of a vehicle, from outside the class"""
        if not (isinstance(vehicle, Vehicle) or vehicle == None):
            print(type(vehicle))
            raise NotVehicleError
        self.leader = vehicle

    def spacing_with_leader(self):
        """Return the spacing between the car and its leader
        If there is no leader, the distance is infinite"""
        if self.leader == None:
            return 250
        else:
            if type(self.leader) is FakeLeader or self.leader.road != self.road:
                return self.road.length - self.x + self.leader.x
            else:
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
        delta_v = v - self.speed_of_leader()
        return (self.s0 + max(0, v*self.T + v*delta_v/(2*(self.a*self.b)**0.5))) /s

    def acceleration_IDM(self):
        return self.a * (1 - (self.v/self.v0)**self.delta - ((self.s0 + max(0, self.v * self.T + (self.v * (self.v-self.speed_of_leader())/2*(self.a*self.b)**0.5)))/self.spacing_with_leader())**2)

    def acceleration(self):
        """Return the global acceleration"""
        v = self.v
        z = self.z(v)
        a = self.a
        a_free = self.a_free(v)
        if v < self.v0:
            if z >= 1:
                return max(-self.b_max, a * (1 - z**2))
            else:
                return max(-self.b_max, a_free * (1 - z**(2*a / a_free)))

        else:
            if z >= 1:
                return max(-self.b_max, a_free + a * (1 - z**2))
            else:
                return max(-self.b_max,a_free)

class FakeLeader(Vehicle):
    """Ahaha"""
    def __init__(self,x):
        self.x = x + 6
        self.v = 0
