from manimlib import *

class MyThreedAxes(ThreeDAxes):
    def __init__(
        self,
        x_range: RangeSpecifier = (-6.0, 6.0, 1.0),
        y_range: RangeSpecifier = (-5.0, 5.0, 1.0),
        z_range: RangeSpecifier = (-4.0, 4.0, 1.0),
        z_axis_config: dict = dict(),
        z_normal: Vect3 = DOWN,
        depth: float | None = None,
        x_custom: bool = False,
        x_ticks_handler: callable = lambda x: Tex(str(x)),
        y_custom: bool = False,
        y_ticks_handler: callable = lambda x: Tex(str(x)),
        z_custom: bool = False,
        z_ticks_handler: callable = lambda x: Tex(str(x)),
        **kwargs
    ):
        ThreeDAxes.__init__(
                self,
               x_range=x_range,
               y_range=y_range,
               z_range=z_range,
               z_axis_config=z_axis_config,
               z_normal=z_normal,
               depth=depth,
               **kwargs,
               ) 


        def attach_custom_tick_values(handler, xyz_range=x_range,to_axes_point:callable = lambda a: self.c2p(a, -.35, 0)):
            ticks_vg = VGroup()
            steps_in_negative = int(xyz_range[0]/xyz_range[2])
            steps_in_postive = int(xyz_range[1]/xyz_range[2])

            start = steps_in_negative if steps_in_negative < 0 else 0
            end = steps_in_postive
            print(f'start: {start}, end:{end}')

            pos_value = xyz_range[0]
            for tick_value in range(start, end+1, 1):
                ticks_vg.add(
                        handler(tick_value).scale(.4).move_to(to_axes_point(pos_value))
                )
                pos_value += xyz_range[2]
            return ticks_vg

        if x_custom:
            self.x_ticks = attach_custom_tick_values(x_ticks_handler, x_range, to_axes_point= lambda value: self.c2p(value, -.35, 0))
            self.add(self.x_ticks)
        if y_custom:
            self.y_ticks = attach_custom_tick_values(y_ticks_handler, y_range, to_axes_point= lambda value: self.c2p(-.35, value, 0))
            self.add(self.y_ticks)
        if z_custom:
            self.z_ticks = attach_custom_tick_values(z_ticks_handler, z_range, to_axes_point= lambda value: self.c2p(0, -.35, value))
            self.add(self.z_ticks)




class Lecture1(InteractiveScene):
    def construct(self) -> None:
        self.clear()
        axes = MyThreedAxes(
                # x_range=(-2*PI/4, PI, PI/4),
                x_custom=True,
                x_ticks_handler=lambda x: Tex(
                    "0" if x == 0 else rf"{int(x)} \cdot \frac{{\pi}}{{4}}"
                ),
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                },
                y_axis_config={
                    'color':BLUE,
                },
                z_axis_config={
                    'color':YELLOW,
                },
        )
        self.add(Square3D())

        self.add(axes)


