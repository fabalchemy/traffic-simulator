from math import floor

def minimum(liste):
    mini_x, mini_y = liste[0]
    for x in liste:
        if x[0] < mini_x:
            mini_x = x[0]
        if x[1] < mini_y:
            mini_y = x[1]

    return mini_x,mini_y

def minimize(liste,dx,dy):
    for i in range(len(liste)):
        liste[i] = (liste[i][0] - dx, liste[i][1] - dy)

def pixel_to_meter(liste):
    for i in range(len(liste)):
        liste[i] = (floor(liste[i][0]*200/89),floor(liste[i][1]*200/89))

cross = [(797,641), (701,388), (910,357), (945,470), (768,571),(656,602),(608,619),(481,703),(471,730),(465,569),(435,431),(452,890),(526,897),(576,760),(680,779),(613,900),(763,923),(797,818),(799,763),(866,766),(873,633),(1003,633),(1044,726),(990,735),(979,864),(1113,885),(1530,758),(1375,685),(1717,666), (1671,381), (1190,281),(1250,104),(1054,79),(979,206),(831,118),(799,197),(779,113),(722,225),(679,308),(684,102)]

generator_cross = [(194,444),(324,692),(513,1036),(1197,1036),(1896,692), (1170,-50),(685,-50)]

dx_cross,dy_cross = minimum(cross)
dx_generator,dy_generator = minimum(generator_cross)
dx = min(dx_cross,dx_generator)
dy = min(dy_cross,dy_generator)

print(dx,dy)

minimize(cross,dx,dy)
minimize(generator_cross,dx,dy)

pixel_to_meter(cross)
pixel_to_meter(generator_cross)

file = open("map_data.txt", "w")
file.write("{} \n {}".format(str(cross), str(generator_cross)))
file.close()
