# python-brightsense
This repository contains the EmBright code for the pico's.   
The code can handle both 'controllers' as 'sensors'.   

## WLAN
The `pico` should be connected to a wireless network.   
On this network the `pico` should be able to reach a timeserver (NTP) and the MQQT server.  
It should also get its IP address from the DHCP server.   
The SSID and credentials can be configured in the `configuration.py`-file.   

## MQTT Messages
The `pico` will communicate to the `Linq` using MQTT.   
The server, username and password can be configured in the `configuration.py`-file.   

## Topics
We have 4 topics:
- `broadcast/cmd`: On this topic the Linq will send message which are meant for all modules
- `broadcast/rsp`: On this topic the Pico's will send replies on broadcast messages. It is also used for the initial 'register' message
- `<clientid>/cmd`: On this topic the Linq will send commands to a specific Pico
- `<clientid>/rsp`: On this topic the Pico will reply on a command

### discovery.register
When connecting to the MQTT broker, the `pico` will send a `discovery.register`-message on the `broadcast/rsp`-topic.  
The message contains the following data:
```json
 { 
    "client_id": "<unique ID of the Pico>", 
    "mac": "<MAC of the pico>", 
     "ip": "IP of the pico", 
    "type": "<Type of the module. e.g. CONTROL_RELAY_4>", 
    "version": "<Version of the sofware running on the Pico>",
    "method": "<Method used to discover the pico>"
}
```

### discovery.scan
The `Linq` can send a `discovery.scan`-message on the `broadcast/cmd`-topic.   
When this happens all pico's will reply with the a `discovery.register`-message on the `broadcast/rsp`-topic.   
Request:   
```json
{
    "method":"discovery.scan"
}
```

Response:
```json
 { 
    "client_id": "<unique ID of the Pico>", 
    "mac": "<MAC of the pico>", 
     "ip": "IP of the pico", 
    "type": "<Type of the module. e.g. CONTROL_RELAY_4>", 
    "version": "<Version of the sofware running on the Pico>"
}
```

### device.get
The `Linq` can send a `device.get`-message on the `<client_id>/cmd`-topic.  
This command should contain the `channel` (which corresponds to one of the peripherals) for which you want to get the data.   
The command should also contain a `message_id` so you can identify to which request the pico replied.   
For all received commands, the pico will reply on the `<client_id>/rsp`-topic.   
Request:   
```json
{
    "channel": 5, // peripheral for which you want to get the data
    "client_id": "c1469b3b30050ced", // ID of the pico
    "message_id": "<UUID>", // random UUID
    "method": "device.get"
}
```

Response:
```json
{
    "method": "device.get", 
    "data": {   // peripheral spefic data
        "raw": [140, 39, 72, 30], 
        "interval": 5, 
        "channel": 5,   // will always be available in reply
        "polling": false, 
        "type": "RGBSensorModule",  // Type of peripheral; will always be available in reply
        "brightness": 2, 
        "led": false, 
        "rgb": [71, 131, 54], 
        "light": 140
    }, 
    "message_id": "<UUID>", // same UUID as request 
    "epoch": 1751542739,  // epoch time stamp in UTC
    "status": 200,  // status code; similar to REST status codes
    "client_id": "c1469b3b30050ced",    // ID of the pico
    "message": "OK" // message field for additional info about the status
}
```

### device.set
The `Linq` can send a `device.set`-message on the `<client_id>/cmd`-topic.  
With this command one or more parameters of a peripheral can be set.   
e.g. set color, start polling, enable relay, ... 
The data which is send is peripheral specific.   
When the parameters are update, the pico will respond with the same message as with a 'device.get'.   

Request:   
```json
{
    "channel": 6,
    "client_id": "c1469b3b30050ced",
    "data": {    // parameters which should be set
        "red": 255, 
        "green": 0, 
        "blue": 255
    },
    "message_id": "<UUID>",
    "method": "device.set"
}
```

Response:
```json
{
    "method": "device.set", 
    "data": {
        "white": 0, 
        "green": 0, 
        "leds": 5, 
        "type": "NeoPixelLedModule", 
        "channel": 6, 
        "blue": 255, 
        "red": 255
    }, 
    "message_id": "12345689", 
    "epoch": 1751543485, 
    "status": 200, 
    "client_id": "c1469b3b30050ced", 
    "message": "OK"
}
```

### device.list
The `Linq` can send a `device.list`-message on the `<client_id>/cmd`-topic.  
When the pico receives this command, it will send the info off all its peripherals to the Linq.   

Request:   
```json
{
    "client_id": "c1469b3b30050ced",
    "message_id": "<UUID>",
    "method": "device.list"
}
```

Response:
```json
{
    "method": "device.list", 
    "data": [
        {
            "state": false, 
            "type": "RelayModule", 
            "channel": 0
        }, 
        {
            "state": false, 
            "type": "RelayModule", 
            "channel": 1
        }, 
        {
            "state": false, 
            "type": "RelayModule", 
            "channel": 2
        }, 
        {
            "state": false, 
            "type": "RelayModule", 
            "channel": 3
        },
        {
            "polling": false, 
            "interval": 5, 
            "type": "LightSensorModule", 
            "channel": 4, 
            "value": 399
        }, 
        {
            "raw": [52692, 5663, 9640, 35077], 
            "interval": 5, 
            "channel": 5, 
            "polling": false, 
            "type": "RGBSensorModule", 
            "brightness": 804, 
            "led": false, 
            "rgb": [27, 46, 169], 
            "light": 52698
        }, 
        {
            "white": 0, 
            "green": 0, 
            "leds": 5, 
            "type": "NeoPixelLedModule", 
            "channel": 6, 
            "blue": 255, 
            "red": 255
        }
    ], 
    "message_id": "<UUID>", 
    "epoch": 1751544072, 
    "status": 200, 
    "client_id": "c1469b3b30050ced", 
    "message": "OK"
}
```

### device.whois
The `Linq` can send a `device.whois`-message on the `<client_id>/cmd`-topic.  
The pico will reply by flashing its power LED.   
This can be used to identify a specific pico when multiple are used.   

Request:   
```json
{
    "client_id": "c1469b3b30050ced",
    "message_id": "<UUID>",
    "method": "device.whois"
}
```

### device.push
Similar to `device.get`, but in this case the pico will send the data without a request.   
It will be used when sensors are in 'polling'-mode, in which they send the measurements automatically to the `Linq`.   

The `Linq` can send a `device.get`-message on the `<client_id>/cmd`-topic.  
This command should contain the `channel` (which corresponds to one of the peripherals) for which you want to get the data.   
The command should also contain a `message_id` so you can identify to which request the pico replied.   
For all received commands, the pico will reply on the `<client_id>/rsp`-topic.   

Response:
```json
{
    "method": "device.push", 
    "data": {   // peripheral spefic data
        "raw": [140, 39, 72, 30], 
        "interval": 5, 
        "channel": 5,   // will always be available in reply
        "polling": false, 
        "type": "RGBSensorModule",  // Type of peripheral; will always be available in reply
        "brightness": 2, 
        "led": false, 
        "rgb": [71, 131, 54], 
        "light": 140
    }, 
    "message_id": "NA", // same UUID as request 
    "epoch": 1751542739,  // epoch time stamp in UTC
    "status": 200,  // status code; similar to REST status codes
    "client_id": "c1469b3b30050ced",    // ID of the pico
    "message": "OK" // message field for additional info about the status
}
```


## Creating a 'peripheral'
Each `peripheral` or `module` should contain the following methods and properties:
- handle_message: will be used to handle MQTT messages
- main_task: used to execute background tasks (e.g. toggle LEDs, poll sensors, ...)
- TYPE: a unique name for the peripheral
- get_status: method which returns a status object
- __str__: human readable representation of the class
- setup: initialisation of the class
- to_device_list: method to return the data which is replied on a 'device.list' request

The constructor should at least have one argument for `channels`.

For each type of peripheral the initialisation logic should be added to the main class (in peripherals loop):
```python
if (peripheral['type'] == MyModule.TYPE) and (peripheral['enabled'] == True):
    print('Configuring my module: ' + str(peripheral))
    output_pin = peripheral['gpio_pin']
    my_module = MyModule(channels, output_pin).setup()
    device.register_peripheral(my_module)
```

Once the registration logic is added, the module can be added to the 'peripherals'-section of the configuration:
```
{
    'type': 'MyModule',     # should match the TYPE-property of the module
    'enabled': True,        # the module is only registered when it's enabled
    'gpio_pin': 26,         # custom property for the module
    "channels": [9]         # the channel to which the module should reply
},
```

# Peripherals
Overview of the existing peripherals.

## LightSensor
With the LightSensor-module it is possible to read the `VEML7700` light sensor.   
The module is using I2C to communicate with the sensor.  
Configuration:   
```python
{
    'type': 'LightSensorModule',    # The configuration applies on the LightSensorModule
    'enabled': True,                # The module is enabled and should be set-up
    'channels': [0],                # The module is listening to channel 1
    'i2c': {                        # I2C configuration of the sensor
        'sda': 16,                  # GPIO PIN 16 is used for SDA
        'scl': 17,                  # GPIO PIN 17 is used for SCL
        'frequency': 10000,         # The communication is at a rate of 10_000
        'bus': 0                    # We are using I2C bus 0
    }
}
```

The module will reply with the measured light value on a `device.get`.   
But it can also be configured to do a reading each X seconds and send the data using a `device.push`.   

The sensor replies to the following requests:

### device.get
The module will reply with the following module-specific data:
```python
{
    'type' : 'LightSensorModule',   # Identifier of the module
    'channel': 0,                   # Channel on which the module is listening
    'value': 325,                   # Value of the light sensor
    'interval': 5,                  # Polling interval in seconds
    'polling': False                # Determine whether polling is enabled
}
```

### device.set
The following data can be configured using a `device.set`
```python
{
    'interval': 5,                  # Polling interval in seconds
    'polling': False                # Determine whether polling is enabled
}
```

The request can contain one or more configuration parameters.
After setting the new values, module will reply with the same data as a `device.get`

### device.push
When the `polling`-parameter is set to `True`, the module will perform a reading at the set `interval` (default 5 seconds).   
This data will be send as a `device.push`, containing the same data as a regular `device.get`.   
Polling can be disabled by setting the `polling`-parameter to `False`, which is also the default.   

### Status codes
The module has 2 status codes:
- `200` : operation was successfull
- `500` : something went wrong while getting or setting a parameter; additional info in provided in the `message`-field

### Additional info
Each I2C bus can only contain one VEML7700 sensor, since each sensor has the same I2C address.  
The `polling` mechanism is using time comparison instead of a real `sleep`-command, so it is not blocking the main thread.   

## RBG sensor
TBD

## NeoPixel
TBD

## RelayModule
TBD

## EPaper display
TBD

# Boards
We will build a few boards with a fixed setup.   
All boards are running the same software, but with different configurations.   
To determine which configuration should be used, the `BOARD_TYPE`-property in `configuration.py` can be changed to any of the following types:
- BOARD_CONTROL_RGB_3
- BOARD_CONTROL_RELAY_4
- BOARD_SENSE_LUX_RGB_1
- BOARD_PROTOTYPE_SETUP_1 (used for prototyping only)

In one of the next versions we will determine the board type using `jumpers` on the board itself.   
That way we can flash each board with the exact same software.  
Base on the state of the `jumpers` the software will know which configuration to use.   

Below an overview of the existing boards.   

## CONTROL_RGB_3
This board is using the `NeoPixel`-module to control a RGB(W) LED strip with 3 LEDs.   
The LED strip can be controlled by sending data to channel 0.   
All LEDs will always have the same color.   

## CONTROL_RELAY_4
With this board it is possible to control 4 relays, using the `RelayModule`.   
Each relay has its own channel and can be controlled by sending a `state` to that channel.   

## BOARD_SENSE_LUX_RGB_1
This board contains a LUX and RGB sensor, controlled by the `LightSensorModule` and `RGBSensorModule`.   
The light sensor can be controlled on channel 0.   
While the RGB sensor is listening on channel 1.   