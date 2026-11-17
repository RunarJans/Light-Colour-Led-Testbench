from machine import Pin, I2C
import time
from lib.umqttsimple import MQTTClient
import ujson
from framework.mqttmethods import MQTTMethods
from configuration import Configuration
from lib.tcs3472 import tcs3472

class RGBSensor:
    SLAVE_ADDRESS: int = 0x29
    TYPE = "RGBSensorModule"
    DEFAULT_POLLING_INTERVAL = 5
    DEFAULT_POLLING_ENABLED = False
    DEFAULT_LED_STATUS = False
    
    _channel: int
    _scl_pin: Pin
    _sda_pin: Pin
    _ic2_bus: int
    _frequency: int
    _i2c: I2C
    _tcs: tcs3472

    # Configuration
    _interval_in_seconds: int
    _polling_enabled: bool

    # Sensor polling
    _last_message = 0

    # Error handling
    _last_status: int
    _last_status_message: str
    _has_error: bool

    _led_pin: Pin
    _led_status: bool

    def get_status(self):
        return { 'status': self._last_status, 'message': self._last_status_message, 'has_error': self._has_error }

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)

    def __init__(self, channels: list[int], led_pin_number: int, scl_pin: Pin, sda_pin: Pin, i2c_bus: int = 0, frequency: int = 10000):
        self._channel = channels[0] # Light sensors only have one channel
        self._scl_pin = scl_pin
        self._sda_pin = sda_pin
        self._ic2_bus = i2c_bus
        self._frequency = frequency

        self._last_status = 200
        self._last_status_message = 'OK'
        self._has_error = False

        self._interval_in_seconds = self.DEFAULT_POLLING_INTERVAL
        self._polling_enabled = self.DEFAULT_POLLING_ENABLED

        self._led_pin = Pin(led_pin_number, Pin.OUT)
        self._led_status = self.DEFAULT_LED_STATUS
        
    def add_device(self, device) -> "RGBSensor":
        self.device = device
        return self

    def set_led(self):
        if self._led_status:
            self._led_pin.value(1)
        else:
            self._led_pin.value(0)

    def setup(self) -> "RGBSensor":
        # pull up on I2C signal
        self._scl_pin.PULL_UP
        self._sda_pin.PULL_UP

        print("Initializing I2C communication")
        self._i2c = I2C(self._ic2_bus, scl=self._scl_pin, sda=self._sda_pin, freq=self._frequency)
        
        address = I2C.scan(self._i2c)
        print("I2C device found with address: ", address)

        print("Setup TCS3472 RGB sensor")
        # Do note that I2C bus should already be started!!!
        self._tcs = tcs3472(self._i2c, self.SLAVE_ADDRESS)

        print("TCS3472 RGB sensor setup done.")
        return self

    # Task which will be executed in main-loop, without trigger
    def main_task(self, topic: str, client: MQTTClient, client_id: str) -> None:
        pass
        if (time.time() - self._last_message) > self._interval_in_seconds:
            if self._polling_enabled:
                result = ujson.dumps(self._to_dict(client_id, MQTTMethods.DEVICE_PUSH, 'NA'))
                print("PUSH reply " + result)
                client.publish(topic, result)
            
            self._last_message = time.time()

    def _get_rgb_value(self) -> tuple:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False
            rgb_value = self._tcs.rgb()
            return rgb_value
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return ()
        
    def _get_raw_value(self) -> tuple:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False
            raw_value = self._tcs.raw()
            return raw_value
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return ()
        
    def _get_light_value(self) -> int:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False
            light_value = self._tcs.light()
            return light_value
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return -1
    
    def _get_brightness_value(self) -> int:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False
            brightness_value = self._tcs.brightness()
            return brightness_value
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return -1
    
    def _to_class_dict(self):
        return {
                'type' : self.TYPE,
                'channel': self._channel,
                'rgb': self._get_rgb_value(),
                'light': self._get_light_value(),
                'brightness': self._get_brightness_value(),
                'raw': self._get_raw_value(),
                'led': self._led_status,
                'interval': self._interval_in_seconds,
                'polling': self._polling_enabled,
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
    
    # When an error occured we don't want to fetch the 'data' which my trigger a new error
    def _to_error_dict(self, client_id, method, message_id):
        return {
            'client_id': client_id,
            'method': method,
            'message_id': message_id,
            'epoch': time.time(),
            'status': self._last_status,
            'message': self._last_status_message
        }

    def handle_message(self, message: str, topic: str, client: MQTTClient):
        message_object = ujson.loads(message)
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
                # Set polling settings
                try:
                    message_data = message_object['data']
                    interval = message_data.get('interval', self._interval_in_seconds)
                    self._interval_in_seconds = interval

                    polling = message_data.get('polling', self._polling_enabled)
                    self._polling_enabled = polling

                    led = message_data.get('led', self._led_status)
                    self._led_status = led
                    self.set_led()
                    
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
