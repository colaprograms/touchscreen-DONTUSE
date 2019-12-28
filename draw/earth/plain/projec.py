import math

def alternateqf(a, b, c):
    return 2 * c / (-b + math.sqrt(b*b - 4*a*c))
    
def pt2sphere(x, y):
    return x * math.sqrt(1/2 - y*y / 6), y * math.sqrt(1/2 - x*x/6), math.sqrt(1 - x*x/2 - y*y/2 + x*x*y*y/3)

def sphere2pt(x, y):
    xplane = alternateqf(1/2, y*y - 3/2 - x*x, 3 * x*x)
    yplane = alternateqf(1/2, x*x - 3/2 - y*y, 3 * y*y)
    return math.copysign(math.sqrt(xplane), x), math.copysign(math.sqrt(yplane), y)

def _cmp(a, b, c):
    b2 = b * b
    c2 = c * c
    return a * math.sqrt(1 - b2 / 2 - c2 / 2 + b2 * c2 / 3)

def pt_to_sphere(x, y, z):
    return _cmp(x, y, z), _cmp(y, z, x), _cmp(z, x, y)

# z = 1

"""
X = x/2 - xy/6
Y = y/2 - xy/6

X = x/2 (1 - y/3)
x = 2X / (1 - y/3)

Y = y/2 (1 - x/3) = y/2 (1 - 2X/(3-y)) =

(3-y) Y = y/2 (3 - y) - yX

yy/2 + y(-Y - 3/2 + X) + 3Y = 0

(Y - 3/2 - X) +- sqrt((-Y + 3/2 + X)^2 - 6Y) over 1
yy - 3y/2 - yx - 3y/2 + 9/4 + 3x/2 -xy + 3x/2 + xx + 6y
yy + 3y - 2xy + 9/4 + 3x + xx
"""

def test(many=300000):
    import random
    for i in range(many):
        x, y = 2 * random.random() - 1, 2 * random.random() - 1
        a, b, _ = pt2sphere(x, y)
        x1, y1 = sphere2pt(a, b)
        if abs(x - x1) > 1e-12 or abs(y - y1) > 1e-12:
            print("error")
            print(f"\t{x} {y}")
            print(f"\t{x1} {y1}")
            