# coding = utf-8
from classes import *

import decimal
import os
file = open("results_new_ver.txt", "w")

cross_list = C = []
cross_list.append(Cross((0,0)))
cross_list.append(Cross((0,0)))

road_list = R = []
road_list.append(Road(C[0], C[1], 54/3.6))

vehicle_list = V = []
vehicle_list.append(Vehicle(R[0], C[0], T=1, leader = None, s0 = 3, a =2))

decimal.getcontext().prec = 3
t = decimal.Decimal(0)
dtd = decimal.Decimal(1)/decimal.Decimal(10)
dt = float(dtd)

while t < 100:
    for veh in vehicle_list:
        a = veh.acceleration()
        veh.v = max(0, veh.v + a*dt)
        veh.x = veh.x + veh.v*dt + max(0, 0.5*a*dt*dt)

        # write the results in a file
        # format : index_voiture, temps, accélération, vitesse, position, écart avec leader
        file.write("{0}     {1:.4f}     {2:.4f}     {3:.4f}     {4:.4f}     {5:.4f}"
                    .format(V.index(veh), t, a, veh.v, veh.x, veh.spacing_with_leader()) + "\n")

    # apparition d'une voiture à 2 secondes
    if t == 2 :
        vehicle_list.append(Vehicle(R[0], C[0], T=1, leader = V[0], s0=3, a=2))

    if t==70 :
        V[0].v0 = 30/3.6

    t+= dtd

file.close()
