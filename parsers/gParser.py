'''
Created on 2 march 2015

@author Lasse
'''
from math import ceil, cos, pi, sin, radians
from model.mathFunctions import rotate_x_y_coordinates, cos_ra, sin_ra
from model.helperFunctions import rotate_valve_coords, get_rotated_x_list, get_rotated_y_list


class SimulatorGCode:

    def __init__(self):

        self.svg_map = None
        self.library = None
        self.conf = None
        self.simulate_g_code_list = None

        self.new_line = "\n"
        self.drill_top = "10"
        self.drill_low = "1"
        self.drill_hole_top = "10"
        self.drill_hole_low = "-3"

    def create_simulator_g_code_list(self, svg_map, library, conf):

        self.svg_map = svg_map
        self.library = library
        self.conf = conf
        self.simulate_g_code_list = []

        # GCode options
        self.g_code_options()

        # Starting position
        self.starter_position()

        # Flow channels tool
        self.flow_channel_tool()

        # Flow channels
        self.flow_channels()

        # Hole tool
        self.hole_tool()

        # Holes
        self.holes()

        # Ending position and finishing up
        self.move_back_to_origin()

        return self.simulate_g_code_list

    def g_code_options(self):

        # Machine options
        self.simulate_g_code_list.append("; Height: " + self.svg_map['height'])
        self.simulate_g_code_list.append("; Width: " + self.svg_map['width'])
        self.simulate_g_code_list.append("G21")
        self.simulate_g_code_list.append("G90")
        self.simulate_g_code_list.append("F250")
        self.simulate_g_code_list.append("S2000")

    def starter_position(self):

        line = "G00 X0 Y0 Z10"
        self.simulate_g_code_list.append(line)
        line = "X10 Y10 Z10"
        self.simulate_g_code_list.append(line)

    def flow_channel_tool(self):

        self.simulate_g_code_list.append("T1 M6")

    def hole_tool(self):

        self.simulate_g_code_list.append("T2 M6")

    def flow_channels(self):

        # Lines with fixed x-axis
        # xAxisLines = []
        # Lines with fixed y-axis
        y_axis_lines = []
        '''
        Remember to add 10mm to all measures. This is only for the simulator.
        '''
        for line in self.svg_map['lines']:
            if line[0] == line[2]:
                line1 = "G1 X" + str(int(line[0])/10 + 10) + " Y" + str(int(line[1])/10 + 10) + " Z" + \
                        self.drill_top + self.new_line
                line2 = "Z" + self.drill_low + self.new_line
                line3 = "Y" + str(int(line[3])/10 + 10) + self.new_line
                line4 = "Z" + self.drill_top
                self.simulate_g_code_list.append(line1 + line2 + line3 + line4)
            else:
                line1 = "G1 X" + str(int(line[0])/10 + 10) + " Y" + str(int(line[1])/10 + 10) + " Z" + \
                        self.drill_top + self.new_line
                line2 = "Z" + self.drill_low + self.new_line
                line3 = "X" + str(int(line[2])/10 + 10) + self.new_line
                line4 = "Z" + self.drill_top
                y_axis_lines.append(line1 + line2 + line3 + line4)

        for element in y_axis_lines:
            self.simulate_g_code_list.append(element)

    def holes(self):

        '''
        Remember to add 10.5mm to all measures. This is only for the simulator.
        '''
        for hole in self.svg_map['holes']:
            line1 = "G1 X" + str(int(hole[0])/10 + 10.5) + " Y" + str(int(hole[1])/10 + 10.5) + self.new_line
            line2 = "Z" + self.drill_hole_low + self.new_line
            line3 = "Z" + self.drill_hole_top
            self.simulate_g_code_list.append(line1 + line2 + line3)

    def move_back_to_origin(self):

        line = "G0 X0 Y0"
        self.simulate_g_code_list.append(line)
        self.simulate_g_code_list.append("G28")
        self.simulate_g_code_list.append("M30")

    def get_simulator_g_code(self):

        return self.simulate_g_code_list


class MicroMillingFlowGCode:

    def __init__(self):

        self.architecture_map = None
        self.library = None
        self.conf = None
        self.mm_g_code_list = None
        self.flow_hole_list = None
        self.scale = None

    def create_mm_g_code_list(self, architecture_map, library, conf):

        self.architecture_map = architecture_map
        self.library = library
        self.conf = conf
        self.mm_g_code_list = []
        self.flow_hole_list = []

        # Current config
        self.drill_flow_depth = self.conf['Flow_Layer_Options']['Flow_Depth']
        self.drill_hole_depth = self.conf['Flow_Layer_Options']['Hole_Depth']
        self.drill_flow_size = self.conf['Flow_Layer_Options']['Flow_Drill_Size']
        self.drill_hole_size = self.conf['Flow_Layer_Options']['Hole_Drill_Size']
        self.drill_top = self.conf['Flow_Layer_Options']['Drill_Z_Top']
        self.discontinuity_width = float(self.conf['Flow_Layer_Options']['Valve_Discontinuity_Width'])

        # Scale config
        self.scale = float(self.drill_flow_size)

        # Calculate number of drilling in one flow channel
        if ((float(self.drill_flow_depth) * -1.0) / (self.scale / 4.0)) <= 1.0:
            self.repeat = 1
        else:
            self.repeat = int(ceil((float(self.drill_flow_depth) * -1.0) / (self.scale / 4.0)))

        if len(self.architecture_map['lines']) != 0 or len(self.architecture_map['components']) != 0:

            self.g_code_options()

            self.components()

            self.flow_channels()

            self.flow_holes()

            self.move_back_to_origin()

        else:
            self.mm_g_code_list.append('(No Components or Lines in Biochip Architecture!)')

        return self.mm_g_code_list

    def g_code_options(self):

        '''
        Parenthese in GCode is comments
        '''
        self.mm_g_code_list.append("(PROGRAM START)")
        '''
        Drill used for flow channels
        '''
        self.mm_g_code_list.append("(" + self.drill_flow_size + "MM FLOW DRILL)")
        '''
        M00 is break in Gcode, and machine pauses (Drill change or similar)
        '''
        self.mm_g_code_list.append("M00")
        '''
        With a spindle controller, the spindle speed is ignored.
        self.mmGCodeList.append("S2000")
        '''
        '''
        Feed rate - how fast drill moves in X,Y or Z direction
        '''
        self.mm_g_code_list.append("F250")

    def components(self):

        if self.architecture_map['components']:
            # Start going through each component in 'components'
            for component in self.architecture_map['components']:
                if component[0] in self.library:
                    component_x = float(component[1]) * self.scale
                    component_y = float(component[2]) * self.scale
                    component_width = float(self.library[component[0]]['Size'].find('Width').text) * self.scale
                    component_height = float(self.library[component[0]]['Size'].find('Height').text) * self.scale
                    component_actual_position_x = component_x - component_width/2
                    component_actual_position_y = component_y - component_height/2

                    for i_component in self.library[component[0]]['Internal']:
                        if i_component.tag == 'FlowLine':
                            self.internal_flow_channel(i_component,
                                                       [component_actual_position_x],
                                                       [component_actual_position_y],
                                                       [component[3] % 360],
                                                       [component_width],
                                                       [component_height],
                                                       rotate_valve_coords(self.library[component[0]]['Control'],
                                                                           [component_actual_position_x],
                                                                           [component_actual_position_y],
                                                                           [component[3] % 360.0],
                                                                           [component_width],
                                                                           [component_height]))
                        elif i_component.tag == 'FlowCircle':
                            self.internal_flow_circle(i_component,
                                                      [component_actual_position_x],
                                                      [component_actual_position_y],
                                                      [component[3] % 360],
                                                      [component_width],
                                                      [component_height])
                        elif i_component.tag == "FlowHole":
                            self.internal_flow_hole(i_component,
                                                    [component_actual_position_x],
                                                    [component_actual_position_y],
                                                    [component[3] % 360],
                                                    [component_width],
                                                    [component_height])
                        else:
                            self.internal_component(i_component,
                                                    [component_actual_position_x],
                                                    [component_actual_position_y],
                                                    [component[3] % 360],
                                                    [component_width],
                                                    [component_height])
                else:
                    print("Component \"" + component[0] + "\" not found in library - skipping!")

    def flow_channels(self):

        if self.architecture_map['lines']:
            # Start going through each line in 'lines'
            for line in self.architecture_map['lines']:
                self.flow_channel_g_code(float(line[0]) * self.scale,
                                         float(line[1]) * self.scale,
                                         float(line[2]) * self.scale,
                                         float(line[3]) * self.scale)

    def flow_holes(self):

        '''
        Pausing the drilling, since drill for drilling all the way through is different than flow channels
        '''

        if len(self.flow_hole_list) != 0:
            self.mm_g_code_list.append("(PAUSE FOR DRILL CHANGE)")
            self.mm_g_code_list.append("(" + self.drill_hole_size + "MM HOLE DRILL)")
            self.mm_g_code_list.append("(*************************************************)")
            self.mm_g_code_list.append("(*                                               *)")
            self.mm_g_code_list.append("(* REMEMBER PLATE UNDER FOR PENETRATION DRILLING *)")
            self.mm_g_code_list.append("(*                                               *)")
            self.mm_g_code_list.append("(*************************************************)")
            self.mm_g_code_list.append("M00")

            for flowHole in self.flow_hole_list:
                self.flow_hole_g_code(flowHole[0], flowHole[1])

    def move_back_to_origin(self):

        self.mm_g_code_list.append("G00 X0.0 Y0.0")
        self.mm_g_code_list.append("M30")
        self.mm_g_code_list.append("(PROGRAM END)")

    def internal_component(self, component, component_x_list, component_y_list,
                           component_rotation_list, component_width_list, component_height_list):
        if component.tag in self.library:
            component_x = float(component.find('X').text) * self.scale
            component_y = float(component.find('Y').text) * self.scale
            component_width = float(self.library[component.tag]['Size'].find('Width').text) * self.scale
            component_height = float(self.library[component.tag]['Size'].find('Height').text) * self.scale
            component_x_list.append(component_x - component_width / 2)
            component_y_list.append(component_y - component_height / 2)
            component_rotation_list.append(float(component.find('Rotation').text) % 360.0)
            component_width_list.append(component_width)
            component_height_list.append(component_height)

            for i_component in self.library[component.tag]['Internal']:
                if i_component.tag == 'FlowLine':
                    self.internal_flow_channel(i_component,
                                               component_x_list,
                                               component_y_list,
                                               component_rotation_list,
                                               component_width_list,
                                               component_height_list,
                                               rotate_valve_coords(self.library[component.tag]['Control'],
                                                                   component_x_list, component_y_list,
                                                                   component_rotation_list, component_width_list,
                                                                   component_height_list))
                elif i_component.tag == 'FlowCircle':
                    self.internal_flow_circle(i_component,
                                              component_x_list,
                                              component_y_list,
                                              component_rotation_list,
                                              component_width_list,
                                              component_height_list)
                elif i_component.tag == 'FlowHole':
                    self.internal_flow_hole(i_component,
                                            component_x_list,
                                            component_y_list,
                                            component_rotation_list,
                                            component_width_list,
                                            component_height_list)
                else:
                    self.internal_component(i_component,
                                            component_x_list,
                                            component_y_list,
                                            component_rotation_list,
                                            component_width_list,
                                            component_height_list)
                    component_x_list.pop()
                    component_y_list.pop()
                    component_rotation_list.pop()
                    component_width_list.pop()
                    component_height_list.pop()
        else:
            print("Component \"" + component.tag + "\" not found in library - skipping!")

    def internal_flow_channel(self, flow_channel, component_x_list, component_y_list, component_rotation_list,
                              component_width_list, component_height_list, control_valves):
        flow_start_x = float(flow_channel.find('Start').find('X').text) * self.scale
        flow_start_y = float(flow_channel.find('Start').find('Y').text) * self.scale
        flow_end_x = float(flow_channel.find('End').find('X').text) * self.scale
        flow_end_y = float(flow_channel.find('End').find('Y').text) * self.scale

        new_start_coordinates = rotate_x_y_coordinates(flow_start_x, flow_start_y,
                                                       component_x_list, component_y_list,
                                                       component_width_list, component_height_list,
                                                       component_rotation_list)

        new_end_coordinates = rotate_x_y_coordinates(flow_end_x, flow_end_y,
                                                     component_x_list, component_y_list,
                                                     component_width_list, component_height_list,
                                                     component_rotation_list)

        if control_valves is not None:
            current_y = new_start_coordinates[1]
            current_x = new_start_coordinates[0]
            if new_start_coordinates[1] == new_end_coordinates[1]:
                if new_start_coordinates[0] < new_end_coordinates[0]:
                    sorted_valves = sorted(control_valves, key=lambda elem: elem[0])
                else:
                    sorted_valves = sorted(control_valves, key=lambda elem: -elem[0])

                for valve in sorted_valves:
                    x = valve[0]
                    y = valve[1]
                    if new_start_coordinates[1] == y and ((new_start_coordinates[0] < x < new_end_coordinates[0]) or
                                                          (new_start_coordinates[0] > x > new_end_coordinates[0])):
                        if new_start_coordinates[0] < new_end_coordinates[0]:
                            next_x = x - self.discontinuity_width / 2
                        else:
                            next_x = x + self.discontinuity_width / 2
                        self.flow_channel_g_code(current_x,
                                                 new_start_coordinates[1],
                                                 next_x,
                                                 new_end_coordinates[1])
                        if new_start_coordinates[0] < new_end_coordinates[0]:
                            current_x = x + self.discontinuity_width / 2
                        else:
                            current_x = x - self.discontinuity_width / 2
                self.flow_channel_g_code(current_x,
                                         new_start_coordinates[1],
                                         new_end_coordinates[0],
                                         new_end_coordinates[1])
            else:
                if new_start_coordinates[1] < new_end_coordinates[1]:
                    sorted_valves = sorted(control_valves, key=lambda elem: elem[1])
                else:
                    sorted_valves = sorted(control_valves, key=lambda elem: -elem[1])

                for valve in sorted_valves:
                    x = valve[0]
                    y = valve[1]
                    if new_start_coordinates[0] == x and ((new_start_coordinates[1] < y < new_end_coordinates[1]) or
                                                          (new_start_coordinates[1] > y > new_end_coordinates[1])):
                        if new_start_coordinates[1] < new_end_coordinates[1]:
                            next_y = y - self.discontinuity_width / 2
                        else:
                            next_y = y + self.discontinuity_width / 2
                        self.flow_channel_g_code(new_start_coordinates[0],
                                                 current_y,
                                                 new_end_coordinates[0],
                                                 next_y)
                        if new_start_coordinates[1] < new_end_coordinates[1]:
                            current_y = y + self.discontinuity_width / 2
                        else:
                            current_y = y - self.discontinuity_width / 2

                self.flow_channel_g_code(new_start_coordinates[0],
                                         current_y,
                                         new_end_coordinates[0],
                                         new_end_coordinates[1])
        else:
            self.flow_channel_g_code(new_start_coordinates[0],
                                     new_start_coordinates[1],
                                     new_end_coordinates[0],
                                     new_end_coordinates[1])

    def internal_flow_circle(self, flow_circle, component_x_list, component_y_list, component_rotation_list,
                             component_width_list, component_height_list):
        flow_circle_center_x = float(flow_circle.find('Center').find('X').text) * self.scale
        flow_circle_center_y = float(flow_circle.find('Center').find('Y').text) * self.scale

        new_coordinates = rotate_x_y_coordinates(flow_circle_center_x, flow_circle_center_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        flow_circle_radius = float(flow_circle.find('Radius').text) * self.scale

        flow_circle_start_x = flow_circle_center_x
        flow_circle_start_y = flow_circle_center_y

        angle_list = [float(angle.text) for angle in
                      sorted(list(flow_circle.find('Valves')), key=lambda elem: float(elem.text) % 360.0)]

        valve_length_angle = (360 * float(self.discontinuity_width)) / (2 * flow_circle_radius * pi)

        if len(angle_list) == 0:
            self.complete_circle_g_code(str(flow_circle_start_x + flow_circle_radius),
                                        str(flow_circle_start_y),
                                        flow_circle_radius)
        elif len(angle_list) == 1:
            self.one_angle_circle_g_code(flow_circle_center_x,
                                         flow_circle_center_y,
                                         flow_circle_radius,
                                         str(flow_circle_start_x + flow_circle_radius), str(flow_circle_start_y),
                                         valve_length_angle / 2, (angle_list[0]+new_coordinates[2]) % 360.0)
        else:
            if new_coordinates[2] % 360 == 90:
                flow_circle_start_y += flow_circle_radius
            elif new_coordinates[2] % 360 == 180:
                flow_circle_start_x -= flow_circle_radius
            elif new_coordinates[2] % 360 == 270:
                flow_circle_start_y -= flow_circle_radius
            else:
                flow_circle_start_x += flow_circle_radius

            for i in range(0, len(angle_list)):
                if i == 0:
                    if angle_list[i] != 0.0:
                        flow_end_x = str(cos_ra(angle_list[i]-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                         flow_circle_radius + flow_circle_center_x)
                        flow_end_y = str(sin_ra(angle_list[i]-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                         flow_circle_radius + flow_circle_center_y)
                        self.flow_circle_g_code(str(flow_circle_start_x),
                                                str(flow_circle_start_y),
                                                flow_end_x,
                                                flow_end_y,
                                                flow_circle_radius if angle_list[i] <= 180 else -flow_circle_radius)
                    else:
                        pass
                else:
                    flow_start_x = str(cos_ra(angle_list[i-1]+valve_length_angle/2+new_coordinates[2] % 360.0) *
                                       flow_circle_radius + flow_circle_center_x)
                    flow_start_y = str(sin_ra(angle_list[i-1]+valve_length_angle/2+new_coordinates[2] % 360.0) *
                                       flow_circle_radius + flow_circle_center_y)
                    flow_end_x = str(cos_ra(angle_list[i]-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                     flow_circle_radius + flow_circle_center_x)
                    flow_end_y = str(sin_ra(angle_list[i]-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                     flow_circle_radius + flow_circle_center_y)
                    self.flow_circle_g_code(flow_start_x, flow_start_y, flow_end_x, flow_end_y,
                                            flow_circle_radius if angle_list[i] - angle_list[i-1] <= 180
                                            else -flow_circle_radius)

                    if i == len(angle_list)-1:
                        flow_start_x = str(cos_ra(angle_list[i]+valve_length_angle/2+new_coordinates[2] % 360.0) *
                                           flow_circle_radius + flow_circle_center_x)
                        flow_start_y = str(sin_ra(angle_list[i]+valve_length_angle/2+new_coordinates[2] % 360.0) *
                                           flow_circle_radius + flow_circle_center_y)
                        if angle_list[0] != 0.0:
                            self.flow_circle_g_code(flow_start_x, flow_start_y,
                                                    str(flow_circle_start_x),
                                                    str(flow_circle_start_y),
                                                    flow_circle_radius if (360.0 - angle_list[i]) <= 180
                                                    else -flow_circle_radius)
                        else:
                            flow_end_x = str(cos_ra(0-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                             flow_circle_radius + flow_circle_center_x)
                            flow_end_y = str(sin_ra(0-valve_length_angle/2+new_coordinates[2] % 360.0) *
                                             flow_circle_radius + flow_circle_center_y)
                            self.flow_circle_g_code(flow_start_x, flow_start_y, flow_end_x, flow_end_y,
                                                    flow_circle_radius if (360.0 - angle_list[i]) <= 180
                                                    else -flow_circle_radius)

    def internal_flow_hole(self, flow_hole, component_x_list, component_y_list, component_rotation_list,
                           component_width_list, component_height_list):

        flow_hole_center_x = float(flow_hole.find('Center').find('X').text)
        flow_hole_center_y = float(flow_hole.find('Center').find('Y').text)

        new_coordinates = rotate_x_y_coordinates(flow_hole_center_x, flow_hole_center_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        self.flow_hole_list.append([new_coordinates[0], new_coordinates[1]])

    def complete_circle_g_code(self, start_x, start_y, flow_circle_radius):

        current_drill_level = 0.0

        self.mm_g_code_list.append("G00 X" + start_x + " Y" + start_y + " Z" + self.drill_top)

        for i in range(0, self.repeat):
            current_drill_level -= (self.scale / 4.0)
            if current_drill_level < float(self.drill_flow_depth):
                current_drill_level = float(self.drill_flow_depth)
            self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
            if i % 2 == 0:
                self.mm_g_code_list.append("G03 I-" + str(flow_circle_radius))
            else:
                self.mm_g_code_list.append("G02 I-" + str(flow_circle_radius))
        self.mm_g_code_list.append("G01 Z" + self.drill_top)

    def one_angle_circle_g_code(self, flow_circle_center_x,
                                flow_circle_center_y,
                                flow_circle_radius,
                                flow_circle_start_x,
                                flow_circle_start_y,
                                valve_length_angle,
                                angle):

        if angle != 0:
            flow_end_x = str(cos_ra(angle - valve_length_angle) * flow_circle_radius + flow_circle_center_x)
            flow_end_y = str(sin_ra(angle - valve_length_angle) * flow_circle_radius + flow_circle_center_y)
            self.flow_circle_g_code(flow_circle_start_x, flow_circle_start_y, flow_end_x, flow_end_y,
                                    flow_circle_radius if angle <= 180.0 else -flow_circle_radius)
            flow_start_x = str(cos_ra(angle + valve_length_angle) * flow_circle_radius + flow_circle_center_x)
            flow_start_y = str(sin_ra(angle + valve_length_angle) * flow_circle_radius + flow_circle_center_y)
            self.flow_circle_g_code(flow_start_x, flow_start_y, flow_circle_start_x, flow_circle_start_y,
                                    -flow_circle_radius if angle <= 180.0 else flow_circle_radius)
        else:
            flow_start_x = str(cos_ra(valve_length_angle) * flow_circle_radius + flow_circle_center_x)
            flow_start_y = str(sin_ra(valve_length_angle) * flow_circle_radius + flow_circle_center_y)
            flow_end_x = str(cos_ra(360 - valve_length_angle) * flow_circle_radius + flow_circle_center_x)
            flow_end_y = str(sin_ra(360 - valve_length_angle) * flow_circle_radius + flow_circle_center_y)
            self.flow_circle_g_code(flow_start_x, flow_start_y, flow_end_x, flow_end_y, -flow_circle_radius)

    def flow_channel_g_code(self, flow_start_x, flow_start_y, flow_end_x, flow_end_y):

        current_drill_level = 0.0
        if flow_start_x == flow_end_x:
            self.mm_g_code_list.append("G00 X" + str(flow_start_x) + " Y" + str(flow_start_y) + " Z" + self.drill_top)
            for i in range(0, self.repeat):
                current_drill_level -= self.scale / 4.0
                if current_drill_level < float(self.drill_flow_depth):
                    current_drill_level = float(self.drill_flow_depth)
                self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
                if i % 2 == 0:
                    self.mm_g_code_list.append("Y" + str(flow_end_y))
                else:
                    self.mm_g_code_list.append("Y" + str(flow_start_y))
            self.mm_g_code_list.append("Z" + self.drill_top)
        else:
            self.mm_g_code_list.append("G00 X" + str(flow_start_x) + " Y" + str(flow_start_y) + " Z" + self.drill_top)
            for i in range(0, self.repeat):
                current_drill_level -= self.scale / 4.0
                if current_drill_level < float(self.drill_flow_depth):
                    current_drill_level = float(self.drill_flow_depth)
                self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
                if i % 2 == 0:
                    self.mm_g_code_list.append("X" + str(flow_end_x))
                else:
                    self.mm_g_code_list.append("X" + str(flow_start_x))
            self.mm_g_code_list.append("Z" + self.drill_top)

    def flow_circle_g_code(self, flow_start_x, flow_start_y, flow_end_x, flow_end_y, flow_circle_radius):

        current_drill_level = 0.0

        self.mm_g_code_list.append("G00 X" + flow_start_x + " Y" + flow_start_y + " Z" + self.drill_top)

        for i in range(0, self.repeat):
            current_drill_level -= (self.scale / 4.0)
            if current_drill_level < float(self.drill_flow_depth):
                current_drill_level = float(self.drill_flow_depth)
            self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
            if i % 2 == 0:
                self.mm_g_code_list.append("G03 X" + flow_end_x + " Y" + flow_end_y + " R" +
                                           str(flow_circle_radius))
            else:
                self.mm_g_code_list.append("G02 X" + flow_start_x + " Y" + flow_start_y + " R" +
                                           str(flow_circle_radius))
        self.mm_g_code_list.append("G01 Z" + self.drill_top)

    def flow_hole_g_code(self, flow_hole_center_x, flow_hole_center_y):

        self.mm_g_code_list.append("G00 X" + str(flow_hole_center_x) +
                                   " Y" + str(flow_hole_center_y))
        self.mm_g_code_list.append("G01 Z" + self.drill_hole_depth)
        self.mm_g_code_list.append("Z" + self.drill_top)


class MicroMillingControlGCode:

    def __init__(self):

        self.svg_map = None
        self.library = None
        self.conf = None
        self.mm_g_code_list = None
        self.control_map = None
        self.scale = None

    def create_mm_g_code_list(self, svg_map, library, conf):

        self.svg_map = svg_map
        self.library = library
        self.conf = conf
        self.mm_g_code_list = []
        self.control_map = []

        # Current config
        self.drill_valve_subsidence_depth = self.conf['Control_Layer_Options']['Subsidence_Depth']
        self.drill_valve_hole_depth = self.conf['Control_Layer_Options']['Hole_Depth']
        self.drill_subsidence_size = self.conf['Control_Layer_Options']['Subsidence_Drill_Size']
        self.drill_hole_size = self.conf['Control_Layer_Options']['Hole_Drill_Size']
        self.drill_top = self.conf['Control_Layer_Options']['Drill_Z_Top']
        self.valve_width = '9'
        self.valve_height = '6'

        # Calculate number of drilling in one flow channel
        if ((float(self.drill_valve_subsidence_depth) * -1.0) / (float(self.drill_subsidence_size) / 4.0)) <= 1.0:
            self.repeat = 1
        else:
            self.repeat = int(ceil((float(self.drill_valve_subsidence_depth) * -1.0) /
                                   (float(self.drill_subsidence_size) / 4.0)))

        # Scale for scaling according to drillsize
        self.scale = float(self.drill_subsidence_size)

        # Use chip size, to modify control layer so it fits correctly on top
        self.svg_map_width = float(self.svg_map['width']) * self.scale
        self.svg_map_height = float(self.svg_map['height']) * self.scale

        # Create GCode List
        if len(self.svg_map['lines']) != 0 or len(self.svg_map['components']) != 0:

            self.fetch_valves()

            if len(self.control_map) != 0:
                self.g_code_options()

                self.valves()

                self.valve_holes_g_code()

                self.move_back_to_origin()
            else:
                self.mm_g_code_list.append('(No Valves in Biochip Architecture!')
        else:
            self.mm_g_code_list.append('(No Components or Lines in Biochip Architecture!)')

        return self.mm_g_code_list

    def g_code_options(self):

        '''
        Parenthese in GCode is comments
        '''
        self.mm_g_code_list.append("(PROGRAM START)")
        '''
        Drill used for flow channels
        '''
        self.mm_g_code_list.append("(" + self.drill_subsidence_size + "MM SUBSIDENCE DRILL)")
        '''
        M00 is break in Gcode, and machine pauses (Drill change or similar)
        '''
        self.mm_g_code_list.append("M00")
        '''
        With a spindle controller, the spindle speed is ignored.
        self.mmGCodeList.append("S2000")
        '''
        '''
        Feed rate - how fast drill moves in X,Y or Z direction
        '''
        self.mm_g_code_list.append("F250")

    def fetch_valves(self):

        if self.svg_map['components']:
            # Start going through each component in 'components'
            for component in self.svg_map['components']:
                if component[0] in self.library:
                    component_x = float(component[1]) * self.scale
                    component_y = float(component[2]) * self.scale
                    component_width = float(self.library[component[0]]['Size'].find('Width').text) * self.scale
                    component_height = float(self.library[component[0]]['Size'].find('Height').text) * self.scale
                    component_actual_position_x = component_x - component_width/2
                    component_actual_position_y = component_y - component_height/2

                    control_valves = self.library[component[0]]['Control']
                    if control_valves is not None and len(control_valves) != 0:
                        self.append_control_valves(control_valves,
                                                   [component_actual_position_x],
                                                   [component_actual_position_y],
                                                   [component[3] % 360],
                                                   [component_width],
                                                   [component_height])

                    for i_component in self.library[component[0]]['Internal']:
                        if i_component.tag in {'FlowLine', 'FlowHole'}:
                            pass
                        elif i_component.tag == 'FlowCircle':
                            self.internal_flow_circle(i_component,
                                                      [component_actual_position_x],
                                                      [component_actual_position_y],
                                                      [component[3] % 360],
                                                      [component_width],
                                                      [component_height])
                        else:
                            self.internal_component(i_component,
                                                    [component_actual_position_x],
                                                    [component_actual_position_y],
                                                    [component[3] % 360],
                                                    [component_width],
                                                    [component_height])
                else:
                    print("Component \"" + component[0] + "\" not found in library - skipping!")

    def move_back_to_origin(self):

        self.mm_g_code_list.append("G00 X0.0 Y0.0")
        self.mm_g_code_list.append("M30")
        self.mm_g_code_list.append("(PROGRAM END)")

    def internal_component(self, component, component_x_list, component_y_list,
                           component_rotation_list, component_width_list, component_height_list):
        if component.tag in self.library:
            component_x = float(component.find('X').text) * self.scale
            component_y = float(component.find('Y').text) * self.scale
            component_width = float(self.library[component.tag]['Size'].find('Width').text) * self.scale
            component_height = float(self.library[component.tag]['Size'].find('Height').text) * self.scale
            component_x_list.append(component_x - component_width / 2)
            component_y_list.append(component_y - component_height / 2)
            component_rotation_list.append(float(component.find('Rotation').text) % 360.0)
            component_width_list.append(component_width)
            component_height_list.append(component_height)

            control_valves = self.library[component.tag]['Control']
            if control_valves is not None and len(control_valves) != 0:
                self.append_control_valves(control_valves, component_x_list, component_y_list,
                                           component_rotation_list, component_width_list, component_height_list)

            for i_component in self.library[component.tag]['Internal']:
                if i_component.tag in {'FlowLine', 'FlowHole'}:
                    pass
                elif i_component.tag == 'FlowCircle':
                    self.internal_flow_circle(i_component,
                                              component_x_list,
                                              component_y_list,
                                              component_rotation_list,
                                              component_width_list,
                                              component_height_list)
                else:
                    self.internal_component(i_component,
                                            component_x_list,
                                            component_y_list,
                                            component_rotation_list,
                                            component_width_list,
                                            component_height_list)
                    if len(component_x_list) != 0:
                        component_x_list.pop()
                        component_y_list.pop()
                        component_rotation_list.pop()
                        component_width_list.pop()
                        component_height_list.pop()
        else:
            print("Component \"" + component.tag + "\" not found in library - skipping!")

    def append_control_valves(self, valve_list, component_x_list, component_y_list,
                              component_rotation_list, component_width_list, component_height_list):

        for valve in valve_list:
            valve_center_x = float(valve.find('X').text) * self.scale
            valve_center_y = float(valve.find('Y').text) * self.scale
            valve_rotation = float(valve.find('Rotation').text)

            new_coordinates = rotate_x_y_coordinates(valve_center_x, valve_center_y,
                                                     component_x_list, component_y_list,
                                                     component_width_list, component_height_list,
                                                     component_rotation_list)

            xyxy = [self.svg_map_width - new_coordinates[0],
                    new_coordinates[1],
                    (valve_rotation - new_coordinates[2]) % 360.0,
                    None]

            self.control_map.append(xyxy)

    def internal_flow_circle(self, flow_circle, component_x_list, component_y_list, component_rotation_list,
                             component_width_list, component_height_list):
        flow_circle_center_x = float(flow_circle.find('Center').find('X').text) * self.scale
        flow_circle_center_y = float(flow_circle.find('Center').find('Y').text) * self.scale

        new_coordinates = rotate_x_y_coordinates(flow_circle_center_x, flow_circle_center_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        flow_circle_radius = float(flow_circle.find('Radius').text) * self.scale

        angle_list = sorted(list(flow_circle.find('Valves')), key=lambda elem: float(elem.text) % 360.0)

        for valve in angle_list:
            valve_degree = float(valve.text)
            valve_center_x = new_coordinates[0] + (cos(radians(valve_degree+new_coordinates[2] % 360.0)) *
                                                   flow_circle_radius)
            valve_center_y = new_coordinates[1] + (sin(radians(valve_degree+new_coordinates[2] % 360.0)) *
                                                   flow_circle_radius)

            xy = [self.svg_map_width - valve_center_x,
                  valve_center_y,
                  None,
                  (valve_degree-new_coordinates[2]) % 360.0]

            self.control_map.append(xy)

    def valves(self):
        valve_width = float(self.valve_width) * self.scale
        valve_height = float(self.valve_height) * self.scale
        valve_outer_r = float(2.5/6) * valve_height * self.scale
        valve_inner_r = float(1.5/6) * valve_height * self.scale

        for valve in self.control_map:

            x = valve[0]
            y = valve[1]
            valve_rot = valve[2]
            circle_rot = valve[3]

            x_left = x + (-1.5/9) * valve_width
            x_left_left = x + (-2.0/9) * valve_width
            x_right = x + (1.5/9) * valve_width
            x_right_right = x + (2.0/9) * valve_width

            y_top_top = y + (2.5/6) * valve_height
            y_top_middle = y + (1.5/6) * valve_height
            y_top_low = y + (0.5/6) * valve_height
            y_low_top = y + (-0.5/6) * valve_height
            y_low_middle = y + (-1.5/6) * valve_height
            y_low_low = y + (-2.5/6) * valve_height

            x_list = [x_left, x_left_left,
                      x_right, x_right_right]

            y_list = [y_top_top, y_top_middle,
                      y_top_low, y_low_top,
                      y_low_middle, y_low_low]

            if valve_rot is not None:
                if valve_rot in {90.0, 270.0}:
                    self.valve_g_code(get_rotated_x_list(x, y, x_list, y_list, valve_rot),
                                      get_rotated_y_list(x, y, x_list, y_list, valve_rot),
                                      90.0, valve_outer_r, valve_inner_r)

                else:
                    self.valve_g_code(x_list, y_list, None, 2.5, 1.5)
            else:
                if circle_rot in {90.0, 270.0}:
                    self.valve_g_code(x_list, y_list, None, 2.5, 1.5)

                elif circle_rot in {0.0, 180.0}:
                    self.valve_g_code(get_rotated_x_list(x, y, x_list, y_list, circle_rot + 90.0),
                                      get_rotated_y_list(x, y, x_list, y_list, circle_rot + 90.0),
                                      90.0, valve_outer_r, valve_inner_r)
                else:
                    self.valve_g_code(get_rotated_x_list(x, y, x_list, y_list, 90.0 - circle_rot),
                                      get_rotated_y_list(x, y, x_list, y_list, 90.0 - circle_rot),
                                      circle_rot, valve_outer_r, valve_inner_r)

    def valve_g_code(self, x_list, y_list, valve_rotate, valve_outer_r, valve_inner_r):

        current_drill_level = 0.0

        for i in range(0, self.repeat):
            current_drill_level -= self.scale / 4.0
            if current_drill_level < float(self.drill_valve_subsidence_depth):
                current_drill_level = float(self.drill_valve_subsidence_depth)

            if valve_rotate is None:
                self.mm_g_code_list.append("G00 X" + str(x_list[0]) +
                                           " Y" + str(y_list[0]) +
                                           " Z" + self.drill_top)
                self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
                self.mm_g_code_list.append("X" + str(x_list[2]) +
                                           " Y" + str(y_list[0]))
                self.mm_g_code_list.append("G02 X" + str(x_list[2]) +
                                           " Y" + str(y_list[5]) +
                                           " R" + str(valve_outer_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[0]) +
                                           " Y" + str(y_list[5]))
                self.mm_g_code_list.append("G02 X" + str(x_list[0]) +
                                           " Y" + str(y_list[0]) +
                                           " R" + str(valve_outer_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[0]) +
                                           " Y" + str(y_list[1]))
                self.mm_g_code_list.append("X" + str(x_list[2]) +
                                           " Y" + str(y_list[1]))
                self.mm_g_code_list.append("G02 X" + str(x_list[2]) +
                                           " Y" + str(y_list[4]) +
                                           " R" + str(valve_inner_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[0]) +
                                           " Y" + str(y_list[4]))

                self.mm_g_code_list.append("G02 X" + str(x_list[0]) +
                                           " Y" + str(y_list[1]) +
                                           " R" + str(valve_inner_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[0]) +
                                           " Y" + str(y_list[2]))
                self.mm_g_code_list.append("X" + str(x_list[2]) +
                                           " Y" + str(y_list[2]))
                self.mm_g_code_list.append("G02 X" + str(x_list[2]) +
                                           " Y" + str(y_list[3]) +
                                           " R" + str(float(self.drill_subsidence_size) / 2))
                self.mm_g_code_list.append("G01 X" + str(x_list[0]) +
                                           " Y" + str(y_list[3]))
                self.mm_g_code_list.append("G02 X" + str(x_list[0]) +
                                           " Y" + str(y_list[2]) +
                                           " R" + str(float(self.drill_subsidence_size) / 2))
                self.mm_g_code_list.append("G01 Z" + self.drill_top)
            else:
                self.mm_g_code_list.append("G00 X" + str(x_list[0]) +
                                           " Y" + str(y_list[0]) +
                                           " Z" + self.drill_top)
                self.mm_g_code_list.append("G01 Z" + str(current_drill_level))
                self.mm_g_code_list.append("X" + str(x_list[1]) +
                                           " Y" + str(y_list[1]))
                self.mm_g_code_list.append("G02 X" + str(x_list[2]) +
                                           " Y" + str(y_list[2]) +
                                           " R" + str(valve_outer_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[3]) +
                                           " Y" + str(y_list[3]))
                self.mm_g_code_list.append("G02 X" + str(x_list[0]) +
                                           " Y" + str(y_list[0]) +
                                           " R" + str(valve_outer_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[4]) +
                                           " Y" + str(y_list[4]))
                self.mm_g_code_list.append("X" + str(x_list[5]) +
                                           " Y" + str(y_list[5]))
                self.mm_g_code_list.append("G02 X" + str(x_list[6]) +
                                           " Y" + str(y_list[6]) +
                                           " R" + str(valve_inner_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[7]) +
                                           " Y" + str(y_list[7]))
                self.mm_g_code_list.append("G02 X" + str(x_list[4]) +
                                           " Y" + str(y_list[4]) +
                                           " R" + str(valve_inner_r))
                self.mm_g_code_list.append("G01 X" + str(x_list[8]) +
                                           " Y" + str(y_list[8]))
                self.mm_g_code_list.append("X" + str(x_list[9]) +
                                           " Y" + str(y_list[9]))
                self.mm_g_code_list.append("G02 X" + str(x_list[10]) +
                                           " Y" + str(y_list[10]) +
                                           " R" + str(float(self.drill_subsidence_size) / 2))
                self.mm_g_code_list.append("G01 X" + str(x_list[11]) +
                                           " Y" + str(y_list[11]))
                self.mm_g_code_list.append("G02 X" + str(x_list[8]) +
                                           " Y" + str(y_list[8]) +
                                           " R" + str(float(self.drill_subsidence_size) / 2))
                self.mm_g_code_list.append("G01 Z" + self.drill_top)

    def valve_holes_g_code(self):

        self.mm_g_code_list.append("(PAUSE FOR DRILL CHANGE)")
        self.mm_g_code_list.append("(" + self.drill_hole_size + "MM HOLE DRILL)")
        self.mm_g_code_list.append("(*************************************************)")
        self.mm_g_code_list.append("(*                                               *)")
        self.mm_g_code_list.append("(* REMEMBER PLATE UNDER FOR PENETRATION DRILLING *)")
        self.mm_g_code_list.append("(*                                               *)")
        self.mm_g_code_list.append("(*************************************************)")
        self.mm_g_code_list.append("M00")

        for valve in self.control_map:

            self.mm_g_code_list.append("G00 X" + str(valve[0]) + " Y" + str(valve[1]))
            self.mm_g_code_list.append("G01 Z" + self.drill_valve_hole_depth)
            self.mm_g_code_list.append("Z" + self.drill_top)
