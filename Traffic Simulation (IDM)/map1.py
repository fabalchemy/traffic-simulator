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


# Important: Crosses MUST be created BEFORE Generator Crosses
# to work map_data properly
# IF NOT : the map will be totally false
for i in range(len(cross_coords)):
    cross_list.append(Cross(cross_coords[i],i))

for coords in generator_cross_coords:
    gen = GeneratorCross(coords = coords, time_lapse = 3)
    generator_list.append(gen)
    cross_list.append(gen)

# mini = 4000
for i in range(len(roads)):
    road_list.append(Road(cross_list[roads[i][0]],cross_list[roads[i][1]],15,i))
#     if road_list[-1].length < mini:
#         mini = road_list[-1].length
#
# print("MINIMUM : ", mini)



gui.map.draw_cross(C)
gui.map.draw_road(R)

for i in range(len(cross_coords)):
    axis = priority_axis[i]
    if axis != None:
        C[i].define_priority_axis((R[axis[0]],R[axis[1]]))
        C[i].sort_roads()
        C[i].set_dispatch(copy_list(disp[len(C[i].roads)]))


# for crs in cross_list:
#     msg = "Cross #" + str(cross_list.index(crs)) + " "
#     for road in crs.roads:
#         msg = msg + str(road_list.index(road)) + " "
#     print(msg)
#     if len(crs.roads) >= 3:
#         print("disp envoyé", copy_list(disp[len(crs.roads)]))
#         crs.set_dispatch(copy_list(disp[len(crs.roads)]))
#         if crs == C[1]:
#             print("prout", disp[3])
