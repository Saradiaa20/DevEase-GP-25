import os

def very_long_function(a, b, c, d, e, f, g):
    x = 0
    for i in range(100):
        if i > 10:
            if i > 20:
                if i > 30:
                    if i > 40:
                        x += 999  # magic number
    return x


def duplicate1():
    x = 1
    y = 2
    return x + y


def duplicate2():
    x = 1
    y = 2
    return x + y


def infinite():
    while True:
        break