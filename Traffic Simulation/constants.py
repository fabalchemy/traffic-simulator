# Exceptions
NotRoadError = TypeError("Input road is not Road type")
NotVehicleError = TypeError("Input vehicle is not Vehicle type")
NotCrossError = TypeError("Input cross is not Cross type")
NotLinkedRoad = ValueError("Input road is not linked to this cross")
NotLinkedCross = ValueError("Input cross is not linked to this road")
TooManyRoads = ValueError("Crosses cannot be linked with more than 4 roads")
WrongAxisFormat = TypeError("axis must be a tuple of 2 roads or None")
