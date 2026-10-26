from manimlib import *
import random
import numpy as np
import mcubes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marching import get_contour_lines, circle_eq, gas_leek_eq, GAS_LEEK_SHIFT_UP_BY, heated_metal_plate_eq, METAL_SHIFT_UP_BY, METAL_STRETCH,heated_metal_plate_gradient_eq, review_dir_vec_eq, electric_potential_eq, ELECTRIC_FIELD_AT_0, submaric_lagrange_eq, lec14_eq, safest_point_eq, expr_eq, expr_eq_1

class Simple3DVec(VMobject):
    def __init__(
        self,
        axes,
        start: Vect3 | Mobject = LEFT,
        end: Vect3 | Mobject = RIGHT,
        buff: float = 0.0,
        path_arc: float = 0.0,
        **kwargs
    ):
        super().__init__()
        self.start = start
        self.end = end
        self.l = Line(
            axes.c2p(*start), axes.c2p(*(start + end)), buff, path_arc, **kwargs
            )

        self.add(self.l)

        self.color = WHITE
        if 'color' in kwargs:
            self.color = kwargs['color']

        self.tip = Dot().move_to(axes.c2p(*(start+end))).set_color(self.color)
        self.vec = VGroup(self.l, self.tip)
        self.add(self.vec)

    def set_color(self, color: ManimColor | Iterable[ManimColor] | None, opacity: float | Iterable[float] | None = None, recurse: bool = True) -> Self:
        self.color = color
        self.l.set_color(color)
        self.tip.set_color(color)
        return super().set_color(color, opacity, recurse)

    def get_end(self) -> Vect3:
        return self.l.get_end()
    def get_start(self) -> Vect3:
        return self.l.get_start()

    def move_to_tip_of(self,other):
        newL = Line(
                start=other.get_end(),
                end=self.get_end() + other.get_end(),
                color=self.color,
                )
        newTip = Dot().move_to(newL.get_end()).set_color(self.color)
        return VGroup(newL, newTip)

    def move_vec_to_other(self, scene, other):
        newVec = self.move_to_tip_of(other)
        scene.play(
                Transform(self.vec ,newVec)
                )
        self.vec = newVec

class MyThreedAxes(ThreeDAxes):
    def __init__(
        self,
        activeScene,
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

        self.scene = activeScene


        def attach_custom_tick_values(handler, xyz_range=x_range,to_axes_point:callable = lambda a: self.c2p(a, -.35, 0)):
            ticks_vg = VGroup()
            steps_in_negative = int(xyz_range[0]/xyz_range[2])
            steps_in_postive = int(xyz_range[1]/xyz_range[2])

            start = steps_in_negative if steps_in_negative < 0 else 0
            end = steps_in_postive

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


        self.xy_plane = self.get_parametric_surface(
                lambda u, v: np.array([u, v, 0]),
                u_range=self.x_range[0:2],
                v_range=self.y_range[0:2],
                opacity=0.3,
                ).set_color_by_gradient(RED, GREEN)

        self.yz_plane = self.get_parametric_surface(
                lambda u, v: np.array([0, u, v]),
                u_range=self.y_range[0:2],
                v_range=self.z_range[0:2],
                opacity=0.3,
                ).set_color_by_gradient(GREEN,BLUE)
        self.zx_plane = self.get_parametric_surface(
                lambda u, v: np.array([u, 0, v]),
                u_range=self.x_range[0:2],
                v_range=self.z_range[0:2],
                opacity=0.3,
                ).set_color_by_gradient(BLUE, RED)

        self.xy_plane_active = False
        self.yz_plane_active = False
        self.zx_plane_active = False
        self.toggle_xy_plane()
        self.toggle_yz_plane()
        self.toggle_zx_plane()

    def toggle_xy_plane(self):
        if self.xy_plane_active:
            self.scene.remove(self.xy_plane)
        else:
            self.scene.add(self.xy_plane)
        self.xy_plane_active = not self.xy_plane_active

    def toggle_yz_plane(self):
        if self.yz_plane_active:
            self.scene.remove(self.yz_plane)
        else:
            self.scene.add(self.yz_plane)
        self.yz_plane_active = not self.yz_plane_active
    def toggle_zx_plane(self):
        if self.zx_plane_active:
            self.scene.remove(self.zx_plane)
        else:
            self.scene.add(self.zx_plane)
        self.zx_plane_active = not self.zx_plane_active
    def toggle_planes(self):
        self.toggle_xy_plane()
        self.toggle_yz_plane()
        self.toggle_zx_plane()

    def render_contour(self, x_range, y_range, level, eq, step=0.1,color=YELLOW):
        segs = get_contour_lines(x_range, y_range, step, level, eq)
        shape = VGroup()
        for s in segs:
            start, end = s
            shape.add(
                Line(
                    start=self.c2p(*start, level),
                    end=self.c2p(*end, level),
                    color=color,
                )
            )
        return shape


    def render_level_surface(self, eq, level, bli=(-10,-10,-10), tro=(10,10,10),color=YELLOW):
        vertices, triangles = mcubes.marching_cubes_func(bli, tro, 50, 50, 50, eq, level)

        mesh = VGroup()
        for tri in triangles:
            p1 = vertices[tri[0]]
            p2 = vertices[tri[1]]
            p3 = vertices[tri[2]]

            mesh.add(
                Polygon(
                    self.c2p(*p1),
                    self.c2p(*p2),
                    self.c2p(*p3),
                    stroke_width=0,
                    fill_opacity=1,
                    color=YELLOW,
                )
            )
        
        return mesh



class Lecture12(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)

        # def eq(x, y, z):
        #     return 3 *x + y**2 - z**3
        # def px(x, y, z):
        #     return 3
        # def py(x, y, z):
        #     return 2 * y
        # def pz(x, y, z):
        #     return -3 * z**2

        # def random_point_on_surface(level, bli=(-10,-10,-10), tro=(10,10,10)):
        #     x = random.uniform(bli[0], tro[0])
        #     y = random.uniform(bli[1], tro[1])
        #     z = np.cbrt(3*x + y**2) #depending on the function 
        #     return (x, y, z)

        # mesh = axes.render_level_surface(eq, 10).set_color(TEAL).set_opacity(.4)
        # self.add(mesh)

        # def gen_gradient(level):
        #     head = random_point_on_surface(level)
        #     delvec = np.array([px(*head), py(*head), pz(*head)])
        #     return head, delvec




        # head, delvec = gen_gradient(10)
        # p1dot = Dot().set_color(PURPLE).scale(.5).move_to(axes.c2p(*head))
        # p1vev = Simple3DVec(
        #     axes,
        #     head,
        #     np.array(head)+delvec,
        # ).set_color(PURPLE)
        # self.add(p1dot, p1vev)


        # def eq(x, y):
        #     return 4 - x**2 - y**2

        # def gradient_at(x, y, _):
        #     return np.array([-2*x, -2*y, 0])

        # s = axes.get_parametric_surface(
        #     lambda x, y: [x, y, eq(x, y)],
        #     u_range=(-2, 2),
        #     v_range=(-2, 2),
        #     color=TEAL,
        #     opacity=.4,
        # )
        # self.add(s)

        # sample_at = ValueTracker(np.array([-2, 2, 0]))

        # dir_vec_val = ValueTracker(np.array([3, 2, 0]))
        # dir_vec_start_post = sample_at


        # def get_end_position(start, end):
        #     vec = end - start
        #     magnitude = np.linalg.norm(vec)
        #     return start + vec/magnitude

        # dir_vec = always_redraw(
        #     lambda: Simple3DVec(
        #         axes,
        #         start=dir_vec_start_post.get_value(),
        #         end=get_end_position(dir_vec_start_post.get_value() ,dir_vec_val.get_value()),
        #         color=RED,
        #     )
        # )


        # def get_dir_curve():
        #     dirx, diry, _ = get_end_position(dir_vec_start_post.get_value() ,dir_vec_val.get_value())
        #     passx, passy, _ = dir_vec_start_post.get_value()
        #     return axes.get_parametric_curve(
        #         lambda t: [passx + dirx * t, passy + diry * t, eq(passx + dirx * t, passy + diry * t)],
        #         t_range=(-2, 2, 0.1),
        #         color=ORANGE,
        #     )


        # dir_curve = always_redraw(
        #     lambda: get_dir_curve(),
        # )

        # gradient_vec = always_redraw(
        #     lambda: Simple3DVec(
        #         axes,
        #         start=sample_at.get_value(),
        #         end=sample_at.get_value() + gradient_at(*sample_at.get_value()),
        #         color=GREEN,
        #     )
        # )


        # self.add(dir_vec, gradient_vec, dir_curve)
        def eq(x, y):
            return 4 - x**2 - y**2


        def gradient_at(x, y, _):
            return np.array([-2 * x, -2 * y, 0])


        s = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(x, y)],
            u_range=(-2, 2),
            v_range=(-2, 2),
            color=TEAL,
            opacity=0.4,
        )
        self.add(s)


        # Point on the surface (xy coordinates)
        sample_at = ValueTracker(np.array([1, 2, 0]))

        # Direction vector (NOT an endpoint)
        dir_vec_val = ValueTracker(np.array([3, 2, 0]))


        def get_unit_direction():
            d = dir_vec_val.get_value().copy()
            d[2] = 0

            norm = np.linalg.norm(d)
            if norm == 0:
                return np.array([1, 0, 0])

            return d / norm


        dir_vec = always_redraw(
            lambda: Simple3DVec(
                axes,
                start=sample_at.get_value(),
                end=get_unit_direction(),
                color=RED,
            )
        )


        def get_dir_curve():
            px, py, _ = sample_at.get_value()
            dx, dy, _ = get_unit_direction()

            return axes.get_parametric_curve(
                lambda t: [
                    px + dx * t,
                    py + dy * t,
                    eq(px + dx * t, py + dy * t),
                ],
                t_range=(-2, 2, 0.05),
                color=ORANGE,
            )


        dir_curve = always_redraw(get_dir_curve)


        marker = always_redraw(
            lambda: VGroup(
                Dot().set_color(RED).move_to(axes.c2p(sample_at.get_value()[0], sample_at.get_value()[1], eq(sample_at.get_value()[0], sample_at.get_value()[1]))),
                Line(start=axes.c2p(sample_at.get_value()[0], sample_at.get_value()[1], 0),
                     end=axes.c2p(sample_at.get_value()[0], sample_at.get_value()[1], eq(sample_at.get_value()[0], sample_at.get_value()[1])),
                     color=RED,
                     ),
                )
        )
        gradient_vec = always_redraw(
            lambda: Simple3DVec(
                axes,
                start=sample_at.get_value(),
                end=gradient_at(*sample_at.get_value()),
                color=GREEN,
            )
        )


        self.add(dir_vec, gradient_vec, dir_curve, marker)

        self.embed()

class GasLeak(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)


        s = axes.get_parametric_surface(
            lambda x, y: [x, y, gas_leek_eq(x, y)],
            u_range=(-5, 5),
            v_range=(-5, 5),
            opacity=.3,
        )

        x_lines = [
            axes.get_parametric_curve(
                lambda x: [x, yy*.25, gas_leek_eq(x, yy * .25)],
                t_range=(-5, 5, 0.05),
                color=YELLOW,
                stroke_opacity=.5
            ) for yy in range(-20, 20)
        ]
        y_lines = [
            axes.get_parametric_curve(
                lambda y: [xx * .25, y, gas_leek_eq(xx * .25, y)],
                t_range=(-5, 5, 0.05),
                color=GREEN,
                stroke_opacity=.5,
            ) for xx in range(-20, 20)
        ]

        self.add(s, *x_lines, *y_lines)

        eng_plane_pos = ValueTracker(np.array([3, 2]))
        eng_marker = always_redraw(
            lambda: Dot().set_color(PINK).scale(.4).move_to(axes.c2p(*eng_plane_pos.get_value(), gas_leek_eq(*eng_plane_pos.get_value())))
        )

        self.add(eng_marker)

        gradient_vec = ValueTracker(np.array([-eng_plane_pos.get_value()[0], -2 * eng_plane_pos.get_value()[1]]))
        gradient_vec_line = always_redraw(
            lambda: Simple3DVec(
                axes, [*eng_plane_pos.get_value(), gas_leek_eq(*eng_plane_pos.get_value())],
                 np.array([*gradient_vec.get_value(), 0]), color=WHITE,
            )
        )
        self.add(gradient_vec_line)


        s1 = axes.render_contour((-5, 5), (-5, 5), gas_leek_eq(*eng_plane_pos.get_value()), gas_leek_eq, 0.05, PURPLE)
        self.add(s1)

        s2 = axes.render_contour((-5, 5), (-5, 5), gas_leek_eq(*eng_plane_pos.get_value())+.4, gas_leek_eq, 0.05, PURPLE)
        self.add(s2)


        curve_along_gradient = always_redraw(
            lambda: axes.get_parametric_curve(
                lambda t: [
                        eng_plane_pos.get_value()[0] + t * gradient_vec.get_value()[0],
                        eng_plane_pos.get_value()[1] + t * gradient_vec.get_value()[1],
                        gas_leek_eq(
                            eng_plane_pos.get_value()[0] + t * gradient_vec.get_value()[0],
                            eng_plane_pos.get_value()[1] + t * gradient_vec.get_value()[1],
                        )
                        ],
                t_range=(-4, 4, 0.1),
                color=ORANGE,
            )
        )
        self.add(curve_along_gradient)

        self.embed()

class HeatedMetalPlate(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)

        s =  axes.get_parametric_surface(
            lambda x, y: [x, y, heated_metal_plate_eq(x, y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
        )
        self.add(s)


        x_graph_at = lambda y, color: axes.get_parametric_curve(
            lambda x: [x, y, heated_metal_plate_eq(x, y)],
            t_range=(-4, 4, 0.05),
            color=color,
        )
        y_graph_at = lambda x, color: axes.get_parametric_curve(
            lambda y: [x, y, heated_metal_plate_eq(x, y)],
            t_range=(-4, 4, 0.05),
            color=color,
        )

        x_values = [y * .2 for y in range(-20, 20)]
        y_values = [x * .2 for x in range(-20, 20)]

        x_colors = color_gradient([BLUE, RED], len(y_values))
        y_colors = color_gradient([YELLOW, ORANGE], len(y_values))

        x_graphs = [x_graph_at(y, color) for y, color in zip(y_values, x_colors)]
        y_graphs = [y_graph_at(x, color) for x, color in zip(x_values, y_colors)]
        # self.add(*x_graphs, *y_graphs)
        # self.frame.reorient(0, 90, 0)

        robot_pos = ValueTracker(np.array([2, 3]))
        robot_marker = always_redraw(
            lambda: Dot().scale(1).set_color(RED).move_to(axes.c2p(*robot_pos.get_value(), heated_metal_plate_eq(*robot_pos.get_value())))
        )
        self.add(robot_marker)

        lcs = [axes.render_contour((-5, 5), (-5, 5), heated_metal_plate_eq(*robot_pos.get_value() + buff * .2), heated_metal_plate_eq, 0.04) for buff in range(-4, 4)]
        self.add(*lcs)

        gvec = always_redraw(
            lambda: Simple3DVec(
                axes, np.array([*robot_pos.get_value(), heated_metal_plate_eq(*robot_pos.get_value())]), np.array([*heated_metal_plate_gradient_eq(*robot_pos.get_value()), 0])
            )
        )

        self.add(gvec)

        hottest_direction = always_redraw(
            lambda: Simple3DVec(
                axes,
                np.array([*robot_pos.get_value(), heated_metal_plate_eq(*robot_pos.get_value())]),
                np.array([*heated_metal_plate_gradient_eq(*robot_pos.get_value()), 0])/np.linalg.norm(heated_metal_plate_gradient_eq(*robot_pos.get_value())),
                color=PURPLE,
            )
        )

        self.add(hottest_direction)

        coldest_direction = always_redraw(
            lambda: Simple3DVec(
                axes,
                np.array([*robot_pos.get_value(), heated_metal_plate_eq(*robot_pos.get_value())]),
                -np.array([*heated_metal_plate_gradient_eq(*robot_pos.get_value()), 0])/np.linalg.norm(heated_metal_plate_gradient_eq(*robot_pos.get_value())),
                color=ORANGE,
            )
        )

        self.add(coldest_direction)

        curve_at_gradient = always_redraw(
            lambda: axes.get_parametric_curve(
                lambda s: [robot_pos.get_value()[0] - s, robot_pos.get_value()[1] + 2 *s, heated_metal_plate_eq(robot_pos.get_value()[0] - s, robot_pos.get_value()[1] + 2 *s)],
                t_range=(-4, 4, 0.05),
                color=GREEN,
            )
        )

        self.add(curve_at_gradient)


        tangent_line = always_redraw(
            lambda: axes.get_parametric_curve(
                lambda s: [robot_pos.get_value()[0] - 2 * s, robot_pos.get_value()[1] - s, heated_metal_plate_eq(*robot_pos.get_value())],
                t_range=(-4, 4, 0.05),
                color=PINK,
            )
        )

        self.add(tangent_line)
        self.embed()



class DroneInTemperatureField(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)
        
        drone_path_curve = axes.get_parametric_curve(
            lambda t: [t, np.sin(t), t/2],
            t_range=(-5, 10, 0.05),
            color=TEAL,
        )

        drone_marker = always_redraw(lambda: Dot().set_color(ORANGE).move_to(drone_path_curve.get_end()))
        self.add(drone_marker)

        self.frame.reorient(50, 50, 0)


        gradient_vec = always_redraw(
            lambda: Simple3DVec(
                axes,
                drone_path_curve.get_end(),
                drone_path_curve.get_end() + np.array([3, 2, -1]),
                color=YELLOW,
            )
        )
        self.wait(5)
        self.add(gradient_vec)
        self.play(ShowCreation(drone_path_curve), run_time=4, rate_func=linear)

        self.embed()

class ElectricPotential(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)


        s = axes.get_parametric_surface(
            lambda x, y: [x, y, electric_potential_eq(x, y)],
            u_range=(-5, 5),
            v_range=(-5, 5),
        )

        self.add(s)

        marker_x = 1
        marker_y = 2
        marker_pos = np.array([marker_x, marker_y])
        marker = Dot().set_color(PURPLE).move_to(axes.c2p(*marker_pos, electric_potential_eq(*marker_pos)))
        self.add(marker)

        
        gradient = np.array([
            (marker_x**2 + marker_y**2 + 1)**(-3/2) * (-marker_x*ELECTRIC_FIELD_AT_0), (marker_x**2 + marker_y**2 + 1)**(-3/2) * (-marker_y*ELECTRIC_FIELD_AT_0)
            ,0])

        gradient_vec = Simple3DVec(
            axes,
            np.array([*marker_pos, electric_potential_eq(*marker_pos)]),
            gradient,
            color=WHITE,
        )
        gradient_vec_unit = Simple3DVec(
            axes,
            np.array([*marker_pos, electric_potential_eq(*marker_pos)]),
            gradient/np.linalg.norm(gradient),
            color=RED,
        )

        self.add(gradient_vec_unit, gradient_vec)

        levels = [
            axes.render_contour((-5, 5), (-5, 5), electric_potential_eq(*marker_pos) + 0.25 * buff,electric_potential_eq, 0.05) for buff in range(-4, 4)
        ]

        self.add(*levels)
        self.embed()


class MinMaxReview(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)


        X_SCALER = .2
        Y_SCALER = .4
        eq = lambda x, y: (X_SCALER * x**2) - (Y_SCALER * y**2)

        partial_x = lambda x, y: 2 * X_SCALER * x
        partial_y = lambda x, y: - 2 * Y_SCALER * y

        s = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(x, y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
            color=ORANGE,
            opacity=.15,
        )
        self.add(s)

        marker_pos = np.array([1, -1, eq(1, -1)])
        marker = Dot().set_color(BLUE).move_to(axes.c2p(*marker_pos))

        x_curve = axes.get_parametric_curve(
            lambda x: [x, marker_pos[1], eq(x, marker_pos[1])],
            t_range=(-4, 4, 0.05),
            color=YELLOW,
            stroke_opacity=.5,
        )
        x_tangent = axes.get_parametric_curve(
            lambda x: [x, marker_pos[1], (x - marker_pos[0])*partial_x(*marker_pos[0:2]) + eq(*marker_pos[0:2])],
            t_range=(marker_pos[0] - 1, marker_pos[0] + 1, 0.05),
            color=YELLOW,
        )

        y_curve = axes.get_parametric_curve(
            lambda y: [marker_pos[0], y, eq(marker_pos[1], y)],
            t_range=(-4, 4, 0.05),
            color=GREEN,
            stroke_opacity=.5,
        )
        y_tangent = axes.get_parametric_curve(
            lambda y: [marker_pos[0], y, (y - marker_pos[1]) * partial_y(*marker_pos[0:2]) + eq(*marker_pos[0:2])],
            t_range=(marker_pos[1] - 1, marker_pos[1] + 1, 0.05),
            color=GREEN,
        )

        self.add(x_curve, y_curve, x_tangent, y_tangent, marker)

        fake_height_for_rendering = 0.01
        tangent_plane = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(*marker_pos[0:2]) + partial_x(*marker_pos[0:2])*(x - marker_pos[0]) + partial_y(*marker_pos[0:2])*(y - marker_pos[1]) + fake_height_for_rendering],
            u_range=(marker_pos[0] - 0.25, marker_pos[0] + .25),
            v_range=(marker_pos[1] - .25, marker_pos[1] + .25),
        )
        self.add(tangent_plane)


        self.embed()


class LagrangeMultiplier(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)

        def eq(x, y):
            return 3 - (1/2) * x**2 - (1/4) * y**2


        s = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(x, y)],
            u_range=(-2, 2),
            v_range=(-2, 2),
            color=ORANGE,
            opacity=.3,
        )
        self.add(s)


        gx = lambda t: 2 * np.cos(t)
        gy = lambda t: 2 * np.sin(t)

        gc = axes.get_parametric_curve(
            lambda t: [gx(t), gy(t), 0],
            t_range=(0, TAU, 0.05),
        )
        self.add(gc)

        c = axes.get_parametric_curve(
            lambda t: [gx(t), gy(t), eq(gx(t), gy(t))],
            t_range=(0, TAU, 0.05),
            color=GREEN,
        )
        self.add(c)


        slider = ValueTracker(PI/4)

        marker_pos = ValueTracker(np.array([gx(slider.get_value()), gy(slider.get_value()), eq(gx(slider.get_value()), gy(slider.get_value()))]))

        marker = always_redraw(
            lambda: Sphere().scale(.1).set_color(RED).move_to(axes.c2p(*marker_pos.get_value()))
        )

        self.add(marker)


class Climber(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)

        def eq(x, y):
            return  10 - x**2 - 2 * y**2

        mounten = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(x, y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
            color=GREEN_D,
            opacity=.4
        )
        self.add(mounten)


        t_range=(0, 6, 0.05)
        gx_eq = lambda t: t - 3
        gy_eq = lambda t: 5 - t

        gc = axes.get_parametric_curve(
            lambda t: [gx_eq(t),gy_eq(t), 0],
            t_range=t_range,
            color=YELLOW,
        )

        self.add(gc)

        trace = axes.get_parametric_curve(
            lambda t: [gx_eq(t), gy_eq(t), eq(gx_eq(t), gy_eq(t))],
            t_range=t_range,
            color=PINK,
        )
        self.add(trace)



        t = ValueTracker(0)
        marker = always_redraw(
            lambda: Line(
                start=axes.c2p(gx_eq(t.get_value()), gy_eq(t.get_value()), 0),
                end=axes.c2p(gx_eq(t.get_value()), gy_eq(t.get_value()), eq(gx_eq(t.get_value()), gy_eq(t.get_value()))),
            )
        )

        self.add(marker)

        def gradient_eq(t):
            return np.array([-2 * gx_eq(t), -4 * gy_eq(t), 0])

        gv = always_redraw(
            lambda: Simple3DVec(
                axes,
                start=np.array([gx_eq(t.get_value()), gy_eq(t.get_value()), eq(gx_eq(t.get_value()), gy_eq(t.get_value()))]),
                end=gradient_eq(t.get_value()),
                color=RED,
            )
        )

        def dir_gradient(t):
            return np.array([1, 1, 0])


        dir_gv = always_redraw(
            lambda: Simple3DVec(
                axes,
                start=np.array([gx_eq(t.get_value()), gy_eq(t.get_value()), 0]),
                end=dir_gradient(t.get_value()),
                color=PURPLE,
            )
        )
        self.add(dir_gv)

        self.add(gv)

        self.embed()


class Submarine(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)


        s = axes.get_parametric_surface(
            lambda x, y: [x, y, submaric_lagrange_eq(x, y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
            color=BLUE,
            opacity=.4,
        )
        self.add(s)


        self.c1_level = 2
        self.axes = axes
        self.c1 = axes.render_contour(
            (-4, 4), (-4, 4), self.c1_level, submaric_lagrange_eq, 0.05
        )
        self.add(self.c1)


        def gx_eq(t):
            return 2 * np.cos(t)

        def gy_eq(t):
            return np.sin(t)

        t_range=(0, TAU, 0.05)
        gc = axes.get_parametric_curve(
            lambda t: [gx_eq(t), gy_eq(t), 0],
            t_range=t_range,
            color=WHITE,
        )
        self.add(gc)

        tc = axes.get_parametric_curve(
            lambda t: [gx_eq(t), gy_eq(t), submaric_lagrange_eq(gx_eq(t), gy_eq(t))],
            t_range=t_range,
            color=RED,
        )
        self.add(tc)

        t = ValueTracker(0)
        height = always_redraw(
            lambda: Line(
                start=axes.c2p(*[gx_eq(t.get_value()), gy_eq(t.get_value()), 0]),
                end=axes.c2p(*[gx_eq(t.get_value()), gy_eq(t.get_value()), submaric_lagrange_eq(gx_eq(t.get_value()), gy_eq(t.get_value()))]),
                color=YELLOW,
            )
        )
        self.add(height)

        self.embed()

    def on_key_press(self, symbol, modifiers):
        key_pressed = ''
        try:
            key_pressed = chr(symbol)
        except:
            print("invalid key")
            return

        match key_pressed:
            case 'w':
                self.remove(self.c1)
                self.c1_level += 0.2
                self.c1 = self.axes.render_contour(
                    (-4, 4), (-4, 4), self.c1_level, submaric_lagrange_eq, 0.05
                )
                self.add(self.c1)
            case 's':
                self.remove(self.c1)
                self.c1_level -= 0.2
                self.c1 = self.axes.render_contour(
                    (-4, 4), (-4, 4), self.c1_level, submaric_lagrange_eq, 0.05
                )
                self.add(self.c1)
            case _:
                return



class Lecture14(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)

        self.level = 8
        self.axes = axes
        self.level_s = axes.render_level_surface(
            lec14_eq, self.level, color=TEAL
        ).set_opacity(.4)
        self.add(self.level_s)
        marker = Sphere().scale(.3).set_color(RED).move_to(axes.c2p(2, 3, 1))
        self.add(marker)

        self.embed()

    def on_key_press(self, symbol, modifiers):
        char = chr(symbol)
        match char:
            case 'w':
                self.remove(self.level_s)
                self.level += .2
                self.level_s = self.axes.render_level_surface(
                    lec14_eq, self.level,
                ).set_opacity(.4).set_color(TEAL)
                self.add(self.level_s)
            case 's':
                self.remove(self.level_s)
                self.level -= .2
                self.level_s = self.axes.render_level_surface(
                    lec14_eq, self.level
                ).set_opacity(.4).set_color(BLUE)
                self.add(self.level_s)

class SafestPoint(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)


        A = (8)
        B = (3)
        C = (2)
        D = (2)

        def original_eq(x, y):
            return 4 + (A)*x - (B)*x**2 - (C) * y**2 + (D) * x * y

        s = axes.get_parametric_surface(
            lambda x, y:[x, y, original_eq(x, y)],
            color=TEAL,
            opacity=.4,
            u_range=(-4, 4),
            v_range=(-4, 4),
        )
        self.add(s)

        def get_zx(y, color):
            return axes.get_parametric_curve(
                lambda x: [x, y, original_eq(x, y)],
                t_range=(-4, 4, 0.05),
                color=color
            )

        y_range=(-4, 4)
        step = 0.1
        cs = []
        current_y = y_range[0]

        colors = color_gradient([BLUE, RED], int((y_range[1]-y_range[0])/step) + 1)

        i = 0
        while current_y <= y_range[1]:
            cs.append(get_zx(current_y, color=colors[i]))
            current_y += step
            i += 1

        self.add(*cs)

        crt_point = np.array([8/5, 4/5])
        crt = Dot().move_to(axes.c2p(*crt_point, original_eq(*crt_point))).set_color(WHITE)
        self.add(crt)


class MinMaxTest(InteractiveScene):
    def construct(self):
        axes = MyThreedAxes(
                activeScene=self,
                x_custom=True,
                y_custom=True,
                z_custom=True,
                x_axis_config={
                    'color':RED,
                    'include_tip':True,
                },
                y_axis_config={
                    'color':GREEN,
                    'include_tip':True,
                },
                z_axis_config={
                    'color':BLUE,
                    'include_tip':True,
                },
        )

        axes.toggle_planes()
        self.add(axes)
        


        def eq(x, y):
            return 2 + (1) * x + (1/2)*y

        s = axes.get_parametric_surface(
            lambda x, y:[x, y, eq(x,y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
            opacity=.3,
            color=WHITE,
        )
        self.add(s)

        pos = np.array([2, 1])
        delta_x, delta_y = (.5, .5)

        s1 = axes.get_parametric_surface(
            lambda x, y:[x, y, eq(x,y)+0.05],
            u_range=(pos[0]-delta_x, pos[0]+delta_x),
            v_range=(pos[1]-delta_y, pos[1]+delta_y),
            color=ORANGE,
        )
        d = Dot().move_to(axes.c2p(*pos, eq(*pos)))

        self.add(s1, d)


class Approximation2D(InteractiveScene):
    def construct(self):
        axes = Axes()
        self.add(axes)


        A = ValueTracker(1)
        pos = ValueTracker(1)

        def eq(x):
            return A.get_value() * (x**2)


        # act 1
        c = always_redraw(lambda: axes.get_graph(
            lambda x: eq(x),
            x_range=(-4, 4, 0.05),
            color=RED,
        ))

        marker = always_redraw(lambda: Dot().scale(.2).move_to(axes.c2p(pos.get_value(), eq(pos.get_value()))).set_color(WHITE))
        marker_l = always_redraw(
            lambda: VGroup().add(DashedLine(
                start=axes.c2p(pos.get_value(), eq(pos.get_value())),
                end=axes.c2p(pos.get_value(), 0),
                color=WHITE,
            )).add(
                Tex("x0").scale(.2).move_to(axes.c2p(pos.get_value(), -0.1)).set_color(WHITE)
            )
        )

        delta_x = .5
        def ap0(x):
            return eq(pos.get_value())

        ap0_c = always_redraw(lambda: axes.get_graph(
            lambda x: ap0(x),
            x_range=(pos.get_value() - delta_x, pos.get_value()+delta_x, 0.05),
            color=YELLOW,
        ))


        dx = ValueTracker(0.05)

        diff_line = always_redraw(
            lambda: Line(
                start=axes.c2p(pos.get_value() + dx.get_value(), eq(pos.get_value()+dx.get_value())),
                end=axes.c2p(pos.get_value() + dx.get_value(), ap0(pos.get_value()+dx.get_value())),
                color=BLUE,
            )
        )

        self.add(c)
        self.add(ap0_c)
        self.add(marker, marker_l, diff_line)


        equations = VGroup()
        equations.add(
            Tex(R"""
            y = f(x)
            """).set_color(RED)
            )
        equations.add(Tex(r"g(x) \simeq f(x0)").set_color(YELLOW))
        equations.add(
            Tex(R"""
            diff = f(x0 + dx) - g(x0 + dx)
            """).set_color(BLUE)
            )
        equations.fix_in_frame()
        equations.arrange(DOWN)

        equations.to_edge(UL)
        self.add(equations)

        self.play(
            self.frame.animate.reorient(0, 0, 0, (pos.get_value(), eq(pos.get_value()), 0), 1),
            run_time=4
        )

        self.wait(2)
        self.play(dx.animate.set_value(-0.2), run_time=2)
        self.wait(2)
        self.play(dx.animate.set_value(0.2), run_time=2)
