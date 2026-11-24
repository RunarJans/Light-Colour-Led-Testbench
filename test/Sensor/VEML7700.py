from machine import Pin, I2C
import time

# ==========================================
# ESP32 + HW-395 + VEML7700
# Gain: 1/8
# Integration time: 100 ms
# Supply: 3.3 V
# ==========================================

I2C_SDA = 21
I2C_SCL = 22
I2C_FREQ = 100000

VEML7700_ADDR = 0x10

ALS_CONFIG = 0x00
ALS_DATA = 0x04
WHITE_DATA = 0x05

# Gain 1/8, integration time 100 ms,
# shutdown disabled.
CONFIG_VALUE = 0x1000

# Official resolution for gain 1/8, IT 100 ms
LUX_RESOLUTION = 0.4608

# I2C
i2c = I2C(
    0,
    scl=Pin(I2C_SCL),
    sda=Pin(I2C_SDA),
    freq=I2C_FREQ
)


def write_register(register, value):
    data = bytearray(2)
    data[0] = value & 0xFF
    data[1] = (value >> 8) & 0xFF
    i2c.writeto_mem(VEML7700_ADDR, register, data)


def read_register(register):
    data = i2c.readfrom_mem(
        VEML7700_ADDR,
        register,
        2
    )
    return data[0] | (data[1] << 8)


def init_sensor():
    write_register(ALS_CONFIG, CONFIG_VALUE)

    # Allow sensor to start and complete integration
    time.sleep_ms(250)

    config = read_register(ALS_CONFIG)

    print("Configuration readback:", hex(config))

    if config != CONFIG_VALUE:
        raise Exception("VEML7700 configuration incorrect")


def calculate_lux(raw):
    # Convert raw counts to linear lux
    lux = raw * LUX_RESOLUTION

    # Vishay non-linearity correction.
    # Applied when ALS raw count is above 100.
    if raw > 100:
        lux = (
            6.0135e-13 * lux**4
            - 9.3924e-9 * lux**3
            + 8.1488e-5 * lux**2
            + 1.0023 * lux
        )

    return lux


def read_light():
    raw = read_register(ALS_DATA)
    white = read_register(WHITE_DATA)

    lux_linear = raw * LUX_RESOLUTION
    lux_corrected = calculate_lux(raw)

    return raw, white, lux_linear, lux_corrected


# ==========================================
# MAIN
# ==========================================

print()
print("ESP32 VEML7700 Lux Meter")
print("========================")

devices = i2c.scan()
print("I2C devices:", [hex(d) for d in devices])

if VEML7700_ADDR not in devices:
    print("ERROR: VEML7700 not found!")

else:
    init_sensor()

    print("Sensor initialized")
    print("Gain: 1/8")
    print("Integration: 100 ms")
    print("Resolution:", LUX_RESOLUTION, "lux/count")
    print("========================")

    while True:
        try:
            raw, white, linear, corrected = read_light()

            print("ALS raw       :", raw)
            print("WHITE raw     :", white)
            print("Linear lux    : {:.2f}".format(linear))
            print("Corrected lux : {:.2f}".format(corrected))

            if raw > 60000:
                print("WARNING: Sensor near saturation!")

            elif raw < 100:
                print("WARNING: Low raw count; consider higher gain.")

            print("------------------------")

        except Exception as e:
            print("Measurement error:", e)

        time.sleep_ms(1000)
