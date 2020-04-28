import time

# Default event list
from metrics import timer

_do_nothing = tuple()


class RotaryButton:
    def __init__(self, rotary, button,
                 on_increment: list = _do_nothing,
                 on_click: list = _do_nothing,
                 longhold_duration: float = 0.3,
                 on_longhold_hold: list = _do_nothing,
                 on_longhold_release: list = _do_nothing
    ):
        """
        Wraps an Adafruit rotary encoder with events.  Call loop() on this when you want to invoke your callbacks if
          the button has been pressed.
        https://www.adafruit.com/product/377

        :param rotary: a rotaryio.RotaryEncoder
        :param button: a digital pin adafruit_debouncer.Debounce
        :param on_click: void ()
        :param longhold_duration: float seconds: Shorter than this is a click, longer than this is a "longhold"
        :param on_longhold_hold: void ()
        :param on_longhold_release: void ()
        :param on_increment: void (int amount)
        """
        self._rotary = rotary
        self._button = button
        self.on_click = on_click
        self._longhold_duration = longhold_duration
        self.on_longhold_hold = on_longhold_hold
        self.on_longhold_release = on_longhold_release
        self.on_increment = on_increment
        self._rotaryposition = rotary.position
        self._current_press_start = None
        self._longheld = False

    @timer('rotary')
    def loop(self):
        self._button.update()  # for debounce.  Inspect .rose and .fell for press/release events
        self._update_rotary_position()
        self._update_button()

    def _update_button(self):
        if self._current_press_start:
            assert not self._button.fell, 'button is already down, it has to come up first doesn\'t it?'
            pressed_time = time.monotonic() - self._current_press_start
            if self._button.rose:
                self._longheld = False  # whether or not we longheld, we're definitely not longholding now
                self._current_press_start = None
                if pressed_time < self._longhold_duration:
                    for listener in self.on_click:
                        listener()
                else:
                    for listener in self.on_longhold_release:
                        listener()
            elif not self._longheld and pressed_time >= self._longhold_duration:
                self._longheld = True
                for listener in self.on_longhold_hold:
                    listener()
        elif self._button.fell:
            self._current_press_start = time.monotonic()

    def _update_rotary_position(self):
        if self._rotaryposition == self._rotary.position:
            return
        difference = self._rotaryposition - self._rotary.position
        self._rotaryposition = self._rotary.position
        print('Rotary activity: {}'.format(difference))
        for listener in self.on_increment:
            listener(difference)
