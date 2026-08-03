from manimlib import *
import random
import numpy as np
import mcubes

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
            axes.c2p(*start), axes.c2p(*end), buff, path_arc, **kwargs
            )

        self.add(self.l)

        self.color = WHITE
        if 'color' in kwargs:
            self.color = kwargs['color']

        self.tip = Dot().move_to(axes.c2p(*end)).set_color(self.color)
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

    def get_line(self, a, b, c, d, level, eq):
        def encode(a, b, c, d, level):
            return (1 if a > level else 0) | (1 if b > level else 0) << 1 | (1 if c > level else 0) << 2 | (1 if d > level else 0) << 3

        def interp(p1, p2, v1, v2, level):
            if abs(v2 - v1) < 1e-12:
                return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

            t = (level - v1) / (v2 - v1)

            return (
                p1[0] + t * (p2[0] - p1[0]),
                p1[1] + t * (p2[1] - p1[1]),
            )
        aval, bval, cval, dval = eq(*a), eq(*b), eq(*c), eq(*d)
        encoding = encode(dval, aval, cval, bval, level)

        ax, ay = a
        bx, by = b
        cx, cy = c
        dx, dy = d

        ab_p = ((ax + bx) / 2, (ay + by) / 2)
        bc_p = ((bx + cx) / 2, (by + cy) / 2)
        cd_p = ((cx + dx) / 2, (cy + dy) / 2)
        ad_p = ((ax + dx) / 2, (ay + dy) / 2)

        match encoding:
            case 0 | 15:
                return (0, None, None, None)

            case 1:
                return (1, (cd_p, ad_p), None, ORANGE)

            case 2:
                return (1, (ab_p, ad_p), None, PINK)

            case 3:
                return (1, (ab_p, cd_p), None, ORANGE)

            case 4:
                return (1, (ab_p, bc_p), None, YELLOW)

            case 5:
                return (
                    2,
                    (ab_p, bc_p),
                    (ad_p, cd_p),
                    YELLOW,
                )

            case 6:
                return (1, (ad_p, bc_p), None, YELLOW)

            case 7:
                return (1, (bc_p, cd_p), None, YELLOW)

            case 8:
                return (1, (bc_p, cd_p), None, YELLOW)

            case 9:
                return (1, (ad_p, bc_p), None, YELLOW)

            case 10:
                return (
                    2,
                    (ab_p, ad_p),
                    (bc_p, cd_p),
                    YELLOW,
                )

            case 11:
                return (1, (ab_p, bc_p), None, YELLOW)

            case 12:
                return (1, (ab_p, cd_p), None, ORANGE)

            case 13:
                return (1, (ab_p, ad_p), None, PINK)

            case 14:
                return (1, (cd_p, ad_p), None, ORANGE)

    def get_contour_lines(self, x_range, y_range, step, level, eq):
        segments = []
        x, x_end = x_range
        while x <= x_end:
            y, y_end = y_range
            while y <= y_end:
                a, b, c, d = (x, y), (x, y + step), (x+step, y+step), (x+step, y)
                aval, bval, cval, dval = eq(x, y), eq(x, y + step), eq(x+step, y+step), eq(x+step, y)
                n, line1, line2, color = self.get_line(a, b, c, d, level, eq)

                lines = []
                if n == 2:
                    segments.append(
                        line1
                    )
                    segments.append(
                        line2
                    )
                elif n == 1:
                    segments.append(line1)
                y += step 
            x += step
        return segments

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


        x_eq = lambda t: 2*t
        x_der = lambda t: 2

        y_eq = lambda t: .5 * t**2
        y_der = lambda t: t

        t_eq = lambda t: x_eq(t)**2 + 1*y_eq(t)
        eq = lambda x, y: x**2 + .5*(y**2)

        px = lambda x, y: 2 * x 
        py = lambda x, y: y

        x_graph = lambda y, color=YELLOW: axes.get_parametric_curve(
            lambda x: [x, y, eq(x, y)],
            t_range=(-2, 2, .1),
            color=color,
        )
        y_graph = lambda x, color=GREEN: axes.get_parametric_curve(
            lambda y: [x, y, eq(x, y)],
            t_range=(-2, 2, .1),
            color=color,
        )

        xs = [x_graph(y * .25) for y in range(-8, 8)]
        ys = [y_graph(x * .25) for x in range(-8, 8)]

        s = axes.get_parametric_surface(
            lambda x, y: [x, y, eq(x, y)],
            u_range=(-2, 2),
            v_range=(-2, 2),
        )
        self.add(s, *xs, *ys)

        self.frame.reorient(0, 0, 0, (0, 0, 0))

        traj = axes.get_parametric_curve(
            lambda t: [x_eq(t), y_eq(t), t_eq(t)],
            t_range=(-2, 2, .1),
            color=PURPLE
        )


        def get_vel_vector(t, dt=.1, color=ORANGE):
            tail_pos = (x_eq(t), y_eq(t), t_eq(t))
            direction = dt*np.array([x_der(t), y_der(t), t_eq(t)])

            start = axes.c2p(*tail_pos)
            end=start+axes.c2p(*direction)

            return Line(
                start=start,
                end=end,
            ).set_color(color)

        def divergent(t, dt=.1, color=RED):
            tail_pos = (x_eq(t), y_eq(t), t_eq(t))
            direction = dt*np.array([px(x_eq(t), y_eq(t)), py(x_eq(t), y_eq(t)), t_eq(t)])

            start = axes.c2p(*tail_pos)
            end=start+axes.c2p(*direction)

            return Line(
                start=start,
                end=end,
            ).set_color(color)


        self.play(ShowCreation(traj), run_time=3, rate_func=linear)

        r_vel = get_vel_vector(0.2)
        di_vel = divergent(0.2)
        self.add(r_vel, di_vel)
        
        self.embed()


# class Lecture1(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         self.add(axes)


# class Lecture2(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         self.add(axes)


# class Lecture3(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         A = np.array([3, -1, 2])
#         B = np.array([1, 1, 3])
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         Avec = Simple3DVec(axes,start=[0, 0, 0],end=A, color=YELLOW)
#         Bvec = Simple3DVec(axes,start=[0,0,0],end=B, color=GOLD)
#         self.add(Avec)
#         self.add(Bvec)

#         def det(A, B):
#             return A[0] * B[1] - A[1] * B[0]

#         def equation1(u, v):
#             return ( 
#                     -u * det(A[1:], B[1:]) + 
#                     v * det([A[0], A[2]], [B[0], B[2]])
#                     ) /det(A[0:2], B[0:2])

#         pl = axes.get_parametric_surface(
#                 lambda u, v : [u, v, equation1(u, v)],
#                 u_range=(-10, 10),
#                 v_range=(-10, 10),
#                 )
#         ABCross = np.cross(A, B)
#         N = ABCross/np.linalg.norm(ABCross)
#         def equation2(u, v):
#             return ((-u *N[0]) - (v *N[1]))/N[2]

#         pl2 = axes.get_parametric_surface(
#                 lambda u, v : [u, v, equation2(u, v)],
#                 u_range=(-10, 10),
#                 v_range=(-10, 10),
#                 )
#         self.add(axes)

# class Lecture4(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )


#         pl = axes.get_parametric_surface(
#                 lambda u, v: [u, np.sin(u), v],
#                 color=PURPLE,
#                 u_range=(-4, 4),
#                 v_range=(-4, 4),
#                 )
#         self.add(pl)
#         self.add(axes)

# class Lecture5(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         def det(p0, p1):
#             return p0[0] * p1[0] + p0[1] * p1[1] + p0[2] * p1[2]

#         P0 = ValueTracker(np.array([1, 2, 1]))
#         n = np.array([-1, 2, 1])

#         nv = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=P0.get_value(),
#                     end=(n + P0.get_value()),
#                     color=PURPLE,
#                     )
#                 )
#         p0v = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=(0, 0, 0),
#                     end=P0.get_value(),
#                     color=RED,
#                     )
#                 )
#         def equation(x, y):
#             return det(n, P0.get_value()) - (n[0]/n[2]) * x - (n[1]/n[2]) * y


#         surface = always_redraw(
#                 lambda: axes.get_parametric_surface(
#                     lambda x, y: [x, y, equation(x, y)],
#                     u_range=(-3, 3),
#                     v_range=(-3, 3),
#                     color=[BLUE, YELLOW]
#                     )
#             )

#         self.add(axes)

# class Lecture6(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )
#         self.add(axes)
#         SIM_TIME=20
#         UNIT_ROTATION_TIME=5
#         RADIUS = .5
#         run_time = ValueTracker(0)

#         def x(t):
#             return RADIUS * (2* np.pi/UNIT_ROTATION_TIME) * t - RADIUS * np.sin(2 * np.pi * t/UNIT_ROTATION_TIME)

#         def y(t):
#             return RADIUS - RADIUS * np.cos(2 * np.pi * t/UNIT_ROTATION_TIME)

#         def R(t):
#             return np.array([x(t), y(t), 0]) # 0 for z axes

#         def xprime(t):
#             return (RADIUS * (2 * np.pi/UNIT_ROTATION_TIME)) * (1 - np.cos(2 * np.pi * t / UNIT_ROTATION_TIME))
#         def yprime(t):
#             return (RADIUS * 2 * np.pi / UNIT_ROTATION_TIME) * np.sin(2 * np.pi * t/UNIT_ROTATION_TIME)

#         def V(t):
#             return np.array([xprime(t), yprime(t), 0])

#         def xdoubleprimve(t):
#             return (RADIUS * (2 * np.pi/UNIT_ROTATION_TIME)) * (2 * np.pi / UNIT_ROTATION_TIME) * np.sin(2 * np.pi * t / UNIT_ROTATION_TIME)
#         def ydoubleprime(t):
#             return (RADIUS * 2 * np.pi / UNIT_ROTATION_TIME) *2 * np.pi  /UNIT_ROTATION_TIME * np.cos(2 * np.pi * t/UNIT_ROTATION_TIME)
#         def A(t):
#             return np.array([xdoubleprimve(t), ydoubleprime(t), 0])

#         def distance(V):
#             return np.sqrt(sum([V[0] * V[0], V[1] * V[1], V[2] * V[2]]))

#         RVec = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=(0, 0,0),
#                     end=R(run_time.get_value()),
#                     color=RED_B,
#                     )
#                 )
#         RVecUnit = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=np.array([0, 0, 0]) + R(run_time.get_value()),
#                     end=R(run_time.get_value())/distance(R(run_time.get_value())) + R(run_time.get_value()),
#                     color=YELLOW,
#                     )
#                 )

#         self.add(RVec, RVecUnit)

#         VVec = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=R(run_time.get_value()),
#                     end=V(run_time.get_value()) + R(run_time.get_value()),
#                     color=GREEN,
#                     )
#                 )
#         VVecUnit = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=R(run_time.get_value()),
#                     end=V(run_time.get_value())/distance(V(run_time.get_value()) ) + R(run_time.get_value()),
#                     color=PINK,
#                     )
#                 )

#         self.add(VVec, VVecUnit)
#         AVec = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=R(run_time.get_value()),
#                     end=A(run_time.get_value()) + R(run_time.get_value()),
#                     color=PURPLE,
#                     )
#                 )
#         AVecUnit = always_redraw(
#                 lambda: Simple3DVec(
#                     axes,
#                     start=R(run_time.get_value()),
#                     end=A(run_time.get_value())/distance(A(run_time.get_value()) ) + R(run_time.get_value()),
#                     color=ORANGE,
#                     )
#                 )

#         self.add(AVec, AVecUnit)
#         c = always_redraw(
#                 lambda: axes.get_parametric_curve(
#                     lambda t: R(t),
#                     t_range=(0, run_time.get_value(), 0.01)
#                     )

#                 )
#         self.add(c)
#         self.wait(4)
#         self.play(run_time.animate.set_value(SIM_TIME), run_time=SIM_TIME, rate_func=linear)

# class Lecture7(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         p1 = ValueTracker(np.array([1, 2, 3]))
#         p2 = ValueTracker(np.array([-1, 0, 3]))
#         p3 = ValueTracker(np.array([-1, 0, -3]))
#         p4 = ValueTracker(np.array([1, 1, -3]))
#         o =  ValueTracker(np.array([-3, 2, 1]))

#         def construct_plane(axes, p1, p2, o, color):
#             normal = ValueTracker(np.cross(p1.get_value(), p2.get_value())/np.linalg.norm(np.cross(p1.get_value(), p2.get_value())))

#             p1v = always_redraw(lambda: Simple3DVec(
#                     axes,
#                     start=o.get_value(),
#                     end=p1.get_value() + o.get_value(),
#                     color=GREEN,
#                     ))
#             p2v = always_redraw(lambda:Simple3DVec(
#                     axes,
#                     start=o.get_value(),
#                     end=p2.get_value() + o.get_value(),
#                     color=GREEN,
#                     ))
#             normalv = always_redraw(lambda:Simple3DVec(
#                     axes,
#                     start=o.get_value(),
#                     end=normal.get_value() + o.get_value(),
#                     color=BLUE,
#                     ))
#             ov = always_redraw(lambda:Simple3DVec(
#                     axes,
#                     start=np.array([0, 0, 0]),
#                     end=o.get_value(),
#                     color=YELLOW,
#                     ))

#             plane = always_redraw(lambda: axes.get_parametric_surface(
#                     lambda u, v: [u, v, (np.dot(normal.get_value(), o.get_value()) - normal.get_value()[0]*u - normal.get_value()[1] * v)/normal.get_value()[2]],
#                     u_range=(-4, 4),
#                     v_range=(-4, 4),
#                     color=color,
#                     ))
#             return p1v, p2v, normalv, ov, plane

#         p1v, p2v, normalv1, ov1, plane1 = construct_plane(axes, p1, p2, o, color=YELLOW)
#         p3v, p4v, normalv2, ov2, plane2 = construct_plane(axes, p3, p4, o, color=TEAL)

#         self.add(axes, p1v, p2v, normalv1, ov1, plane1)
#         self.add(axes, p3v, p4v, normalv2, ov2, plane2)

# class Lecture8(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )
#         self.add(axes)

#         # function with multiple parameters
#         # f(x, y) = 1 - x^2 - y^2

#         def f(x, y):
#             return 1 - x**2 - y**2

#         plane = axes.get_parametric_surface(
#                 lambda u, v: [v, u, f(u, v)], u_range=(0, 2), v_range=(-2, 2), color=[BLUE, YELLOW],
#                 resolution = (10, 10),
#                 )

#         # trying to workout 
#         # f(x, y) = x^3 * y + y ^2
#         # 1 let's take look at yz
#         # f(z) = P(players role of some x) * y + y ^2


#         # f(x, y) = 1 - x**2 - y**2
#         #zy plane
#         def yz_shapes(xs, color):
#             shapes = []
#             for x in xs:
#                 shapes.append(
#                         axes.get_parametric_curve(
#                             lambda y: [x, y, 1 - x**2 - y**2],
#                             t_range=(-2, 2, 0.1),
#                             color=color,
#                             )
#                         )
#             return shapes

#         def zx_shapes(ys, color):
#             shapes = []
#             for y in ys:
#                 shapes.append(
#                         axes.get_parametric_curve(
#                             lambda x: [x, y, 1 - x**2 - y**2],
#                             t_range=(-2, 2, 0.1),
#                             color=color,
#                             )
#                         )
#             return shapes

#         def xy_shapes(zs, color):
#             shapes = []
#             for z in zs:
#                 shapes.append(
#                         axes.get_parametric_curve(
#                             lambda o: [np.sqrt(1 - z) * np.cos(o), np.sqrt(1 - z) * np.sin(o), z],
#                             t_range=(0, TAU, 0.1),color=color,
#                             )
#                         )
#             return shapes
#         zy = yz_shapes([0.1 * x for x in range(-10, 10)], color=PURPLE)
#         zx = zx_shapes([0.1 * y for y in range(-10, 10)], color=PINK)
#         xy = xy_shapes([0.1 * z for z in range(-10, 10)], color=YELLOW)

#         x_slider = ValueTracker(0.5)
#         y_slider = ValueTracker(-0.3)
#         def eq(x, y):
#             z = 1 - x**2 - y**2
#             return z


#         yz_curve = always_redraw(lambda:yz_shapes([x_slider.get_value()], color=PINK)[0])
#         self.add(yz_curve)

#         zx_curve = always_redraw(lambda:zx_shapes([y_slider.get_value()], color=YELLOW)[0])
#         self.add(zx_curve)

#         xy_curve = always_redraw(lambda:xy_shapes([eq(x_slider.get_value(), y_slider.get_value())], color=WHITE)[0])
#         self.add(xy_curve)

#         def pzx(x):
#             return -2 * x
#         def pzy(y):
#             return -2 * y

#         def new_p_for_pzx(x0, y0, z0, dx):
#             return (x0 + dx, y0, z0 + pzx(x0)*dx)

#         def new_p_for_pzy(x0, y0, z0, dy):
#             return (x0, y0, z0 + pzy(y0)*dy)

#         p0d = always_redraw(lambda:Sphere().scale(.03).set_color(ORANGE).move_to(
#             axes.c2p(x_slider.get_value(), y_slider.get_value(), eq(x_slider.get_value(), y_slider.get_value()))))

#         self.add(p0d)


# class Lecture9(InteractiveScene):
#     def construct(self) -> None:
#         self.clear()
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )
#         self.add(axes)

#         # trying to understand
#         # F(x, y) = x**2 - 2*x*y + 3*y**2 + 3*y**2 + 2*x - 2*y
#         def eq(x, y):
#             return x**2 - 2*x*y + 3*y**2 + 3*y**2 + 2*x - 2*y
    
#         ygraph_slider = ValueTracker(0)
#         ygraph_get = ygraph_slider.get_value
#         xgraph_slider = ValueTracker(0)
#         xgraph_get = xgraph_slider.get_value

#         demo_zx_graph = always_redraw(
#                 lambda: axes.get_parametric_curve(
#                     lambda x: [x, ygraph_get(), eq(x, ygraph_get())],
#                     t_range=(-6, 6, 0.1),
#                     color=YELLOW,
#                     )
#                 ) 
#         demo_zy_graph = always_redraw(
#                 lambda: axes.get_parametric_curve(
#                     lambda y: [xgraph_get(), y, eq(xgraph_get(), y)],
#                     t_range=(-6, 6, 0.1),
#                     color=PURPLE,
#                     )
#                 ) 

#         def get_zx_shapes(start_y, gap, max_y):
#             zx_shapes = VGroup()
#             current_y = start_y
#             while current_y <= max_y:
#                 zx_shapes.add(
#                         axes.get_parametric_curve(
#                             lambda x: [x, current_y, eq(x, current_y)],
#                             t_range=(-4, 4, 0.1),
#                             color=YELLOW,
#                             )
#                         )
#                 current_y += gap
#             return zx_shapes

#         def get_yz_shapes(start_x, gap, max_x):
#             yz_shapes = VGroup()
#             current_x = start_x
#             while current_x <= max_x:
#                 yz_shapes.add(
#                         axes.get_parametric_curve(
#                             lambda y: [current_x, y, eq(current_x, y)],
#                             t_range=(-4, 4, 0.1),
#                             color=PURPLE,
#                             )
#                         )
#                 current_x += gap
#             return yz_shapes

#         zx_shapes = get_zx_shapes(-1, 0.5, 2)
#         yz_shapes = get_yz_shapes(-1, 0.5, 2)
#         self.add(zx_shapes, yz_shapes)

#         surf = axes.get_parametric_surface(
#                 lambda x, y: [x, y, eq(x, y)],
#                 u_range=(-2, 2),
#                 v_range=(-2, 2),
#                 )

#         # min or max any this is where partial derivatives are zero
#         self.add(Sphere().scale(.1).set_color(ORANGE).move_to(axes.c2p(-1, 0, eq(-1, 0))))
        
#         self.add(surf, demo_zx_graph, demo_zy_graph)
#         self.remove(surf)


# class Daily(InteractiveScene):
#     def construct(self) -> None:
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )
#         axes.toggle_planes()
#         self.add(axes)

#         # controls
#         x_slider = ValueTracker(0)
#         y_slider = ValueTracker(0)
#         x_get = x_slider.get_value
#         y_get = y_slider.get_value

#         # f(x, y) = x**2 + y**2
#         def eq(x, y):
#             return x**2 + y**2

#         def eqzx(yget, x):
#             return eq(x, yget())
#         def eqyz(xget, y):
#             return eq(xget(), y)


#         # demo curves
#         zx_curve = always_redraw(
#             lambda: axes.get_parametric_curve(
#                 lambda x: [x, y_get(), eqzx(y_get, x)],
#                 t_range=(-2, 2, 0.1),
#                 color=PURPLE,
#             )
#         )

#         yz_curve = always_redraw(
#             lambda: axes.get_parametric_curve(
#             lambda y: [x_get(), y, eqyz(x_get, y)],
#             t_range=(-2, 2, 0.1),
#             color=YELLOW,
#         ))

#         self.add(zx_curve)
#         self.add(yz_curve)

#         # surface
#         surf = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-2, 2),
#         )
#         self.add(surf)

#         self.clear()
#         # f(x, y) = x**2 - y**2

#         def eq(x, y):
#             return (1/4)*(x**2) - (1/8)*(y**2)

#         def get_zx_curve_at(y, color=PURPLE):
#             return axes.get_parametric_curve(
#                 lambda x: [x, y, eq(x, y)],
#                 t_range=(-2, 2, 0.1),
#                 color=color,
#             )
            
#         def get_yz_curve_at(x, color=PINK):
#             return axes.get_parametric_curve(
#                 lambda y: [x, y, eq(x, y)],
#                 t_range=(-2, 2, 0.1),
#                 color=color,
#             )
#         zx_curve = always_redraw(
#             lambda: get_zx_curve_at(y_get()),
#         )

#         yz_curve = always_redraw(
#             lambda: get_yz_curve_at(x_get()),
#         )

#         zx_range = range(-5, 6)
#         num_of_zx_curve_samples = len(zx_range)
#         zx_colors = color_gradient([YELLOW, PURPLE], num_of_zx_curve_samples)
#         zx_curve_samples = VGroup()
#         zx_curve_samples.add(*[get_zx_curve_at(y*.1, zx_colors[y]) for y in zx_range])

#         axes.toggle_zx_plane()
#         self.add(axes)

#         self.add(zx_curve, zx_curve_samples)
#         self.add(yz_curve)

#         # sruface
#         surf = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             color=PURPLE,
#             u_range=(-2, 2),
#             v_range=(-2, 2),
#         )
#         self.add(surf)


#         self.clear()
#         self.add(axes)


#         # f(x, y) = x + y
#         x_tilt_slider = ValueTracker(1)
#         y_tilt_slider = ValueTracker(1)
#         ytilt = y_tilt_slider.get_value
#         xtilt = x_tilt_slider.get_value
#         x_shift_slider = ValueTracker(1)
#         xshift = x_shift_slider.get_value
#         y_shift_slider = ValueTracker(1)
#         yshift = y_shift_slider.get_value

#         def eq(x, y):
#             return 2 * x - 3 * y
#             # return xtilt()*(x + xshift()) + ytilt()*(y + yshift())

#         def gen_zx_curves(color=YELLOW, start_y=-1, end_y=2, step=.5):
#             shape = VGroup()
#             while start_y <= end_y:
#                 shape.add(
#                     axes.get_parametric_curve(
#                         lambda x: [x, start_y, eq(x, start_y)],
#                         t_range=(-2, 2, 0.1),
#                         color=color,
#                     )
#                 )
#                 start_y += step
#             return shape

#         def gen_yz_curves(color=PURPLE, start_x=-1, end_x=2, step=.5):
#             shape = VGroup()
#             while start_x <= end_x:
#                 shape.add(
#                     axes.get_parametric_curve(
#                         lambda y: [start_x, y, eq(start_x, y)],
#                         t_range=(-2, 2, 0.1),
#                         color=color,
#                     )
#                 )
#                 start_x += step

#             return shape

#         zx_lines = gen_zx_curves(start_y=-2, end_y=2, step=.5)
#         yz_lines = gen_yz_curves(start_x=-2, end_x=2, step=.5)

#         surf_1 = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-0.5, 0.5),
#             color=RED,
#         )


#         surf_2 = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-1, -0.5),
#             color=[TEAL]
#         )

#         surf_3 = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(0.5, 1),
#             color=[PURPLE]
#         )


#         surf = always_redraw(lambda: axes.get_parametric_surface(
#             lambda x, y:[x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-2, 2),
#             color=ORANGE,
#         ))
#         self.add(surf)
#         self.clear()

#         axes.toggle_zx_plane()
#         self.add(axes)

#         # f(x, y) = (x + y)**2
#         x_factor = ValueTracker(1)
#         y_factor = ValueTracker(1)
#         all_factor = ValueTracker(1)
#         eq = lambda x, y: all_factor.get_value() * (x_factor.get_value() * x + y_factor.get_value() * y)**2


#         gen_zx_graph = lambda y, color=YELLOW: axes.get_parametric_curve(
#             lambda x: [x, y, eq(x,y)],
#             t_range=(-4-y, 4-y, 0.1),
#             color=YELLOW,
#         )
         

#         l1 = always_redraw(lambda: gen_zx_graph(0))
#         l2 = always_redraw(lambda: gen_zx_graph(1))
#         l3 = always_redraw(lambda: gen_zx_graph(-1))
#         self.add(l1, l2, l3)
#         axes.toggle_xy_plane()
#         surf = always_redraw(lambda: axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             color=[TEAL, YELLOW, BLUE, RED, ORANGE, GREEN],
#             u_range=(-3, 3),
#             v_range=(-3, 3),
#         ))
#         self.add(surf)
        
#         self.embed()


# class Lecture10(InteractiveScene):
#     def construct(self) -> None:
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )
#         axes.toggle_planes()
#         self.add(axes)

#         def eq(x, y):
#             return  x + y + 1/(x*y)

#         s = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(0.1, 4),
#             v_range=(0.1, 4),
#         )
#         self.add(s)

#         self.embed()

# class TryingToUnderstandWhy_dxdy_same_as_dydx(InteractiveScene):
#     def construct(self):
#         #https://www.youtube.com/watch?v=J08-L2buigM&list=PLSQl0a2vh4HC5feHa6Rc5c0wbRTx56nF7&index=19
#         #https://www.youtube.com/watch?v=DmB8I0TFlc8
#         # axes = MyThreedAxes(
#         #         activeScene=self,
#         #         x_custom=True,
#         #         y_custom=True,
#         #         z_custom=True,
#         #         x_axis_config={
#         #             'color':RED,
#         #             'include_tip':True,
#         #         },
#         #         y_axis_config={
#         #             'color':GREEN,
#         #             'include_tip':True,
#         #         },
#         #         z_axis_config={
#         #             'color':BLUE,
#         #             'include_tip':True,
#         #         },
#         # ).to_edge(RIGHT*1.5)



#         # axes.toggle_planes()
#         # self.add(axes)

#         # # f(x, y) = (x + y)**2
#         # # later f(x, y) = x * y * e**(-(x**2 + y**2)/4)
#         # # df/dxdy = df/dydx
#         # # let's use f(x, y) = x**2 * y**2

#         # def eq(x, y):
#         #     return x**2 * y**4 + 0.5

#         # def partial_x(x, y):
#         #     return 2 * x * y**4
#         # def partial_y(x, y):
#         #     return 4 * y**3 * x**2

#         # surf = axes.get_parametric_surface(
#         #     lambda x, y: [x, y, eq(x, y)],
#         #     u_range=(-1.5, 1.5),
#         #     v_range=(-1.5, 1.5),
#         #     opacity=.3,
#         # )
#         # self.add(surf)

#         # def get_x_curve(y, color=YELLOW):
#         #     return axes.get_parametric_curve(
#         #         lambda x: [x, y, eq(x, y)],
#         #         t_range=(-1.5, 1.5, 0.2),
#         #         color=color,
#         #         stroke_opacity=.5,
#         #     )
#         # def get_y_curve(x, color=GREEN):
#         #     return axes.get_parametric_curve(
#         #         lambda y: [x, y, eq(x, y)],
#         #         t_range=(-1.5, 1.5, 0.2),
#         #         color=color,
#         #         stroke_opacity=.5,
#         #     )

#         # def get_px_curve(y, color=YELLOW):
#         #     return axes.get_parametric_curve(
#         #         lambda x: [x, y, partial_x(x, y)],
#         #         t_range=(-2, 2, 0.1),
#         #         color=color
#         #     )
#         # def get_py_curve(x, color=GREEN):
#         #     return axes.get_parametric_curve(
#         #         lambda y: [x, y, partial_y(x, y)],
#         #         t_range=(-2, 2, 0.1),
#         #         color=color
#         #     )

#         # x_net = [get_x_curve(y * .3) for y in range(-6, 7)]
#         # y_net = [get_y_curve(x * .3) for x in range(-6, 7)]

#         # self.add(*x_net)
#         # self.add(*y_net)

#         # # ref_x, ref_y = (ValueTracker(.6), ValueTracker(-.6))
#         # # mark = always_redraw(lambda: Sphere().move_to(axes.c2p(ref_x.get_value(), ref_y.get_value(), eq(ref_x.get_value(), ref_y.get_value()))).scale(0.05).set_color(ORANGE))
#         # # self.add(mark)

#         # # dx, dy = 0.2, 0.2
#         # # x_slope = partial_x(ref_x.get_value(), ref_y.get_value())
#         # # y_slope = partial_y(ref_x.get_value(), ref_y.get_value())

#         # # x_slope_line = always_redraw(lambda: Line(
#         # #     start=axes.c2p(ref_x.get_value() - dx, ref_y.get_value(), eq(ref_x.get_value(), ref_y.get_value()) - dx * partial_x(ref_x.get_value(), ref_y.get_value())),
#         # #     end=axes.c2p(ref_x.get_value() + dx, ref_y.get_value(), eq(ref_x.get_value(), ref_y.get_value()) + dx * partial_x(ref_x.get_value(), ref_y.get_value())),
#         # #     color=WHITE,
#         # # ))

#         # # y_slope_line = always_redraw(lambda: Line(
#         # #     start=axes.c2p(ref_x.get_value(), ref_y.get_value() - dy, eq(ref_x.get_value(), ref_y.get_value() - dy) - dy * partial_y(ref_x.get_value(), ref_y.get_value())),
#         # #     end=axes.c2p(ref_x.get_value(), ref_y.get_value() + dy, eq(ref_x.get_value(), ref_y.get_value() + dy) + dy * partial_y(ref_x.get_value(), ref_y.get_value())),
#         # #     color=RED,
#         # # ))

#         # # self.add(x_slope_line)
#         # # self.add(y_slope_line)

#         # derxaxes = MyThreedAxes(
#         #         x_range=  (-4.0, 4.0, 1.0),
#         #         activeScene=self,
#         #         x_custom=True,
#         #         y_custom=True,
#         #         z_custom=True,
#         #         x_axis_config={
#         #             'color':RED,
#         #             'include_tip':True,
#         #         },
#         #         y_axis_config={
#         #             'color':GREEN,
#         #             'include_tip':True,
#         #         },
#         #         z_axis_config={
#         #             'color':BLUE,
#         #             'include_tip':True,
#         #         },
#         # ).to_edge(LEFT*1.5)
#         # derxaxes.toggle_planes()
#         # self.add(derxaxes)

#         # deryaxes = MyThreedAxes(
#         #         y_range=  (-2.0, 2.0, 1.0),
#         #         x_range=  (-2.0, 2.0, 1.0),
#         #         activeScene=self,
#         #         x_custom=True,
#         #         y_custom=True,
#         #         z_custom=True,
#         #         x_axis_config={
#         #             'color':RED,
#         #             'include_tip':True,
#         #         },
#         #         y_axis_config={
#         #             'color':GREEN,
#         #             'include_tip':True,
#         #         },
#         #         z_axis_config={
#         #             'color':BLUE,
#         #             'include_tip':True,
#         #         },
#         # ).shift(UP*2)

#         # deryaxes.toggle_planes()
#         # self.add(deryaxes)

#         # fx = derxaxes.get_parametric_surface(
#         #     lambda x, y: [x, y, partial_x(x, y)],
#         #     u_range=(-1.5, 1.5),
#         #     v_range=(-1.5, 1.5),
#         #     color=ORANGE,
#         #     opacity=.5,
#         # )
#         # fy = deryaxes.get_parametric_surface(
#         #     lambda x, y: [x, y, partial_y(x, y)],
#         #     u_range=(-1.5, 1.5),
#         #     v_range=(-1.5, 1.5),
#         #     color=PURPLE,
#         #     opacity=.5,
#         # )

#         # def get_random_point(x_range, y_range, eqs, target_axes, color=WHITE):
#         #     x = random.uniform(*x_range)
#         #     y = random.uniform(*y_range)
#         #     markers = []

#         #     for eq, ax in zip(eqs, target_axes):
#         #         z = eq(x, y)
#         #         markers.append(Sphere().scale(.05).set_color(color).move_to(ax.c2p(x, y, z)))
#         #     return markers

#         # def add_random_point_in_x_surface_slope():
#         #     ms = get_random_point(x_range=(-1, 1), y_range=(-1, 1), eqs=[eq, partial_x], target_axes=[axes, derxaxes])
#         #     self.add(*ms)

#         # s1 = Sphere().scale(.05).set_color(WHITE).move_to(derxaxes.c2p(1, 1, partial_x(1, 1)))

#         # self.add(fx, fy)
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         ).to_edge(RIGHT*1.5)

#         axes.toggle_planes()
#         self.add(axes)

#         scaler = 0.2
#         def eq(x, y):
#             return scaler * x * y

#         def partial_x(x, y):
#             return scaler * y
#         def partial_y(x, y):
#             return scaler * x

#         s = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(0, 3),
#             v_range=(0, 3),
#             color=ORANGE,
#             opacity=.2,
#         )
#         self.add(s)

#         dx, dy = 1, 1
#         x_slope_x_main, x_slope_y_main = ValueTracker(0), ValueTracker(0)
#         x_slope_main = always_redraw(
#             lambda: Line(
#                 start=axes.c2p(
#                     x_slope_x_main.get_value(), x_slope_y_main.get_value(),
#                     eq(x_slope_x_main.get_value(), x_slope_y_main.get_value())),
#                 end=axes.c2p(
#                     x_slope_x_main.get_value() + dx, x_slope_y_main.get_value(),
#                     eq(x_slope_x_main.get_value(), x_slope_y_main.get_value()) + dx * partial_x(x_slope_x_main.get_value(), x_slope_y_main.get_value())),
#                 color=GREEN,
#             )
#         )

#         self.add(Line(
#                 start=axes.c2p(
#                     0, 0,
#                     eq(0,0)),
#                 end=axes.c2p(
#                     0+dx,0,
#                     eq(0, 0) + dx * partial_x(0,0)),
#                 color=GREEN,
#                 ))
 


#         self.add(x_slope_main)

#         y_slope_x_main, y_slope_y_main = ValueTracker(0), ValueTracker(0)
#         y_slope_main = always_redraw(
#             lambda: Line(
#                 start=axes.c2p(
#                     y_slope_x_main.get_value(), y_slope_y_main.get_value(),
#                     eq(y_slope_x_main.get_value(), y_slope_y_main.get_value())),
#                 end=axes.c2p(
#                     y_slope_x_main.get_value(), y_slope_y_main.get_value()+dy,
#                     eq(y_slope_x_main.get_value(), y_slope_y_main.get_value()) + dy * partial_y(y_slope_x_main.get_value(), y_slope_y_main.get_value())),
#                 color=BLUE,
#             )
#         )


#         self.add(
#             Line(
#                 start=axes.c2p(
#                     0, 0,
#                     eq(0,0)),
#                 end=axes.c2p(
#                     0, 0 + dy,
#                     eq(0, 0 + dy * partial_y(0, 0),)),
#                 color=BLUE,
#             ))



#         self.add(y_slope_main)

#         self.play(
#             y_slope_x_main.animate.set_value(1),
#             x_slope_y_main.animate.set_value(1),
#             run_time=2, rate_func=linear,
#             )

#         self.embed()


# class GrantTayler(InteractiveScene):
#     def construct(self):
#         axes = Axes(
#             x_range=(-2*TAU, 2 * TAU, TAU/4),
#         )
#         self.add(axes)

#         def eq(x):
#             return np.cos(x)

#         original_graph = axes.get_graph(
#             lambda x: eq(x),
#             x_range=(-TAU, TAU, 0.05),
#             color=TEAL,
#         )
#         self.add(original_graph)



#         #approximation 1
#         def der_1(x):
#             return -np.sin(x)

#         dx = .2
#         start_x = 0
#         slope_x1 = der_1(start_x)

#         s1 = Line(
#             start=axes.c2p(0 - dx, eq(0) - dx * slope_x1),
#             end=axes.c2p(0+dx, eq(0) + dx * slope_x1),
#             color=YELLOW
#         )
#         self.add(s1)

#         self.embed()




# #TODO when i approximate stuff using tayler series how would i deal with error
# # or at least measure it

# class PracticeAfterLecture10(InteractiveScene):
#     def construct(self):
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         axes.toggle_planes()
#         self.add(axes)

#         def eq(x, y):
#             return x**2 + 4*y**2

#         s = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-2, 2),
#             color=TEAL,
#         )

#         self.add(s)

#         def x_graph(y, color=YELLOW):
#             return axes.get_parametric_curve(
#                 lambda x: [x, y, eq(x, y)],
#                 t_range=(-2, 2, 0.1),
#                 color=color,
#             )

#         def y_graph(x, color=PURPLE):
#             return axes.get_parametric_curve(
#                 lambda y: [x, y, eq(x, y)],
#                 t_range=(-2, 2, 0.1),
#                 color=color,
#             )

#         x_graphs = [x_graph(y*0.25) for y in range(-8, 8)]
#         y_graphs = [y_graph(x* 0.25) for x in range(-8, 8)]
#         self.add(*x_graphs)
#         self.add(*y_graphs)

#         self.clear()

#         self.add(axes)
#         eq = lambda x, y: x**2 - y**2
#         x_graph = lambda y, color=YELLOW: axes.get_parametric_curve(
#             lambda x: [x, y, eq(x, y)],
#             t_range=(-2, 2, 0.1),
#             color=color,
#         )

#         y_graph = lambda x, color=PURPLE: axes.get_parametric_curve(
#             lambda y: [x, y, eq(x, y)],
#             t_range=(-2, 2, 0.1),
#             color=color,
#         )

#         s = axes.get_parametric_surface(
#             lambda x, y: [x, y, eq(x, y)],
#             u_range=(-2, 2),
#             v_range=(-2, 2),
#             color=TEAL,
#         )

#         self.add(s)

#         x_graphs = [x_graph(y*0.5) for y in range(-8, 8)]
#         y_graphs = [y_graph(x* 0.25) for x in range(1)]
#         self.add(*x_graphs)
#         self.add(*y_graphs)


#         self.embed()

# class Lecture11(InteractiveScene):
#     def construct(self):
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         axes.toggle_planes()
#         self.add(axes)
#         def eq(x, y, z):
#             return (x**2 + y**2 + z**2) / 75 

#         def range_on(start, end, step):
#             while start <= end:
#                 yield start
#                 start += step

#         def colored_shape(axes, x_range=(0, 2, 0.1), y_range=(0, 2, .1), z_range=(0, 2, .1), eq=eq):
#             points = []
#             colors = []
#             for x in range_on(*x_range):
#                 for y in range_on(*y_range):
#                     for z in range_on(*z_range):
#                         res = eq(x, y, z)
#                         color = interpolate_color(BLUE, RED, res)
#                         colors.append(color)
#                         points.append(axes.c2p(x, y, z))
#             return  points, colors

#         p, c = colored_shape(axes)
#         d = DotCloud(points=p)
#         d.set_rgba_array_by_color(c)
#         self.add(d)
#         self.embed()


# # @ very important try to have function
# # that takes 3 parameters f(x, y, z)
# # let's plot it and it's output will color at that point
# # see what that get you can we think of it like that 
# # even if we can not visuilize it

# class WorkBookPartialDerivatives(InteractiveScene):
#     def construct(self):
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         )

#         axes.toggle_planes()
#         self.add(axes)

#         eq = lambda x, t : 0.3 * x * np.sin(t)
#         get_zx_graph = lambda t, color=YELLOW: axes.get_parametric_curve(
#             lambda x: [x, t, eq(x, t)],
#             t_range=(-5, 5, 0.1),
#             color=color,
#         )
#         get_yz_graph = lambda x, color=YELLOW: axes.get_parametric_curve(
#             lambda t: [x, t, eq(x, t)],
#             t_range=(-TAU, TAU, 0.1),
#             color=color,
#         )

#         self.frame.reorient(0, 90, 0, (0, 0, 0))
#         zx_samples = [get_zx_graph(t * 1/16 * PI) for t in range(-9*8, 9*8)]


#         s = axes.get_parametric_surface(
#             lambda x, t: [x, t, eq(x, t)],
#             u_range=(-5, 5),
#             v_range=(-2 * TAU, 2 * TAU),
#         )
#         self.add(s)
#         self.add(*zx_samples)


#         # self,
#         # theta_degrees: float | None = None,
#         # phi_degrees: float | None = None,
#         # gamma_degrees: float | None = None,
#         # center: Vect3 | tuple[float, float, float] | None = None,
#         # height: float | None = None



#         # def eq(x, y):
#         #     return 4 * (x ** 3) * (y**2)

#         # get_zx_graph = lambda y, color=YELLOW: axes.get_parametric_curve(
#         #     lambda x: [x, y, eq(x, y)],
#         #     t_range=(-2, 2, 0.1),
#         #     color=color,
#         # )

#         # zx_samples_pos_y = [get_zx_graph(y * .5) for y in range(0, 5)]
#         # zx_samples_neg_y = [get_zx_graph(y * .5, color=PURPLE) for y in range(-5, 1)]

#         # self.frame.reorient(0, 90, 0, (np.float32(-0.0), np.float32(-0.0), np.float32(-0.00)))

#         # for g in zx_samples_pos_y:
#         #     self.play(ShowCreation(g), run_time=1, rate_func=linear)
#         # for g in zx_samples_neg_y:
#         #     self.play(ShowCreation(g), run_time=1, rate_func=linear)

#         # self.play(self.frame.animate.reorient(90, 90, 0, (np.float32(-0.0), np.float32(-0.0), np.float32(-0.00))), run_time=5)

#         # get_yz_graph = lambda x, color=GREEN: axes.get_parametric_curve(
#         #     lambda y: [x, y, eq(x, y)],
#         #     t_range=(-2, 2, 0.1),
#         #     color=color,
#         # )

#         # yz_samples_pos_x = [get_yz_graph(x * .5) for x in range(0, 5)]
#         # yz_samples_neg_x = [get_yz_graph(x * .5, color=ORANGE) for x in range(-5, 1)]


#         # for g in yz_samples_pos_x:
#         #     self.play(ShowCreation(g), run_time=1, rate_func=linear)
#         # for g in yz_samples_neg_x:
#         #     self.play(ShowCreation(g), run_time=1, rate_func=linear)

#         # s = axes.get_parametric_surface(
#         #     lambda x, y: [x, y, eq(x, y)],
#         #     u_range=(-2, 2),
#         #     v_range=(-2, 2),
#         # )
#         # self.add(s)

#         self.embed()


# class TempertureDronExample(InteractiveScene):
#     def construct(self):
#         axes = MyThreedAxes(
#                 activeScene=self,
#                 x_custom=True,
#                 y_custom=True,
#                 z_custom=True,
#                 x_axis_config={
#                     'color':RED,
#                     'include_tip':True,
#                 },
#                 y_axis_config={
#                     'color':GREEN,
#                     'include_tip':True,
#                 },
#                 z_axis_config={
#                     'color':BLUE,
#                     'include_tip':True,
#                 },
#         ).shift(3 * RIGHT)

#         axes.toggle_planes()
#         self.add(axes)

#         # play time
#         play_time_in_sec = 15
#         unit_radius = 1
#         radius_scaler = .2
#         rotation_speed = 2
#         elevation_speed = .25
        
#         # warehouse dimenstions
#         width, height, depth = 4, 6, 4

#         twodaxes = Axes(
#             x_range=(0, play_time_in_sec),
#             y_range=(-1 * unit_radius * radius_scaler * play_time_in_sec, unit_radius * radius_scaler * play_time_in_sec),
#         ).shift(UL + 4 * LEFT).scale(.5)
#         twodaxes.fix_in_frame()
#         self.add(twodaxes)

#         outline_warehouse = Prism(
#             width=width,
#             height=height,
#             depth=depth,
#             opacity=.1,
#             color=WHITE,
#         ).shift(OUT * depth/2 + 3 * RIGHT)

#         self.add(outline_warehouse)

#         x_eq = lambda t: unit_radius * radius_scaler * t * np.cos(t * rotation_speed)
#         y_eq = lambda t: unit_radius * radius_scaler * t * np.sin(t * rotation_speed)
#         z_eq = lambda t: elevation_speed * t

#         t_eq_drone = lambda t: 3 * x_eq(t) + 2 * y_eq(t)  - z_eq(t)

#         x_graph = twodaxes.get_graph(
#             lambda t: x_eq(t),
#             x_range=(0, play_time_in_sec, 0.1),
#             color=RED,
#         ).fix_in_frame()
#         y_graph = twodaxes.get_graph(
#             lambda t: y_eq(t),
#             x_range=(0, play_time_in_sec, 0.1),
#             color=GREEN,
#         ).fix_in_frame()
#         z_graph = twodaxes.get_graph(
#             lambda t: z_eq(t),
#             x_range=(0, play_time_in_sec, 0.1),
#             color=BLUE,
#         ).fix_in_frame()
#         t_dron_graph = twodaxes.get_graph(
#             lambda t: t_eq_drone(t),
#             x_range=(0, play_time_in_sec, .1),
#             color=PURPLE,
#         ).fix_in_frame()
        

#         # random point in time
#         random.seed(time.time())
#         target_time = random.uniform(0, play_time_in_sec)
#         x_marker = Dot().set_color(RED).move_to(twodaxes.c2p(target_time, x_eq(target_time))).fix_in_frame()
#         y_marker = Dot().set_color(GREEN).move_to(twodaxes.c2p(target_time, y_eq(target_time))).fix_in_frame()
#         z_marker = Dot().set_color(BLUE).move_to(twodaxes.c2p(target_time, z_eq(target_time))).fix_in_frame()

#         self.add(x_marker)
#         self.add(y_marker)
#         self.add(z_marker)
#         drone_trajectory = axes.get_parametric_curve(
#             lambda t: [x_eq(t), y_eq(t), z_eq(t)],
#             color=ORANGE,
#             t_range=(0, play_time_in_sec, 0.1),
#         )

#         def eq(x, y, z):
#             return (20 + 3*x + 2*y - z)
#         def color_eq(x, y, z):
#             return eq(x, y, z)/eq(play_time_in_sec, play_time_in_sec, 0)

#         def range_on(start, end, step):
#             while start <= end:
#                 yield start
#                 start += step

#         def colored_shape(axes, x_range=(0, 2, 0.1), y_range=(0, 2, .1), z_range=(0, 2, .1), eq=eq):
#             points = []
#             colors = []
#             for x in range_on(*x_range):
#                 for y in range_on(*y_range):
#                     for z in range_on(*z_range):
#                         res = eq(x, y, z)
#                         color = interpolate_color(BLUE, RED, res)
#                         colors.append(color)
#                         points.append(axes.c2p(x, y, z))
#             return  points, colors

#         # p, c = colored_shape(
#         #     axes,
#         #     x_range=(-1 * unit_radius * radius_scaler * play_time_in_sec, unit_radius * radius_scaler * play_time_in_sec, 0.1),
#         #     y_range=(-1 * unit_radius * radius_scaler * play_time_in_sec, unit_radius * radius_scaler * play_time_in_sec, 0.1),
#         #     z_range=(0, z_eq(play_time_in_sec), 0.1), eq=color_eq)

#         # d = DotCloud(points=p, opacity=.15)

#         # d.set_rgba_array_by_color(c)
#         # self.add(d)

#         self.play(
#             ShowCreation(drone_trajectory),
#             ShowCreation(x_graph),
#             ShowCreation(y_graph),
#             ShowCreation(z_graph),
#             ShowCreation(t_dron_graph),
#             run_time=play_time_in_sec, rate_func=linear)

#         marker = GlowDot().move_to(axes.c2p(x_eq(target_time), y_eq(target_time), z_eq(target_time))).set_color(interpolate_color(BLUE, RED, color_eq(target_time, target_time, target_time)))
#         self.add(marker)

        
#         self.embed()
