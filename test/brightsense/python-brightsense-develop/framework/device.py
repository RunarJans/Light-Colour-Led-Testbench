import machine
from framework.lightsensor import LightSensor
from framework.relaymodule import RelayModule
from framework.statusmodule import StatusModule
from framework.rgbstatusmodule import RGBStatusModule
from lib.umqttsimple import MQTTClient
import ubinascii
import machine
from machine import Pin
import network
from utime import sleep
from model.broadcastregistrationmodel import BroadcastRegistrationModel
import ntptime
from framework.mqttmethods import MQTTMethods

class Device:
    BROADCAST_TOPIC_RSP = 'broadcast/rsp'
    BROADCAST_TOPIC_CMD = 'broadcast/cmd'

    name: str
    client_id: bytes
    mac: str
    hostname: str
    ip: str

    mqtt_client: MQTTClient

    indication_led: Pin
    _status_module: RGBStatusModule

    personal_topic_rsp: str
    personal_topic_cmd: str

    device_type: str

    def __init__(self, name, device_type: str, status_module: RGBStatusModule):
        self.name = name
        self.client_id = ubinascii.hexlify(machine.unique_id())
        self.personal_topic_rsp = self.client_id.decode() + '/rsp'
        self.personal_topic_cmd = self.client_id.decode() + '/cmd'

        self.device_type = device_type

        #self.indication_led = Pin("LED", Pin.OUT)
        # ESP32: configure the onboard indication LED using a GPIO number.
        self.indication_led = Pin(2, Pin.OUT)
        self._status_module = status_module
        self._status_module.enablePowerLED()

        self._peripherals = []

    # Wait until the expected wifi network is available
    def waitForWifiNetwork(self, wlan: network.WLAN, ssid):
        wifi_scan_cnt = 0
        while True:
            print('Scanning for wifi networks')
            
            # Scan for available networks
            available_networks = wlan.scan()
            wifi_scan_cnt += 1

            # Map Tuple to something more readable
            network_mapping = [
                {
                    "ssid": t[0].decode(),
                    "bssid": ubinascii.hexlify(t[1]).decode('utf-8'),
                    "channel": t[2],
                    "RSSI": t[3],
                    "security": t[4],
                    "hidden": t[5]
                }
                for t in available_networks
            ]
            print(network_mapping)

            # Check if list of networks contains expected SSID
            found = False
            for net in network_mapping:
                print('Found network: ' + str(net))
                if net['ssid'] == ssid:
                    print('Wifi network found with SSID ' + ssid)
                    found = True
                    break
            
            # Break out of the loop when SSID is available
            if found:
                break
            elif wifi_scan_cnt > 5:
                print('Could not find expected network "'+ ssid +'" in time')
                self._status_module.enableErrorLED()
                raise Exception("Could not find expected network")

            # Wait 5 seconds to try again
            sleep(5)

    # This will setup the WLAN connection
    def setup(self, ssid, password):
        # Show that the Pico is alive
        self.indication_led.on()
        sleep(0.5)
        self.indication_led.off()

        print("Activating WLAN")
        self._status_module.enableWlanLED()
        wlan = network.WLAN(network.STA_IF)
       
        wlan.active(True)

        self.waitForWifiNetwork(wlan, ssid)

        if not wlan.isconnected():
            print("Connecting to " + ssid + "...")
            wlan.connect(ssid, password)
        else:
            print("Already connected to " + ssid + "!")

        status = -128
        retries = 0
        while not wlan.isconnected():
            self.indication_led.toggle()
            status = wlan.status()

            if status == network.STAT_IDLE:
                # device is not trying to connect yet; so start the connection
                # print("Connecting to " + ssid + "...")
                wlan.connect(ssid, password)

            elif status == network.STAT_GOT_IP:
                print("Connected, IP address:", wlan.ifconfig()[0])
                break

            elif status == network.STAT_CONNECT_FAIL:
                print("Connection failed!")
                self._status_module.enableErrorLED()
                retries += 1
                if retries < 5:
                    print('Retry connecting...')
                    wlan.connect(ssid, password)
                else:
                    break

            elif status == network.STAT_WRONG_PASSWORD:
                print("Wrong password! Tried '" + password + "'")
                retries += 1
                if retries >= 5:
                    break

            elif status == network.STAT_CONNECTING:
                print('Connecting...')

            else:
                print("Unknown status code: " + str(status))
            
            sleep(1)

        # Reset controller when unable to connect to wifi network
        if not wlan.isconnected():
            raise Exception("Unable to connect to Wifi network, try hard reset")
            #self.restart('Unable to connect to Wifi network, trying hard reset', 5)
        else:
            self._status_module.disableErrorLED()

        print('Connected successfully to ' + ssid)
        self._status_module.enableWlanLED()
        self.indication_led.value(1)
        
        print('Network details:')
        print(wlan.ifconfig())
        
        self.mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
        self.hostname = str(wlan.config('hostname'))
        self.ip = wlan.ifconfig()[0]
        print("Device details:")
        print("MAC address: " + self.mac)
        print('Hostname: ' + self.hostname)
        print('Client ID: "' + self.client_id.decode() + '"')
        print('IP: ' + self.ip)

        try:
            # Synchronise clock with time server
            # Ignore when synchronisation failed
            # print("Sync NTP time")
            # ntptime.settime()
            # print("Time sync done")
            print("ntp disabled")
        except Exception as e:
            print('Unable to set NTP time: ' + str(e))

        return self

    def mqtt_setup(self, server, username, password, callback, topics: list[str] = [] ):
        print("Connecting to MQTT server...")
        self._status_module.enableMqttLED()
        self.mqtt_client = MQTTClient(self.client_id, server, user=username, password=password, port=1883)
        self.mqtt_client.set_callback(callback)

        success = False
        retries = 0
        originalError = None
        while success == False and retries < 3:
            try:
                self.mqtt_client.connect()
                success = True
            except Exception as e:
                retries += 1
                originalError = e
                print('Unable to connect to MQTT broker: ' + str(e))
                sleep(3)

        if success == False:
            raise Exception('Unable to connect to MQTT broker: ' + str(originalError))

        print("Subscribing to channels...")
        topics.append(self.BROADCAST_TOPIC_CMD)
        topics.append(self.personal_topic_cmd)

        for topic in topics:
            print('subscribing to ' + topic)
            self.mqtt_client.subscribe(topic)

        print('Connected to "%s" MQTT broker, subscribed to "%s" topic' % (server, topics))
        print('Client id: ' + self.client_id.decode())

        print("Notifying server")
        self.broadcast(MQTTMethods.DISCOVERY_REGISTER)

        print("Connected successfully to MQTT server")

        return self.mqtt_client
    
    def broadcast(self, method: str):
        broadcastmodel = BroadcastRegistrationModel(self.client_id.decode(), self.ip, self.mac, self.device_type, method)
        print('Broadcasting ' + broadcastmodel.toJSON())
        self.mqtt_client.publish(self.BROADCAST_TOPIC_RSP, broadcastmodel.toJSON())

    def restart(self, reason: str, timeout: int):
        print(reason)
        sleep(timeout)
        machine.reset()

    def register_peripheral(self, peripheral):
        self._peripherals.append(peripheral)

    def get_peripherals(self):
        return self._peripherals

    def get_peripherals_by_type(self, peripheralType: str):
        result = [x for x in self._peripherals if x.TYPE == peripheralType]
        return result
