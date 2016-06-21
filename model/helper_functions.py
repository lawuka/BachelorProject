'''

Created on 8 june 2015

@author Lasse

'''
from model.math_functions import rotate_x_y_coordinates, rotate_coordinate


# Rotate valve coordinates, done for each component on a biochip.
# If no valves exist in a component, return None.
def rotate_valve_coords(valve_list, component_x_list, component_y_list,
                        component_rotation_list, component_width_list, component_height_list):

    if valve_list is None:
        return None
    else:
        new_valve_list = []

        for valve in valve_list:
            valve_center_x = float(valve.find('X').text)
            valve_center_y = float(valve.find('Y').text)

            new_coordinates = rotate_x_y_coordinates(valve_center_x, valve_center_y,
                                                     component_x_list, component_y_list,
                                                     component_width_list, component_height_list,
                                                     component_rotation_list)

            new_valve_list.append([new_coordinates[0], new_coordinates[1]])

        return new_valve_list


# Rotated x coordinate list, used by valves in the control layer to know each x position
# needed by the G-code
def get_rotated_x_list(x, y, x_list, y_list, valve_rot):

    rotated_x_list = [rotate_coordinate(x_list[0] - x, y_list[0] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[0] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[5] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[0] - x, y_list[5] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[0] - x, y_list[1] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[1] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[4] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[0] - x, y_list[4] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[0] - x, y_list[2] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[2] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[2] - x, y_list[3] - y, valve_rot, 'x') + x,
                      rotate_coordinate(x_list[0] - x, y_list[3] - y, valve_rot, 'x') + x]
    return rotated_x_list


# Rotated y coordinate list, used by valves in the control layer to know each y position
# needed by the G-code
def get_rotated_y_list(x, y, x_list, y_list, valve_rot):

    rotated_y_list = [rotate_coordinate(x_list[0] - x, y_list[0] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[0] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[5] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[0] - x, y_list[5] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[0] - x, y_list[1] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[1] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[4] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[0] - x, y_list[4] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[0] - x, y_list[2] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[2] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[2] - x, y_list[3] - y, valve_rot, 'y') + y,
                      rotate_coordinate(x_list[0] - x, y_list[3] - y, valve_rot, 'y') + y]
    return rotated_y_list
