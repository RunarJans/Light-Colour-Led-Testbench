
from machine import Pin, I2C
import time

# =====================================
# ESP32 HW-395 V0.0.3
# ISL29125 RGB SENSOR
# =====================================

SDA_PIN = 21
SCL_PIN = 22

ISL_ADDRESS = 0x44

# Registeradressen
DEVICE_ID = 0x00
CONFIG_1 = 0x01
CONFIG_2 = 0x02
CONFIG_3 = 0x03

STATUS = 0x08

GREEN_LOW = 0x09
RED_LOW = 0x0B
BLUE_LOW = 0x0D

# =====================================
# I2C INITIALISEREN
# =====================================

i2c = I2C(
    0,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=100000
)

# =====================================
# REGISTER FUNCTIES
# =====================================

def write_reg(reg, value):
    i2c.writeto_mem(
        ISL_ADDRESS,
        reg,
        bytes([value])
    )


def read_reg(reg):
    return i2c.readfrom_mem(
        ISL_ADDRESS,
        reg,
        1
    )[0]


def read_color(reg):
    data = i2c.readfrom_mem(
        ISL_ADDRESS,
        reg,
        2
    )

    return data[0] | (data[1] << 8)


# =====================================
# SENSOR INITIALISEREN
# =====================================

def init_sensor():

    sensor_id = read_reg(DEVICE_ID)

    print("Sensor ID:", hex(sensor_id))

    if sensor_id != 0x7D:
        raise Exception("Verkeerde sensor ID!")

    # RGB modus
    # 16-bit resolutie
    # Meetbereik 375 lux
    write_reg(CONFIG_1, 0x05)

    # Standaard configuratie
    write_reg(CONFIG_2, 0x00)
    write_reg(CONFIG_3, 0x00)

    # Sensor laten stabiliseren
    time.sleep_ms(400)

    print("ISL29125 succesvol gestart")


# =====================================
# RGB METING
# =====================================

def read_rgb():

    red = read_color(RED_LOW)
    green = read_color(GREEN_LOW)
    blue = read_color(BLUE_LOW)

    return red, green, blue


# =====================================
# HOOFDPROGRAMMA
# =====================================

print("")
print("ESP32 - ISL29125 RGB SENSOR")
print("============================")

devices = i2c.scan()

print("I2C apparaten:",
      [hex(device) for device in devices])

if ISL_ADDRESS not in devices:

    print("FOUT: ISL29125 niet gevonden!")

else:

    try:
        init_sensor()

        while True:

            red, green, blue = read_rgb()

            print("")
            print("----- RGB METING -----")

            print("ROOD  :", red)
            print("GROEN :", green)
            print("BLAUW :", blue)

            print("----------------------")

            time.sleep(1)

    except Exception as e:
        print("Sensorfout:", e)
