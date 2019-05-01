# coding = utf-8
from simulation import *
from map_from_data import *
from time import *
from math import exp
import decimal

# Discretize time
decimal.getcontext().prec = 8 # Set the precision for the decimal module
t = decimal.Decimal(0)
dt_s = decimal.Decimal(1)/decimal.Decimal(100)
dt_g = 40 # [ms] # Time interval for graphic update()

delay = 0
average_speed = 0

def next_steps(dt_d, steps):
    T = perf_counter()
    global t
    global average_speed
    dt = float(dt_d)
    for i in range(steps):
        average_speed = 0
        # Generate vehicles
        for gen in generators:
            gen.generate(t)

        for cross in crosses:
            cross.get_intentions()

        # Update acceleration, speed and position of each vehicle
        for veh in vehicles:
            try:
                a = veh.acceleration_IIDM()
                veh.dx += veh.v*dt + max(0, 0.5*a*dt*dt)
                veh.x += veh.v*dt + max(0, 0.5*a*dt*dt)
                veh.v = max(0, veh.v + a*dt)
                average_speed += veh.v

                if veh.slow_down > 1:
                    veh.slow_down -= 1
                elif veh.slow_down == 1:
                    veh.slow_down = 0
                    veh.v0 = veh.road.speed_limit

                if (veh.road.length - veh.x) <= ((veh.v*veh.v)/(2*veh.b_max) + 30) and veh.slow_down == 0 :
                    veh.turn_speed()

                # if (veh.leader != None and (veh.leader.road != veh.road and veh.leader.road != veh.next_road
                #     and veh.destination_cross != veh.leader.destination_cross)):
                #     veh.find_leader()

            except:
                next_road_id = None if veh.next_road == None else veh.next_road.id
                leader_index = None if veh.leader == None or veh.leader.rep == None else vehicles.index(veh.leader)

                print("ERROR DURING THE SIMULATION, while working on {}, going from road {} to {}, following {}, spacing: {}"
                .format(vehicles.index(veh), veh.road.id, next_road_id, leader_index, veh.spacing_with_leader()))
                raise


        if len(vehicles) > 0:
            average_speed = (average_speed / len(vehicles)) * 3.6

        # Check if the vehicles must change road
        for road in roads:
            road.outgoing_veh(road.first_vehicle(road.cross1))
            road.outgoing_veh(road.first_vehicle(road.cross2))

        for veh in deleted_vehicles:
            gui.map.delete(veh.rep)
            gui.map.delete(veh.brake_rep)
        deleted_vehicles.clear()

        t+= dt_d

    global delay
    delay = perf_counter() - T

def update():
    global delay
    global average_speed
    T = perf_counter()
    if gui.controls.play.get():
        next_steps(dt_s, int((dt_g/(1000*float(dt_s)))*gui.controls.speed.get()))
        gui.map.draw_vehicle(vehicles)
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
                    leader_index = None if veh.leader == None or veh.leader.rep == None else vehicles.index(veh.leader)
                    txt = txt + "Vehicle {} \n(speed: {:.2f}, v0: {:.2f}, d_to_cross: {:.2f}, going to: {}, leader: {}, decision: {}, angle: {:.2f})".format(vehicles.index(veh), veh.v*3.6, veh.v0*3.6, veh.d_to_cross(), next_road_id, leader_index, veh.decision, veh.angle)
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
