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

default_dispatch_3=[[0   , 0.2 , 0.8],
                    [0.5 , 0   , 0.5],
                    [0.8 , 0.2 , 0  ]]

default_dispatch_4=[[0   , 0.15, 0.7 , 0.15],
                    [0.4 , 0   , 0.4 , 0.2 ],
                    [0.7 , 0.15, 0   , 0.15],
                    [0.4 , 0.2 , 0.4 , 0   ]]
disp = {3:default_dispatch_3, 4:default_dispatch_4}

ecart = e = 100
# coords_gen = [(150, 150-e), (150, 150+e), (150-e, 150), (150+e, 150)]
coords_gen = [(150, 150-e), (150, 150+e), (150-e, 150)]

cross_list.append(Cross((150,150)))

for coords in coords_gen:
    gen = GeneratorCross(coords = coords, time_lapse = random.randint(1,4))
    generator_list.append(gen)
    cross_list.append(gen)


road_list.append(Road(C[0], C[1], 54/3.6))
road_list.append(Road(C[0], C[2], 54/3.6))
road_list.append(Road(C[0], C[3], 54/3.6))
# road_list.append(Road(C[0], C[4], 54/3.6))

gui.map.draw_cross(C)
gui.map.draw_road(R)

C[0].define_priority_axis((R[0], R[1]))
C[0].sort_roads()

for crs in cross_list:
    msg = "Cross #" + str(cross_list.index(crs)) + " "
    for road in crs.roads:
        msg = msg + str(road_list.index(road)) + " "
    print(msg)
    if len(crs.roads) >= 3:
        crs.set_dispatch(copy_list(disp[len(crs.roads)]))
