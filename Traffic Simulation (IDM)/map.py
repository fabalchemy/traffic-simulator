from simulation import *
import gui

generator_list = G = []
cross_list = C = []
road_list = R = []
vehicle_list = V = []


gen = GeneratorCross(coords = (25,25), time_lapse=5)
generator_list.append(gen)
cross_list.append(gen)
cross_list.append(Cross((100,20)))
cross_list.append(Cross((50,50)))
cross_list.append(GeneratorCross((50, 100), time_lapse=10))
gen = GeneratorCross((50, 150), time_lapse=10)
generator_list.append(gen)
cross_list.append(gen)

road_list.append(Road(C[0], C[1], 54/3.6))
R.append(Road(C[1], C[2], 54/3.6))
# R.append(Road(C[2], C[0], 54/3.6))
R.append(Road(C[2], C[3], 54/3.6))
R.append(Road(C[1], C[3], 54/3.6))
R.append(Road(C[3], C[4], 54/3.6))
gui.map.draw_cross(C)

gui.map.draw_road(R)

C[0].define_priority_axis((R[0], R[2]))
C[1].define_priority_axis((R[0], R[1]))
C[2].define_priority_axis((R[1], R[3]))
C[0].sort_roads()
C[1].sort_roads()
C[2].sort_roads()

for crs in cross_list:
    msg = "Cross #" + str(cross_list.index(crs)) + " "
    for road in crs.roads:
        msg = msg + str(road_list.index(road)) + " "
    print(msg)
