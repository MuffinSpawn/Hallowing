import os
import time
import math

import board
import displayio
import neopixel
import touchio

class Animation:
    # @abstractmethod
    def step(self):
        pass

class ScrollingRedWhitBlue(Animation):
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)

    def __init__(self, strip):
        self.__strip = strip

        self.COLORS = [0]*self.__strip.n
        for index in range(10):
            self.COLORS[index] = self.RED
            self.COLORS[index+10] = self.WHITE
            self.COLORS[index+20] = self.BLUE

        self.__lead_pixel = 0

    def step(self):
        for index in range(self.__strip.n):
            pixel = self.__lead_pixel + index
            if pixel >= self.__strip.n:
                pixel = pixel - self.__strip.n
            self.__strip[pixel] = self.COLORS[index]
        self.__strip.show()
        self.__lead_pixel += 1
        if self.__lead_pixel >= self.__strip.n:
            self.__lead_pixel = 0

class WavingFlag(Animation):
    def __init__(self, display):
        self.__display = display
        self.__sprite = displayio.Group()
        self.__display.show(self.__sprite)
        self.__tiles = []
        filenames = [filename for filename in os.listdir('images/') if filename.endswith('.bmp')].sort()
        for filename in filenames:
            with open(filename, "rb") as file:
                image = displayio.OnDiskBitmap(file)
                tile = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
                self.__tiles.append(tile)
        self.__index = 0
        self.__lead_pixel = 0

    def step(self):
        self.__sprite.append(self.__tiles[self.__index])
        self.__display.wait_for_frame()
        self.__sprite.pop()
        self.__index += 1
        if self.__index >= len(self.__tiles):
            self.__index = 0

def main():
    NUM_PIXELS = 30                        # NeoPixel strip length (in pixels)
    NEOPIXEL_PIN = board.EXTERNAL_NEOPIXEL # Pin where NeoPixels are connected
    strip = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=0.01, auto_write=False)

    board.DISPLAY.brightness = 1.0

    increase_brightness_pad = touchio.TouchIn(board.A5)
    decrease_brightness_pad = touchio.TouchIn(board.A2)

    DELAY = 0.0
    BRIGHTNESS_INCREMENT = 0.01

    brightness = 0.01
    strip_animation = ScrollingRedWhitBlue(strip)
    display_animation = WavingFlag(board.DISPLAY)
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

        strip_animation.step()
        display_animation.step()

if __name__ == '__main__':
    main()
