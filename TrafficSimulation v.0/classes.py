"""TrafficSimulation v.1
Necessary classes for the program"""

alphabet = "abcdefghijklmnopqrstuvwxyz"

class Road:
    """Class creating a road between two vertices / crosses"""

    vehicles_interdistance = 5 # Constant to define or modify : average distance between two vehicles centers [m]

    def __init__(self,name,cross1,cross2):
        """Road linking cross1 and cross2"""

        self.name = name
        self.distance = distance(cross1,cross2)

        self.max_vehicles_on_road = self.distance // vehicles_interdistance # Max number of vehicles that can contain the current road

        self.nb_vehicles

    def distance(cross1,cross2):
        """Euclidean distance between two crosses"""
        x1,y1 = cross1.coordinates
        x2,y2 = cross2.coordinates

        return ((x2-x1)**2 + (y2-y1)**2)**0.5




class Cross:
    """Class creating a cross of different roads

    Objet name should be : bor006 or tal152"""

    def __init__(self, name, coordinates, roads_list, flux_mat, duration_light_mat):
        """Cross of different roads defined by:
        - Name (form : 'bor106')
        - Geographical coordinates (x,y) [m]
        - List of roads in/outcoming
        - Matrix of flux (number /time unit , origin/destination)(where and how many cars from road 1 are going to road 2,3 ...)
        - Matrix of duration of each traffic light"""


        # We check the cross name is of the expected form 'abc123'
        CrossNameError = NameError("Object name must have 'abc123' form")
        if len(name) != 6:
            raise CrossNameError
        for i in range(3):
            if name[i].lower() not in alphabet:
                raise CrossNameError
        try:
            val = int(name[3:6])
        except ValueError:
            raise CrossNameError

        self.name = name.lower()

        # We check coordinates are valid
        CoordinatesError = TypeError("Coordinates must be of (x,y) form, x,y are float/int values")
        if not (type(coordinates) is tuple and len(coordinates) == 2):
            raise CoordinatesError
        else:
            if not (type(coordinates[0]) in (int,float) and type(coordinates[1]) in (int,float)):
                raise CoordinatesError

        self.coordinates = float(coordinates[0]), float(coordinates[1])

        self.roads_list = roads_list

        # We check flux_mat is of the exepected form
        #Example of matrix: cross linking 3 roads  : [[a1,b1,cross1],[a2,b2,cross2],[a3,b3,c3]]
        MatrixDimensionError = ValueError("Invalid entered matrix : Matrix dimension must be = number of roads incoming")
        if len(flux_mat) != len(roads_list):
            raise MatrixDimensionError
        else:
            for element in flux_mat:
                if len(element) != len(roads_list):
                    raise MatrixDimensionError

        self.flux_mat = flux_mat

        # Same verification for duration_light_mat
        if len(duration_light_mat) != len(roads_list):
            raise MatrixDimensionError
        else:
            for element in duration_light_mat:
                if len(element) != len(roads_list):
                    raise MatrixDimensionError

        self.duration_light_mat = duration_light_mat
