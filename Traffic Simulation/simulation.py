# coding = utf-8

from constants import *
from functions import angle, random_color
from math import pow, cos, sin
from random import randint, random

# Lists of simulated objects
generators = []
crosses = []
roads = []
vehicles = []
deleted_vehicles = []


class Road:
    """Class representing a road, which is a segment between two intersections"""

    def __init__(self, cross1, cross2, speed_limit, id=None):
        """Initialize a Road object connected to two Intersections, with a speed_limit"""
        if not isinstance(cross1, Cross) or not isinstance(cross2, Cross):
            raise NotCrossError
        if type(speed_limit) not in (int,float):
            raise TypeError("speed_limit is not int/float")

        self.cross1 = cross1
        self.cross2 = cross2
        self.speed_limit = speed_limit
        self.id = id
        self.rep = None

        x1,y1 = cross1.coords
        x2,y2 = cross2.coords
        self.angle = angle(x2-x1, y2-y1)
        self.cos_angle = cos(self.angle)
        self.sin_angle = sin(self.angle)
        self.length = float(((x2-x1)**2 + (y2-y1)**2)**0.5)
        self.width = 6

        self.stop = Vehicle(self, cross1)
        self.stop.v = 0
        self.stop.x = self.length - 1

        cross1.add_road(self)
        cross2.add_road(self)

        self.vehicle_list_12 = list()
        self.vehicle_list_21 = list()

    def incoming_veh(self, veh, origin_cross, x = 0):
        """Incoming vehicle on the road from origin_cross
        x is the position of the vehicle on the road when arriving
        (useful when vehicles come from another road with a certain speed)"""

        if type(veh) is not Vehicle:
            raise notVehicleError
        if not isinstance(origin_cross, Cross):
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise NotLinkedCross
        if x > self.length:
            print("ROAD = {}, ROAD LENGTH = {}, RECEIVED ABSCISSA = {}".format(self.id,self.length,x))
            raise ValueError("Incoming abscissa is too high")

        veh.changed_road = True
        veh.decision = False
        veh.change_leader(self.last_vehicle(origin_cross))

        # We add the vehicle at the beginning of the road, in the corresponding direction
        if origin_cross == self.cross1:
            self.vehicle_list_12.append(veh)
            veh.destination_cross = self.cross2
        else:
            self.vehicle_list_21.append(veh)
            veh.destination_cross = self.cross1

        veh.x = x
        veh.dx = 0
        veh.road = self
        veh.origin_cross = origin_cross
        veh.v0 = self.speed_limit

        # Choose the next road
        veh.next_road = veh.destination_cross.choose_direction(self)

        if veh.next_road != None:
            i = veh.destination_cross.roads.index(veh.road)
            j = veh.destination_cross.roads.index(veh.next_road)
            if j == i-1:
                veh.direction = "right"
            elif j == i+1:
                veh.direction = "left"
            else:
                veh.direction = None
        else:
            veh.direction = None

        if veh.leader == None and veh.next_road != None:
            leader = veh.next_road.last_vehicle(veh.destination_cross)
            if leader != None:
                veh.change_leader(leader)

    def outgoing_veh(self, veh):
        """Outgoing vehicle of the road"""
        if veh != None:
            destination_cross = veh.destination_cross

            if type(veh) is not Vehicle:
                raise notVehicleError

            # TODO: Change road length when turning right
            if veh.direction == "right":
                length = self.length - veh.length/2
                add = veh.length/2
            else:
                length = self.length
                add = 0

            if veh.x >= length:
                if veh in self.vehicle_list_12:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_12[0]
                        veh.destroy()
                        # Update follower's leader to None
                        if len(self.vehicle_list_12) > 0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_12.pop(0), veh.next_road, veh.x - self.length +add)
                        # if len(self.vehicle_list_12)>0:
                        #     destination_cross.new_leader(veh) # Alert vehicles arrving next to it that it's their new leader

                elif veh in self.vehicle_list_21:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_21[0]
                        veh.destroy()
                        # Update follower's leader to None
                        if len(self.vehicle_list_21) > 0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_21.pop(0), veh.next_road, veh.x - self.length +add)
                        # if len(self.vehicle_list_21)>0:
                        #     destination_cross.new_leader(veh) # Alert vehicles arrving next to it that it's their new leader

                else:
                    raise ValueError("Vehicle not on this road")

    def first_vehicle(self,destination_cross):
        """Return the first vehicle arriving on destination_cross from this road"""

        if not isinstance(destination_cross, Cross):
            raise notCrossError
        if destination_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        if destination_cross is self.cross1:
            return None if len(self.vehicle_list_21) == 0 else self.vehicle_list_21[0]
        else:
            return None if len(self.vehicle_list_12) == 0 else self.vehicle_list_12[0]

    def last_vehicle(self, origin_cross):
        """Return the last vehicle arrived on the road from the origin_cross"""

        if not isinstance(origin_cross, Cross):
            raise notCrossError
        if origin_cross not in [self.cross1,self.cross2]:
            raise crossNotOnRoad

        if origin_cross is self.cross1:
            return None if len(self.vehicle_list_12) == 0 else self.vehicle_list_12[-1]
        else:
            return None if len(self.vehicle_list_21) == 0 else self.vehicle_list_21[-1]


class Cross:
    """Class modelizing a cross"""

    def __init__(self, coords, id=None):
        """Generate a Cross at coords (x,y)"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float)
            and type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")

        self.coords = coords
        self.roads = list()
        self.id = id
        self.rep = None

    def add_road(self, road):
        """Connects the road to the cross, adding it to self.roads"""
        if type(road) is not Road:
            raise NotRoadError

        if len(self.roads) < 4:
            self.roads.append(road)
        else:
            print("Cross ID: ",self.id)
            raise TooManyRoads

    def define_priority_axis(self, axis):
        """Define the priority axis of the cross
        axis : a tuple of 2 roads"""
        if (type(axis) is not tuple) and axis != None:
            raise WrongAxisFormat
        if axis != None and (len(axis) != 2 or (type(axis[0]) is not Road) or (type(axis[1]) is not Road)):
            raise WrongAxisFormat

        self.priority_axis = axis

    def sort_roads(self):
        temp_list = []
        # Put every road in temp_list with the correct angle
        for road in self.roads:
            if road.cross1 == self:
                temp_list.append((road, road.angle))
            else:
                angle = road.angle % (2*3.1415) - 3.1415
                temp_list.append((road, angle))

        # Sort the roads by angle
        temp_list.sort(key = lambda item : item[1])
        self.roads = [item[0] for item in temp_list]

        # Re-arrange the roads so that priority_axis are on indexes 0 and 2
        # only for 3 and 4-road crosses
        if len(self.roads) > 2:
            while not (self.priority_axis[0] in (self.roads[0], self.roads[2]) and self.priority_axis[1] in (self.roads[0], self.roads[2])):
                self.roads.append(self.roads.pop(0))

    def transfer_vehicle(self, vehicle, next_road, x=0):
        """Put vehicle on next_road at x"""
        if type(vehicle) is not Vehicle:
            raise NotVehicleError
        if next_road not in self.roads:
            raise NotLinkedRoad
        next_road.incoming_veh(vehicle, self, x)

    def choose_direction(self, origin_road):
        """Return the next road for a vehicle arriving on the cross,
        using the probability to go on each road (dispatch)"""

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

        rand = 0
        while rand == 0:
            rand = random()

        for j in range(len(self.roads)):
            if rand <= self.dispatch[self.roads.index(origin_road)][j]:
                return self.roads[j]

    def set_dispatch(self, dispatch):
        """Set the dispatch matrix of the cross,
        converting a probability matrix into a cumulated frequencies matrix"""
        if type(dispatch) is not list:
            raise TypeError("dispatch must be list type")

        # Check if dispatch is a list of lists of the same length (same number of incoming and outgoing roads)
        roads_nb = len(dispatch)
        for road in range(roads_nb):
            if type(dispatch[road]) is not list:
                raise TypeError("dispatch must be a list of lists")
            if len(dispatch[road]) != roads_nb:
                raise ValueError("dispatch must have the same number of incoming and outgoing roads")

        # Cars cannot turn back when arriving to a cross : dispatch[i][i] = 0
            if dispatch[road][road] != 0:
                raise ValueError("Vehicles cannot turn back at a cross: dispatch[road i][road i] != 0.")


        for i in range(len(dispatch)):
            for j in range(1,len(dispatch)):
                dispatch[i][j] += dispatch[i][j-1]
            if dispatch[i][-1] != 1:
                raise ValueError("Frequencies sum must equal 1")

        self.dispatch = dispatch

    # def get_intentions(self):
    #     incoming_veh = []
    #     # Search for the first vehicles on non-prioritary axis
    #     if len(self.roads) >= 3:
    #         veh = self.roads[1].first_vehicle(self)
    #         if veh != None:
    #             incoming_veh.append(veh)
    #     # if len(self.roads) == 4:
    #     #     veh = self.roads[3].first_vehicle(self)
    #     #     if veh != None:
    #     #         incoming_veh.append(veh)
    #
    #     for veh in incoming_veh:
    #         i = veh.destination_cross.roads.index(veh.road)
    #         if veh.d_to_cross() <= ((veh.v*veh.v)/(2*veh.b_max) + 30) : # if close enough to the cross
    #             others = []
    #             others.append(self.roads[(i-1)%4].first_vehicle(self)) # find problematic vehicles
    #             others.append(self.roads[(i+1)%4].first_vehicle(self))
    #
    #             for other in others:
    #                 if other != None and other.next_road == veh.next_road:
    #                     if other.d_to_cross() < veh.d_to_cross() + PRIORITY_GAP: # next vehicle is arriving before us to the cross
    #                         # check space with next vehicle
    #                         for follower in other.followers:
    #                             if follower.road == other.road: # it's a true follower (there should only be one)
    #                                 space = other.x - follower.x
    #                                 req_space = follower.s0 + veh.s0 + veh.v * veh.T + follower.v * follower.T + veh.length + (follower.road.speed_limit - veh.v)**2/(2*veh.a) # Required space :
    #
    #                                 if space < req_space + PRIORITY_GAP:
    #                                     veh.change_leader(veh.road.stop)
    #                                     other.change_leader(veh.next_road.last_vehicle(veh.destination_cross))
    #                                 elif other not in veh.followers:
    #                                     print("ahah")
    #                                     veh.change_leader(other)
    #                                     follower.change_leader(veh)
    #                     else:
    #                         leader = veh.next_road.last_vehicle(veh.destination_cross)
    #                         if leader != None:
    #                             veh.change_leader(leader)
    #                         if not veh in other.followers:
    #                             other.change_leader(veh)

    # def get_intentions(self):
    #     incoming_veh = []
    #     # Search for the first vehicles on non-prioritary axis
    #     if len(self.roads) >= 3:
    #         veh = self.roads[1].first_vehicle(self)
    #         if veh != None:
    #             incoming_veh.append(veh)
    #     # if len(self.roads) == 4:
    #     #     veh = self.roads[3].first_vehicle(self)
    #     #     if veh != None:
    #     #         incoming_veh.append(veh)
    #
    #     for veh in incoming_veh:
    #         if not veh.decision:
    #             i = veh.destination_cross.roads.index(veh.road)
    #             if veh.d_to_cross() <= ((veh.v*veh.v)/(2*veh.b_max) + 30) : # if close enough to the cross
    #                 others = []
    #                 others.append(self.roads[(i-1)%4].first_vehicle(self)) # find problematic vehicles
    #                 others.append(self.roads[(i+1)%4].first_vehicle(self))
    #
    #                 for other in others:
    #                     if other != None:
    #                         if other.next_road == veh.next_road:
    #                             if other.time_to_cross() < veh.time_to_cross() + PRIORITY_GAP: # next vehicle is arriving before us to the cross
    #                                 # check space with next vehicle
    #                                 for follower in other.followers:
    #                                     if follower.road == other.road: # it's a true follower (there should only be one)
    #                                         space = (other.x - follower.x)/other.v
    #                                         req_space = (follower.road.speed_limit - veh.v)/veh.a
    #
    #                                         if space < req_space + PRIORITY_GAP:
    #                                             veh.change_leader(veh.road.stop)
    #                                             other.change_leader(other.next_road.last_vehicle(other.destination_cross))
    #                                         elif other not in veh.followers:
    #                                             print("insertion entre 2 véhicules")
    #                                             veh.change_leader(other)
    #                                             follower.change_leader(veh)
    #                                             veh.decision = True
    #                             else:
    #                                 leader = veh.next_road.last_vehicle(veh.destination_cross)
    #                                 veh.decision = True
    #                                 if leader != None:
    #                                     veh.change_leader(leader)
    #                                 if not veh in other.followers:
    #                                     other.change_leader(veh)
    #                         else:
    #                             if other.next_road != veh.road:
    #                                 if other.d_to_cross() / other.v < veh.time_to_cross():
    #                                     print("stop, priorité à la route", other.d_to_cross() / other.v, veh.time_to_cross())
    #                                     veh.decision = False
    #                                     veh.change_leader(veh.road.stop)
    #                                     for follower in veh.followers:
    #                                         if follower.road != veh.road:
    #                                             follower.change_leader(follower.next_road.last_vehicle(follower.destination_cross))

    def get_intentions(self):
        incoming_veh = []
        # Search for the first vehicles on non-prioritary axis
        if len(self.roads) >= 3:
            veh = self.roads[1].first_vehicle(self)
            if veh != None:
                incoming_veh.append(veh)

        for veh in incoming_veh:
            if not veh.decision:
                if veh.d_to_cross() <= ((veh.v*veh.v)/(2*veh.b_max) + 30):
                    i = veh.destination_cross.roads.index(veh.road)
                    j = veh.destination_cross.roads.index(veh.next_road)

                    other = self.roads[(i-(j-i))%4].first_vehicle(self)

                    if other != None:
                        if other.time_to_cross() < veh.time_to_cross() + PRIORITY_GAP:
                            for follower in other.followers:
                                if follower.road == other.road: # it's a true follower (there should only be one)
                                    space = other.time_to_cross() - follower.time_to_cross()
                                    req_space = (follower.road.speed_limit - veh.v)/veh.a

                                    if space < req_space :
                                        veh.change_leader(veh.road.stop)
                                        other.change_leader(veh.next_road.last_vehicle(veh.destination_cross))
                                    elif other not in veh.followers:
                                        veh.change_leader(other)
                                        follower.change_leader(veh)
                                        veh.decision = True
                        else:
                            leader = veh.next_road.last_vehicle(veh.destination_cross)
                            veh.decision = True
                            if leader != None:
                                veh.change_leader(leader)
                            if not veh in other.followers:
                                other.change_leader(veh)

                    anti = self.roads[(i+(j-i))%4].first_vehicle(self)

                    if anti != None and veh.direction == "left":
                        if anti.time_to_cross() < veh.time_to_cross() + PRIORITY_GAP:
                            veh.change_leader(veh.road.stop)
                            other.change_leader(veh.next_road.last_vehicle(veh.destination_cross))
                            veh.decision = False




class GeneratorCross(Cross):
    """Generator cross, at the edges of the map, to add or delete vehicles on/off the map"""

    RAND_GAP = 5 # Bigger this constant is, more random is the generation of vehicles

    def __init__(self, coords, period):
        """coords : (x,y) coordinates
        period [s] : time between two vehicle income"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")
        if type(period) not in (int,float):
            raise TypeError("period is not int/float")

        self.coords = coords
        self.period = period
        self.next_period = period
        self.roads = list()
        self.rand_period = None
        self.last_t = 0

    def generate(self, t):
        """Generate vehicles on the map"""
        road = self.roads[0]
        vehicle_ahead = road.last_vehicle(self)

        if self.rand_period  == None:
            self.rand_period = randint(-GeneratorCross.RAND_GAP, GeneratorCross.RAND_GAP)
            self.next_period = self.period + self.rand_period

        if (t - self.last_t) >= self.next_period :
            veh_type = "car" if random() < 0.93 else "truck"
            if (vehicle_ahead == None or vehicle_ahead.x > (self.roads[0].speed_limit**2)/(2*Vehicle.VEH_B_MAX[veh_type]) + vehicle_ahead.s0 + (vehicle_ahead.length + Vehicle.VEH_LENGTH[veh_type])/2):
                self.last_t = t

                new_vehicle = Vehicle(road, self, vehicle_type = veh_type)
                vehicles.append(new_vehicle)
                new_vehicle.change_leader(vehicle_ahead)
                new_vehicle.v = road.speed_limit
                self.transfer_vehicle(new_vehicle, road)
                self.rand_period = None
                return new_vehicle

class Vehicle:
    """Representation of a vehicle"""

    VEH_LENGTH = {"car": 4, "truck": 10}
    VEH_B_MAX = {"car": 10, "truck": 5}

    def __init__(self, road, origin_cross, T = 1, s0 = 2, a = 2, vehicle_type = "car", b = 1.5):
        """road : Road on which the car is summoned
        origin_cross : Cross by where the car enter on the road
        T : Desired time headway [s]
        leader : vehicle ahead
        s0 = minimal distance (bumper-to-bumper) with the leader [m]
        vehicle_type = car, truck
        b = comfortable deceleration of the driver, b > 0 [m/s²]
        """
        # We check that input parameters have the expected types
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
        self.leader = None
        self.followers = []
        self.leadership_color = random_color()
        self.x = 0 # Position of the vehicle on the road
        self.dx = 0
        self.v = 0 # Speed of the vehicle

        self.T = T
        self.s0 = s0
        self.delta = 4
        self.b = b

        self.decision = False

        self.changed_road = True
        self.rep = None # Index for graphic representation
        self.brake_rep = None
        self.last_a = 0
        self.blinker_rep = None
        self.direction = None
        self.blinker_state = 0

        if vehicle_type == "car": # It's a car
            self.a = a # Acceleration
            self.b_max = Vehicle.VEH_B_MAX[vehicle_type] # Maximum vehicle deceleration (in case of danger ahead)
            self.length = Vehicle.VEH_LENGTH["car"]
            self.width = 2
        elif vehicle_type == "truck" : # It's a truck
            self.a = 1
            self.b_max = Vehicle.VEH_B_MAX[vehicle_type]
            self.length = Vehicle.VEH_LENGTH["truck"]
            self.width = 2.5
        else:
            raise TypeError("Non existing type of vehicle, car or truck?")

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

    def turn_speed(self):
        """Give the optimal speed for changing road
        f(0) = 0, f(PI/2) = 15/50, f(PI) = 1"""
        if self.next_road != None:
            angle = abs(self.next_road.angle - self.road.angle) % 3.1415
            if angle < 0.01:
                angle = 3.1415
            self.v0 = (0.08 *angle*angle + 0.06 * angle) * self.road.speed_limit

    def destroy(self):
        """Delete a vehicle from the map and give a new leader to the followers"""
        deleted_vehicles.append(self)
        for veh in self.followers:
            veh.leader = None
            veh.find_leader()
        vehicles.remove(self)

    def time_to_cross(self):
        if self.v != 0:
            return self.d_to_cross() / self.v
        else:
            return 1

    # def time_to_cross(self):
    #     if self.v > 0.01:
    #         d_to_cross = self.d_to_cross()
    #         T_slow_down = (self.v - self.v0) / self.b  #Time to reach the turn speed (new v0)
    #         d_slow_down = ((self.v - self.v0) / 2) * T_slow_down # Distance travelled slowing down
    #         T_to_cross = ((d_to_cross - d_slow_down) / self.v0) + T_slow_down
    #         return T_to_cross
    #     else:
    #         return 1 # arbitrary constant

    def d_to_cross(self):
        return self.road.length - self.x

    def change_leader(self, vehicle):
        """To change the leader of a vehicle, from outside the class"""
        if not (isinstance(vehicle, Vehicle) or vehicle == None):
            print(type(vehicle))
            raise NotVehicleError
        self.leave_leader()
        self.leader = vehicle
        if self.leader != None :
            self.leader.followers.append(self)

    def leave_leader(self):
        """Tell the leader that we don't follow it anymore"""
        if self.leader != None:
            if self in self.leader.followers:
                self.leader.followers.remove(self)
            else:
                raise ValueError("The vehicle is not a follower")

    def find_leader(self):
        if self.next_road != None:
            leader = self.next_road.last_vehicle(self.destination_cross)
            if leader != None:
                self.change_leader(leader)

    def spacing_with_leader(self):
        """Return the spacing between the car and its leader
        If there is no leader, the distance is 250"""
        if self.leader == None:
            return 250 # arbitrary constant
        else:
            if self.leader.road == self.road:
                if self.leader.rep != None:
                    # "standard" leader
                    return self.leader.x - self.x - (self.leader.length + self.length)/2
                else :
                    # "stop" leader
                    return max(0.01, self.leader.x - self.x - (self.leader.length + self.length)/2)
            elif self.leader.road == self.next_road:
                return self.d_to_cross() + self.leader.x - (self.leader.length + self.length)/2
            elif self.leader.destination_cross == self.destination_cross:
                # "fake" leader: self follows a projection
                return max(0.01,self.d_to_cross() - self.leader.d_to_cross() - (self.leader.length + self.length)/2)
            else:
                return 250

    def speed_of_leader(self):
        """Return the speed of the leader, if it exists
        Otherwise, return the speed of the car to cancel the interaction acceleration"""
        if self.leader == None:
             return self.v
        else:
            return self.leader.v

    def a_free(self):
        """Return the freeway acceleration (with no car ahead)"""
        v = self.v
        if v < self.v0 :
            return self.a * (1 - pow(v/self.v0,self.delta))
        elif v == 0 :
            return 0
        else:
            return -self.b * (1 - pow(self.v0/v, self.a*self.delta/self.b))

    def z(self):
        """Acceleration term linked to distance to the leader"""
        v = self.v
        delta_v = v - self.speed_of_leader()
        return (self.s0 + max(0, v*self.T + v*delta_v/(2*(self.a*self.b)**0.5))) / self.spacing_with_leader()

    def acceleration_IIDM(self):
        """Return the global acceleration"""
        v = self.v
        a = self.a
        z = self.z()
        a_free = self.a_free()
        if v < self.v0:
            if z >= 1:
                self.last_a = max(-self.b_max, a * (1 - z**2))
            else:
                self.last_a = max(-self.b_max, a_free * (1 - z**(2*a / a_free)))

        else:
            if z >= 1:
                self.last_a = max(-self.b_max, a_free + a * (1 - z**2))
            else:
                self.last_a = max(-self.b_max,a_free)

        return self.last_a

    def acceleration_IDM(self):
        return self.a * (1 - (self.v/self.v0)**self.delta - ((self.s0 + max(0, self.v * self.T + (self.v * (self.v-self.speed_of_leader())/2*(self.a*self.b)**0.5)))/self.spacing_with_leader())**2)
