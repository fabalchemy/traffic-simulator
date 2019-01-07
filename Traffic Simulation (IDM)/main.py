from classes import *

def RK4(v, f, dt):
    v1 = f(v)*dt
    v2 = f(v+v1*0.5)*dt
    v3 = f(v+v2*0.5)*dt
    v4 = f(v+v3)*dt
    v = v + (v1 + 2*(v2 + v3) + v4)/6
    return v

def euler(v, acc, dt):
    return v + acc(v)*dt

C1 = Cross((0,0), True)
C2 = Cross((100,0), False)
R = Road("R", C1, C2, 80/3.6)
veh1 = Vehicle(road = R, T=.1, leader = None, s0 = 2, a=1)
veh2 = None
t = 0
dt = 0.001
while t < 100:
    if t > 10 and t<10.2 :
        veh2 = Vehicle(road = R, T=.1, leader = veh1, s0=2, a=1)

    if t<=10:
        veh1.v = RK4(veh1.v, veh1.acceleration, dt)
        veh1.x += (veh1.v + veh1.v_old) / 2 * dt
        veh1.v_old = veh1.v
        print(t, veh1.acceleration(veh1.v), veh1.v, veh1.x)
    else:
        veh1.v = RK4(veh1.v, veh1.acceleration, dt)
        veh1.x += (veh1.v + veh1.v_old) / 2 * dt
        veh1.v_old = veh1.v
        veh2.v = RK4(veh2.v, veh2.acceleration, dt)
        veh2.x += (veh2.v + veh2.v_old) / 2 * dt
        veh2.v_old = veh2.v
        print(t, veh1.acceleration(veh1.v), veh1.v, veh1.x, veh2.acceleration(veh2.v), veh2.v, veh2.x)

    t = t + dt
