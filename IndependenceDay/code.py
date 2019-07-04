import time
import math
import board
import neopixel

NUM_PIXELS = 30                        # NeoPixel strip length (in pixels)
NEOPIXEL_PIN = board.EXTERNAL_NEOPIXEL # Pin where NeoPixels are connected
strip = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=0.01, auto_write=False)
strip.fill(0)                          # NeoPixels off ASAP on startup
strip.show()

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

COLORS = [0]*NUM_PIXELS
for index in range(10):
    COLORS[index] = RED
    COLORS[index+10] = WHITE
    COLORS[index+20] = BLUE

DELAY = 0.0

lead_pixel = 0
while True:
    # strip.brightness = 0.05 * lead_pixel / NUM_PIXELS
    for index in range(NUM_PIXELS):
        pixel = lead_pixel + index
        if pixel >= NUM_PIXELS:
            pixel = pixel - NUM_PIXELS
        strip[pixel] = COLORS[index]
    strip.show()
    lead_pixel += 1
    if lead_pixel >= NUM_PIXELS:
        lead_pixel = 0