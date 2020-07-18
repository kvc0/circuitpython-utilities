import math
import time

import displayio
import vectorio

import random


# This example demonstrates some of the features in `vectorio`.
#
# It was written for a Feather M4 Express with an ST7789 320x240 display.
#
# Individually scheduled active shapes:
# * Randart polygon
#     Makes 40 random points on the left side of the screen
#     and interprets them as directed points on a Polygon.
#     Updates every 5 seconds.
# * Wobbly star polygon
#     Shows how to make a star with polygon points (it's like
#     how you'd draw a regular 5 point star by hand) and
#     animates it at 6hz.
# * Orbiting circle
#     A circle that travels around the wobbly star (occasionally
#     eclipsing a point or two) and changes radius over time.


def run():
    RED = 0xff0000
    GREEN = 0x00ff00
    VIOLET = 0xEE82EE
    BACKGROUND = 0xA0A000

    # Initialize the hardware
    display = get_display()
    group = displayio.Group(max_size=10)

    # Assemble the displaygroup (only using 1)
    new_randart_fn = append_randart_shape(group, color=BACKGROUND)
    wobble_star_fn = append_wobbly_star_shape(group, color=RED)
    revolve_circle_fn, resize_circle_fn = append_circle_shape(group, color=GREEN)
    # Add a thing to revolve the circle under
    group.append(
        vectorio.VectorShape(
            shape=vectorio.Polygon(points=[(0, 0), (18, 32), (-10, 20)]),
            pixel_shader=monochrome(0xA0B0C0),
            x=110,
            y=65
        )
    )
    append_vectorio_shape(group, color=VIOLET)

    # Schedule the animations
    new_randart_fn = rate_limited(hz=1/5)(new_randart_fn)
    wobble_star_fn = rate_limited(hz=6)(wobble_star_fn)
    resize_circle_fn = rate_limited(hz=7)(resize_circle_fn)
    revolve_circle_fn = rate_limited(hz=20)(revolve_circle_fn)

    # And turn on the display
    display.brightness = 1
    display.show(group)

    # Now drive the scheduled animations forever
    while True:
        new_randart_fn()
        wobble_star_fn()
        resize_circle_fn()
        revolve_circle_fn()


# ############ Application coroutine constructors ############ #

def append_randart_shape(group: displayio.Group, color):
    # Make a random polygon to sit on the left side of the screen.
    # We'll update its points every now and then with the returned function.
    random_polygon = vectorio.Polygon(
        points=[(random.randrange(0, 100), random.randrange(0, 240)) for _ in range(40)]
    )
    random_shape = vectorio.VectorShape(
        shape=random_polygon,
        pixel_shader=monochrome(color),
    )
    group.append(random_shape)

    def new_randart():
        random_polygon.points = [(random.randrange(0, 100), random.randrange(0, 240)) for _ in range(40)]

    return new_randart


def append_wobbly_star_shape(group: displayio.Group, color):
    # Make a wobbly star.  The returned function wobbles its points a little.
    wobbly_star_points = [
        (8, 50),
        (33, 0),
        (58, 50),
        (0, 20),
        (66, 20),
    ]
    star_center_x = 170 - 25
    star_center_y = 120 - 33
    wobbly_star_polygon = vectorio.Polygon(points=wobbly_star_points)
    wobbly_star_shape = vectorio.VectorShape(
        shape=wobbly_star_polygon,
        pixel_shader=monochrome(color),
        x=star_center_x,
        y=star_center_y
    )
    group.append(wobbly_star_shape)

    def make_star_wobble():
        tremble = 4
        shake = 3
        trembling_points = [
            (random.randrange(x - tremble, x + tremble), random.randrange(y - tremble, y + tremble))
             for x,  y in wobbly_star_points
        ]
        wobbly_star_polygon.points = trembling_points
        wobbly_star_shape.x = random.randrange(star_center_x - shake, star_center_x + shake)
        wobbly_star_shape.y = random.randrange(star_center_y - shake, star_center_y + shake)

    return make_star_wobble


def append_circle_shape(group: displayio.Group, color):
    # Make a circle that will revolve around the star while changing size
    min_circle_radius = 5
    max_circle_radius = 20
    circle_axis = 170, 120
    circle_revolution_radius = 60
    circle = vectorio.Circle(radius=max_circle_radius)
    circle_shape = vectorio.VectorShape(
        shape=circle,
        pixel_shader=monochrome(color),
        x=circle_axis[0], y=circle_axis[1]
    )
    group.append(circle_shape)

    radians_in_circle = 2 * math.pi

    def revolve_circle():
        seconds_per_revolution = 8
        revolution_ratio = (time.monotonic() % seconds_per_revolution) / seconds_per_revolution
        revolution_radians = revolution_ratio * radians_in_circle
        s = math.sin(revolution_radians)
        c = math.cos(revolution_radians)
        x = s * circle_revolution_radius + circle_axis[0]
        y = c * circle_revolution_radius + circle_axis[1]
        circle_shape.x = round(x)
        circle_shape.y = round(y)

    def resize_circle():
        seconds_per_size_cycle = 13
        size_ratio = abs(int(time.monotonic() % (
                    2 * seconds_per_size_cycle) / seconds_per_size_cycle) - time.monotonic() % seconds_per_size_cycle / seconds_per_size_cycle)
        new_radius = min_circle_radius + size_ratio * (max_circle_radius - min_circle_radius)
        circle.radius = int(new_radius)

    return revolve_circle, resize_circle


def append_vectorio_shape(group: displayio.Group, color):
    # Making fonts with vector points is a pain but the memory benefits are pretty nice.
    # Also you can rotate points for spinny text if you want!
    v_polygon = vectorio.Polygon(
        points=[
            (0, 0), (10, 0),
            (18, 24),
            (26, 0), (36, 0),
            (22, 34), (10, 34),
        ]
    )
    v_shape = vectorio.VectorShape(
        shape=v_polygon,
        pixel_shader=monochrome(color),
        x=160, y=16
    )
    group.append(v_shape)


# ############ Copy pastas and support code ############ #

def monochrome(color):
    """
    :return: A palette for a vectorio shape
    """
    palette = displayio.Palette(2)
    palette.make_transparent(0)
    palette[1] = color
    return palette


def rate_limited(hz: float):
    """
    Pasted from https://github.com/WarriorOfWire/circuitpython-utilities/blob/master/functional/rate_limited.py
    """
    def decorator_rate_limit(decorated_fn):
        last_invocation = 0
        nanos_per_invocation = 1000000000 / hz
        rate_limited_value = None

        def rate_limited_fn(*args, **kwargs):
            nonlocal last_invocation
            nonlocal rate_limited_value
            now = time.monotonic_ns()
            if now - last_invocation > nanos_per_invocation:
                # Normally we can schedule at the intended rate.
                last_invocation += nanos_per_invocation
                if last_invocation + nanos_per_invocation < now:
                    # If we're falling behind, fall back to "with fixed delay"
                    last_invocation = now
                rate_limited_value = decorated_fn(*args, **kwargs)
            return rate_limited_value
        return rate_limited_fn
    return decorator_rate_limit


def get_display():
    """
    :return: displayio.Display
    """
    from adafruit_st7789 import ST7789
    import board
    displayio.release_displays()
    spi = board.SPI()
    tft_cs = board.D4
    tft_dc = board.D12
    tft_reset = board.D13
    tft_backlight = board.D11
    spi.try_lock()
    spi.configure(baudrate=24000000)
    spi.unlock()
    display_bus = displayio.FourWire(
        spi,
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_reset,
        baudrate=24000000
    )
    # https://circuitpython.readthedocs.io/en/4.x/shared-bindings/displayio/Display.html
    display = ST7789(
        display_bus,
        width=320,
        height=240,
        rotation=90,
        backlight_pin=tft_backlight,
        brightness=0,
    )
    return display


if __name__ == '__main__':
    run()
