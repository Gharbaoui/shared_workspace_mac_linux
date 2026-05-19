from manimlib import *
import numpy as np

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
                opacity=0.5,
                ).set_color_by_gradient(RED, GREEN)

        self.yz_plane = self.get_parametric_surface(
                lambda u, v: np.array([0, u, v]),
                u_range=self.y_range[0:2],
                v_range=self.z_range[0:2],
                opacity=0.5,
                ).set_color_by_gradient(GREEN,BLUE)
        self.zx_plane = self.get_parametric_surface(
                lambda u, v: np.array([u, 0, v]),
                u_range=self.x_range[0:2],
                v_range=self.z_range[0:2],
                opacity=0.5,
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


class Lecture1(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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

        self.add(axes)


class Lecture2(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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

        self.add(axes)


class Lecture3(InteractiveScene):
    def construct(self) -> None:
        self.clear()
        A = np.array([3, -1, 2])
        B = np.array([1, 1, 3])
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

        Avec = Simple3DVec(axes,start=[0, 0, 0],end=A, color=YELLOW)
        Bvec = Simple3DVec(axes,start=[0,0,0],end=B, color=GOLD)
        self.add(Avec)
        self.add(Bvec)

        def det(A, B):
            return A[0] * B[1] - A[1] * B[0]

        def equation1(u, v):
            return ( 
                    -u * det(A[1:], B[1:]) + 
                    v * det([A[0], A[2]], [B[0], B[2]])
                    ) /det(A[0:2], B[0:2])

        pl = axes.get_parametric_surface(
                lambda u, v : [u, v, equation1(u, v)],
                u_range=(-10, 10),
                v_range=(-10, 10),
                )
        ABCross = np.cross(A, B)
        N = ABCross/np.linalg.norm(ABCross)
        def equation2(u, v):
            return ((-u *N[0]) - (v *N[1]))/N[2]

        pl2 = axes.get_parametric_surface(
                lambda u, v : [u, v, equation2(u, v)],
                u_range=(-10, 10),
                v_range=(-10, 10),
                )
        self.add(axes)

class Lecture4(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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


        pl = axes.get_parametric_surface(
                lambda u, v: [u, np.sin(u), v],
                color=PURPLE,
                u_range=(-4, 4),
                v_range=(-4, 4),
                )
        self.add(pl)
        self.add(axes)

class Lecture5(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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

        def det(p0, p1):
            return p0[0] * p1[0] + p0[1] * p1[1] + p0[2] * p1[2]

        P0 = ValueTracker(np.array([1, 2, 1]))
        n = np.array([-1, 2, 1])

        nv = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=P0.get_value(),
                    end=(n + P0.get_value()),
                    color=PURPLE,
                    )
                )
        p0v = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=(0, 0, 0),
                    end=P0.get_value(),
                    color=RED,
                    )
                )
        def equation(x, y):
            return det(n, P0.get_value()) - (n[0]/n[2]) * x - (n[1]/n[2]) * y


        surface = always_redraw(
                lambda: axes.get_parametric_surface(
                    lambda x, y: [x, y, equation(x, y)],
                    u_range=(-3, 3),
                    v_range=(-3, 3),
                    color=[BLUE, YELLOW]
                    )
            )

        self.add(axes)

class Lecture6(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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
        self.add(axes)
        SIM_TIME=20
        UNIT_ROTATION_TIME=5
        RADIUS = .5
        run_time = ValueTracker(0)

        def x(t):
            return RADIUS * (2* np.pi/UNIT_ROTATION_TIME) * t - RADIUS * np.sin(2 * np.pi * t/UNIT_ROTATION_TIME)

        def y(t):
            return RADIUS - RADIUS * np.cos(2 * np.pi * t/UNIT_ROTATION_TIME)

        def R(t):
            return np.array([x(t), y(t), 0]) # 0 for z axes

        def xprime(t):
            return (RADIUS * (2 * np.pi/UNIT_ROTATION_TIME)) * (1 - np.cos(2 * np.pi * t / UNIT_ROTATION_TIME))
        def yprime(t):
            return (RADIUS * 2 * np.pi / UNIT_ROTATION_TIME) * np.sin(2 * np.pi * t/UNIT_ROTATION_TIME)

        def V(t):
            return np.array([xprime(t), yprime(t), 0])

        def xdoubleprimve(t):
            return (RADIUS * (2 * np.pi/UNIT_ROTATION_TIME)) * (2 * np.pi / UNIT_ROTATION_TIME) * np.sin(2 * np.pi * t / UNIT_ROTATION_TIME)
        def ydoubleprime(t):
            return (RADIUS * 2 * np.pi / UNIT_ROTATION_TIME) *2 * np.pi  /UNIT_ROTATION_TIME * np.cos(2 * np.pi * t/UNIT_ROTATION_TIME)
        def A(t):
            return np.array([xdoubleprimve(t), ydoubleprime(t), 0])

        def distance(V):
            return np.sqrt(sum([V[0] * V[0], V[1] * V[1], V[2] * V[2]]))

        RVec = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=(0, 0,0),
                    end=R(run_time.get_value()),
                    color=RED_B,
                    )
                )
        RVecUnit = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=np.array([0, 0, 0]) + R(run_time.get_value()),
                    end=R(run_time.get_value())/distance(R(run_time.get_value())) + R(run_time.get_value()),
                    color=YELLOW,
                    )
                )

        self.add(RVec, RVecUnit)

        VVec = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=R(run_time.get_value()),
                    end=V(run_time.get_value()) + R(run_time.get_value()),
                    color=GREEN,
                    )
                )
        VVecUnit = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=R(run_time.get_value()),
                    end=V(run_time.get_value())/distance(V(run_time.get_value()) ) + R(run_time.get_value()),
                    color=PINK,
                    )
                )

        self.add(VVec, VVecUnit)
        AVec = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=R(run_time.get_value()),
                    end=A(run_time.get_value()) + R(run_time.get_value()),
                    color=PURPLE,
                    )
                )
        AVecUnit = always_redraw(
                lambda: Simple3DVec(
                    axes,
                    start=R(run_time.get_value()),
                    end=A(run_time.get_value())/distance(A(run_time.get_value()) ) + R(run_time.get_value()),
                    color=ORANGE,
                    )
                )

        self.add(AVec, AVecUnit)
        c = always_redraw(
                lambda: axes.get_parametric_curve(
                    lambda t: R(t),
                    t_range=(0, run_time.get_value(), 0.01)
                    )

                )
        self.add(c)
        self.wait(4)
        self.play(run_time.animate.set_value(SIM_TIME), run_time=SIM_TIME, rate_func=linear)

class Lecture7(InteractiveScene):
    def construct(self) -> None:
        self.clear()
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

        p1 = ValueTracker(np.array([1, 2, 3]))
        p2 = ValueTracker(np.array([-1, 0, 3]))
        p3 = ValueTracker(np.array([-1, 0, -3]))
        p4 = ValueTracker(np.array([1, 1, -3]))
        o =  ValueTracker(np.array([-3, 2, 1]))

        def construct_plane(axes, p1, p2, o, color):
            normal = ValueTracker(np.cross(p1.get_value(), p2.get_value())/np.linalg.norm(np.cross(p1.get_value(), p2.get_value())))

            p1v = always_redraw(lambda: Simple3DVec(
                    axes,
                    start=o.get_value(),
                    end=p1.get_value() + o.get_value(),
                    color=GREEN,
                    ))
            p2v = always_redraw(lambda:Simple3DVec(
                    axes,
                    start=o.get_value(),
                    end=p2.get_value() + o.get_value(),
                    color=GREEN,
                    ))
            normalv = always_redraw(lambda:Simple3DVec(
                    axes,
                    start=o.get_value(),
                    end=normal.get_value() + o.get_value(),
                    color=BLUE,
                    ))
            ov = always_redraw(lambda:Simple3DVec(
                    axes,
                    start=np.array([0, 0, 0]),
                    end=o.get_value(),
                    color=YELLOW,
                    ))

            plane = always_redraw(lambda: axes.get_parametric_surface(
                    lambda u, v: [u, v, (np.dot(normal.get_value(), o.get_value()) - normal.get_value()[0]*u - normal.get_value()[1] * v)/normal.get_value()[2]],
                    u_range=(-4, 4),
                    v_range=(-4, 4),
                    color=color,
                    ))
            return p1v, p2v, normalv, ov, plane

        p1v, p2v, normalv1, ov1, plane1 = construct_plane(axes, p1, p2, o, color=YELLOW)
        p3v, p4v, normalv2, ov2, plane2 = construct_plane(axes, p3, p4, o, color=TEAL)

        self.add(axes, p1v, p2v, normalv1, ov1, plane1)
        self.add(axes, p3v, p4v, normalv2, ov2, plane2)
