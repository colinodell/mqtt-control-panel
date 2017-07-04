import RPi.GPIO as GPIO
import time


class Motion:
    def __init__(self, ui, pin, timeout=30):
        self._ui = ui
        self._pin = int(pin)
        self._timeout = int(timeout)
        self._last_motion = time.time()

        GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
        GPIO.setup(self._pin, GPIO.IN)

    def check(self):
        now = time.time()
        if GPIO.input(self._pin):
            self._last_motion = now

        if (now - self._last_motion) <= self._timeout:
            self._ui.on()
            #if not self._ui.backlight_on:
            #    print "Turning UI on"
        else:
            # elif self._ui.backlight_on:
            self._ui.off()

