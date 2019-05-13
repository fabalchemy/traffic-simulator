# coding = utf-8
from simulation import *
# Change next line with the map you want to use
from maps.map_from_data import *
from time import *
from math import exp
import decimal

# Discretize time
decimal.getcontext().prec = 8 # Set the precision for the decimal module
t = decimal.Decimal(0)
dt_s = decimal.Decimal(1)/decimal.Decimal(100)
dt_g = 100 # [ms] # Time interval for graphic update()

delay = 0
average_speed = 0

# file = open("results.txt", "w")

def next_steps(dt_d, steps):
    """Update all the simulation :
    - vehicle acceleration, velocity and position
    - vehicle crossing order for each cross according to the priority
    - traffic light state """
    T = perf_counter()
    global t
    global average_speed
    dt = float(dt_d)

    # if t == 0 or t == 2 or t == 4 :
    #     veh = Vehicle(roads[0], crosses[0])
    #     vehicles.append(veh)
    #     roads[0].incoming_veh(veh, crosses[0])

    for i in range(steps):
        # file.write("{}\t".format(t))
        average_speed = 0
        # Generate vehicles
        for gen in generators:
            gen.generate(t)

        for cross in crosses:
            cross.updateTrafficLights(t)
            cross.get_intentions()

        # Update acceleration, speed and position of each vehicle
        for veh in vehicles:
            try:
                a = veh.acceleration_IIDM()
                veh.x += veh.v*dt + max(0, 0.5*a*dt*dt)
                veh.v = max(0, veh.v + a*dt)
                average_speed += veh.v

                # file.write("{} {} {} ".format(a, veh.v, veh.x))

                if veh.slow_down > 1:
                    veh.slow_down -= 1
                elif veh.slow_down == 1:
                    veh.slow_down = 0
                    veh.v0 = veh.road.speed_limit

                if (veh.road.length - veh.x) <= ((veh.v*veh.v)/(2*veh.b_max) + 30) and veh.slow_down == 0 :
                    veh.turn_speed()

                if veh.leader != None and veh.leader.veh_type != "stop" and veh.leader.road == veh.road and veh.destination_cross != veh.leader.destination_cross:
                    veh.decision = False
                    veh.find_leader()

            except:
                next_road_id = None if veh.next_road == None else veh.next_road.id
                leader_index = None if veh.leader == None or veh.leader.veh_type == "stop" else vehicles.index(veh.leader)

                print("ERROR DURING THE SIMULATION, while working on {}, going from road {} to {}, following {} on {}, spacing: {}"
                .format(vehicles.index(veh), veh.road.id, next_road_id, leader_index, veh.leader.road.id, veh.spacing_with_leader()))
                raise

        # file.write("\n")

        if len(vehicles) > 0:
            average_speed = (average_speed / len(vehicles)) * 3.6

        # Check if the vehicles must change road
        for road in roads:
            road.outgoing_veh(road.first_vehicle(road.cross1))
            road.outgoing_veh(road.first_vehicle(road.cross2))

        for veh in deleted_vehicles:
            # Delete the vehicles that left the map
            gui.map.delete(veh.rep)
            gui.map.delete(veh.brake_rep)
        deleted_vehicles.clear()

        t+= dt_d

    global delay
    delay = perf_counter() - T

def update():
    """Update the graphic interface :
    Compute the correct number of simulation steps
    Update the position of the vehicles, the traffic lights and the leadership arrows"""

    global delay
    global average_speed
    T = perf_counter()
    if gui.controls.play.get():
        next_steps(dt_s, int((dt_g/(1000*float(dt_s)))*gui.controls.speed.get()))
        gui.map.draw_vehicle(vehicles)
        gui.map.draw_traffic_lights(crosses)
        gui.controls.time_str.set("Current time : " + str(t) + " s.")
        gui.controls.nb_veh.set(len(vehicles))
        gui.controls.avg_speed.set("{:.4f}".format(average_speed))
        mouseover()
        if gui.controls.leadership.get():
            gui.map.draw_leadership(vehicles)
        else:
            gui.map.delete("leadership")
        delay += perf_counter() - T + delay
        gui.map.after(int(dt_g * exp(-delay*1000/dt_g)), update)
    else:
        mouseover()
        gui.map.after(dt_g, update)
        if gui.controls.leadership.get():
            gui.map.draw_leadership(vehicles)
        else:
            gui.map.delete("leadership")


mouse_x, mouse_y = 0, 0

def click(event):
    """Slow down a vehicle when clicking on it"""
    x, y = gui.map.canvasx(event.x), gui.map.canvasy(event.y)
    objects = gui.map.find_overlapping(x,y,x,y)
    for obj in objects:
        tags = gui.map.gettags(obj)
        if "vehicle" in tags:
            for veh in vehicles:
                if veh.rep == obj:
                    veh.v0 = veh.v/3
                    veh.slow_down = 10*int(1/dt_s)
                    break

def mouseover():
    """Update the text to give information to the user"""
    x, y = gui.map.canvasx(mouse_x), gui.map.canvasy(mouse_y)
    objects = gui.map.find_overlapping(x,y,x,y)
    txt = ""
    for obj in objects:
        tags = gui.map.gettags(obj)
        if "road" in tags:
            for road in roads:
                if road.rep == obj:
                    txt = txt + "Road {} (angle: {:.2f}) ".format(roads.index(road), road.angle)
                    break
        elif "cross" in tags:
            for cross in crosses:
                if cross.rep == obj:
                    txt = txt + "Cross " + str(crosses.index(cross)) + "  "
                    break
        elif "vehicle" in tags:
            for veh in vehicles:
                if veh.rep == obj:
                    next_road_id = None if veh.next_road == None else veh.next_road.id
                    leader_index = None if veh.leader == None or veh.leader.veh_type == "stop" else vehicles.index(veh.leader)
                    leader_index = "stop" if veh.leader != None and veh.leader.veh_type == "stop" else leader_index
                    txt = txt + "Vehicle {} \n(speed: {:.2f}, v0: {:.2f}, d_to_cross: {:.2f}, going to: {}, leader: {}, decision: {})".format(vehicles.index(veh), veh.v*3.6, veh.v0*3.6, veh.d_to_cross(), next_road_id, leader_index, veh.decision)
                    break
    gui.map.itemconfigure(tag, text=txt)
    gui.map.coords(tag, x+15, y+15)

def moved(event):
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y

gui.map.bind("<Motion>", moved)
gui.map.bind("<ButtonPress-3>", click)
tag = gui.map.create_text(10, 10, text="", anchor="nw")

gui.map.after(dt_g, update)
gui.root.mainloop()
