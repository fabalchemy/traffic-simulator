from math import acos, sqrt

def angle(x,y):
    """Give the oriented angle [-3.14 ; +3.14] between the vector (x,y) and the horizontal axis (1,0)"""
    # The y-axis is "reversed" in Tkinter !
    # We use vector product to find the orientation of the vectors
    sign = 1 if y >= 0 else -1
    # We use scalar product to find the angle and multiply it by the orientation
    return acos((x) / sqrt(x*x + y*y)) * sign
