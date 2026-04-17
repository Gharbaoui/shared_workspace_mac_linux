import numpy as np
from manimlib import *

class Lec5(InteractiveScene):
    def construct(self):
        def equation(t):
            return 2 ** t
        max_x = 6
        max_y = equation(max_x)
        axes = Axes(
                x_range=(-1, max_x, 1),
                y_range=(-1, max_y, max_y/max_x),
                x_axis_config={
                    'color':BLUE,
                    'include_numbers':True,
                    },
                y_axis_config={
                    'color':RED,
                    'line_to_number_direction':UP,
                    'include_numbers':True,
                    },
                width=8,
                height=4.5,
                )

        graph = axes.get_graph(equation, x_range=(-1, max_x, .4),color=YELLOW)

        self.add(axes)
        self.play(ShowCreation(graph))

        self.dtsize = ValueTracker(.5)

        def draw():
            value = float(self.dtsize.get_value())

            xs = np.arange(-1, max_x, value)
            points = [axes.c2p(x, (2**value - 1)/value) for x in xs]
            shape = VGroup(*[Dot(p, fill_color=RED) for p in points])
            return shape

        shape = always_redraw(lambda: draw())
        self.add(shape)


        self.embed()
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if chr(symbol) == "w":
            self.dtsize.set_value(self.dtsize.get_value() + .1)
        if chr(symbol) == "s":
            self.dtsize.set_value(self.dtsize.get_value() - .1)
        return super().on_key_press(symbol, modifiers)
