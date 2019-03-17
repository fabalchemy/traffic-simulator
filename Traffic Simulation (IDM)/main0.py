# coding = utf-8
from simulation import *
from map1 import *
from time import *
from math import exp

import decimal
file = open("results.txt", "w")

decimal.getcontext().prec = 6 # Set the precision for the decimal module
t = decimal.Decimal(0.1)
dt_s = decimal.Decimal(1)/decimal.Decimal(100)
dt_g = 40 # [ms] # Time interval for graphic update()

delai = 0

def next_steps(dt_d, steps):
    T = perf_counter()
    global t
    dt = float(dt_d)
    for i in range(steps):
        # file.write(str(t) + "\n")

        # Generate vehicles
        for gen in generator_list:
            veh = gen.generate(t)

        # Update acceleration, speed and position of each vehicle
        for veh in vehicle_list:

            a = veh.acceleration()
            veh.x = veh.x + veh.v*dt + max(0, 0.5*a*dt*dt)
            veh.v = max(0, veh.v + a*dt)

            if (veh.road.length - veh.x) <= ((veh.v*veh.v)/(2*veh.b_max) + 30):
                veh.destination_cross.decision_maker(veh)

        # Check if the vehicles must change road
        for road in road_list:
            road.outgoing_veh(road.first_vehicle(road.cross1))
            road.outgoing_veh(road.first_vehicle(road.cross2))

        for veh in vehicle_to_delete:
            gui.map.delete(veh.rep)
            vehicle_to_delete.remove(veh)

        t+= dt_d

    global delai
    delai = perf_counter() - T

def update():
    global delai
    T = perf_counter()
    if gui.controls.play.get():
        next_steps(dt_s, int((dt_g/(1000*float(dt_s)))*gui.controls.speed.get()))
        gui.map.draw_vehicle(vehicle_list)
        gui.controls.time_str.set("Current time : " + str(t) + " s.")
        gui.controls.nb_veh.set(len(vehicle_list))
    delai += perf_counter() - T + delai
    gui.map.after(int(dt_g * exp(-delai*1000/dt_g)), update)

gui.map.after(dt_g, update)
gui.root.mainloop()
file.close()
