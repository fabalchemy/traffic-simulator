# Exceptions
NotRoadError = TypeError("Input road is not Road type")
NotVehicleError = TypeError("Input vehicle is not Vehicle type")
NotCrossError = TypeError("Input cross is not Cross type")
NotLinkedRoad = ValueError("Input road is not linked to this cross")
NotLinkedCross = ValueError("Input cross is not linked to this road")
TooManyRoads = ValueError("Crosses cannot be linked with more than 4 roads")
WrongAxisFormat = TypeError("axis must be a tuple of 2 roads or None")

GRADIENT = [[0, "#ed1c24"], [0.7, "#f7931e"], [1, "#3d923b"]]
GRADIENT_1 = [[0, "#9e1313"], [0.3, "#e60000"], [0.6, "#f07d02"], [1, "#84ca50"]]

# BACKGROUND_COLOR = "#f7f7f7"
BACKGROUND_COLOR = "#e5e5e5"
ROAD_COLOR = "#ffffff"
ROAD_OUTLINE_COLOR = "#ffffff"

# CONSTANTS
PRIORITY_GAP = {"car" : 1.5, "truck": 3, "stop":0}
TIME_TO_CROSS = {"right": {"car": 0.5, "truck":2, "stop":0}, "other":{"car": 3, "truck":4, "stop":0}}
RAND_GAP = 5 # Bigger this constant is, more random is the generation of vehicles
