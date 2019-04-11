from simulation import *
import gui
from map_data import *

def copy_list(a):
    b = list()
    for i in range(len(a)):
        b.append(list())
        for j in range(len(a[i])):
            b[i].append(a[i][j])
    return b

default_dispatch_3=[[0   , 0.35, 0.65],
                    [0.5 , 0   , 0.5 ],
                    [0.65, 0.35, 0   ]]

default_dispatch_4=[[0   , 0.2, 0.6 , 0.2],
                    [0.4 , 0  , 0.4 , 0.2],
                    [0.6 , 0.2, 0   , 0.2],
                    [0.4 , 0.2, 0.4 , 0  ]]
disp = {1: None, 2: None, 3:default_dispatch_3, 4:default_dispatch_4}

generator_list = []
cross_list = []
road_list = []

file = open("map_data.txt", "r")
lines = file.readlines()

state = "generator"

for line in lines:
    if state == "generator":
        if line != "\n":
            x,y = line.split()
            x,y = float(x), float(y)
            gen = GeneratorCross(coords = (x,y), time_lapse = 3)
            generator_list.append(gen)
            cross_list.append(gen)
        else:
            state = "cross"
    elif state == "cross":
        if line != "\n":
            x,y = line.split()
            x,y = float(x), float(y)
            cross = Cross(coords = (x,y))
            cross_list.append(cross)
        else:
            state = "road"

    elif state == "road":
        if line != "\n":
            c1, c2 = line.split()
            c1, c2 = int(c1), int(c2)
            c1 = cross_list[c1]
            c2 = cross_list[c2]
            road = Road(c1, c2, 50/3.6)
            road_list.append(road)
        else:
            state = "priority"

    elif state == "priority":
        if line != "\n":
            c, r1, r2 = line.split()
            c, r1, r2 = int(c), int(r1), int(r2)
            cross_list[c].define_priority_axis((road_list[r1], road_list[r2]))
            cross_list[c].sort_roads()
            cross_list[c].set_dispatch(copy_list(disp[len(cross_list[c].roads)]))

    gui.map.draw_cross(cross_list)
    gui.map.draw_road(road_list)
