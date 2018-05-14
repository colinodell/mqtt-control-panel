import os

import pygame

from alarmpanel.button import STATE_DEFAULT

BACKLIGHT_CONTROL = '/sys/class/backlight/soc:backlight/brightness'

# A simple UI which only redraws parts of the screen as needed (faster than redrawing the whole screen all the time)
class UI:
    def __init__(self, background = None):
        # Init framebuffer/touchscreen environment variables
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_FBDEV', '/dev/fb1')
        os.putenv('SDL_MOUSEDRV', 'TSLIB')
        os.putenv('SDL_MOUSEDEV', '/dev/input/event0')

        self._backlight_on = True
        self.on()

        # Init pygame and screen
        print "Initting..."
        pygame.init()
        print "Setting Mouse invisible..."
        pygame.mouse.set_visible(False)
        print "Setting fullscreen..."
        modes = pygame.display.list_modes(16)
        self._screen = pygame.display.set_mode(modes[0], pygame.FULLSCREEN, 16)
        self._needs_update = True

        # Load background
        self._background = pygame.image.load(background)
        self._screen.fill(0)
        self._screen.blit(self._background, (0, 0))
        pygame.display.update()

        # Load font
        self._font = pygame.font.SysFont("Arial", 24)

        self._images = []
        self._buttons = []
        self._status_lines = []

        self.update()

    def blit(self, *args, **kwargs):
        self._screen.blit(*args, **kwargs)
        self.schedule_update()

    def blit_background(self, rect):
        self._screen.blit(self._background, rect, rect)
        self.schedule_update()

    def load_images(self, path):
        import fnmatch
        from alarmpanel.image import Image

        for file in os.listdir(path):
            if fnmatch.fnmatch(file, '*.png'):
                name = file.split('.')[0]
                self._images.append(Image(path, name))

    def create_button(self, rect, **kwargs):
        from alarmpanel import Button

        button = Button(self, rect, **kwargs)

        for buttonState, imageFile in button.imageFiles.iteritems():  # For each image name defined on the button...
            for image in self._images:  # For each icon...
                if imageFile == image.name:  # Compare names; match?
                    button.bitmaps[buttonState] = image.bitmap  # Assign Icon to Button
                    button.imageFiles[buttonState] = None  # Name no longer used; allow garbage collection

        button.draw()

        self._buttons.append(button)

        return button

    def create_status_line(self, rect, color=(255, 255, 255)):
        from alarmpanel import StatusLine
        status_line = StatusLine(self, pygame.Rect(rect), color)

        self._status_lines.append(status_line)

        return status_line

    def render_text(self, text, color):
        return self._font.render(text, 1, color)

    def schedule_update(self):
        self._needs_update = True

    def update(self):
        if self._needs_update:
            self._needs_update = False
            pygame.display.update()

    def process_input(self):
        # Process touchscreen input
        from alarmpanel.button import STATE_PRESSED
        for event in pygame.event.get():
            if event.type is pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for b in self._buttons:
                    if b.down(pos): break
            elif event.type is pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                for b in self._buttons:
                    if b.up(pos): pass
                    # Redraw other buttons which might be stuck in the down position
                    elif b.state == STATE_PRESSED:
                        b.set_state(STATE_DEFAULT)

    def off(self):
        if self._backlight_on:
            print "Turning display off"
            with open(BACKLIGHT_CONTROL, 'w') as f:
                f.write('0')
            self._backlight_on = False

    def on(self):
        if not self._backlight_on:
            print "Turning display on"
            with open(BACKLIGHT_CONTROL, 'w') as f:
                f.write('1')
            self._backlight_on = True
