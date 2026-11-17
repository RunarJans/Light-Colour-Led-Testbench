
from machine import Pin, I2C
import time

# --------------------------------
# ESP32 HW-395 - VEML7700
# --------------------------------

I2C_SDA = 21
I2C_SCL = 22
VEML7700_ADDR = 0x10

# I2C initialiseren
i2c = I2C(
    0,
    scl=Pin(I2C_SCL),
    sda=Pin(I2C_SDA),
    freq=100000
)

# Sensorregisters
ALS_CONFIG = 0x00
ALS_DATA = 0x04
WHITE_DATA = 0x05


def write_register(register, value):
    data = bytearray(2)
    data[0] = value & 0xFF
    data[1] = (value >> 8) & 0xFF
    i2c.writeto_mem(
        VEML7700_ADDR,
        register,
        data
    )


def read_register(register):
    data = i2c.readfrom_mem(
        VEML7700_ADDR,
        register,
        2
    )
    return data[0] | (data[1] << 8)


def init_sensor():
    # Gain = 1
    # Integration time = 100 ms
    # Sensor ingeschakeld
    write_register(ALS_CONFIG, 0x0000)

    time.sleep_ms(150)


def read_light():
    raw = read_register(ALS_DATA)
    white = read_register(WHITE_DATA)

    # Lux-conversie bij gain 1 en 100 ms
    lux = raw * 0.0672

    return raw, white, lux


# --------------------------------
# Hoofdprogramma
# --------------------------------

print("ESP32 VEML7700 gestart")

devices = i2c.scan()
print("I2C apparaten:", [hex(d) for d in devices])

if VEML7700_ADDR not in devices:
    print("FOUT: VEML7700 niet gevonden!")
else:
    init_sensor()

    print("VEML7700 gevonden")
    print("------------------------------")

    while True:
        try:
            raw, white, lux = read_light()

            print("ALS waarde :", raw)
            print("White      :", white)
            print("Lichtsterkte: {:.2f} lux".format(lux))
            print("------------------------------")

        except Exception as e:
            print("Meetfout:", e)

        time.sleep(1)
