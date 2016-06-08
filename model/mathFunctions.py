'''
Created on 8 june 2016

@author Lasse
'''

from math import cos, radians, sin


def rotate_coordinate(x_coord, y_coord, rotation, return_coord):
    if return_coord == 'x':
        return x_coord * cos(radians(rotation)) - y_coord * sin(radians(rotation))
    elif return_coord == 'y':
        return x_coord * sin(radians(rotation)) + y_coord * cos(radians(rotation))
