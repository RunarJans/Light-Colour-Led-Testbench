from utime import sleep
from machine import Pin
import ujson
from framework.mqttmethods import MQTTMethods
import time
from configuration import Configuration
from lib.umqttsimple import MQTTClient
import ubinascii

import ubinascii
from machine import Pin, SPI


from lib.picoepaper import EPD_2in9_B
from lib.bmptoframebuffer import BMPToFramebuffer

logo = "Qk0+CAAAAAAAAD4AAAAoAAAAgAAAAIAAAAABAAEAAAAAAAAIAADCDgAAwg4AAAAAAAAAAAAAAAAAAP///wD////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////gB///////////////////wAH//////////////////4AAAAAf//////////////8AAAAAD//////////////+AAAAAAf//////////////B/4H/8D//////////////g//B//wf/////////////wf/4P/+D/////////////4P//B//wf//////////AAAAAD4P/+D//////////gAAAAA+D//wf/////////wAAAAAPwf/+D/////////4AAAAAD+H//wB////////8D/+H///h//+AP///////+B//h///4f//gB////////A//4f//+H//4If///////gf/+AAAAAD/+HD//////+AP//gAAAAAf/jw//////+AH//4AAAAAD/4cP//////AD//+AAAAAAf+AH//////wA///h////+D/wB//////4cP//8f////wf+A//////+Hj///H////+D/5///////hw/8AAAAAA/wf////////8AP8AAAAAAH+D/////////AH+AAAAAAB/wf////////4B/AAAAAAAf+D/////////B/gf4f//+H/wf//////////wP+H///h/+D//////////4H/h///4f/wf/////////8D/4f//+H/+D/////////+B/+H///h//wf/////////A//h///4f/+D/////////gf/w////D//wf////////wP/8P///w//+D////////4H/+H///+H//wf///////8D//B////g//+H///////+B//g////8H//w////////A//wf////g//8P///////wf/4P////8H//D///////8P/8H/////g//w////////D/+D/////8P/8P///////w//g//////B//D///////8P/wf/3///4P/gf///////D/8P/4f///D/wD///////w/+H/8D///4f4Af//////8P/h/+Af//+H+GH///////D/w//AD///w/Dx///////w/8P/gAf//8Pw8f//////wD/D/wAD///D8OH//////4Afh/4AAf//4fgB//////+AH4f8AAD//+H4A///////jh+H+AAAf//h/Af//////w8Ph/ADAD//4f8f//////+GH4fgB4Af//H/////////gB+P4A/AD//x/////////4A/j+Af4Af/8P/////////AP4/wP/AD//H/////////8P+H+H/4Af/x////////////h/z//AD/4f///////////4f///4Af+H///////////+H////AD/h////////////h////4Af4f///////////4f////AD+H////////////D////4A/D////////////w/////APw////////////8H////4D4P////////////h/////B+H////////////4P////4/B/////////////D//////w/////////////wf/////4P////////////+D/////8H/////////////wf////+D/////////////8D/////A//////////////gf////gf/////////////8D////wP//////////////gP///4H//////////////8B///4D///////////////wH//4B///////////////+AH/gB////////////////4AAAA///////////////z/gAAA///////////////4f+AAB/4f////////////8H/+AH/+D////////////+B//////gf////////////A//////8D////////////gf//////gf///////////wP//////8D///////////4H///n///gf//////////+D///w///8H///////////h///8P///h///////////4////D///8f///////////////w////////////////////8P////////////////////D////////////////////w////////////////////8P////////////////////D////////////////////w////////////////////8P////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////w=="

class EpaperModule:
    TYPE = 'EpaperModule'
    _gpio_pin: Pin
    _channel: int

    _checksum: str

    _last_status: int
    _last_status_message: str
    _has_error: bool

    def get_status(self):
        return { 'status': self._last_status, 'message': self._last_status_message, 'has_error': self._has_error }

    def __str__(self) -> str:
        return 'Type: ' + self.TYPE + ', channel: ' + str(self._channel)
    
    def _add_device_info(self, y=130, lines = None):
        if lines == None:
            lines = [self.TYPE, self.device.client_id.decode(), self.device.ip]
        self._eink.imageblack.hline(0, y, 128, 0x00)
        y+=10
        for line in lines:
            self._eink.imageblack.text(line, 0, y, 0x00)
            y+=15

    def display_bmp_and_device_info(self, bmp_data, x_offset=0, y_offset=0):
        self._eink.init()
        self._eink.clear_buffer()
        bmp_processor = BMPToFramebuffer()
        _, _, height, _ = bmp_processor.parse_bmp_header(bmp_data)
        image_fb = bmp_processor.convert_bmp_to_mono_buffer(bmp_data)
        self._eink.imageblack.blit(image_fb, x_offset, y_offset)
        self._add_device_info(y=height+2)
        self._eink.display()
        self._eink.delay_ms(2000)
        self._eink.sleep()

    def __init__(self, channels: list[int], sck: int = 10, mosi: int = 11, cs: int = 9, dc: int = 8, rst: int = 12, busy: int = 13):   # Default pins assigned for Waveshare 2.9inch epaper display module
        print("Setup Epaper module")
        self._channel = channels[0] # module can only have one channel

        spi = SPI(1, baudrate=4000_000, phase=0, polarity=0, sck=Pin(sck), mosi=Pin(mosi))
        self._eink = EPD_2in9_B(spi, cs, dc, rst, busy)
        
        self._last_status = 200
        self._last_status_message = 'OK'
        self._has_error = False
        self._checksum = ""

    def setup(self) -> "EpaperModule":
        self._checksum = "logo"
        bmp_data = ubinascii.a2b_base64(logo)
        self.display_bmp_and_device_info(bmp_data)

        return self
    
    def add_device(self, device) -> "EpaperModule":
        self.device = device
        return self

    def _to_class_dict(self):
        return {
                'channel': self._channel,
                'checksum': self._checksum,
                'image': self._checksum
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
                    if message_object['data']['image'] == None:
                        raise NameError(f"No data object provided in request json")
                    if message_object['data']['image'] == "":
                        # Display logo
                        bmp_data = ubinascii.a2b_base64(logo)
                        self._checksum = "logo"
                        self.display_bmp_and_device_info(bmp_data)
                        
                    else:
                        # Display received image
                        message_data = message_object['data']['image']
                        message_object['data']['image'] = ""        
                        bmp_data = ubinascii.a2b_base64(message_data)
                        self._checksum = ubinascii.crc32(message_data)
                        del message_data
                        self.display_bmp_and_device_info(bmp_data)

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
