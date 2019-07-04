import time
import math
import board
import neopixel
import touchio

NUM_PIXELS = 30                        # NeoPixel strip length (in pixels)
NEOPIXEL_PIN = board.EXTERNAL_NEOPIXEL # Pin where NeoPixels are connected
strip = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=0.01, auto_write=False)

increase_brightness_pad = touchio.TouchIn(board.A5)
decrease_brightness_pad = touchio.TouchIn(board.A2)

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

COLORS = [0]*NUM_PIXELS
for index in range(10):
    COLORS[index] = RED
    COLORS[index+10] = WHITE
    COLORS[index+20] = BLUE

DELAY = 0.0
BRIGHTNESS_INCREMENT = 0.01

lead_pixel = 0
brightness = 0.01
while True:
    if increase_brightness_pad.value:
        brightness += BRIGHTNESS_INCREMENT
        if brightness > 1.0:
            brightness = 1.0
    elif decrease_brightness_pad.value:
        brightness -= BRIGHTNESS_INCREMENT
        if brightness < 0.0:
            brightness = 0.0
    if strip.brightness != brightness:
        strip.brightness = brightness

    for index in range(NUM_PIXELS):
        pixel = lead_pixel + index
        if pixel >= NUM_PIXELS:
            pixel = pixel - NUM_PIXELS
        strip[pixel] = COLORS[index]
    strip.show()
    lead_pixel += 1
    if lead_pixel >= NUM_PIXELS:
        lead_pixel = 0