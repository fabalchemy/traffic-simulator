from simulation import *
import gui

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

gen = GeneratorCross(coords = (25,25), time_lapse=3)
generator_list.append(gen)
cross_list.append(gen)

cross_list.append(Cross((50,25)))
cross_list.append(Cross((75,25)))
cross_list.append(Cross((50,100)))

gen = GeneratorCross((50, 150), time_lapse=3)
generator_list.append(gen)
cross_list.append(gen)


road_list.append(Road(C[0], C[1], 54/3.6))
road_list.append(Road(C[1], C[2], 54/3.6))
road_list.append(Road(C[2], C[3], 54/3.6))
road_list.append(Road(C[1], C[3], 54/3.6))
road_list.append(Road(C[3], C[4], 54/3.6))

gui.map.draw_cross(C)
gui.map.draw_road(R)

C[1].define_priority_axis((R[0], R[1]))
C[3].define_priority_axis((R[2], R[4]))
C[1].sort_roads()
C[3].sort_roads()

for crs in cross_list:
    msg = "Cross #" + str(cross_list.index(crs)) + " "
    for road in crs.roads:
        msg = msg + str(road_list.index(road)) + " "
    print(msg)
    if len(crs.roads) >= 3:
        print("disp envoyé", copy_list(disp[len(crs.roads)]))
        crs.set_dispatch(copy_list(disp[len(crs.roads)]))
        if crs == C[1]:
            print("prout", disp[3])
