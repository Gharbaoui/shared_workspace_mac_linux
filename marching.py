import numpy as np
from concurrent.futures import ProcessPoolExecutor
import os

workers = os.cpu_count()

def encode(a, b, c, d, level):
    return (1 if a > level else 0) | (1 if b > level else 0) << 1 | (1 if c > level else 0) << 2 | (1 if d > level else 0) << 3

def get_line(a, b, c, d, aval, bval, cval, dval, level):
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
            return (0, None, None)

        case 1:
            return (1, (cd_p, ad_p), None)

        case 2:
            return (1, (ab_p, ad_p), None)

        case 3:
            return (1, (ab_p, cd_p), None)

        case 4:
            return (1, (ab_p, bc_p), None)

        case 5:
            return (
                2,
                (ab_p, bc_p),
                (ad_p, cd_p)
            )

        case 6:
            return (1, (ad_p, bc_p), None)

        case 7:
            return (1, (bc_p, cd_p), None)

        case 8:
            return (1, (bc_p, cd_p), None)

        case 9:
            return (1, (ad_p, bc_p), None)

        case 10:
            return (
                2,
                (ab_p, ad_p),
                (bc_p, cd_p),
            )

        case 11:
            return (1, (ab_p, bc_p), None)

        case 12:
            return (1, (ab_p, cd_p), None)

        case 13:
            return (1, (ab_p, ad_p), None)

        case 14:
            return (1, (cd_p, ad_p), None)




def get_contour_lines_serial(x_range, y_range, step, level, eq):
    segments = []
    x, x_end = x_range
    while x <= x_end:
        y, y_end = y_range
        while y <= y_end:
            a, b, c, d = (x, y), (x, y + step), (x+step, y+step), (x+step, y)
            aval, bval, cval, dval = eq(x, y), eq(x, y + step), eq(x+step, y+step), eq(x+step, y)
            n, line1, line2 = get_line(a, b, c, d, aval, bval, cval, dval, level)

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


def get_contour_lines(x_range, y_range, step, level, eq):
    with ProcessPoolExecutor(workers) as pool:
        futures = []
        x_start, x_end = x_range
        chunk_width = (x_end - x_start)/workers

        for i in range(workers):
            xs = x_start + i * chunk_width
            xe = x_start + (i + 1) * chunk_width
            futures.append(
                pool.submit(
                    get_contour_lines_serial,
                    (xs, xe),
                    y_range,
                    step,
                    level,
                    eq
                )
            )

        segments = []
        for f in futures:
            segments.extend(f.result())
        return segments

def circle_eq(x, y):
    return x**2 + y

GAS_LEEK_SHIFT_UP_BY = 10
def gas_leek_eq(x, y):
    return GAS_LEEK_SHIFT_UP_BY - .5 * x**2 - y**2

METAL_SHIFT_UP_BY = 4
METAL_STRETCH = 1 
def heated_metal_plate_eq(x, y):
    return METAL_SHIFT_UP_BY + METAL_STRETCH * x*y - METAL_STRETCH * x**2

def heated_metal_plate_gradient_eq(x, y):
    return np.array([y - 2 * x, x])


def review_dir_vec_eq(x, y, z):
    return x**2 + y**2 - z**2

ELECTRIC_FIELD_AT_0 = 5
def electric_potential_eq(x, y):
    return ELECTRIC_FIELD_AT_0/np.sqrt(x**2 + y**2 + 1)

def submaric_lagrange_eq(x, y):
    return 4 - x**2 - y**2


def lec14_eq(x, y, z):
    return x**2 + y*z + z**3

def safest_point_eq(x, y):
    return (4 + 8*x + 2 * x * y) - (3 * x**2 + 2 * y**2)

def expr_eq(x, y):
    return 4 - (3 * x**2 + 2 * y**2) + (8) * x + (0 * x * y)

def expr_eq_1(x, y):
    return 4 - (3 * x**2 + 2 * y**2) + (8) * x + (10 * x * y)
