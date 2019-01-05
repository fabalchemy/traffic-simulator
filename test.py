"""Ceci est un test de synchronisation"""
"""Ce fichier regroupe les classes nécessaires pour notre graphe"""

class Road:
    """Class creating a road between two vertices / crosses"""

    def __init__(self,name,s1,s2):
        """Road linking two crosses s1 and s2"""

        self.name = name
        self.distance = distance(s1,s2)


class Cross:
    """Class creating a cross of different roads

    Objet name should be : bor006 or tal152"""

    def __init__(self, roads_list, flux_mat, duration_light_mat):
        """Cross of different roads defined by:
        - List of roads in/outcoming
        - Matrix of flux (number /time unit , origin/destination)(where and how many cars from road 1 are going to road 2,3 ...)
        - Matrix of duration of each traffic light"""

        # We verify the cross name is as wanted 'abc123'
        if len(self.name) != 6:
            raise NameError("Object name must have 'abc123' form")
        for i in range(6):
            if i // 3 == 0:
                if self.name[i] not in alphabet:
                    raise NameError("Object name must have 'abc123' form")
            else:
                try:
                    val = int(self.name[i])
                except ValueError:
                    raise NameError("Object name must have 'abc123' form")
