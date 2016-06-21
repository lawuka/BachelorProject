'''
Created on 8 june 2016

@author Lasse
'''

from math import cos, radians, sin


# Cosinus to a specific degree
def cos_ra(argument):

    return cos(radians(argument))


# Sinus to a specific degree
def sin_ra(argument):

    return sin(radians(argument))


# Rotate a x or y coordinate according to the degree.
def rotate_coordinate(x_coord, y_coord, rotation, return_coord):
    if return_coord == 'x':
        return x_coord * cos_ra(rotation) - y_coord * sin_ra(rotation)
    elif return_coord == 'y':
        return x_coord * sin_ra(rotation) + y_coord * cos_ra(rotation)


# Rotate x and y coordinates through each parent component, so that the rotation
# is done correctly. Also returns the total rotation done.
def rotate_x_y_coordinates(x, y, component_x_list, component_y_list,
                           component_width_list, component_height_list,
                           component_rotation_list):

    total_rotation = 0

    for i in range(len(component_x_list) - 1, -1, -1):
        if component_rotation_list[i] != 0.0:
            temp_valve_center_x = rotate_coordinate(x - component_width_list[i] / 2,
                                                    y - component_height_list[i] / 2,
                                                    component_rotation_list[i],
                                                    'x')
            temp_valve_center_y = rotate_coordinate(x - component_width_list[i] / 2,
                                                    y - component_height_list[i] / 2,
                                                    component_rotation_list[i],
                                                    'y')
            x = temp_valve_center_x + component_x_list[i] + component_width_list[i] / 2
            y = temp_valve_center_y + component_y_list[i] + component_height_list[i] / 2
        else:
            x += component_x_list[i]
            y += component_y_list[i]

        total_rotation += component_rotation_list[i]

    return [x, y, total_rotation]
