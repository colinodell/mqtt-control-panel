# Button is a simple tappable screen region.  Each has:
#  - bounding rect ((X,Y,W,H) in pixels)
#  - a state
#  - image bitmap
#  - optional single callback function
#  - optional single value passed to callback

# Default state for all buttons
STATE_DEFAULT = 0
# State when the button is currently pressed
STATE_PRESSED = 1
# Action buttons: action is available (proper pin has been entered)
STATE_AVAILABLE = 2
# Action buttons: used to indicate which state the alarm is in
STATE_ACTIVE = 3
# The following states are for the pin input indicator
STATE_1 = 4
STATE_2 = 5
STATE_3 = 6
STATE_4_GOOD = 7
STATE_4_BAD = 8


class Button(object):
    def __init__(self, ui, rect, **kwargs):
        self.ui = ui
        self.rect = rect  # Bounds
        self.imageFiles = {}
        self.bitmaps = {} # Lazy-loaded
        self.callback = None  # Callback function
        self.value = None  # Value passed to callback
        self.state = 0
        for key, value in kwargs.iteritems():
            if key == 'imageFiles':
                self.imageFiles = value
            elif key == 'cb':
                self.callback = value
            elif key == 'value':
                self.value = value

    def set_state(self, state):
        if state != self.state:
            self.state = state
            self.draw()

    def down(self, pos):
        if self.selected(pos):
            if self.state == STATE_DEFAULT and self.bitmaps.has_key(STATE_PRESSED):
                self.set_state(STATE_PRESSED)

            if self.callback:
                if self.value is None:
                    self.callback()
                else:
                    self.callback(self.value)

            return True

    def up(self, pos):
        if self.selected(pos) and self.state == STATE_PRESSED:
            self.set_state(STATE_DEFAULT)
            return True

    def selected(self, pos):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        if ((pos[0] >= x1) and (pos[0] <= x2) and
                (pos[1] >= y1) and (pos[1] <= y2)):
            return True
        return False

    def draw(self):
        if self.bitmaps:
            bitmap = self.bitmaps[self.state] if self.state in self.bitmaps else self.bitmaps[0]
            self.ui.blit(bitmap,
                        (self.rect[0] + (self.rect[2] - bitmap.get_width()) / 2,
                         self.rect[1] + (self.rect[3] - bitmap.get_height()) / 2))
