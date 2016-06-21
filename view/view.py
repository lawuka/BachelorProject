'''

Created on 24 feb 2015

@author Lasse

'''

from tkinter import *
from tkinter import filedialog
from math import pi, cos, sin, radians
from model.mathFunctions import rotate_x_y_coordinates
from model.helperFunctions import rotate_valve_coords


class View(Tk):
    def __init__(self, c):

        self.c = c
        self.library = None
        self.conf = None
        self.canvas_map = None
        self.flow_line_map = None
        self.flow_circle_map = None
        self.flow_hole_map = None
        self.control_map = None
        self.red_box_map = None
        self.discontinuity_width = None

        Tk.__init__(self)
        self.title('Fabrication Tool')
        self.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.scale = None
        self.minsize(784, 748)
        self.canvas = None

        self.current_save_file = None

        self.current_architecture_file = StringVar()
        self.current_architecture_file.set('chip_examples/massive_mixers.xml')  # Should be ''
        self.c.get_model().set_current_architecture_file('chip_examples/massive_mixers.xml')  # Should be ''

        self.current_library_file = StringVar()
        self.current_library_file.set('library/component_library_test.xml')  # Should be ''
        self.c.get_model().set_current_library_file('library/component_library_test.xml')  # Should be ''

        self.current_config_file = StringVar()
        self.current_config_file.set('config/conf.ini')  # Should be ''
        self.c.get_model().set_current_config_file('config/conf.ini')  # Should be ''

        self.current_status_msg = StringVar()
        self.current_status_msg.set('')

        self.layout_shown = False

    def show(self):

        self.canvas = Canvas(width=400, height=400, highlightthickness=1, highlightbackground='grey')
        self.canvas.grid(column=0, row=0, sticky=N + S + E + W)
        self.canvas.bind('<Configure>', self.update_canvas)

        right_view = Frame(self)

        self.show_flow_check_var = IntVar()
        self.show_control_check_var = IntVar()
        self.show_red_box_check_var = IntVar()
        self.show_flow_check_var.set(0)
        self.show_control_check_var.set(0)
        self.show_red_box_check_var.set(0)
        chip_view_frame = LabelFrame(right_view, text='Chip Layout')
        chip_view_frame.grid(row=0, column=0, sticky=E + W, ipady=3, ipadx=5)
        self.show_layout_check = Checkbutton(chip_view_frame, variable=self.show_flow_check_var,
                                             command=self.draw_canvas, text="Show flow layout", state=DISABLED)
        self.show_control_check = Checkbutton(chip_view_frame, variable=self.show_control_check_var,
                                              command=self.draw_canvas, text="Show control layout", state=DISABLED)
        self.show_red_box_check = Checkbutton(chip_view_frame, variable=self.show_red_box_check_var,
                                              command=self.draw_canvas, text="Show red boxes", state=DISABLED)
        self.show_layout_check.pack(side=TOP, anchor=W)
        self.show_control_check.pack(side=TOP, anchor=W)
        self.show_red_box_check.pack(side=TOP, anchor=W)
        Button(chip_view_frame, text="Generate Chip Layout", command=self.show_layout).pack(side=TOP)

        g_code_frame = LabelFrame(right_view, text='GCode')
        Button(g_code_frame, text="Simulator Flow", command=self.produce_sim_g_code,
               state=DISABLED).pack(side=TOP)
        Button(g_code_frame, text="Simulator Control", command=self.produce_sim_control_g_code,
               state=DISABLED).pack(side=TOP)
        Button(g_code_frame, text="Micro Milling Flow", command=self.produce_mm_flow_g_code).pack(side=TOP)
        Button(g_code_frame, text="Micro Milling Control", command=self.produce_mm_control_g_code).pack(side=TOP)
        g_code_frame.grid(row=1, column=0, sticky=E + W, ipady=3, ipadx=5)

        g_code_text_frame = LabelFrame(right_view, text='GCode View')
        self.g_code_text_field = Text(g_code_text_frame, width=30, state=DISABLED, highlightbackground='grey',
                                      highlightthickness=1)
        self.g_code_text_field.pack(side=TOP, expand=True, fill="y", pady=5)
        self.g_code_text_field_copy = Button(g_code_text_frame, text="Copy To Clipboard", state=DISABLED,
                                             command=self.copy_g_code_to_clipboard)
        self.g_code_text_field_copy.pack(side=TOP)
        g_code_text_button_frame = Frame(g_code_text_frame)
        g_code_text_button_frame.pack(side=TOP)
        self.g_code_text_field_save = Button(g_code_text_button_frame, text="Save", state=DISABLED,
                                             command=self.save_g_code_to_file)
        self.g_code_text_field_save.pack(side=LEFT)
        self.g_code_text_field_save_as = Button(g_code_text_button_frame, text="Save As", state=DISABLED,
                                                command=self.save_as_g_code_to_file)
        self.g_code_text_field_save_as.pack(side=LEFT)
        g_code_text_frame.grid(row=2, column=0, sticky=N + E + W + S, ipady=3, ipadx=5)

        right_view.grid(column=1, row=0, rowspan=4, sticky=N + S, padx=5)
        right_view.rowconfigure(2, weight=1)

        svg_info = Frame(self)
        Label(svg_info, text="Architecture File:", width=12, anchor=W).pack(side=LEFT, padx=5)
        Entry(svg_info, textvariable=self.current_architecture_file, relief=SUNKEN, state=DISABLED).pack(side=LEFT,
                                                                                                         expand=True,
                                                                                                         fill="x",
                                                                                                         padx=5)
        Button(svg_info, text="Open", width=5, command=self.open_architecture_file).pack(side=LEFT)
        svg_info.grid(column=0, row=1, sticky=W + E)
        library_info = Frame(self)
        Label(library_info, text='Library File:', width=12, anchor=W).pack(side=LEFT, padx=5, pady=5)
        Entry(library_info, textvariable=self.current_library_file, relief=SUNKEN, state=DISABLED).pack(side=LEFT,
                                                                                                        expand=True,
                                                                                                        fill="x",
                                                                                                        padx=5)
        Button(library_info, text="Open", width=5, command=self.open_library_file).pack(side=LEFT)
        library_info.grid(column=0, row=2, sticky=W + E)
        config_info = Frame(self)
        Label(config_info, text="Config File:", width=12, anchor=W).pack(side=LEFT, padx=5, pady=5)
        Entry(config_info, textvariable=self.current_config_file, relief=SUNKEN, state=DISABLED).pack(side=LEFT,
                                                                                                      expand=True,
                                                                                                      fill="x",
                                                                                                      padx=5)
        Button(config_info, text="Open", width=5, command=self.open_config_file).pack(side=LEFT)
        config_info.grid(column=0, row=3, sticky=W + E)

        status_bar = Frame(self)
        self.status_entry = Entry(status_bar, textvariable=self.current_status_msg, relief=SUNKEN, state=DISABLED)
        self.status_entry.pack(fill="x")
        status_bar.grid(column=0, columnspan=2, row=4, sticky=W + E)

    def update_canvas(self, event):
        if self.layout_shown:
            self.scale = min(event.height / int(self.canvas_map['height']),
                             event.width / int(self.canvas_map['width']))
            self.draw_canvas()

    def show_layout(self):

        self.canvas_map = self.c.get_chip_layout()
        self.library = self.c.get_library_data()
        self.conf = self.c.get_config_data()
        self.discontinuity_width = float(self.conf['Flow_Layer_Options']['Valve_Discontinuity_Width'])

        if self.canvas_map is not None and self.library is not None and self.conf is not None:
            self.show_layout_check['state'] = NORMAL
            self.show_control_check['state'] = NORMAL
            self.show_red_box_check['state'] = NORMAL
            self.clear_maps()
            self.update_maps()

            if 1 in {self.show_flow_check_var.get(),
                     self.show_control_check_var.get(),
                     self.show_red_box_check_var.get()}:
                self.scale = min(self.canvas.winfo_height() / int(self.canvas_map['height']),
                                 self.canvas.winfo_width() / int(self.canvas_map['width']))
                self.draw_canvas()

    def draw_canvas(self):

        self.canvas.delete("all")

        if self.show_flow_check_var.get() == 1:
            self.draw_flow_lines()
            self.draw_flow_circles()
            self.draw_flow_holes()

        if self.show_control_check_var.get() == 1:
            self.draw_control_valves()

        if self.show_red_box_check_var.get() == 1:
            self.draw_red_boxes()

        if not self.layout_shown:
            self.update_maps()
            self.layout_shown = True
        self.update_view()

    def update_maps(self):

        if not self.layout_shown:
            self.scale = min(self.canvas.winfo_height() / int(self.canvas_map['height']),
                             self.canvas.winfo_width() / int(self.canvas_map['width']))

        for line in self.canvas_map['lines']:
            xyxy = [float(line[0]), float(line[1]), float(line[2]), float(line[3])]
            self.flow_line_map.append(xyxy)

        for component in self.canvas_map['components']:
            if component[0] in self.library:
                component_x = float(component[1])
                component_y = float(component[2])
                component_width = float(self.library[component[0]]['Size'].find('Width').text)
                component_height = float(self.library[component[0]]['Size'].find('Height').text)
                component_actual_position_x = component_x - component_width / 2
                component_actual_position_y = component_y - component_height / 2

                self.append_red_box(component_x, component_y, component_width, component_height, component[3])

                control_valves = self.library[component[0]]['Control']
                if control_valves is not None and len(control_valves) != 0:
                    self.append_control_valves(control_valves,
                                               [component_actual_position_x],
                                               [component_actual_position_y],
                                               [component[3] % 360.0],
                                               [component_width],
                                               [component_height])

                for i_component in self.library[component[0]]['Internal']:
                    if i_component.tag == 'FlowLine':
                        self.append_flow_lines(i_component,
                                               [component_actual_position_x],
                                               [component_actual_position_y],
                                               [component[3] % 360.0],
                                               [component_width],
                                               [component_height],
                                               rotate_valve_coords(self.library[component[0]]['Control'],
                                                                   [component_actual_position_x],
                                                                   [component_actual_position_y],
                                                                   [component[3] % 360.0],
                                                                   [component_width],
                                                                   [component_height]))
                    elif i_component.tag == 'FlowCircle':
                        self.append_flow_circles(i_component,
                                                 [component_actual_position_x],
                                                 [component_actual_position_y],
                                                 [component[3] % 360.0],
                                                 [component_width],
                                                 [component_height])
                    elif i_component.tag == 'FlowHole':
                        self.append_flow_holes(i_component,
                                               [component_actual_position_x],
                                               [component_actual_position_y],
                                               [component[3] % 360.0],
                                               [component_width],
                                               [component_height])
                    else:
                        self.draw_component(i_component,
                                            [component_actual_position_x],
                                            [component_actual_position_y],
                                            [component[3] % 360.0],
                                            [component_width],
                                            [component_height])
            else:
                self.c.add_to_log('Skipping drawing of ' + component[0] + ' - component not in Library')
                self.update_status_message()

    def draw_component(self, component, component_x_list, component_y_list,
                       component_rotation_list, component_width_list, component_height_list):

        if component.tag in self.library:
            self.append_red_boxes(component, component_x_list, component_y_list,
                                  component_rotation_list,
                                  component_width_list,
                                  component_height_list)
            component_x = float(component.find('X').text)
            component_y = float(component.find('Y').text)
            component_width = float(self.library[component.tag]['Size'].find('Width').text)
            component_height = float(self.library[component.tag]['Size'].find('Height').text)
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
                if i_component.tag == 'FlowLine':
                    self.append_flow_lines(i_component, component_x_list, component_y_list,
                                           component_rotation_list,
                                           component_width_list,
                                           component_height_list,
                                           rotate_valve_coords(self.library[component.tag]['Control'],
                                                               component_x_list, component_y_list,
                                                               component_rotation_list, component_width_list,
                                                               component_height_list))
                elif i_component.tag == 'FlowCircle':
                    self.append_flow_circles(i_component, component_x_list, component_y_list,
                                             component_rotation_list,
                                             component_width_list,
                                             component_height_list)
                elif i_component.tag == 'FlowHole':
                    self.append_flow_holes(i_component, component_x_list, component_y_list,
                                           component_rotation_list,
                                           component_width_list,
                                           component_height_list)
                else:
                    self.draw_component(i_component, component_x_list, component_y_list,
                                        component_rotation_list,
                                        component_width_list,
                                        component_height_list)
                    component_x_list.pop()
                    component_y_list.pop()
                    component_rotation_list.pop()
                    component_width_list.pop()
                    component_height_list.pop()
        else:
            self.c.add_to_log('Skipping drawing of ' + component[0] + ' - component not in Library')
            self.update_status_message()

    def append_flow_lines(self, flow_line, component_x_list, component_y_list,
                          component_rotation_list, component_width_list, component_height_list, control_valves):
        flow_start_x = float(flow_line.find('Start').find('X').text)
        flow_start_y = float(flow_line.find('Start').find('Y').text)
        flow_end_x = float(flow_line.find('End').find('X').text)
        flow_end_y = float(flow_line.find('End').find('Y').text)

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
                        self.flow_line_map.append([current_x,
                                                   new_start_coordinates[1],
                                                   next_x,
                                                   new_end_coordinates[1]])
                        if new_start_coordinates[0] < new_end_coordinates[0]:
                            current_x = x + self.discontinuity_width / 2
                        else:
                            current_x = x - self.discontinuity_width / 2
                self.flow_line_map.append([current_x,
                                           new_start_coordinates[1],
                                           new_end_coordinates[0],
                                           new_end_coordinates[1]])
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
                        self.flow_line_map.append([new_start_coordinates[0],
                                                   current_y,
                                                   new_end_coordinates[0],
                                                   next_y])
                        if new_start_coordinates[1] < new_end_coordinates[1]:
                            current_y = y + self.discontinuity_width / 2
                        else:
                            current_y = y - self.discontinuity_width / 2

                self.flow_line_map.append([new_start_coordinates[0],
                                           current_y,
                                           new_end_coordinates[0],
                                           new_end_coordinates[1]])
        else:
            self.flow_line_map.append([new_start_coordinates[0], new_start_coordinates[1],
                                       new_end_coordinates[0], new_end_coordinates[1]])

    def draw_flow_lines(self):
        for flowLine in self.flow_line_map:
            self.canvas.create_line(self.scale_coords(flowLine),
                                    width=1)

    def append_flow_circles(self, flow_circle, component_x_list, component_y_list,
                            component_rotation_list, component_width_list, component_height_list):
        circle_center_x = float(flow_circle.find('Center').find('X').text)
        circle_center_y = float(flow_circle.find('Center').find('Y').text)

        new_coordinates = rotate_x_y_coordinates(circle_center_x, circle_center_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        circle_radius = float(flow_circle.find('Radius').text)
        angle_list = [float(angle.text) for angle in
                      sorted(list(flow_circle.find('Valves')), key=lambda elem: float(elem.text) % 360.0)]

        for valve in angle_list:
            valve_degree = valve
            if valve_degree in {0.0, 180.0}:
                valve_center_x = new_coordinates[0] + cos(radians((valve_degree + new_coordinates[2])
                                                                  % 360.0)) * circle_radius
                valve_center_y = new_coordinates[1] + sin(radians((valve_degree + new_coordinates[2])
                                                                  % 360.0)) * circle_radius
            else:
                valve_center_x = new_coordinates[0] + cos(radians((valve_degree + new_coordinates[2])
                                                                  % 360.0)) * circle_radius
                valve_center_y = new_coordinates[1] + sin(radians((valve_degree + new_coordinates[2])
                                                                  % 360.0)) * circle_radius

            self.control_map.append([valve_center_x - 2,
                                     valve_center_y - 2,
                                     valve_center_x + 2,
                                     valve_center_y + 2])

        xy = [(new_coordinates[0] - circle_radius), (new_coordinates[1] - circle_radius),
              (new_coordinates[0] + circle_radius), (new_coordinates[1] + circle_radius)]

        self.flow_circle_map.append([xy, angle_list, new_coordinates[2], circle_radius])

    def draw_flow_circles(self):

        for flowCircle in self.flow_circle_map:
            xy = self.scale_coords(flowCircle[0])
            angle_list = flowCircle[1]
            total_rotation = flowCircle[2]
            circle_radius = flowCircle[3]

            valve_length_angle = (360 * float(self.discontinuity_width)) / (2 * circle_radius * pi)

            if len(angle_list) == 0:
                self.canvas.create_oval(xy)
            else:
                for i in range(len(angle_list) - 1, -1, -1):
                    self.canvas.create_arc(xy,
                                           start=(360.0 - angle_list[i] + valve_length_angle /
                                                  2 - total_rotation) % 360.0,
                                           extent=((360.0 - angle_list[i - 1] - valve_length_angle /
                                                    2 - total_rotation) - (360.0 - angle_list[i] + valve_length_angle /
                                                                           2 - total_rotation)) % 360.0,
                                           style=ARC)

    def append_flow_holes(self, flow_hole, component_x_list, component_y_list,
                          component_rotation_list, component_width_list, component_height_list):

        hole_center_x = float(flow_hole.find('Center').find('X').text)
        hole_center_y = float(flow_hole.find('Center').find('Y').text)

        new_coordinates = rotate_x_y_coordinates(hole_center_x, hole_center_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        xy = [(new_coordinates[0] - 1),
              (new_coordinates[1] - 1),
              (new_coordinates[0] + 1),
              (new_coordinates[1] + 1)]

        self.flow_hole_map.append(xy)

    def draw_flow_holes(self):

        for flow_hole in self.flow_hole_map:
            self.canvas.create_oval(self.scale_coords(flow_hole))

    def append_control_valves(self, valve_list, component_x_list, component_y_list,
                              component_rotation_list, component_width_list, component_height_list):

        for valve in valve_list:
            valve_center_x = float(valve.find('X').text)
            valve_center_y = float(valve.find('Y').text)

            new_coordinates = rotate_x_y_coordinates(valve_center_x, valve_center_y,
                                                     component_x_list, component_y_list,
                                                     component_width_list, component_height_list,
                                                     component_rotation_list)

            xy = [(new_coordinates[0] - 2),
                  (new_coordinates[1] - 2),
                  (new_coordinates[0] + 2),
                  (new_coordinates[1] + 2)]

            self.control_map.append(xy)

    def draw_control_valves(self):
        for control_valve in self.control_map:
            self.canvas.create_oval(self.scale_coords(control_valve), outline='orange')

    def append_red_boxes(self, component, component_x_list, component_y_list, component_rotation_list,
                         component_width_list, component_height_list):

        component_x = float(component.find('X').text)
        component_y = float(component.find('Y').text)

        new_coordinates = rotate_x_y_coordinates(component_x, component_y,
                                                 component_x_list, component_y_list,
                                                 component_width_list, component_height_list,
                                                 component_rotation_list)

        component_width = float(self.library[component.tag]['Size'].find('Width').text)
        component_height = float(self.library[component.tag]['Size'].find('Height').text)
        component_rotation = new_coordinates[2] + float(component.find('Rotation').text)

        self.append_red_box(new_coordinates[0], new_coordinates[1],
                            component_width, component_height,
                            component_rotation)

    def append_red_box(self, component_x, component_y, component_width, component_height, total_rotation):

        half_width = component_width / 2
        half_height = component_height / 2

        append_list = None

        if total_rotation % 360.0 in {0, 180}:
            append_list = [[component_x - half_width, component_y - half_height,
                            component_x + half_width, component_y - half_height],
                           [component_x - half_width, component_y - half_height,
                            component_x - half_width, component_y + half_height],
                           [component_x + half_width, component_y - half_height,
                            component_x + half_width, component_y + half_height],
                           [component_x - half_width, component_y + half_height,
                            component_x + half_width, component_y + half_height]]
        elif total_rotation % 360.0 in {90, 270}:
            append_list = [[component_x - half_height, component_y - half_width,
                            component_x + half_height, component_y - half_width],
                           [component_x - half_height, component_y - half_width,
                            component_x - half_height, component_y + half_width],
                           [component_x + half_height, component_y - half_width,
                            component_x + half_height, component_y + half_width],
                           [component_x - half_height, component_y + half_width,
                            component_x + half_height, component_y + half_width]]

        self.red_box_map.append(append_list)

    def draw_red_boxes(self):

        for red_box in self.red_box_map:
            self.canvas.create_line(red_box[0][0] * self.scale,
                                    red_box[0][1] * self.scale,
                                    red_box[0][2] * self.scale,
                                    red_box[0][3] * self.scale, width=1, fill='red')
            self.canvas.create_line(red_box[1][0] * self.scale,
                                    red_box[1][1] * self.scale,
                                    red_box[1][2] * self.scale,
                                    red_box[1][3] * self.scale, width=1, fill='red')
            self.canvas.create_line(red_box[2][0] * self.scale,
                                    red_box[2][1] * self.scale,
                                    red_box[2][2] * self.scale,
                                    red_box[2][3] * self.scale, width=1, fill='red')
            self.canvas.create_line(red_box[3][0] * self.scale,
                                    red_box[3][1] * self.scale,
                                    red_box[3][2] * self.scale,
                                    red_box[3][3] * self.scale, width=1, fill='red')

    def produce_sim_g_code(self):
        '''
        Produce Simulator G-Code
        '''
        if self.c.create_sim_g_code():
            self.g_code_text_field['state'] = NORMAL
            for line in self.c.get_model().get_simulator_g_code():
                self.g_code_text_field.insert(END, line + "\n")
            self.current_status_msg.set('Produced Simulator G-Code')
            self.g_code_text_field['state'] = DISABLED
            if self.g_code_text_field_copy['state'] == DISABLED:
                self.g_code_text_field_copy['state'] = NORMAL
            self.update_view()

    def produce_sim_control_g_code(self):

        # Not implemented yet!
        pass

    def produce_mm_flow_g_code(self):
        '''
        Produce Micro Milling Machine Flow G-Code
        '''
        if self.c.create_mm_flow_g_code():
            self.g_code_text_field['state'] = NORMAL
            self.g_code_text_field.delete("1.0", END)
            for line in self.c.get_model().get_mm_flow_g_code():
                self.g_code_text_field.insert(END, line + "\n")
            self.g_code_text_field['state'] = DISABLED
            if self.g_code_text_field_copy['state'] == DISABLED:
                self.g_code_text_field_copy['state'] = NORMAL
                self.g_code_text_field_save['state'] = NORMAL
                self.g_code_text_field_save_as['state'] = NORMAL
            self.update_view()

    def produce_mm_control_g_code(self):
        '''
        Produce Micro Milling Machine Control G-Code
        '''
        if self.c.create_mm_control_g_code():
            self.g_code_text_field['state'] = NORMAL
            self.g_code_text_field.delete("1.0", END)
            for line in self.c.get_model().get_mm_control_g_code():
                self.g_code_text_field.insert(END, line + "\n")
            self.g_code_text_field['state'] = DISABLED
            if self.g_code_text_field_copy['state'] == DISABLED:
                self.g_code_text_field_copy['state'] = NORMAL
                self.g_code_text_field_save['state'] = NORMAL
                self.g_code_text_field_save_as['state'] = NORMAL
            self.update_view()

    def open_architecture_file(self):

        file_name = filedialog.askopenfilename()
        if file_name is not '':
            self.current_architecture_file.set(file_name)
            self.c.get_model().set_current_architecture_file(file_name)
            self.update_view()

    def open_library_file(self):

        file_name = filedialog.askopenfilename()
        if file_name is not '':
            self.current_library_file.set(file_name)
            self.c.get_model().set_current_library_file(file_name)
            self.update_view()

    def open_config_file(self):

        file_name = filedialog.askopenfilename()
        if file_name is not '':
            self.current_config_file.set(file_name)
            self.c.get_model().set_current_config_file(file_name)
            self.update_view()

    def copy_g_code_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.g_code_text_field.get("1.0", END))

    def save_g_code_to_file(self):

        if self.current_save_file is None:
            file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
            if file is None:
                return
            text_to_save = str(self.g_code_text_field.get(1.0, END))
            self.c.write_g_code_to_file(file.name, text_to_save)
            self.current_save_file = file.name
        else:
            text_to_save = str(self.g_code_text_field.get(1.0, END))
            self.c.write_g_code_to_file(self.current_save_file, text_to_save)

    def save_as_g_code_to_file(self):
        file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if file is None:
            return
        text_to_save = str(self.g_code_text_field.get(1.0, END))
        self.c.write_g_code_to_file(file.name, text_to_save)
        self.current_save_file = file.name

    def scale_coords(self, coords_list):

        return coords_list[0] * self.scale, coords_list[1] * self.scale, \
               coords_list[2] * self.scale, coords_list[3] * self.scale

    def clear_maps(self):
        self.flow_line_map = []
        self.flow_circle_map = []
        self.flow_hole_map = []
        self.control_map = []
        self.red_box_map = []

    def update_status_message(self):
        if self.c.error_occurred:
            self.current_status_msg.set('Error(s) occured - see log!')
            self.status_entry['disabledforeground'] = 'red'
        else:
            self.current_status_msg.set('All OK!')
            self.status_entry['disabledforeground'] = 'black'
        self.update_view()

    def update_view(self):
        self.update()
