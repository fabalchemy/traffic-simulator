from math import acos, sqrt
import random
from constants import *

def angle(x,y):
    """Give the oriented angle [-3.14 ; +3.14] between the vector (x,y) and the horizontal axis (1,0)"""
    # The y-axis is "reversed" in Tkinter !
    # We use vector product to find the orientation of the vectors
    sign = 1 if y >= 0 else -1
    # We use scalar product to find the angle and multiply it by the orientation
    return acos((x) / sqrt(x*x + y*y)) * sign


def random_color():
    """Get a random color"""
    r = lambda: random.randint(50,255)
    return "#{:02x}{:02x}{:02x}".format(r(), r(), r())

def hex_to_RGB(hex):
  ''' "#FFFFFF" -> [255,255,255] '''
  # Pass 16 to the integer function for change of base
  return [int(hex[i:i+2], 16) for i in range(1,6,2)]

def RGB_to_hex(RGB):
  ''' [255,255,255] -> "#FFFFFF" '''
  # Components need to be integers for hex to make sense
  RGB = [int(x) for x in RGB]
  return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])

def get_color_from_gradient(value, gradient = GRADIENT_1):
    for i in range(1, len(gradient)):
        if value <= gradient[i][0]:
            color1 = hex_to_RGB(gradient[i-1][1])
            color2 = hex_to_RGB(gradient[i][1])
            factor = (value-gradient[i-1][0])/(gradient[i][0]-gradient[i-1][0])
            color = [int((1-factor)*color1[i] + factor*color2[i]) for i in [0, 1, 2]]
            return RGB_to_hex(color)
