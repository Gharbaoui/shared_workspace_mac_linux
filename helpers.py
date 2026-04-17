from matplotlib.pyplot import axes
from manimlib import *
import numpy as np




class TrigVisualization(VMobject):
    def __init__(self, start_angle:float ,**kwargs):
        super().__init__(**kwargs)

        self.circle_visualizer = self.gen_shape(start_angle) 

        self.add(self.circle_visualizer)

    def gen_shape(self, angle:float):
        RADIUS = 1.8
        pos_indicator = VGroup()
        angle = angle % TAU
        current_arc = Arc(0, angle=angle, radius=RADIUS, arc_center=ORIGIN).set_color(ORANGE)
        current_point = Dot().move_to(current_arc.get_end()).set_color(YELLOW)
        self.cos_indicator = Line(
                start=(0,current_arc.get_end()[1],current_arc.get_end()[2]),
                end=current_arc.get_end(),
                ).set_color(RED)
        self.sin_indicator = Line(
                start=(current_arc.get_end()[0],0,current_arc.get_end()[2]),
                end=current_arc.get_end(),
                ).set_color(BLUE)
        angle_indicator = DashedLine(
                start=ORIGIN, end=current_arc.get_end(),
                dash_length=0.1
                )


        pos_indicator.add(current_arc,angle_indicator, current_point)

        circle_visualizer = VGroup()
        base_circle = Circle(radius=RADIUS, stroke_width=.8).set_color(GREEN)
        EDGE = int(RADIUS)
        base_axes = Axes(
                x_range=(-EDGE- 1, EDGE+1, ),
                y_range=(-EDGE - 1, EDGE+1, ),
                axis_config={
                    'include_ticks':False,
                    },
                x_axis_config={
                    'color':RED,
                    },
                y_axis_config={
                    'color':BLUE,
                    }
                )
        circle_visualizer.add(
                base_axes,base_circle,
                self.cos_indicator, self.sin_indicator,
                pos_indicator,
        ).to_edge()
        return circle_visualizer

    def update_angle(self, newAngle:float):
        self.remove(self.circle_visualizer)
        self.circle_visualizer = self.gen_shape(newAngle)
        self.add(self.circle_visualizer)

    def get_cos_line(self):
        return self.cos_indicator

    def get_sin_line(self):
        return self.sin_indicator


class Test(InteractiveScene):
    def construct(self):
        self.clear()

        START_ANGLE = PI/8
        self.tracker = ValueTracker(START_ANGLE)
        self.keys_held = set()

        obj = TrigVisualization(start_angle=float(self.tracker.get_value()))

        def change_angle(m):
            ANGLE_TO_MOVE_BY = PI/180
            angle = self.tracker.get_value()
            if 'w' in self.keys_held:
                angle += ANGLE_TO_MOVE_BY

            if 's' in self.keys_held:
                angle -= ANGLE_TO_MOVE_BY
        
            self.tracker.set_value(angle)

            m.update_angle(angle)
        obj.add_updater(
                change_angle,
                )

        # start of axes
        cos_axes = Axes(
                x_range=(-PI/4, 2*PI, PI/4),
                y_range=(-1.5, 1.5, 1),
                ).to_edge(UR)
        sin_axes = Axes(
                x_range=(-PI/4, 2*PI, PI/4),
                y_range=(-1.5, 1.5, 1),
                ).to_edge(DR)


        cos_group = VGroup()
        cos_graph = always_redraw(lambda: cos_axes.get_graph(
                lambda t: np.cos(t + START_ANGLE), color=RED, x_range=(0, self.tracker.get_value() - START_ANGLE)
                ))
        cos_group.add(cos_graph)

        cos_circle_link_to_time_axes_start = always_redraw(
                lambda :Line(
                    start=(cos_axes.c2p(self.tracker.get_value()-START_ANGLE, 0, 0)),
                    end=obj.get_cos_line().get_start(),
                    stroke_width=.4,
                    ).set_color(RED)
                )
        cos_circle_link_to_time_axes_end = always_redraw(
                lambda :Line(
                    start=(cos_axes.c2p(self.tracker.get_value()-START_ANGLE, np.cos(self.tracker.get_value()), 0)),
                    end=obj.get_cos_line().get_end(),
                    stroke_width=.4,
                    ).set_color(RED)
                )
        cos_veritical_indicator = always_redraw(
                lambda: Line(
                    start=cos_circle_link_to_time_axes_start.get_start(),
                    end=cos_circle_link_to_time_axes_end.get_start(),
                    ).set_color(RED)
                )
        cos_group.add(cos_circle_link_to_time_axes_start)
        cos_group.add(cos_circle_link_to_time_axes_end)
        cos_group.add(cos_veritical_indicator)

        sin_graph = always_redraw(lambda: sin_axes.get_graph(
                lambda t: np.sin(t + START_ANGLE), color=BLUE, x_range=(0, self.tracker.get_value() - START_ANGLE)
                ))


        sin_group = VGroup()
        sin_circle_link_to_time_axes_start = always_redraw(
                lambda :Line(
                    start=(sin_axes.c2p(self.tracker.get_value()-START_ANGLE, 0, 0)),
                    end=obj.get_sin_line().get_start(),
                    stroke_width=.4,
                    ).set_color(BLUE)
                )
        sin_circle_link_to_time_axes_end = always_redraw(
                lambda :Line(
                    start=(sin_axes.c2p(self.tracker.get_value()-START_ANGLE, np.sin(self.tracker.get_value()), 0)),
                    end=obj.get_sin_line().get_end(),
                    stroke_width=.4,
                    ).set_color(BLUE)
                )
        sin_veritical_indicator = always_redraw(
                lambda: Line(
                    start=sin_circle_link_to_time_axes_start.get_start(),
                    end=sin_circle_link_to_time_axes_end.get_start(),
                    ).set_color(BLUE)
                )
        sin_group.add(sin_circle_link_to_time_axes_start, sin_circle_link_to_time_axes_end, sin_veritical_indicator)
        self.add(cos_axes, sin_axes, sin_graph, cos_group, sin_group)

        self.add(obj)


    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if chr(symbol) == 'w' or chr(symbol) == 's':
            self.keys_held.clear()
            self.keys_held.add(chr(symbol))
        if chr(symbol) == ' ':
            self.keys_held.clear()

        return super().on_key_press(symbol, modifiers)
