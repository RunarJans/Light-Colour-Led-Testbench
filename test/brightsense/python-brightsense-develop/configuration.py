class Configuration:
    DEFAULT_CHANNEL = 0
    DEFAULT_SSID = 'IoT' #'BrightLinQ'
    DEFAULT_SSID_PASSWORD = 'InternetOfThings' #'brightlinq'

    DEFAULT_MQTT_SERVER = '192.168.3.107' # 'brightlinq.local'
    DEFAULT_MQTT_USERNAME = ''
    DEFAULT_MQTT_PASSWORD = ''

    BOARD_CONTROL_RGB_3 = 'CONTROL_RGB_3'
    BOARD_NO_IO = 'NO_IO_1'
    BOARD_SENSE_VEML7700_1 = 'SENSE_VEML7700_1'

    BOARD_PROTOTYPE_SETUP_1 = 'FRANKEN_STEIN_1'

    # SELECT ON WHICH TYPE OF BOARD THE SOFTWARE IS USED
    BOARD_TYPE = BOARD_SENSE_VEML7700_1

    FRAMEWORK_VERSION = '0.0.1-beta'

    def __init__(self):
        self._control_rgb_3 = {
            'name': 'Control 3 RGB LEDs',
            'type': self.BOARD_CONTROL_RGB_3,
            'wlan': {
                'ssid': self.DEFAULT_SSID,
                'password': self.DEFAULT_SSID_PASSWORD
            },
            'mqtt': {
                'server': self.DEFAULT_MQTT_SERVER,
                'username': self.DEFAULT_MQTT_USERNAME,
                'password': self.DEFAULT_MQTT_PASSWORD
            },
            'rgb_status_leds': {
                'enabled': True,
                'gpio_status_pin': 16,
                'gpio_error_pin': -1,
            },
            'peripherals': [
                {
                    'type': 'NeoPixelLedModule',
                    'enabled': True,
                    'gpio_pin': 2,
                    'led_count': 3,
                    "channels": [0]
                },
            ],
        }

        # PROTOTYPING SETUP

        self._franken_controller = {
            'name': 'Frankenstein setup',
            'type': self.BOARD_PROTOTYPE_SETUP_1,
            'wlan': {
                'ssid': self.DEFAULT_SSID,
                'password': self.DEFAULT_SSID_PASSWORD
            },
            'mqtt': {
                'server': self.DEFAULT_MQTT_SERVER,
                'username': self.DEFAULT_MQTT_USERNAME,
                'password': self.DEFAULT_MQTT_USERNAME
            },
            'status_leds': {
                'enabled': True,
                'gpio_pins': [18, 19, 20, 21]
            },
            'rgb_status_leds': {
                'enabled': True,
                'gpio_status_pin': 0,
                'gpio_error_pin': 1,
            },
            'peripherals': [
                {
                    'type': 'EpaperModule',
                    'enabled': True,
                    "channels": [0]
                },
                {
                    'type': 'RelayModule',
                    'enabled': False,
                    'gpio_pin': 28,
                    "channels": [0]
                },
                {
                    'type': 'RelayModule',
                    'enabled': False,
                    'gpio_pin': 27,
                    "channels": [1]
                },
                {
                    'type': 'RelayModule',
                    'enabled': False,
                    'gpio_pin': 26,
                    "channels": [2]
                },
                {
                    'type': 'RelayModule',
                    'enabled': False,
                    'gpio_pin': 22,
                    "channels": [3]
                },
                {
                    'type': 'LightSensorModule',
                    'enabled': False,
                    'channels': [4],
                    'i2c': {
                        'sda': 16,
                        'scl': 17,
                        'frequency': 10000,
                        'bus': 0
                    }
                },
                {
                    'type': 'RGBSensorModule',
                    'enabled': True,
                    'channels': [5],
                    'i2c': {
                        'sda': 16,
                        'scl': 17,
                        'frequency': 10000,
                        'bus': 0
                    },
                    'gpio_pin': 15,
                },
                {
                    'type': 'NeoPixelLedModule',
                    'enabled': True,
                    'gpio_pin': 14,
                    'led_count': 5,
                    "channels": [6]
                },
            ],
        }
        self._sense_veml7700_1 = {
            'name': 'VEML7700 Light Sensor',
            'type': self.BOARD_SENSE_VEML7700_1,

            'wlan': {
                'ssid': self.DEFAULT_SSID,
                'password': self.DEFAULT_SSID_PASSWORD
            },

            'mqtt': {
                'server': self.DEFAULT_MQTT_SERVER,
                'username': self.DEFAULT_MQTT_USERNAME,
                'password': self.DEFAULT_MQTT_PASSWORD
            },
            'rgb_status_leds': {
                'enabled': True,
                'gpio_status_pin': 14,
                'gpio_error_pin': 15,
            },
            'peripherals': [
                {
                    'type': 'VEML7700Module',
                    'enabled': True,
                    'channels': [0],
                    'i2c': {
                        'sda': 21,
                        'scl': 22,
                        'frequency': 100000,
                        'bus': 0,
                        'address': 0x10
                    },
                    'settings': {
                        'gain': 1,
                        'integration_time': 100,
                    }
                },
            ],
        }

    def getConfiguration(self):
        print('Using configuration for ' + self.BOARD_TYPE + ' board')
        if self.BOARD_TYPE == self.BOARD_CONTROL_RGB_3:
            return self._control_rgb_3
        elif self.BOARD_TYPE == self.BOARD_SENSE_VEML7700_1:
            return self._sense_veml7700_1
        else:
            print('Unknown board type: ' + self.BOARD_TYPE)
            raise Exception('Unknown board type: ' + self.BOARD_TYPE)
    
    def setConfiguration(self, configuration):
        self._configuration = configuration

    configuration = property(getConfiguration, setConfiguration)
