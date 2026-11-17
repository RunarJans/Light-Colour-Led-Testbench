from utime import sleep
from machine import Pin
import ujson
from framework.mqttmethods import MQTTMethods
import time
from configuration import Configuration
from lib.umqttsimple import MQTTClient
from neopixel import NeoPixel

class NeoPixelLedModule:
    TYPE = 'NeoPixelLedModule'
    _gpio_pin: Pin
    _channel: int
    _led_count: int

    _last_status: int
    _last_status_message: str
    _has_error: bool

    _neopixel: NeoPixel
    _led_type: int # 3 = RGB, 4 = RGBW
    _timing: int # 0 = 400KHz, 1 = 800KHz

    _red: int
    _green: int
    _blue: int
    _white: int

    def get_status(self):
        return { 'status': self._last_status, 'message': self._last_status_message, 'has_error': self._has_error }

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)

    def __init__(self, channels: list[int], gpio_pin: int, led_count: int = 1, led_type: int = 4, timing: int = 1):
        print("Setup NeoPixel module")
        self._channel = channels[0] # module can only have one channel
        self._gpio_pin = Pin(gpio_pin, Pin.OUT)
        self._led_count = led_count
        self._led_type = led_type
        self._timing = timing

        self._red = 0
        self._green = 0
        self._blue = 0
        self._white = 0

        self._last_status = 200
        self._last_status_message = 'OK'
        self._has_error = False

    def setup(self) -> "NeoPixelLedModule":
        print("Initialise NeoPixel protocol")
        self._neopixel = NeoPixel(self._gpio_pin, self._led_count, self._led_type, self._timing)

        for led in range(self._led_count):
            self._neopixel[led] = (self._red, self._green, self._blue, self._white)

        self._neopixel.write()

        print("NeoPixel setup done.")

        return self

    def add_device(self, device) -> "NeoPixelLedModule":
        self.device = device
        return self

    def set_color(self, red: int, green: int, blue: int, white: int):
        for led in range(self._led_count):
            if self._led_type == 4:
                self._neopixel[led] = (red, green, blue, white)
            else:
               self._neopixel[led] = (red, green, blue)

        self._neopixel.write()

    def _get_value(self) -> tuple:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False

            return self._neopixel[0]
            
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return ()

    def _to_class_dict(self):
        return {
                'type' : self.TYPE,
                'channel': self._channel,
                'red': self._get_value()[0],
                'green': self._get_value()[1],
                'blue': self._get_value()[2],
                'white': self._get_value()[3],
                'leds': self._led_count
            }
    
    def to_device_list(self):
        return self._to_class_dict()
    
    def _to_dict(self, client_id, method, message_id):
        return {
            'client_id': client_id,
            'method': method,
            'message_id': message_id,
			'data': self._to_class_dict(),
            'epoch': time.time(),
            'status': self._last_status,
            'message': self._last_status_message
        }
    
    def _to_error_dict(self, client_id, method, message_id):
        return {
            'client_id': client_id,
            'method': method,
            'message_id': message_id,
            'epoch': time.time(),
            'status': self._last_status,
            'message': self._last_status_message
        }
    
    # Task which will be executed in main-loop, without trigger
    def main_task(self, topic: str, client: MQTTClient, client_id: str) -> None:
        pass
    
    def handle_message(self, message_object: dict, topic: str, client: MQTTClient):
        message_method = message_object['method']
        message_id = message_object['message_id']
        message_channel = message_object.get('channel', Configuration.DEFAULT_CHANNEL)
        message_client_id = message_object['client_id']

        if message_channel == self._channel:
            print('This message "' + message_method  + '" is for the ' + self.TYPE + ' on channel ' + str(self._channel))

            if message_method == MQTTMethods.DEVICE_GET:
                result = ujson.dumps(self._to_dict(message_client_id, message_method, message_id))
                print("GET reply " + result)
                client.publish(topic, result)

            if message_method == MQTTMethods.DEVICE_SET:
                try:
                    message_data = message_object['data']
                    self._red = message_data.get('red', self._red)
                    self._green = message_data.get('green', self._green)
                    self._blue = message_data.get('blue', self._blue)
                    self._white = message_data.get('white', self._white)

                    self.set_color(self._red, self._green, self._blue, self._white)
                    
                    result = ujson.dumps(self._to_dict(message_client_id, message_method, message_id))
                    print("SET reply " + result)
                    client.publish(topic, result)

                except Exception as e: 
                    self._last_status = 500
                    self._last_status_message = str(e)
                    self._has_error = True

                    result = ujson.dumps(self._to_error_dict(message_client_id, message_method, message_id))
                    print("SET error reply " + result)
                    client.publish(topic, result)

                
            if message_method == MQTTMethods.DEVICE_LIST:
                # Should be handled at a higher level
                pass
