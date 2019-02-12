# coding = Latin-1

def start_simulation ():
    """Function starting the simulation, by generating the map, ... to complete"""

    if len(cross_list) != len(priority_axis_in_crosses):
        raise ValueError("In map.py, priority_axis_in_crosses and cross_list must have the same number of elements (one priority_axis for each cross)")

    for index in range(cross_list):
        cross_list[index].sort_linked_roads()
        define_priority_axis(cross_list[index], priority_axis_in_crosses[index])
