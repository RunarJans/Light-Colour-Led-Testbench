from utime import sleep
from machine import Pin
import ujson
from framework.mqttmethods import MQTTMethods
import time
from configuration import Configuration
from lib.umqttsimple import MQTTClient

class RelayModule:
    TYPE = 'RelayModule'
    _gpio_pin: Pin
    _channel: int

    _last_status: int
    _last_status_message: str
    _has_error: bool

    def get_status(self):
        return { 'status': self._last_status, 'message': self._last_status_message, 'has_error': self._has_error }

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)

    def __init__(self, channels: list[int], gpio_pin: int):
        print("Setup relay module")
        self._channel = channels[0] # module can only have one channel
        self._gpio_pin = Pin(gpio_pin, Pin.OUT)

        self._last_status = 200
        self._last_status_message = 'OK'
        self._has_error = False

    def setup(self) -> "RelayModule":
        print("Reset relay state to inactive")
        self._gpio_pin.value(1)

        print("Relay setup done.")

        return self
    
    def add_device(self, device) -> "RelayModule":
        self.device = device
        return self

    def _toggle(self):
        self._gpio_pin.toggle()

    def _on(self):
        self._gpio_pin.value(0) # active low

    def _off(self):
        self._gpio_pin.value(1) # active low

    def _get_value(self):
        try:
            self._last_status = 200
            self._last_status_message = 'OK'
            self._has_error = False

            if self._gpio_pin.value() == 0: # active low
                return True
            else:
                return False
            
        except Exception as e:
            self._last_status = 500
            self._last_status_message = str(e)
            self._has_error = True
            return -1

    def _to_class_dict(self):
        return {
                'type' : self.TYPE,
                'channel': self._channel,
                'state': self._get_value(),
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
                    state = message_data['state']
                    if state == True:
                        self._on()
                    elif state == False:
                        self._off()
                    else:
                        raise Exception("Unknown state " + state )
                    
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
