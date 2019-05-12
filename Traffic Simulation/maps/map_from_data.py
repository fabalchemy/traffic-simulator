from simulation import *
import gui

def copy_list(a):
    b = list()
    for i in range(len(a)):
        b.append(list())
        for j in range(len(a[i])):
            b[i].append(a[i][j])
    return b

# default_dispatch_3=[[0   , 0 , 1],
#                     [0 , 0   , 1],
#                     [1 , 0 , 0  ]]
default_dispatch_3=[[0   , 0.2 , 0.8],
                    [0.5 , 0   , 0.5],
                    [0.8 , 0.2 , 0  ]]
# default_dispatch_3=[[0   , 0.8 , 0.2],
#                     [1 , 0   , 0],
#                     [0.2 , 0.8 , 0  ]]

default_dispatch_4=[[0   , 0.2, 0.6 , 0.2],
                    [0.4 , 0  , 0.4 , 0.2],
                    [0.6 , 0.2, 0   , 0.2],
                    [0.4 , 0.2, 0.4 , 0  ]]

disp = {1: None, 2: None, 3:default_dispatch_3, 4:default_dispatch_4}

file = open("maps/map_data.txt", "r")
lines = file.readlines()

state = "generator"
compteur_roads = 0
for line in lines:
    if state == "generator":
        if line != "\n":
            x,y = line.split()
            x,y = float(x), float(y)
            gen = GeneratorCross(coords = (x,y), period = 6)
            generators.append(gen)
            crosses.append(gen)
        else:
            state = "cross"
    elif state == "cross":
        if line != "\n":
            x,y,t = line.split()
            x,y = float(x), float(y)
            t = False if t == "False" else True
            cross = Cross(coords = (x,y), traffic_lights=t)
            crosses.append(cross)
        else:
            state = "road"

    elif state == "road":
        if line != "\n":
            c1, c2 = line.split()
            c1, c2 = int(c1), int(c2)
            c1 = crosses[c1]
            c2 = crosses[c2]
            road = Road(c1, c2, 50/3.6, id=compteur_roads)
            compteur_roads+=1
            roads.append(road)
        else:
            state = "priority"

    elif state == "priority":
        if line != "\n":
            c, r1, r2 = line.split()
            c, r1, r2 = int(c), int(r1), int(r2)
            crosses[c].define_priority_axis((roads[r1], roads[r2]))
            crosses[c].sort_roads()
            crosses[c].set_dispatch(copy_list(disp[len(crosses[c].roads)]))

gui.map.draw_cross(crosses)
gui.map.draw_road(roads)
gui.map.draw_stop(roads)
