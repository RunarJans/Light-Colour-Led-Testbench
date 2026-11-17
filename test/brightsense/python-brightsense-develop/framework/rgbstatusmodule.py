from machine import Pin
import time
from neopixel import NeoPixel

class RGBStatusModule:
    """Represents NeoPixel RGB LEDs to display the status of the controller
    """

    DEFAULT_TOGGLE_DURATION_IN_SECONDS = 30
    DEFAULT_TOGGLE_SPEED_IN_MS = 500

    STATUS_LED_ID = 0
    ERROR_LED_ID = 1

    # NEOPIXEL configuration
    # GREEN = (0, 255, 0, 0)
    # RED = (255, 0, 0, 0)
    # BLUE = (0, 0, 255, 0)

    # YELLOW = (255, 255, 0, 0)
    # PINK = (255, 0, 255, 0)
    # CYAN = (0, 255, 255, 0)

    # BRIGHTEST_YELLOW = (244, 199, 9, 0)
    # BRIGHTEST_YELLOW_DARK = (122,100, 4, 0)

    # OFF = (0, 0, 0, 0)



    GREEN = (255, 0, 0)
    RED = (0,255,  0)
    BLUE = (0, 0, 255)

    YELLOW = (255, 255, 0)
    PINK = (0,255,  255)
    CYAN = (255,0,  255)

    ORANGE = (117, 155, 0)

    BRIGHTEST_YELLOW = (199,244,  9)
    BRIGHTEST_YELLOW_DARK = (100, 122, 4)

    OFF = (0, 0, 0)

    _neopixel_status: NeoPixel
    #_neopixel_error: NeoPixel

    _led_pin_status: Pin
    #_led_pin_error: Pin

    _led_count: int
    _timing: int
    _led_type: int

    _colors: list[tuple]

    _previous_toggle: bool
    _previous_value: list[tuple]

    _last_toggle: int
    _toggle_interval: int

    _toggle_power_led: bool
    _toggle_wlan_led: bool
    _toggle_mqtt_led: bool
    _toggle_error_led: bool
    _toggle_enable: bool

    _toggle_count: int  # how often toggled
    _toggle_time: int   # max number of toggles

    def __init__(self, status_led_pin: int) -> None:
        """Initialise class

        :param status_led_pin: GPIO pin number to which the status LED is connected
        :param error_led_pin: GPIO pin number to which the error LED is connected
        :returns: Instance of class
        """
        self._led_count = 2
        self._timing = 1 # 800kHz ; 0 = 400kHz
        self._led_type = 3 # RGB ; 4 = RGBW

        self._led_pin_status = Pin(status_led_pin, Pin.OUT)
        #self._led_pin_error = Pin(error_led_pin, Pin.OUT)

        self._toggle_power_led = False
        self._toggle_wlan_led = False
        self._toggle_mqtt_led = False
        self._toggle_error_led = False
        self._toggle_enable = False

        self._toggle_count = 0
        self._toggle_time = self.DEFAULT_TOGGLE_DURATION_IN_SECONDS

        self._last_toggle = 0
        self._toggle_interval = self._ms_to_ns(self.DEFAULT_TOGGLE_SPEED_IN_MS)

        self._colors = []
        self._colors.append(self.GREEN)
        self._colors.append(self.GREEN)

        self._previous_toggle = False
        self._previous_value = []
        self._previous_value.append(self.GREEN)
        self._previous_value.append(self.GREEN)

        self._neopixel_status = NeoPixel(self._led_pin_status, self._led_count, self._led_type, self._timing)
        #self._neopixel_error = NeoPixel(self._led_pin_error, self._led_count, self._led_type, self._timing)

        self._neopixel_status[self.STATUS_LED_ID] = self._colors[self.STATUS_LED_ID]
        self._neopixel_status[self.ERROR_LED_ID] = self._colors[self.STATUS_LED_ID]
        self._neopixel_status.write()

        # self._neopixel_error[0] = self._colors[self.ERROR_LED_ID]
        # self._neopixel_error.write()

    # _Internals

    def _ms_to_ns(self, ms):
        """ Convert milliseconds to nanoseconds
        :param ms: The number of milliseconds to convert
        :returns: The number of nanoseconds
        """
        return ms * 1_000_000

    def _set_color(self, grb: tuple, neopixel: NeoPixel, led_id: int, history = True):
        """Send a color to a NeoPixel LED

        :param grb: A tuple containing the "Green Red Blue" value which should be displayed on the LED
        :param neopixel: The NeoPixel instance on which we want to display it
        :param led_id: ID of the LED on which we want to display it (0 = status; 1 = error)
        """
        self._colors[led_id] = grb
        print('setting color ' + str(grb) + ' on index ' + str(led_id))
        neopixel[led_id] = grb
        neopixel.write()
        if history:
            self._previous_value[led_id] = grb

    def _toggle_led(self, neopixel: NeoPixel, led_id: int):
        """ Toggle state of LED between color and off

        :param neopixel: The NeoPixel instance on which we want to display it
        :param led_id: ID of the LED on which we want to display it (0 = status; 1 = error)
        """
        # when going from color to off
        if self._previous_toggle == False:
            # store previous color
            self._previous_value[led_id] = self._colors[led_id]
            # turn led off
            self._set_color(self.OFF, neopixel, led_id, False)
        else:
            # when going from off to color
            # restore last color
            self._set_color(self._previous_value[led_id], neopixel, led_id, False)
        
        # toggle state
        self._previous_toggle = not self._previous_toggle


    def enableBootColor(self) -> None:
        self._set_color(self.BRIGHTEST_YELLOW, self._neopixel_status, self.STATUS_LED_ID)
        self._set_color(self.BRIGHTEST_YELLOW_DARK, self._neopixel_status, self.ERROR_LED_ID)
    
    def enableReadyColor(self) -> None:
        self._set_color(self.GREEN, self._neopixel_status, self.STATUS_LED_ID)
        self._set_color(self.OFF, self._neopixel_status, self.ERROR_LED_ID)

    # POWER LED

    def enablePowerLED(self) -> None:
        """ Set the color of the status LED to yellow
        """
        self._set_color(self.YELLOW, self._neopixel_status, self.STATUS_LED_ID)

    def disablePowerLED(self) -> None:
        """ Turn the status LED off
        """
        self._set_color(self.OFF, self._neopixel_status, self.STATUS_LED_ID)

    def togglePowerLED(self) -> None:
        """ Toggle the status LED between yellow and off
        """
        self._toggle_led(self._neopixel_status, self.STATUS_LED_ID)

    # WLAN LED

    def enableWlanLED(self) -> None:
        """ Set the color of the status LED to blue
        """
        self._set_color(self.BLUE, self._neopixel_status, self.STATUS_LED_ID)

    def disableWlanLED(self) -> None:
        """ Turn the status LED off
        """
        self._set_color(self.OFF, self._neopixel_status, self.STATUS_LED_ID)

    def toggleWlanLED(self) -> None:
        """ Toggle the status LED between blue and off
        """
        self._toggle_led(self._neopixel_status, self.STATUS_LED_ID)

    # MQTT LED

    def enableMqttLED(self) -> None:
        """ Set the color of the status LED to green
        """
        self._set_color(self.ORANGE, self._neopixel_status, self.STATUS_LED_ID)

    def disableMqttLED(self) -> None:
        """ Turn the status LED off
        """
        self._set_color(self.OFF, self._neopixel_status, self.STATUS_LED_ID)

    def toggleMqttLED(self) -> None:
        """ Toggle the status LED between green and off
        """
        self._toggle_led(self._neopixel_status, self.STATUS_LED_ID)

    # ERROR LED

    def enableErrorLED(self) -> None:
        """ Set the color of the error LED to red
        """
        self._set_color(self.RED, self._neopixel_status, self.ERROR_LED_ID)

    def disableErrorLED(self) -> None:
        """ Turn the error LED off
        """
        self._set_color(self.OFF, self._neopixel_status, self.ERROR_LED_ID)

    def toggleErrorLED(self) -> None:
        """ Toggle the error LED between green and off
        """
        self._toggle_led(self._neopixel_status, self.ERROR_LED_ID)
    
    # Methods to trigger routine for led toggle (blink LED for 30 seconds)

    def set_trigger_power_toggle(self, trigger: bool):
        """ Set a flag to start the toggle routine for the 'power' color  
        """
        self._toggle_power_led = trigger
        self._toggle_enable = trigger

    def set_trigger_wlan_toggle(self, trigger: bool):
        """ Set a flag to start the toggle routine for the 'wlan' color  
        """
        self._toggle_wlan_led = trigger
        self._toggle_enable = trigger

    def set_trigger_mqtt_toggle(self, trigger: bool):
        """ Set a flag to start the toggle routine for the 'mqtt' color  
        """
        self._toggle_mqtt_led = trigger
        self._toggle_enable = trigger

    def set_trigger_error_toggle(self, trigger: bool):
        """ Set a flag to start the toggle routine for the 'error' color  
        """
        self._toggle_error_led = trigger
        self._toggle_enable = trigger

    # TODO: add fading effect instead of plain toggle
    def _fade_led(self, neopixel: NeoPixel, led_id: int, from_color: tuple, to_color: tuple, steps: int = 20, delay_ms: int = 20):
        """
        Fades the LED from from_color to to_color in given steps.
        """
        for i in range(steps + 1):
            r = int(from_color[0] + (to_color[0] - from_color[0]) * i / steps)
            g = int(from_color[1] + (to_color[1] - from_color[1]) * i / steps)
            b = int(from_color[2] + (to_color[2] - from_color[2]) * i / steps)
            self._colors[led_id] = (r, g, b)
            neopixel[0] = (r, g, b)
            neopixel.write()
            # time.sleep_ms(delay_ms) # replace this with loop logic

    # Toggle routine

    def main_task(self):
        """ Task which can run in the 'main'-method to execute the toggle routine 
        """
        # Only execute when one of the LEDs should be toggled
        if self._toggle_enable:

            # Toggle the LED each 500ms
            if (time.time_ns() - self._last_toggle) > self._toggle_interval:
                
                # Do this for 30 seconds
                if self._toggle_count < self._toggle_time:
                    self._toggle_count += 1

                    if self._toggle_power_led:
                        self.togglePowerLED()

                    if self._toggle_wlan_led:
                        self.toggleWlanLED()

                    if self._toggle_mqtt_led:
                        self.toggleMqttLED()

                    if self._toggle_error_led:
                        self.toggleErrorLED()

                else:
                    print('Resetting toggle state')
                    self._toggle_count = 0
                    
                    # Restore last color on LED
                    if self._toggle_power_led:
                        self._toggle_power_led = False  # when the LED blinked for 30 seconds; disable the routine
                        previous_color = self._previous_value[self.STATUS_LED_ID]
                        self._set_color(previous_color, self._neopixel_status, self.STATUS_LED_ID)
                    
                    if self._toggle_wlan_led:   
                        self._toggle_wlan_led = False
                        previous_color = self._previous_value[self.STATUS_LED_ID]
                        self._set_color(previous_color, self._neopixel_status, self.STATUS_LED_ID)
                    
                    if self._toggle_mqtt_led:
                        self._toggle_mqtt_led = False
                        previous_color = self._previous_value[self.STATUS_LED_ID]
                        self._set_color(previous_color, self._neopixel_status, self.STATUS_LED_ID)
                    
                    if self._toggle_error_led:
                        self._toggle_error_led = False
                        previous_color = self._previous_value[self.ERROR_LED_ID]
                        self._set_color(previous_color, self._neopixel_status, self.ERROR_LED_ID)
                    
                    # disable toggle routine globally when routine ended
                    self._toggle_enable = False     
                
                self._last_toggle = time.time_ns()
