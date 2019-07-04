import os
import random
import time
import math

from adafruit_display_text import label
import board
import displayio
import neopixel
import terminalio
import touchio


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
WHITE = (255, 255, 255)

def mix(color_1, color_2, weight_2):
    """
    Blend between two colors with a given ratio.
    @param color_1:  first color, as an (r,g,b) tuple
    @param color_2:  second color, as an (r,g,b) tuple
    @param weight_2: Blend weight (ratio) of second color, 0.0 to 1.0
    @return: (r,g,b) tuple, blended color
    """
    if weight_2 < 0.0:
        weight_2 = 0.0
    elif weight_2 > 1.0:
        weight_2 = 1.0
    weight_1 = 1.0 - weight_2
    return (int(color_1[0] * weight_1 + color_2[0] * weight_2),
            int(color_1[1] * weight_1 + color_2[1] * weight_2),
            int(color_1[2] * weight_1 + color_2[2] * weight_2))

class Animation:
    # @abstractmethod
    def step(self):
        pass

class ScrollingRedWhitBlue(Animation):
    def __init__(self, strip):
        self.__strip = strip
        self.__strip.fill(0)
        self.__strip.show()

        self.COLORS = [0]*self.__strip.n
        for index in range(10):
            self.COLORS[index] = RED
            self.COLORS[index+10] = WHITE
            self.COLORS[index+20] = BLUE

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

class PulsingRedWhitBlue(Animation):
    def __init__(self, strip):
        self.__strip = strip
        self.__strip.fill(0)
        self.__strip.show()

        self.COLORS = [RED, WHITE, BLUE]
        self.INCREMENT_MAGNITUDE = 0.02
        self.BRIGHTNESS_MAX = 0.4
        self.__brightness = 0
        self.__increment = self.INCREMENT_MAGNITUDE
        self.__color_index = 0

    def step(self):
        self.__strip.brightness = self.__brightness
        self.__strip.fill(self.COLORS[self.__color_index])
        self.__strip.show()
        self.__brightness += self.__increment
        if self.__brightness > self.BRIGHTNESS_MAX:
            self.__brightness = self.BRIGHTNESS_MAX
            self.__increment = -self.__increment
        elif self.__brightness < 0:
            self.__brightness = 0
            self.__increment = -self.__increment
            self.__color_index += 1
            if self.__color_index >= 3:
                self.__color_index = 0

class RainbowExplosion(Animation):
    def __init__(self, strip):
        self.__strip = strip
        self.__strip.fill(0)
        self.__strip.show()

        self.COLORS = [0]*self.__strip.n
        third_range = self.__strip.n / 3.0
        for index in range(self.__strip.n):
            if index < int(third_range):
                self.COLORS[index] = mix(RED, GREEN, index/third_range)
            elif index < int(2*third_range):
                self.COLORS[index] = mix(GREEN, BLUE, (index-third_range)/third_range)
            else:
                self.COLORS[index] = mix(BLUE, PURPLE, (index-2*third_range)/third_range)

        self.__stage = int(0)
        self.__index = 0

    def step(self):
        if self.__stage == 0:
            self.__strip[self.__index] = WHITE
            self.__strip[self.__strip.n-self.__index-1] = WHITE
            if self.__index > 0:
                self.__strip[self.__index-1] = (0,0,0)
                self.__strip[self.__strip.n-self.__index] = (0,0,0)
            self.__strip.show()
            self.__index += 1
            if self.__index >= self.__strip.n/2:
                self.__index = 0
                self.__strip.fill(0)
                self.__strip.show()
                self.__stage += 1
        elif self.__stage == 1:
            self.__strip[random.randint(0, self.__strip.n-1)] = self.COLORS[random.randint(0, self.__strip.n-1)]
            self.__strip.show()
            self.__index += 1
            if self.__index >= 2*self.__strip.n:
                self.__index = 0
                self.__strip.fill(0)
                self.__strip.show()
                self.__stage += 1
        # elif self.__stage == 2:
        #     self.__strip[self.__index] = self.COLORS[self.__index]
        #     self.__strip.show()

        #     self.__index += 1
        #     if self.__index >= self.__strip.n:
        #         self.__index = 0
        #         self.__strip.fill(0)
        #         self.__strip.show()
        #         self.__stage += 1
        if self.__stage > 1:
            self.__stage = 0


class WavingFlag(Animation):
    def __init__(self, display):
        self.__display = display
        self.__sprite = displayio.Group()
        self.__display.show(self.__sprite)
        self.__tiles = []
        self.__filenames = ['images/'+filename for filename in os.listdir('images/') if filename.endswith('.bmp')]
        self.__filenames.sort()
        self.__index = 0
        self.__lead_pixel = 0

    def step(self):
        # text_area = label.Label(terminalio.FONT, text='Loading {}'.format(filename))
        # text_area.x = 10
        # text_area.y = 10
        # self.__display.show(text_area)        # for filename in filenames:

        sprite = displayio.Group()
        with open(self.__filenames[self.__index], "rb") as file:
            image = displayio.OnDiskBitmap(file)
            tile = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
            sprite.append(tile)
            self.__display.show(sprite)
            self.__display.wait_for_frame()
        # if len(self.__sprite) > 1:
        #     self.__sprite.pop()
        self.__index += 1
        if self.__index >= len(self.__filenames):
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
    strip_animations = [ScrollingRedWhitBlue, PulsingRedWhitBlue, RainbowExplosion]
    display_animation = WavingFlag(board.DISPLAY)
    display_animation.step()
    animation_index = 0
    strip_animation = strip_animations[animation_index](strip)
    start_time = time.time()
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

        lapsed_time = time.time() - start_time
        if lapsed_time > 20:
            start_time = time.time()
            animation_index += 1
            if animation_index >= len(strip_animations):
                animation_index = 0
            strip_animation = strip_animations[animation_index](strip)
        strip_animation.step()

if __name__ == '__main__':
    main()
