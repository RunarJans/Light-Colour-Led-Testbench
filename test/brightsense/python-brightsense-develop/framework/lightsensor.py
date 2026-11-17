from machine import Pin, I2C
from lib.veml7700 import VEML7700
import time
from lib.umqttsimple import MQTTClient
from model.sensordatamodel import SensorDataModel
import ujson
from framework.mqttmethods import MQTTMethods
from configuration import Configuration

class LightSensor:
    SLAVE_ADDRESS: int = 0x10
    TYPE = "LightSensorModule"
    DEFAULT_POLLING_INTERVAL = 5
    DEFAULT_POLLING_ENABLED = False
    
    _channel: int
    _scl_pin: Pin
    _sda_pin: Pin
    _ic2_bus: int
    _frequency: int
    _i2c: I2C
    _veml: VEML7700

    # Configuration
    _interval_in_seconds: int
    _polling_enabled: bool

    # Sensor polling
    _last_message = 0

    # Error handling
    _last_status: int
    _last_status_message: str
    _has_error: bool

    def get_status(self):
        return { 'status': self._last_status, 'message': self._last_status_message, 'has_error': self._has_error }

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)

    def __init__(self, channels: list[int], scl_pin: Pin, sda_pin: Pin, i2c_bus: int = 0, frequency: int = 10000):
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

    def setup(self, integration_time: int = 100, gain: float = 1/8) -> "LightSensor":
        # pull up on I2C signal
        self._scl_pin.PULL_UP
        self._sda_pin.PULL_UP

        print("Initializing I2C communication")
        self._i2c = I2C(self._ic2_bus, scl=self._scl_pin, sda=self._sda_pin, freq=self._frequency)
        
        address = I2C.scan(self._i2c)
        print("I2C device found with address: ", address)

        print("Setup VEML7700 light sensor")
        self.veml = VEML7700(address=self.SLAVE_ADDRESS, i2c=self._i2c, it=integration_time, gain=gain)

        print("VEML7700 light sensor setup done.")

        return self
    
    def add_device(self, device) -> "LightSensor":
        self.device = device
        return self

    # def postValue(self, mqtt_client: MQTTClient, topic: str) -> None:
    #     sensor_value = self.get_value()
    #     data_model = SensorDataModel(str(self._channel), sensor_value).toJSON()
        
    #     print('Posting light sensor data: ' + data_model)
    #     mqtt_client.publish(topic, data_model)

    # Task which will be executed in main-loop, without trigger
    def main_task(self, topic: str, client: MQTTClient, client_id: str) -> None:
        if (time.time() - self._last_message) > self._interval_in_seconds:
            if self._polling_enabled:
                result = ujson.dumps(self._to_dict(client_id, MQTTMethods.DEVICE_PUSH, 'NA'))
                print("PUSH reply " + result)
                client.publish(topic, result)
            
            self._last_message = time.time()

    def _get_value(self) -> int:
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False
            return self.veml.read_lux()
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return -1
    
    def _to_class_dict(self):
        return {
                'type' : self.TYPE,
                'channel': self._channel,
                'value': self._get_value(),
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
                # Set polling settings
                try:
                    message_data = message_object['data']
                    interval = message_data.get('interval', self._interval_in_seconds)
                    self._interval_in_seconds = interval

                    polling = message_data.get('polling', self._polling_enabled)
                    self._polling_enabled = polling
                    
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