# coding = utf-8

from constants import *
from functions import angle, random_color
from math import pow, cos, sin
from random import randint, random
from math import log, e, pi

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

        self.stop1 = Vehicle(self, cross1, vehicle_type="stop")
        self.stop1.v = 0
        self.stop1.x = self.length - 1
        self.stop2 = Vehicle(self, cross2, vehicle_type="stop")
        self.stop2.v = 0
        self.stop2.x = self.length - 1

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
        veh.last_road = veh.road
        veh.road = self
        veh.origin_cross = origin_cross
        if veh.slow_down == 0:
            veh.v0 = self.speed_limit

        # Choose the next road
        veh.next_road = veh.destination_cross.choose_direction(self)

        if veh.next_road != None:
            nb_roads = len(veh.destination_cross.roads)
            if nb_roads == 2 or veh.road in veh.destination_cross.priority_axis and veh.next_road in veh.destination_cross.priority_axis:
                veh.direction = None
            else:
                i = veh.destination_cross.roads.index(veh.road)
                j = veh.destination_cross.roads.index(veh.next_road)
                if j == (i-1)%nb_roads:
                    veh.direction = "right"
                elif j == (i+1)%nb_roads:
                    veh.direction = "left"
        else:
            veh.direction = None

        # for follower in veh.followers:
        #     follower.decision = False

        for follower in veh.followers:
            if follower.next_road != veh.road:
                follower.decision = False
                follower.find_leader()

    def outgoing_veh(self, veh):
        """Outgoing vehicle of the road"""
        if veh != None:
            destination_cross = veh.destination_cross

            if type(veh) is not Vehicle:
                raise notVehicleError

            # Change road length when turning right
            if veh.direction == "right":
                length = self.length - veh.length/2
                add = veh.length
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

    def __init__(self, coords, id=None, traffic_lights=True):
        """Generate a Cross at coords (x,y)"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float)
            and type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")

        self.coords = coords
        self.roads = list()
        self.id = id
        self.rep = None

        self.priority = 1
        self.traffic_lights_enabled = traffic_lights
        self.traffic_lights = [ [0, 15, 18, 33],
                                [1,  0,  0,  0],
                                [0,  0,  1,  0]]

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

    def get_intentions(self):

        # Ensure that a vehicle has a unique fake-follower
        if len(self.roads) > 2:
            last1 = self.roads[0].last_vehicle(self)
            last2 = self.roads[2].last_vehicle(self)
            if last1 != None:
                nb_followers = 0
                for fol in last1.followers:
                    if fol.road != last1.road and fol.road != last1.last_road:
                        nb_followers += 1
                if nb_followers > 1:
                    for fol in last1.followers:
                        if fol.road != last1.road:
                            fol.stop()
                            fol.decision = False
                            break
            if last2 != None:
                nb_followers = 0
                for fol in last2.followers:
                    if fol.road != last2.road and fol.road != last2.last_road:
                        nb_followers += 1
                if nb_followers > 1:
                    for fol in last2.followers:
                        if fol.road != last2.road:
                            fol.stop()
                            fol.decision = False
                            break

        # Priority vehicles first
        if len(self.roads) >= 3:
            if len(self.roads) == 3 :
                veh1 = self.roads[0].first_vehicle(self)
                veh2 = self.roads[2].first_vehicle(self)
            if len(self.roads) == 4:
                if self.priority == 1: # Go
                    veh1 = self.roads[0].first_vehicle(self)
                    veh2 = self.roads[2].first_vehicle(self)
                else:
                    veh1 = self.roads[1].first_vehicle(self)
                    veh2 = self.roads[3].first_vehicle(self)

            # if leader is not the last vehicle on its road
            if veh1!= None and veh1.leader!= None and veh1.leader.road == veh1.next_road and veh1.leader != veh1.leader.road.last_vehicle(veh1.destination_cross):
                veh1.decision = False
                veh1.change_leader(veh1.leader.road.last_vehicle(veh1.destination_cross))
            if veh2!= None and veh2.leader!= None and veh2.leader.road == veh2.next_road and veh2.leader != veh2.leader.road.last_vehicle(veh2.destination_cross):
                veh2.decision = False
                veh2.change_leader(veh2.leader.road.last_vehicle(veh2.destination_cross))

            if veh1 != None and veh2 != None:
                if veh1.direction == veh2.direction == "left":
                        veh1.find_leader()
                        veh1.decision = True
                        veh2.stop()
                        veh2.decision = False

                else:
                    if not veh1.decision:
                        if veh1.direction == "left":
                            if veh2.time_to_cross() < veh1.time_to_cross() + PRIORITY_GAP[veh1.veh_type]:
                                # not enough time to cross the road before the other vehicle
                                veh1.stop()
                                veh2.find_leader()
                            else:
                                veh1.decision = True
                                veh1.change_leader(veh1.next_road.last_vehicle(self))
                                if veh2.next_road == veh1.next_road:
                                    veh2.change_leader(veh1)

                    if not veh2.decision:
                        if veh2.direction == "left":
                            if veh1.time_to_cross() < veh2.time_to_cross() + PRIORITY_GAP[veh2.veh_type]:
                                veh2.stop()
                                veh1.find_leader()
                            else:
                                veh2.decision = True
                                veh2.change_leader(veh2.next_road.last_vehicle(self))
                                if veh1.next_road == veh2.next_road:
                                    veh1.change_leader(veh2)


                # Unblock the situation
                # if veh1.v == 0 or veh2.v == 0:
                #     if random() < 0.5:
                #         veh1.find_leader()
                #         veh1.decision = True
                #     else:
                #         veh2.find_leader()
                        # veh2.decision = True

        # Non-priority vehicles
        # Search for the first vehicles on non-prioritary axis
        if len(self.roads) == 3 and not self.traffic_lights_enabled:
            incoming_veh = []
            veh = self.roads[1].first_vehicle(self)
            if veh != None:
                incoming_veh.append(veh)

            for veh in incoming_veh:
                # if leader is not the last vehicle
                if veh.leader != None and veh.leader.road == veh.next_road and veh.leader != veh.leader.road.last_vehicle(veh.destination_cross):
                    veh.decision = False
                    veh.change_leader(veh.leader.road.last_vehicle(veh.destination_cross))

                if not veh.decision:
                    # close enough from the intersection
                    if veh.d_to_cross() <= ((veh.v*veh.v)/(2*veh.b_max) + veh.v0*PRIORITY_GAP[veh.veh_type]):
                        i = veh.destination_cross.roads.index(veh.road)
                        j = veh.destination_cross.roads.index(veh.next_road)

                        other = self.roads[(i-(j-i))%4].first_vehicle(self)
                        # if abs(i-j) == 2:
                        #     facing = self.roads[(i+1)%4].first_vehicle(self)
                        #     if facing != None and other.time_to_cross() > facing.time_to_cross():
                        #         other = facing

                        if other != None:
                            if other.time_to_cross() > veh.time_to_cross() + PRIORITY_GAP[veh.veh_type]:
                                # the gap is big enough : go!
                                veh.decision = True
                                leader = veh.next_road.last_vehicle(veh.destination_cross)
                                veh.change_leader(leader)
                                if other.next_road == veh.next_road: #and other not in veh.followers:
                                    other.change_leader(veh)

                            else:
                                # the gap is too small, try to insert between other and its follower
                                if len(other.followers) == 0 and other not in veh.followers:
                                    veh.stop()
                                else:
                                    for follower in other.followers:
                                        if follower.road == other.road: # it's a true follower (there should only be one)
                                            space = follower.time_to_cross() - other.time_to_cross()
                                            req_space = (follower.road.speed_limit - veh.v)/veh.a  + PRIORITY_GAP[veh.veh_type]

                                            if space < req_space :
                                                # the gap is too small again, stop!
                                                veh.stop()
                                            elif other not in veh.followers:
                                                # okay, let's go
                                                veh.decision = True
                                                veh.change_leader(other)
                                                if follower.next_road == veh.next_road:
                                                    follower.change_leader(veh)

                        anti = []
                        anti_prio = self.roads[j].first_vehicle(self)
                        if anti_prio != None :
                            anti.append(anti_prio)
                        anti_non_prio = None
                        if len(self.roads) == 4:
                            anti_non_prio = self.roads[(i+2)%4].first_vehicle(self)
                            if anti_non_prio != None:
                                anti.append(anti_non_prio)

                        if veh.direction == "left" or veh.direction == None:
                            for ant in anti:
                                if (ant.time_to_cross() < veh.time_to_cross() + PRIORITY_GAP[veh.veh_type] + PRIORITY_GAP[ant.veh_type]):
                                    veh.decision = False
                                    veh.stop()
                                    if other != None and other.leader != None and other.leader.veh_type != "stop":
                                        other.change_leader(other.next_road.last_vehicle(veh.destination_cross))
                                    break

                    else:
                        veh.find_leader()


    def updateTrafficLights(self, t):
        if len(self.roads) > 2 and self.traffic_lights_enabled:
            for i in range(len(self.traffic_lights[0])):
                if t%(self.traffic_lights[0][-1]+3) == self.traffic_lights[0][i]:
                    # print("Update traffic lights", self.traffic_lights[1][i], self.traffic_lights[2][i])
                    self.priority = self.traffic_lights[1][i]
                    for road_index in range(len(self.roads)):
                        vehicle_list = None
                        if self.roads[road_index].cross1 == self:
                            vehicle_list = self.roads[road_index].vehicle_list_21
                        else:
                            vehicle_list = self.roads[road_index].vehicle_list_12

                        if len(vehicle_list) > 0:
                            veh = vehicle_list[0]
                            if self.traffic_lights[(road_index)%2+1][i] == 1: # GO
                                if self.roads[road_index].stop1 in vehicle_list or self.roads[road_index].stop1 in vehicle_list :
                                    for veh in vehicle_list:
                                        if veh.veh_type == "stop":
                                            vehicle_list.remove(veh)
                                            for follower in veh.followers:
                                                follower.find_leader()
                                                follower.decision = False
                                else:
                                    veh.find_leader()
                                    veh.decision = False

                            elif veh.veh_type != "stop": # STOP
                                for veh in vehicle_list:
                                    if veh.time_to_cross() > PRIORITY_GAP[veh.veh_type] or veh.v < 2:
                                        veh.stop()
                                        vehicle_list.insert(vehicle_list.index(veh), veh.leader)
                                        break
                                if len(vehicle_list) == 0:
                                    if self == self.road.cross1:
                                        vehicle_list.append(self.road.stop1)
                                    else:
                                        vehicle_list.append(self.road.stop2)




class GeneratorCross(Cross):
    """Generator cross, at the edges of the map, to add or delete vehicles on/off the map"""

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
            self.rand_period = randint(RAND_GAP, RAND_GAP)
            self.next_period = self.period + self.rand_period

        if (t - self.last_t) >= self.next_period :
            veh_type = "car" if random() < 0.9 else "truck"
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

    def __init__(self, road, origin_cross, T = 1, s0 = 2, a = 1.5, vehicle_type = "car", b = 1.5):
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
        self.last_road = None
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
        self.slow_down = 0
        self.angle = 0

        self.changed_road = True
        self.rep = None # Index for graphic representation
        self.brake_rep = None
        self.last_a = 0
        self.blinker_rep = None
        self.direction = None
        self.blinker_state = 0

        self.veh_type = vehicle_type

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
        elif vehicle_type == "stop":
            self.a=0
            self.b_max = Vehicle.VEH_B_MAX["car"] # Maximum vehicle deceleration (in case of danger ahead)
            self.length = Vehicle.VEH_LENGTH["car"]
            self.width = 2
        else:
            raise TypeError("Non existing type of vehicle, car or truck?")

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

    def turn_speed(self):
        """Give the optimal speed for changing road
        f(0) = 0, f(PI/2) = 15/50, f(PI) = 1"""
        if self.next_road != None:
            if self.destination_cross == self.road.cross1:
                angle_road = self.road.angle
            elif self.road.angle >= 0:
                angle_road = self.road.angle - pi
            else:
                angle_road = pi + self.road.angle

            if self.destination_cross == self.next_road.cross1:
                angle_next_road = self.next_road.angle
            elif self.next_road.angle >= 0:
                angle_next_road = self.next_road.angle - pi
            else:
                angle_next_road = pi + self.next_road.angle

            angle = abs(angle_road - angle_next_road)
            if angle < 0.01:
                angle = 3.1415
            elif angle > pi:
                 angle = 2*pi - angle
            self.angle = angle
            # self.v0 = log(1+(e-1)*angle/pi) * self.road.speed_limit
            self.v0 = (0.08*angle*angle + 0.06*angle) * self.road.speed_limit

    def destroy(self):
        """Delete a vehicle from the map and give a new leader to the followers"""
        deleted_vehicles.append(self)
        for veh in self.followers:
            veh.leader = None
            veh.find_leader()
        vehicles.remove(self)

    def stop(self):
        if self.destination_cross == self.road.cross1:
            self.change_leader(self.road.stop1)
        else:
            self.change_leader(self.road.stop2)

    def time_to_cross(self):
        if self.v > 0.1 :
            return self.d_to_cross() / self.v
        else:
            if self.direction == "right":
                return TIME_TO_CROSS["right"][self.veh_type]
            else:
                return TIME_TO_CROSS["other"][self.veh_type]

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
            self.change_leader(leader)

    def spacing_with_leader(self):
        """Return the spacing between the car and its leader
        If there is no leader, the distance is 250"""
        if self.leader == None:
            return 250 # arbitrary constant
        else:
            if self.leader.road == self.road:
                if self.leader.veh_type != "stop":
                    # "standard" leader
                    if self.x < self.length:
                        return max(0.01, self.leader.x - self.x - (self.leader.length + self.length)/2)
                    else:
                        return self.leader.x - self.x - (self.leader.length + self.length)/2
                else :
                    # "stop" leader
                    return max(0.00001, self.leader.x - self.x - (self.leader.length + self.length)/2)
            elif self.leader.road == self.next_road:
                return max(0.00001, self.d_to_cross() + self.leader.x - (self.leader.length + self.length)/2)
            elif self.leader.destination_cross == self.destination_cross:
                # "fake" leader: self follows a projection
                return max(0.00001,self.d_to_cross() - self.leader.d_to_cross() - (self.leader.length + self.length)/2)
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
        return max(-self.b_max,self.a * (1 - (self.v/self.v0)**self.delta - ((self.s0 + max(0, self.v * self.T + (self.v * (self.v-self.speed_of_leader())/2*(self.a*self.b)**0.5)))/self.spacing_with_leader())**2))
