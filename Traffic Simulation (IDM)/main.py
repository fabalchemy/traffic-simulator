# coding = Latin-1

from classes import *
from map import *
from start_simulation import *

import os


def RK4(v, f, dt):
    v1 = f(v)*dt
    v2 = f(v+v1*0.5)*dt
    v3 = f(v+v2*0.5)*dt
    v4 = f(v+v3)*dt
    v = v + (v1 + 2*(v2 + v3) + v4)/6
    return v

def euler(v, acc, dt):
    return v + acc(v)*dt

file = open("results.txt", "w")


C1 = Cross((0,0), True)
C2 = Cross((100,0), False)
R = Road("R", C1, C2, 54/3.6)
veh1 = Vehicle(road = R, T=1, leader = None, s0 = 3, a=2)
veh2 = None
t = 0
dt = 0.01
while t < 100:
    if t >= 2 and t<2.1 :
        veh2 = Vehicle(road = R, T=1, leader = veh1, s0=3, a=2)

    if t<=2:
        veh1.x = veh1.x + veh1.v * dt + max(0, 0.5 * veh1.acceleration() * dt * dt)
        veh1.v = max(0, veh1.v + veh1.acceleration()*dt)
        file.write("{0:.4f}     {1:.4f}     {2:.4f}     {3:.4f}".format(t, veh1.acceleration(), veh1.v, veh1.x) + "\n")
    else:
        if t<70:
            veh1.x = veh1.x + veh1.v * dt + max(0, 0.5 * veh1.acceleration() * dt * dt)
            veh1.v = max(0, veh1.v + veh1.acceleration()*dt)
        else:
            veh1.v = 0
        veh2.x = veh2.x + veh2.v * dt + max(0, 0.5 * veh2.acceleration() * dt * dt)
        veh2.v = max(0, veh2.v + veh2.acceleration()*dt)
        file.write("{:.4f}     {:.4f}     {:.4f}     {:.4f}     {:.4f}     {:.4f}      {:.4f}      {:.4f}"
            .format(t, veh1.acceleration(), veh1.v, veh1.x, veh2.acceleration(), veh2.v, veh2.x, veh1.x-veh2.x) + "\n")

    t = t + dt

file.close()
