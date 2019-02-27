# coding = utf-8
from simulation import *
from map import *


import decimal
file = open("results.txt", "w")

decimal.getcontext().prec = 5
t = decimal.Decimal(0)
dt_s = decimal.Decimal(1)/decimal.Decimal(100)
dt_g = 100 #ms

generate()

def next_steps(dt_d, steps):
    global t
    dt = float(dt_d)
    for i in range(steps):
        veh1 = C[0].generate(t)
        if veh1 != None:
            vehicle_list.append(veh1)
        for veh in vehicle_list:
            a = veh.acceleration()
            veh.x = veh.x + veh.v*dt + max(0, 0.5*a*dt*dt)
            veh.v = max(0, veh.v + a*dt)
            # write the results in a file
            file.write("{0}     {1}     {2:.4f}     {3:.4f}     {4:.4f}     {5:.4f}"
                        .format(V.index(veh), road_list.index(veh.road), a, veh.v, veh.x, veh.spacing_with_leader()) + "\n")
        t+= dt_d

def update():
    if gui.controls.play.get() == True:
        next_steps(dt_s, int((dt_g/(1000*float(dt_s)))*gui.controls.speed.get()))
        for veh in V:
            gui.map.draw_vehicle(veh)
    gui.map.after(dt_g, update)

gui.map.after(dt_g, update)
gui.root.mainloop()
file.close()
