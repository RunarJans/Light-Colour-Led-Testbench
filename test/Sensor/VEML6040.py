
from machine import Pin, I2C
import time

# =====================================
# ESP32 HW-395 V0.0.3
# VEML6040 RGBW
# =====================================

ADDR = 0x10

REG_CONF  = 0x00
REG_RED   = 0x08
REG_GREEN = 0x09
REG_BLUE  = 0x0A
REG_WHITE = 0x0B

i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=100000
)

# =====================================
# SCHRIJF 16-BIT REGISTER
# =====================================

def write_word(reg, value):

    data = bytes([
        reg,
        value & 0xFF,
        (value >> 8) & 0xFF
    ])

    i2c.writeto(ADDR, data)


# =====================================
# LEES 16-BIT REGISTER
# =====================================

def read_word(reg):

    # Commandocode versturen
    i2c.writeto(ADDR, bytes([reg]))

    # Twee bytes ontvangen
    data = i2c.readfrom(ADDR, 2)

    # Low byte eerst, high byte daarna
    value = data[0] | (data[1] << 8)

    return value


# =====================================
# SENSOR INITIALISEREN
# =====================================

def init_sensor():

    # IT = 000 : 40 ms
    # TRIG = 0
    # AF = 0 : automatische modus
    # SD = 0 : sensor actief

    write_word(REG_CONF, 0x0000)

    time.sleep_ms(100)

    print("VEML6040 geinitialiseerd")


# =====================================
# RGBW UITLEZEN
# =====================================

def read_rgbw():

    red = read_word(REG_RED)
    green = read_word(REG_GREEN)
    blue = read_word(REG_BLUE)
    white = read_word(REG_WHITE)

    return red, green, blue, white


# =====================================
# HOOFDPROGRAMMA
# =====================================

print("ESP32 VEML6040 RGBW")
print("===================")

print("I2C scan:", [hex(x) for x in i2c.scan()])

if ADDR not in i2c.scan():

    print("Sensor niet gevonden!")

else:

    init_sensor()

    while True:

        try:

            red, green, blue, white = read_rgbw()

            print("")
            print("------ RGBW ------")
            print("RED   :", red)
            print("GREEN :", green)
            print("BLUE  :", blue)
            print("WHITE :", white)

        except Exception as e:

            print("I2C fout:", e)

        time.sleep(1)
