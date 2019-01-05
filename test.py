"""Ceci est un test de synchronisation"""
"""Ce fichier regroupe les classes nécessaires pour notre graphe"""

alphabet = "abcdefghijklmnopqrstuvwxyz"

class Road:
    """Class creating a road between two vertices / crosses"""

    def __init__(self,name,s1,s2):
        """Road linking two crosses s1 and s2"""

        self.name = name
        self.distance = distance(s1,s2)


class Cross:
    """Class creating a cross of different roads

    Objet name should be : bor006 or tal152"""

    def __init__(self, name, roads_list, flux_mat, duration_light_mat):
        """Cross of different roads defined by:
        - List of roads in/outcoming
        - Matrix of flux (number /time unit , origin/destination)(where and how many cars from road 1 are going to road 2,3 ...)
        - Matrix of duration of each traffic light"""


        # We verify the cross name is as wanted 'abc123'
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

        self.name = name

        # We verify flux_mat is like the wanted form
        #Example of matrix: cross with 3 crosses : [[a1,b1,c1],[a2,b2,c2],[a3,b3,c3]]

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
