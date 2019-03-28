# coding = utf-8
from simulation import *
# from map import *

import decimal
file = open("results.txt", "w")

decimal.getcontext().prec = 4
t = decimal.Decimal(0)
dtd = decimal.Decimal(1)/decimal.Decimal(10)
dt = float(dtd)

c1 = Cross((0,0))
c2 = Cross((1000,0))
road = Road(c1, c2, 15)
veh1 = Vehicle(road, c1, b=3)
while t < 100:

    file.write(str(t) + "\n")

    a = veh1.acceleration()
    veh1.x = veh1.x + veh1.v*dt + max(0, 0.5*a*dt*dt)
    veh1.v = max(0, veh1.v + a*dt)
    # write the results in a file
    file.write("{0}     {1:.4f}     {2:.4f}     {3:.4f}"
                .format(a, veh1.v, veh1.x, veh1.spacing_with_leader()) + "\n")

    t += dtd

    if t == 30:
        veh1.v0 = 0

    if t == 50:
        veh1.v0 = 15


file.close()
