from manimlib import *
import random
import numpy as np
import mcubes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marching import get_contour_lines, circle_eq, gas_leek_eq, GAS_LEEK_SHIFT_UP_BY, heated_metal_plate_eq, METAL_SHIFT_UP_BY, METAL_STRETCH

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

        def gradient_eq(x, y):
            return np.array([-x, -2*y, 0])

        s = axes.get_parametric_surface(
            lambda x, y: [x, y, gas_leek_eq(x, y)],
            u_range=(-4, 4),
            v_range=(-4, 4),
            color=BLUE,
            opacity=.4,
        )

        self.add(s)
        engineer_initil_pos = np.array([3, 2])
        con_at_engineer_feet = gas_leek_eq(*engineer_initil_pos)
        engineer = Dot().move_to(axes.c2p(*engineer_initil_pos, con_at_engineer_feet))
        self.add(engineer)


        def draw_gradient_at(x, y):
            return Simple3DVec(
                axes,
                start=np.array([x, y, con_at_engineer_feet]),
                end=gradient_eq(x, y) + np.array([0, 0, 0]),
                color=GREEN,
            )

        gvec = draw_gradient_at(*engineer_initil_pos)
        self.add(gvec)
        level_contour = axes.render_contour((-6, 6), (-6, 6), con_at_engineer_feet, gas_leek_eq, 0.01)
        self.add(level_contour)


        def counter_level_traversal_eq(t, l):
            return np.array([np.sqrt(2 * (GAS_LEEK_SHIFT_UP_BY - l)) * np.cos(t), np.sqrt(GAS_LEEK_SHIFT_UP_BY - l) * np.sin(t), l])

        start_t = np.arccos(engineer_initil_pos[0]/np.sqrt(2 * (GAS_LEEK_SHIFT_UP_BY - con_at_engineer_feet)))
        end_t = start_t + TAU
        c = axes.get_parametric_curve(
            lambda t: counter_level_traversal_eq(t, con_at_engineer_feet),
            t_range=(start_t, end_t, 0.05),
            color=RED,
        )

        def get_traversal_vec(x, y):
            t = np.arccos(x/np.sqrt(2 * (GAS_LEEK_SHIFT_UP_BY - con_at_engineer_feet)))
            dr = np.array([-np.sqrt(2 * (GAS_LEEK_SHIFT_UP_BY - con_at_engineer_feet)) * np.sin(t), np.sqrt(GAS_LEEK_SHIFT_UP_BY - con_at_engineer_feet) * np.cos(t), 0])
            v = Simple3DVec(
                axes,
                np.array([*engineer_initil_pos, con_at_engineer_feet]),
                dr,
            )
            return v

        movement_vector = get_traversal_vec(*engineer_initil_pos)
        self.add(movement_vector)
        self.play(ShowCreation(c), run_time=3, rate_func=linear)

        def get_direction_vector_at(x, y, dx, dy, color=ORANGE):
            level = gas_leek_eq(x, y)
            start = np.array([x, y, level])
            end = np.array([dx, dy, 0])
            return Simple3DVec(
                axes,
                start,
                end/np.linalg.norm(end),
                color=color,
            )

        direction_vector_value = ValueTracker(np.array([-3, -4]))
        direction_vector = always_redraw(lambda: get_direction_vector_at(*engineer_initil_pos, *direction_vector_value.get_value()))
        curve_along_direction = always_redraw(
            lambda: axes.get_parametric_curve(
                lambda t: [*((t * direction_vector_value.get_value()) + engineer_initil_pos), gas_leek_eq(*((t * direction_vector_value.get_value()) + engineer_initil_pos))],
                t_range=(-4, 4, 0.05),
                color=ORANGE,
            )
        )
        self.add(direction_vector, curve_along_direction)


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

        def gradient_eq(x, y):
            return np.array([y - METAL_STRETCH*2*x, x, 0])

        ## trying to understand surface xy - x**2
        # def zx_eq(x, y):
        #     return METAL_SHIFT_UP_BY + x * y - METAL_STRETCH * x**2

        def get_zx_graph(y, color=ORANGE):
            return axes.get_parametric_curve(
                lambda x: [x, y, heated_metal_plate_eq(x, y)],
                t_range=(-4+y, 2+4, 0.05),
                color=color,
            )

        s = axes.get_parametric_surface(
            lambda x, y: [x, y, heated_metal_plate_eq(x, y)],
            u_range=(-5, 5),
            v_range=(-5, 5),
            color=TEAL,
            opacity=.3,
        )
        self.add(s)

        zxs = [get_zx_graph(y * .5) for y in range(-10, 10)]
        self.add(*zxs)
        self.frame.reorient(0.0, 90.0, 0.0, (0, 0, 0))

        target_point = np.array([2, 3])
        target_pos = np.array([*target_point, heated_metal_plate_eq(*target_point)])


        contour = axes.render_contour((-5, 5), (-5, 5), target_pos[-1], heated_metal_plate_eq, step=0.05)
        self.add(contour)

        marker = Dot().scale(.5).set_color(GREEN).move_to(axes.c2p(*target_pos))
        self.add(marker)


        def get_gradient_vec(x, y, z):
            direction = gradient_eq(x, y)
            return Simple3DVec(
                axes,
                start=np.array([x, y, z]),
                end=direction,
                color=RED,
            ), Simple3DVec(
                axes,
                start=np.array([x, y, z]),
                end=direction/np.linalg.norm(direction),
                color=MAROON,
            ), Simple3DVec(
                axes,
                start=np.array([x, y, z]),
                end=-direction/np.linalg.norm(-direction),
                color=PURPLE,
            )
        gvec, hottest, coolest = get_gradient_vec(*target_pos)
        self.add(gvec, hottest, coolest)

        direction = gradient_eq(*target_point)
        direction = direction/np.linalg.norm(direction)
        nochange_dir = Simple3DVec(
            axes,
            start=target_pos,
            end=np.array([direction[1], -direction[0], direction[2]]),
            color=PINK,
        )
        self.add(nochange_dir)

        self.embed()
