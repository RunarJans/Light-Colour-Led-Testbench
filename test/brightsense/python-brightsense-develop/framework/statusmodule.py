from machine import Pin
import time

class StatusModule:
    _status_leds: list[Pin]

    POWER_LED = 0
    WLAN_LED = 1
    MQTT_LED = 2
    ERROR_LED = 3

    DEFAULT_TOGGLE_DURATION_IN_SECONDS = 30
    DEFAULT_TOGGLE_SPEED_IN_MS = 500

    _last_toggle: int
    _toggle_interval: int

    _toggle_power_led: bool
    _toggle_wlan_led: bool
    _toggle_mqtt_led: bool
    _toggle_error_led: bool
    _toggle_enable: bool

    _toggle_count: int  # how often toggled
    _toggle_time: int   # max number of toggles

    def __init__(self, led_pins: list[int]) -> None:
        self._status_leds = []
        self._last_toggle = 0
        self._toggle_interval = self._ms_to_ns(self.DEFAULT_TOGGLE_SPEED_IN_MS)

        self._toggle_power_led = False
        self._toggle_wlan_led = False
        self._toggle_mqtt_led = False
        self._toggle_error_led = False
        self._toggle_enable = False

        self._restore_state_power_led = False
        self._restore_state_wlan_led = False
        self._restore_state_mqtt_led = False
        self._restore_state_error_led = False

        self._toggle_count = 0
        self._toggle_time = self.DEFAULT_TOGGLE_DURATION_IN_SECONDS

        cnt = 0
        # Configure each LED pin as output
        for led_pin in led_pins:
            self._status_leds.insert(cnt, Pin(led_pin, Pin.OUT))
            self._setLow(cnt)
            cnt += 1

    # _Internals

    def _setHigh(self, led: int) -> None:
        self._status_leds[led].value(1)

    def _setLow(self, led: int) -> None:
        self._status_leds[led].value(0)

    def _toggle(self, led: int) -> None:
        self._status_leds[led].toggle()
        
    def _set_state(self, led: int, state: bool):
        if(state):
            self._setHigh(led)
        else:
            self._setLow(led)

    # POWER LED

    def enablePowerLED(self) -> None:
        self._setHigh(self.POWER_LED)
        self._restore_state_power_led = True

    def disablePowerLED(self) -> None:
        self._setLow(self.POWER_LED)
        self._restore_state_power_led = False

    def togglePowerLED(self) -> None:
        self._toggle(self.POWER_LED)
    
    def set_power_led_state(self, state: bool):
        self._set_state(self.POWER_LED, state)

    # WLAN LED

    def enableWlanLED(self) -> None:
        self._setHigh(self.WLAN_LED)
        self._restore_state_wlan_led = True

    def disableWlanLED(self) -> None:
        self._setLow(self.WLAN_LED)
        self._restore_state_wlan_led = False

    def toggleWlanLED(self) -> None:
        self._toggle(self.WLAN_LED)
    
    def set_wlan_led_state(self, state: bool):
        self._set_state(self.WLAN_LED, state)

    # MQTT LED

    def enableMqttLED(self) -> None:
        self._setHigh(self.MQTT_LED)
        self._restore_state_mqtt_led = True

    def disableMqttLED(self) -> None:
        self._setLow(self.MQTT_LED)
        self._restore_state_mqtt_led = False

    def toggleMqttLED(self) -> None:
        self._toggle(self.MQTT_LED)
    
    def set_mqtt_led_state(self, state: bool):
        self._set_state(self.MQTT_LED, state)

    # ERROR LED

    def enableErrorLED(self) -> None:
        self._setHigh(self.ERROR_LED)
        self._restore_state_error_led = True

    def disableErrorLED(self) -> None:
        self._setLow(self.ERROR_LED)
        self._restore_state_error_led = False

    def toggleErrorLED(self) -> None:
        self._toggle(self.ERROR_LED)
    
    def set_error_led_state(self, state: bool):
        self._set_state(self.ERROR_LED, state)

    # Trigger toggle routine
    def set_trigger_power_toggle(self, trigger: bool):
        self._toggle_power_led = trigger
        self._toggle_enable = trigger

    def set_trigger_wlan_toggle(self, trigger: bool):
        self._toggle_wlan_led = trigger
        self._toggle_enable = trigger

    def set_trigger_mqtt_toggle(self, trigger: bool):
        self._toggle_mqtt_led = trigger
        self._toggle_enable = trigger

    def set_trigger_error_toggle(self, trigger: bool):
        self._toggle_error_led = trigger
        self._toggle_enable = trigger

    def _ms_to_ns(self, ms):
        return ms * 1_000_000

    # Toggle routine

    def main_task(self):
        if self._toggle_enable:
            if (time.time_ns() - self._last_toggle) > self._toggle_interval:
                # only flash the led a few times
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
                    
                    # Reset led to previous state
                    if self._toggle_power_led:
                        self._toggle_power_led = False
                        self.set_power_led_state(self._restore_state_power_led)
                    
                    if self._toggle_wlan_led:   
                        self._toggle_wlan_led = False
                        self.set_wlan_led_state(self._restore_state_wlan_led)
                    
                    if self._toggle_mqtt_led:
                        self._toggle_mqtt_led = False
                        self.set_mqtt_led_state(self._restore_state_mqtt_led)
                    
                    if self._toggle_error_led:
                        self._toggle_error_led = False
                        self.set_error_led_state(self._restore_state_error_led)
                    
                    self._toggle_enable = False     
                
                self._last_toggle = time.time_ns()
