from simulation import *
import gui
import random

def copy_list(a):
    b = list()
    for i in range(len(a)):
        b.append(list())
        for j in range(len(a[i])):
            b[i].append(a[i][j])
    return b
#
# default_dispatch_3=[[0 , 1 , 0],
#                     [0 , 0,  1],
#                     [0, 1 , 0]]
default_dispatch_3=[[0   , 0.2 , 0.8],
                    [0.5 , 0   , 0.5],
                    [0.8 , 0.2 , 0  ]]

default_dispatch_4=[[0   , 0.15, 0.7 , 0.15],
                    [0.4 , 0   , 0.4 , 0.2 ],
                    [0.7 , 0.15, 0   , 0.15],
                    [0.4 , 0.2 , 0.4 , 0   ]]
disp = {3:default_dispatch_3, 4:default_dispatch_4}

ecart = e = 200
# coords_gen = [(150, 150-e), (150, 150+e), (150-e, 150), (150+e, 150)]
# coords_gen = [(150, 150-e), (150, 150+e), (150-e, 150)]
coords_gen = [(150-e, 150), (150+e, 150)]

for coords in coords_gen:
    gen = GeneratorCross(coords = coords, period = 4)
    generators.append(gen)
    crosses.append(gen)


roads.append(Road(crosses[0], crosses[1], 54/3.6, 0))
# roads.append(Road(crosses[0], crosses[2], 54/3.6, 1))
# roads.append(Road(crosses[0], crosses[3], 54/3.6, 2))
# road_list.append(Road(C[0], C[4], 54/3.6))

gui.map.draw_road(roads)
gui.map.draw_cross(crosses)

# crosses[0].define_priority_axis((roads[0], roads[1]))
# crosses[0].sort_roads()

for crs in crosses:
    msg = "Cross #" + str(crosses.index(crs)) + " "
    for road in crs.roads:
        msg = msg + str(roads.index(road)) + " "
    print(msg)
    if len(crs.roads) >= 3:
        crs.set_dispatch(copy_list(disp[len(crs.roads)]))
