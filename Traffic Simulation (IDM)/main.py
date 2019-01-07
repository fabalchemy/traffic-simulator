from classes import *

def RK4(f):
    return lambda y, dt: (
            lambda dy1: (
            lambda dy2: (
            lambda dy3: (
            lambda dy4: (dy1 + 2*dy2 + 2*dy3 + dy4)/6
            )( dt * f( y + dy3   ) )
    	    )( dt * f( y + dy2/2 ) )
    	    )( dt * f( y + dy1/2 ) )
    	    )( dt * f( y         ) )

C1 = Cross((0,0), True)
C2 = Cross((100,0), False)
R = Road("R", C1, C2, 50)
veh1 = Vehicle(road = R, T=2, leader = None, s0 = 2)

t = 0
dt = 0.001
while t < 10:
    print(v, x)
    veh1.v = RK4(veh1.acceleration)(veh1.v, dt)
    veh1.x = RK4(lambda x:x)(veh1.x, dt)
    t = t + dt
