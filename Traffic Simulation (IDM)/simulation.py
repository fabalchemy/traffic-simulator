# coding = utf-8
"""Classes necessary to run the mathematical simulation"""

from math import inf, acos, cos, sqrt, fabs, pow
from random import random,randint
from operator import attrgetter

# Exceptions
NotRoadError = TypeError("Input road is not Road type")
NotVehicleError = TypeError("Input vehicle is not Vehicle type")
NotCrossError = TypeError("Input cross is not Cross type")
NotLinkedRoad = ValueError("Input road is not linked to this cross")
NotLinkedCross = ValueError("Input cross is not linked to this road")

# Lists containing every object of the simulation
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
            print("ROAD = {}, ROAD LENGTH = {}, RECEIVED ABSCISSA = {}".format(self.id,self.length,x))
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

            if type(vehicle) is not Vehicle:
                raise notVehicleError

            if vehicle.x > self.length:
                if vehicle in self.vehicle_list_12:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_12[0]
                        vehicle.destroy()
                        # Update follower's leader to None
                        if len(self.vehicle_list_12) > 0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_12.pop(0), vehicle.next_road, vehicle.x - self.length)
                        # if len(self.vehicle_list_12)>0:
                        #     destination_cross.new_leader(vehicle) # Alert vehicles arrving next to it that it's their new leader

                elif vehicle in self.vehicle_list_21:
                    if type(destination_cross) is GeneratorCross:
                        del self.vehicle_list_21[0]
                        vehicle.destroy()
                        # Update follower's leader to None
                        if len(self.vehicle_list_21) > 0:
                            self.first_vehicle(destination_cross).change_leader(None)
                    else:
                        destination_cross.transfer_vehicle(self.vehicle_list_21.pop(0), vehicle.next_road, vehicle.x - self.length)
                        # if len(self.vehicle_list_21)>0:
                        #     destination_cross.new_leader(vehicle) # Alert vehicles arrving next to it that it's their new leader

                else:
                    raise ValueError("Vehicle not on this road")

    def first_vehicle(self,destination_cross):
        """Return the first vehicle arriving on destination_cross from this road"""

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

    def __init__(self, coords, id = None):
        """Generate a Cross at coords (x,y)"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")

        self.coords = coords
        self.roads = list()
        self.id = id

    def add_road(self, road):
        """Connects the road to the cross, adding it to self.roads"""
        if type(road) is not Road:
            raise NotRoadError

        if len(self.roads) < 4:
            self.roads.append(road)
        else:
            print("Cannot add a new road on this cross, crosses cannot be linked with more than 4 roads")
            print("Cross ID: ",self.id)

    def define_priority_axis(self, axis):
        """Define the priority axis of the cross
        axis : a tuple of 2 roads"""
        if (type(axis) is not tuple) and axis != None:
            raise TypeError("Input axis is not a tuple or NoneType")
        if axis != None and (len(axis) != 2 or (type(axis[0]) is not Road) or (type(axis[1]) is not Road)):
            raise ValueError("Input axis must be a tuple of 2 roads or None")

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
        vehicle.decision = False
        next_road.incoming_veh(vehicle,self, x)

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

        ran = 0
        while ran == 0:
            ran = random()

        for j in range(len(self.roads)):
            if ran <= self.dispatch[self.roads.index(origin_road)][j]:
                return self.roads[j]

        raise ValueError("Cannot return the next road")

    def set_dispatch(self, dispatch):
        """Set the dispatch matrix of the cross, converting a probability matrix
        into a cumulated frequecies matrix"""
        # Check dispatch
        if type(dispatch) is not list:
            raise TypeError("dispatch must be list type")
        # Check if dispatch is a list of lists of the same length (same number of incoming and outgoing roads)
        roads_nb = len(dispatch)
        for road in range(roads_nb):
            if type(dispatch[road]) is not list:
                raise TypeError("dispatch must be a list of lists")
            if len(dispatch[road]) != roads_nb:
                raise ValueError("dispatch must have the same number of incoming and outgoing roads")

        # Cars cannot turn back when arriving to a cross
        # This involves that for all incoming road dispatch[i][i] must equal 0
            if dispatch[road][road] != 0:
                raise ValueError("Vehicles cannot turn back at a cross. This involves dispatch[road i][road i] must be 0 for every road.")


        for i in range(len(dispatch)):
            for j in range(1,len(dispatch)):
                dispatch[i][j] += dispatch[i][j-1]
            if dispatch[i][-1] != 1:
                raise ValueError("Frequencies sum must equal 1")

        self.dispatch = dispatch

    def new_leader(self,vehicle):
        """When a car go out of a road, incoming on a new road,
        set this car as leader of the vehicles arriving at the cross and going on the same road"""
        for road in self.roads:
            if road is not vehicle.road:
                arriving_vehicle = road.first_vehicle(self)
                if arriving_vehicle != None and arriving_vehicle.next_road == vehicle.road:
                    arriving_vehicle.change_leader(vehicle)

    def decision_maker(self,veh):
        SECURITY_GAP = 8
        decision = False

        if type(veh.destination_cross) is not GeneratorCross and len(self.roads) > 2:
            if veh.road in self.priority_axis:
                if veh.next_road in self.priority_axis:
                    # Going straight on priority axis
                    if veh == veh.road.first_vehicle(self) and veh.leader != veh.next_road.last_vehicle(self):
                        veh.change_leader(veh.next_road.last_vehicle(self))
                    decision = True # Return decision but don't change speed

                else:
                    veh.turn_speed() # TODO : reduce speed later ?
                    if veh.next_road == self.roads[(self.roads.index(veh.road)+1)%len(self.roads)]:
                        # Turning left
                        front_road = self.priority_axis[1] if veh.road == self.priority_axis[0] else self.priority_axis[0]
                        front_veh = front_road.first_vehicle(self)
                        if front_veh == None or veh.time_to_cross() < front_veh.time_to_cross() - SECURITY_GAP:
                            decision = True
                        else:
                            if veh == veh.road.first_vehicle(self):
                                veh.change_leader(Stop(veh.road.length))
                    else:
                        # Turning right
                        decision = True

            else: # Vehicle not on priority axis
                veh.turn_speed()
                if veh.next_road == self.roads[(self.roads.index(veh.road)-1)%len(self.roads)]:
                    # Turning right
                    left_veh = self.roads[(self.roads.index(veh.road)+1)%len(self.roads)].first_vehicle(self)
                    if left_veh == None or veh.time_to_cross() < left_veh.time_to_cross() - SECURITY_GAP:
                        decision = True
                    else:
                        if veh == veh.road.first_vehicle(self):
                            veh.change_leader(Stop(veh.road.length))

                elif veh.next_road in [self.roads[(self.roads.index(veh.road)+1)%len(self.roads)],self.roads[(self.roads.index(veh.road)+2)%len(self.roads)]]:
                    # Turning left or going straight
                    right_veh = self.roads[(self.roads.index(veh.road)-1)%len(self.roads)].first_vehicle(self)
                    left_veh = self.roads[(self.roads.index(veh.road)+1)%len(self.roads)].first_vehicle(self)
                    if left_veh == None or veh.time_to_cross() < left_veh.time_to_cross() - SECURITY_GAP:
                        if right_veh == None or veh.time_to_cross() < right_veh.time_to_cross() - SECURITY_GAP:
                            if len(self.roads) == 4:
                                if veh.next_road == self.roads[(self.roads.index(veh.road)+2)%len(self.roads)]:
                                    # Going straight
                                    decision = True
                                else:
                                    front_road = self.roads[(self.roads.index(veh.road)+2)%len(self.roads)]
                                    front_veh = front_road.first_vehicle(self)
                                    if front_veh == None or veh.time_to_cross() < front_veh.time_to_cross() - SECURITY_GAP:
                                        decision = True
                            else:
                                decision = True
                        else:
                            if veh == veh.road.first_vehicle(self):
                                veh.change_leader(Stop(veh.road.length))

            if decision:
                if veh.leader == None or type(veh.leader) is Stop or veh.leader.road != veh.road:
                    if veh == veh.road.first_vehicle(self):
                        veh.change_leader(veh.next_road.last_vehicle(self))

            veh.decision = decision


class GeneratorCross(Cross):
    """Generator cross, at the edges of the map, to add or delete vehicles on/of the map"""

    rand_gap = 4

    def __init__(self,coords,time_lapse):
        """coords : (x,y) coordinates
        time_lapse [s] : time between two vehicle income"""

        if not(type(coords) is tuple and len(coords) == 2 and type(coords[0]) in (int,float) and
        type(coords[1]) in (int,float)):
            raise TypeError("coords must be a (x,y) tuple")
        if type(time_lapse) not in (int,float):
            raise TypeError("time_lapse is not int/float")

        self.coords = coords
        self.time_lapse = time_lapse
        self.roads = list()
        self.rand_time_lapse = None
        self.last_t = 0

    def generate(self, t):
        """Generate vehicles on the map"""
        road = self.roads[0]

        vehicle_ahead = self.roads[0].last_vehicle(self)

        if self.rand_time_lapse  == None:
            self.rand_time_lapse = randint(-GeneratorCross.rand_gap, GeneratorCross.rand_gap)
            self.time_lapse += self.rand_time_lapse

        if (t - self.last_t) >= self.rand_time_lapse :
            veh_type = "car" if random() < 0.93 else "truck"
            if (vehicle_ahead == None or vehicle_ahead.x > (self.roads[0].speed_limit**2)/(2*Vehicle.VEH_B_MAX[veh_type]) + vehicle_ahead.s0 + (vehicle_ahead.length + Vehicle.VEH_LENGTH[veh_type])/2):
                leader = self.roads[0].last_vehicle(self)
                if leader == None or leader.x >= leader.s0:
                    self.last_t = t

                    new_vehicle = Vehicle(road, self, vehicle_type = veh_type)
                    vehicle_list.append(new_vehicle)
                    new_vehicle.leader = leader
                    new_vehicle.v = self.roads[0].speed_limit
                    self.transfer_vehicle(new_vehicle, self.roads[0])
                    self.rand_time_lapse = None
                    return new_vehicle

class Vehicle:
    """Representation of a vehicle"""

    VEH_LENGTH = {"car": 4, "truck": 10}
    VEH_B_MAX = {"car": 10, "truck": 5}

    def __init__(self, road, origin_cross, T = 2, s0 = 2, a = 2, vehicle_type = "car", b = 1.5):
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
        self.T = T
        self.leader = None
        self.s0 = s0
        self.delta = 4
        self.b = b
        self.x = 0 # Position of the vehicle on the road
        self.v = 0 # Speed of the vehicle

        self.decision = False # Approbation to cross the next intersection
        self.rep = None # Index for graphic representation

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
            raise TypeError("Non existing type of vehicle, car or truck ?")

        # TODO: Implement some variation for v0 speed (pushy or safe driver)
        self.v0 = road.speed_limit # v0 = desired speed (generally the speed limit)

    def turn_speed(self):
        """Give the recommended speed when changing road
        f(0) = 0, f(PI/2) = 15/50, f(PI) = 1"""
        if self.next_road != None:
            angle = abs(self.next_road.angle - self.road.angle) % 3.1415
            if angle < 0.01:
                angle = 3.1415
            self.v0 = (0.08 *angle*angle + 0.06 * angle) * self.road.speed_limit

    def time_to_cross(self):
        if self.v > 0.01:
            d_to_cross = self.road.length - self.x
            T_slow_down = (self.v - self.v0) / self.b  #Time to reach the turn speed (new v0)
            d_slow_down = ((self.v - self.v0) / 2) * T_slow_down # Distance travelled slowing down
            T_to_cross = ((d_to_cross - d_slow_down) / self.v0) + T_slow_down
            return T_slow_down
        else:
            return 2 # arbitrary constant

    def destroy(self):
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
        If there is no leader, the distance is 250"""
        if self.leader == None:
            return 250
        else:
            if type(self.leader) == FakeLeader:
                return self.road.length - (self.leader.real_veh.road.length - self.leader.real_veh.x) - self.x

            elif type(self.leader) is Stop or  self.leader.road == self.road:
                return self.leader.x - self.x - (self.leader.length + self.length)/2
            else:
                return self.road.length - self.x + self.leader.x - (self.leader.length + self.length)/2

    def speed_of_leader(self):
        """Return the speed of the leader, if it exists
        Otherwise, return the speed of the car to cancel the interaction acceleration"""
        if self.leader == None:
             return self.v
        else:
            return self.leader.v

    def a_free(self, v):
        """Return the freeway acceleration (with no car ahead)"""
        if v < self.v0 :
            return self.a * (1 - pow(v/self.v0,self.delta))
        elif v == 0 :
            return 0
        else:
            return -self.b * (1 - pow(self.v0/v, self.a*self.delta/self.b))

    def z(self, v):
        """Acceleration term linked to distance to the leader"""
        s = self.spacing_with_leader()
        delta_v = v - self.speed_of_leader()
        return (self.s0 + max(0, v*self.T + v*delta_v/(2*(self.a*self.b)**0.5))) /s

    def acceleration_IIDM(self):
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

    def acceleration_IDM(self):
        return self.a * (1 - (self.v/self.v0)**self.delta - ((self.s0 + max(0, self.v * self.T + (self.v * (self.v-self.speed_of_leader())/2*(self.a*self.b)**0.5)))/self.spacing_with_leader())**2)

    def acceleration_RAVTR(self):
        b_f = - self.b
        b_l = - self.b if self.leader == None else - self.leader.b
        v_f = self.v
        v_l = self.speed_of_leader()
        s_0 = self.s0
        s = self.spacing_with_leader()
        tau = 1

        if v_f < self.v0:
            a_f = (b_f*tau - 2*v_f - 2*b_f*sqrt((b_f*b_l*tau*tau + 4*b_l*v_f*tau+4*v_l*v_l-8*b_l*(s-s_0))/(4*b_f*b_l)))/(2*tau)
        else:
            a_f = 0
        return max(-self.b_max, a_f)

class Stop(Vehicle):
    """Ahaha"""
    def __init__(self,x):
        self.x = x
        self.v = 0
        self.length = 2
        self.next_road = None
        self.b = 2

class FakeLeader(Vehicle):
    """Virtual leader"""

    def __init__(self,veh):
        self.real_veh = veh
