from machine import Pin, I2C
import time
from lib.umqttsimple import MQTTClient
import ujson
from framework.mqttmethods import MQTTMethods
from configuration import Configuration

class VEML7700Module:
    TYPE = "VEML7700Module"

    DEFAULT_POLLING_INTERVAL = 5
    DEFAULT_POLLING_ENABLED = False

    SLAVE_ADDRESS = 0x10

    ALS_CONFIG = 0x00
    ALS_DATA = 0x04
    WHITE_DATA = 0x05

    _channel: int
    _scl_pin: Pin
    _sda_pin: Pin
    _i2c_bus: int
    _frequency: int
    _address: int
    _i2c: I2C

    # Configuration
    _interval_in_seconds: int
    _polling_enabled: bool

    # Sensor polling
    _last_message = 0

    # Error handling
    _last_status: int
    _last_status_message: str
    _has_error: bool

    def __init__(
        self,
        channels: list[int],
        scl_pin: Pin,
        sda_pin: Pin,
        i2c_bus: int = 0,
        frequency: int = 100000,
        address: int = 0x10
    ):

        self._channel = channels[0]
        self._scl_pin = scl_pin
        self._sda_pin = sda_pin
        self._i2c_bus = i2c_bus
        self._frequency = frequency
        self._address = address

        self._last_status = 200
        self._last_status_message = 'OK'
        self._has_error = False

        self._interval_in_seconds = self.DEFAULT_POLLING_INTERVAL
        self._polling_enabled = self.DEFAULT_POLLING_ENABLED

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)

    def setup(self) -> "VEML7700Module":

        print("Initializing VEML7700 I2C communication")

        self._i2c = I2C(
            self._i2c_bus,
            scl=self._scl_pin,
            sda=self._sda_pin,
            freq=self._frequency
        )

        devices = self._i2c.scan()

        print("I2C devices found: ", devices)

        if self._address not in devices:
            raise Exception(
                'VEML7700 not found at address ' + hex(self._address)
            )

        print("Setting up VEML7700 sensor")

        # Gain = 1
        # Integration time = 100 ms
        # Sensor enabled
        self._write_register(self.ALS_CONFIG, 0x0000)

        time.sleep_ms(150)

        print("VEML7700 sensor setup done")

        return self

    def add_device(self, device) -> "VEML7700Module":
        self.device = device
        return self

    # --------------------------------
    # I2C REGISTER OPERATIONS
    # --------------------------------

    def _write_register(self, register, value):

        data = bytearray(2)

        data[0] = value & 0xFF
        data[1] = (value >> 8) & 0xFF

        self._i2c.writeto_mem(
            self._address,
            register,
            data
        )

    def _read_register(self, register):

        data = self._i2c.readfrom_mem(
            self._address,
            register,
            2
        )

        return data[0] | (data[1] << 8)

    # --------------------------------
    # SENSOR OPERATIONS
    # --------------------------------

    def _get_value(self):
        try:
            raw = self._read_register(self.ALS_DATA)
            white = self._read_register(self.WHITE_DATA)

            lux = raw * 0.0672

            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False

            return {
                'raw': raw,
                'white': white,
                'lux': round(lux, 2)
            }

        except Exception as e:

            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True

            return {
                'raw': -1,
                'white': -1,
                'lux': -1
            }

    # --------------------------------
    # MQTT / FRAMEWORK INTEGRATION
    # --------------------------------
    def _to_class_dict(self):

        return {
            'type': self.TYPE,
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

    def _to_error_dict(self, client_id, method, message_id):
        return {
            'client_id': client_id,
            'method': method,
            'message_id': message_id,
            'epoch': time.time(),
            'status': self._last_status,
            'message': self._last_status_message
        }

    # --------------------------------
    # MAIN TASK
    # --------------------------------

    def main_task(self, topic: str, client: MQTTClient, client_id: str):
        if (time.time() - self._last_message) > self._interval_in_seconds:

            if self._polling_enabled:

                result = ujson.dumps(
                    self._to_dict(
                        client_id,
                        MQTTMethods.DEVICE_PUSH,
                        'NA'
                    )
                )

                print("PUSH reply " + result)

                client.publish(topic, result)

            self._last_message = time.time()

    # --------------------------------
    # MQTT MESSAGE HANDLING
    # --------------------------------

    def handle_message(self, message_object: dict, topic: str, client: MQTTClient):
        message_method = message_object['method']
        message_id = message_object['message_id']

        message_channel = message_object.get(
            'channel',
            Configuration.DEFAULT_CHANNEL
        )

        message_client_id = message_object['client_id']

        if message_channel == self._channel:

            print(
                'This message "' + message_method +
                '" is for the ' + self.TYPE +
                ' on channel ' + str(self._channel)
            )

            if message_method == MQTTMethods.DEVICE_GET:

                result = ujson.dumps(
                    self._to_dict(
                        message_client_id,
                        message_method,
                        message_id
                    )
                )

                print("GET reply " + result)
                client.publish(topic, result)

            if message_method == MQTTMethods.DEVICE_SET:

                try:

                    message_data = message_object['data']

                    interval = message_data.get(
                        'interval',
                        self._interval_in_seconds
                    )

                    self._interval_in_seconds = interval

                    polling = message_data.get(
                        'polling',
                        self._polling_enabled
                    )

                    self._polling_enabled = polling

                    result = ujson.dumps(
                        self._to_dict(
                            message_client_id,
                            message_method,
                            message_id
                        )
                    )

                    print("SET reply " + result)
                    client.publish(topic, result)

                except Exception as e:

                    self._last_status = 500
                    self._last_status_message = str(e)
                    self._has_error = True

                    result = ujson.dumps(
                        self._to_error_dict(
                            message_client_id,
                            message_method,
                            message_id
                        )
                    )

                    print("SET error reply " + result)
                    client.publish(topic, result)

            if message_method == MQTTMethods.DEVICE_LIST:
                pass

    def get_status(self):

        return {
            'status': self._last_status,
            'message': self._last_status_message,
            'has_error': self._has_error
        }
