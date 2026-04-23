from scipy.integrate._ivp.rk import MAX_FACTOR
from manimlib import *
import numpy as np
import math



class Test(InteractiveScene):
    def point_as_vec(self, x, y, axes, color=GREEN, label='z'):
        line = Line(
                start=axes.c2p(0, 0),
                end=axes.c2p(x, y),
                color=color,
                ).add_tip()
        label = Tex(label).move_to(line.get_end() + line.get_end()/10)
        return VGroup(line, label)

    def construct(self):
        self.clear()
        main_axes = Axes(
                x_range=(-7, 7,1),
                y_range=(-7, 7,1),
                x_axis_config={
                    'color':RED,
                    'include_numbers':True,
                },
                y_axis_config={
                    'color':BLUE,
                    'include_numbers':True,
                    'line_to_number_direction':UP,
                },
            )
        
        za, zb = 3, 2
        z_vec  = self.point_as_vec(za, zb, main_axes, label='z', color=RED)
        self.add(main_axes, z_vec)


def exp(x):
    terms = [x ** n / math.factorial(n) for n in range(20)]
    return sum(terms)

class Ep4(InteractiveScene):
    def construct(self):
        main_axes = Axes()
        points = []
        max_x = 10
        current_x = 0
        STEP = 0.1

        while current_x <= max_x:
            points.append((current_x, exp(current_x), 0))
            current_x += STEP

        points_to_local_axes = [main_axes.c2p(*p) for p in points]
        points_shape = VMobject().set_points_as_corners(points_to_local_axes).set_color(BLUE)

        self.add(main_axes,points_shape)
        self.embed()
