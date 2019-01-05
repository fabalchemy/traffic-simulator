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

    Objetc name should be : bor006 or tal152"""

    def __init__(self):
        """Cross of different roads
        """
