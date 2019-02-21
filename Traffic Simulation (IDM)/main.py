# coding = utf-8
from simulation import *
from map import *

import decimal
file = open("results.txt", "w")

decimal.getcontext().prec = 4
t = decimal.Decimal(0)
dtd = decimal.Decimal(1)/decimal.Decimal(10)
dt = float(dtd)

generate()

while t < 100:
    file.write(str(t) + "\n")
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

    t+= dtd

    if t == 50:
        dumb_leader = Vehicle(R[0], C[0])
        dumb_leader.v = 0
        a = V[0].x + 20
        dumb_leader.x = a
        V[0].leader = dumb_leader

file.close()
