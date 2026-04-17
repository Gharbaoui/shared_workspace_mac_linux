from manimlib import *
from manimlib.utils import color

class Learn(InteractiveScene):
    def construct(self):
        self.clear()
        # axes
        axes = ThreeDAxes(
                x_range=(-4, 4, 1),
                y_range=(0, 4, 1),
                z_range=(-4, 4, 1),
                z_axis_config={
                    "include_tip":False,
                    "color":RED,
                    # "tip_config":{
                    #     "width":0.25,
                    #     "length":1,
                    #     },
                    },
                x_axis_config={
                    "color":GREEN,
                    },
                y_axis_config={
                    "color":BLUE,
                    }
                )
        axes.add_axis_labels()
        self.add(axes)

        s = Sphere(
                resolution=(200, 200),
                color=RED,
        )

        self.add(s)

        self.embed()
    # def on_mouse_motion(self, point, d_point):
    #     print(point)
    #     print(f'd point {d_point}')

    # def on_key_press(self, symbol, modifiers):
    #     if chr(symbol) == "a":
    #         print('a was pressed')
    #     print(f'sm {symbol}')
    #     print(f'mod {modifiers}')
    
