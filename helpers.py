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
        cos_indicator = Line(
                start=(0,current_arc.get_end()[1],current_arc.get_end()[2]),
                end=current_arc.get_end(),
                ).set_color(RED)
        sin_indicator = Line(
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
                cos_indicator, sin_indicator,
                pos_indicator,
        ).to_edge()
        return circle_visualizer

    def update_angle(self, newAngle:float):
        self.remove(self.circle_visualizer)
        self.circle_visualizer = self.gen_shape(newAngle)
        self.add(self.circle_visualizer)



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
        trig_axes = Axes(
                x_range=(-PI/4, 2*PI, PI/4),
                y_range=(-1.5, 1.5, 1),
                ).to_edge(RIGHT)

        cos_graph = always_redraw(lambda: trig_axes.get_graph(
                lambda t: np.cos(t + START_ANGLE), color=RED, x_range=(0, self.tracker.get_value() - START_ANGLE)
                ))
        sin_graph = always_redraw(lambda: trig_axes.get_graph(
                lambda t: np.sin(t + START_ANGLE), color=BLUE, x_range=(0, self.tracker.get_value() - START_ANGLE)
                ))
        self.add(trig_axes,cos_graph, sin_graph)
        # end of axes

        self.add(obj)


    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if chr(symbol) == 'w' or chr(symbol) == 's':
            self.keys_held.clear()
            self.keys_held.add(chr(symbol))
        if chr(symbol) == ' ':
            self.keys_held.clear()

        return super().on_key_press(symbol, modifiers)
