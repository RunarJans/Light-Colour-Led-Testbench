from framework.lightsensor import LightSensor
from framework.relaymodule import RelayModule
from framework.device import Device
from framework.statusmodule import StatusModule
from framework.mqttmethods import MQTTMethods
from framework.rgbsensor import RGBSensor
from framework.neopixelled import NeoPixelLedModule
from framework.rgbstatusmodule import RGBStatusModule
from framework.veml7700module import VEML7700Module
from machine import Pin, I2C
import time
from configuration import Configuration
import ujson
from lib.umqttsimple import MQTTClient
import gc

_known_channels: list[int] = []

configuration = Configuration().getConfiguration()

#_status_leds: list[int] = configuration['status_leds']['gpio_pins']
#status_module = StatusModule(_status_leds)

status_module = RGBStatusModule(configuration['rgb_status_leds']['gpio_status_pin'])
status_module.enableBootColor()

device = Device(configuration['name'], configuration['type'], status_module)

def parse_message(message: str):
    return ujson.loads(message)

def post_error(topic: str, method: str, message_id, status: int, message: str):
    status_module.enableErrorLED()
    error_message = {
            'client_id': device.client_id.decode(),
            'method': method,
            'message_id': message_id,
            'epoch': time.time(),
            'status': status,
            'message': message
        }
    
    error_message_json = ujson.dumps(error_message)
    print(error_message_json)
    device.mqtt_client.publish(topic, error_message_json)

# Check if the channel is known
def is_valid_channel(channel) -> bool:
    return channel in _known_channels

# logic to handle the 'device.list" command
def list_device(message_object, client: MQTTClient):
    peripheral_data = []

    last_status = 200
    last_status_message = "OK"

    peripherals = device.get_peripherals()
    print(peripherals)

    for peripheral in peripherals:
        peripheral_data.append(peripheral.to_device_list())
        peripheral_status = peripheral.get_status()
        
        # Stop the loop and publish the error message
        if peripheral_status['has_error']:
            last_status = peripheral_status['status']
            last_status_message = peripheral_status['message']
            break
    
    response = {
            'client_id': message_object['client_id'],
            'method': message_object['method'],
            'message_id': message_object['message_id'],
			'data': peripheral_data,
            'epoch': time.time(),
            'status': last_status,
            'message': last_status_message
        }
    
    response_json = ujson.dumps(response)
    client.publish(device.personal_topic_rsp, response_json)

def handle_mqtt_messages(tpc:bytes, msg:bytes):
    status_module.disableErrorLED()
    topic, message = tpc.decode(), msg.decode()
    del msg
    del tpc
    #print(topic, message)

    message_object = parse_message(message)
    del message
    message_method = message_object['method']
    message_id = message_object.get('message_id', '')

    # handle device.list
    if (topic == device.personal_topic_cmd) and (message_method == MQTTMethods.DEVICE_LIST):
        list_device(message_object, device.mqtt_client)

    # handle WHOIS
    elif (topic == device.personal_topic_cmd) and (message_method == MQTTMethods.DEVICE_WHOIS):
        status_module.set_trigger_power_toggle(True)

    # handle other device commands
    elif topic == device.personal_topic_cmd:
        # Send error when unknown channel is requested
        requested_channel = message_object.get('channel', Configuration.DEFAULT_CHANNEL)
        if not is_valid_channel(requested_channel):
            post_error(device.personal_topic_rsp, message_method, message_id, 404, 'Channel "' + str(requested_channel)  + '" not found' )
        
        # Otherwise handle request
        else:
            for peripheral in device.get_peripherals():
                peripheral.handle_message(message_object, device.personal_topic_rsp, device.mqtt_client)
    
    # handle broadcasts
    elif topic == device.BROADCAST_TOPIC_CMD:
        if message_method == MQTTMethods.DISCOVERY_SCAN:
            device.broadcast(MQTTMethods.DISCOVERY_SCAN)

    else:
        print('No implementation for ' + topic + ' and/or ' + message_method)
        status_module.enableErrorLED()
       

try:
    wlan_config = configuration['wlan']
    print(wlan_config)
    device.setup(wlan_config['ssid'], wlan_config['password'])

    mqtt_config = configuration['mqtt']
    print(mqtt_config)
    device.mqtt_setup(mqtt_config['server'], mqtt_config['username'], mqtt_config['password'],handle_mqtt_messages)

    peripherals = configuration['peripherals']
    for peripheral in peripherals:
        channels: list[int] = peripheral['channels']
        _known_channels.extend(channels)    # add channel to the known channels
        if (peripheral['type'] == VEML7700Module.TYPE) and (peripheral['enabled'] == True):
            print('Configuring VEML7700 light sensor: ' + str(peripheral))
            i2c_config = peripheral['i2c']
            scl_pin = Pin(i2c_config['scl'])
            sda_pin = Pin(i2c_config['sda'])
            bus = i2c_config['bus']
            frequency = i2c_config['frequency']
            address = i2c_config.get('address', 0x10)

            veml7700_module = VEML7700Module(
                channels,
                scl_pin,
                sda_pin,
                bus,
                frequency,
                address
            ).add_device(device).setup()
            device.register_peripheral(veml7700_module)
        if (peripheral['type'] == LightSensor.TYPE) and (peripheral['enabled'] == True):
            print('Configuring light sensor: ' + str(peripheral))
            i2c_config = peripheral['i2c']
            
            scl_pin = Pin(i2c_config['scl'])
            sda_pin = Pin(i2c_config['sda'])
            bus = i2c_config['bus']
            frequency = i2c_config['frequency']
            lightSensor = LightSensor(channels, scl_pin, sda_pin, bus, frequency).add_device(device).setup()   # TODO: pass configuration-object entirely
            device.register_peripheral(lightSensor)
        
        if (peripheral['type'] == RelayModule.TYPE) and (peripheral['enabled'] == True):
            print('Configuring relais module: ' + str(peripheral))
            relais_pins = peripheral['gpio_pin']
            relayModule = RelayModule(channels, relais_pins).add_device(device).setup()
            device.register_peripheral(relayModule)
        
        if (peripheral['type'] == RGBSensor.TYPE) and (peripheral['enabled'] == True):
            print('Configuring RGB sensor: ' + str(peripheral))
            i2c_config = peripheral['i2c']
            
            led_pin = peripheral['gpio_pin']
            scl_pin = Pin(i2c_config['scl'])
            sda_pin = Pin(i2c_config['sda'])
            bus = i2c_config['bus']
            frequency = i2c_config['frequency']
            rgb_Sensor = RGBSensor(channels, led_pin, scl_pin, sda_pin, bus, frequency).add_device(device).setup()   # TODO: pass configuration-object entirely
            device.register_peripheral(rgb_Sensor)

        if (peripheral['type'] == NeoPixelLedModule.TYPE) and (peripheral['enabled'] == True):
            print('Configuring NeoPixel module: ' + str(peripheral))
            neopixel_pin = peripheral['gpio_pin']
            led_count = peripheral['led_count']
            neopixel_module = NeoPixelLedModule(channels, neopixel_pin, led_count).add_device(device).setup()
            device.register_peripheral(neopixel_module)

    print('Peripheral overview:')
    for registered_peripheral in device.get_peripherals():
        print('Registered peripheral: ' + str(registered_peripheral))

    print('Listening for messages!')

except Exception as e:
    import sys
    sys.print_exception(e)
    status_module.enableErrorLED()
    #raise e
    device.restart('Failed to setup device: ' + str(e.args), 10)

status_module.enableReadyColor()

while True:
  try:
    # Check for new messages on subscribed channels
    device.mqtt_client.check_msg()
    
    # Handle the main task for each peripheral. e.g. poll light sensor
    # Should work for all types of peripherals, when 'main_task' is defined
    # for light_sensor in device.get_peripherals_by_type(LightSensor.TYPE):
    for peripheral in device.get_peripherals():
       peripheral.main_task(device.personal_topic_rsp, device.mqtt_client, device.client_id.decode())

    status_module.main_task()

  except Exception as e:
     status_module.enableErrorLED()
     raise e
     #device.restart('An error occured while handling messages: ' + str(e.args), 10)
