# Quality of life utilities for CircuitPython

## RotaryButton
[Made with this in mind](https://www.adafruit.com/product/377)

### Why
Event-oriented programming is nice.
Declaring what happens in response to named impulses helps provide nicely
  structured software.  The program loop is not littered with conditions
  and the intent and purpose of each statement is salient.

### Example program
This blinks an LED in response to any input on an Adafruit rotary encoder.

```
def _get_hardware():
    encoder = rotaryio.IncrementalEncoder(board.A4, board.A5)
    pin = digitalio.DigitalInOut(board.D5)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    button = Debouncer(pin)

    led = digitalio.DigitalInOut(D2)
    led.direction = digitalio.Direction.OUTPUT

    return button, encoder, led

def _toggle(pin):
    pin.value = not pin.value

def run():
    # ----------------------------------------------
    # Set up hardware
    button, encoder, led = _get_hardware()
    toggle_led = lambda: _toggle(led)
    def toggle_led_times(amount):
        for i in range(abs(amount)):
            toggle_led()

    # ----------------------------------------------
    # Configure events for the program.
    rotarybutton = RotaryButton(
        rotary, button,
        on_increment:        [toggle_led_times],
        on_click:            [toggle_led],
        on_longhold_hold:    [toggle_led],
        on_longhold_release: [toggle_led]
    )

    # ----------------------------------------------
    # Run program forever waiting for input.
    while True:
        rotarybutton.loop()

if __name__ == '__main__':
    run()
```
