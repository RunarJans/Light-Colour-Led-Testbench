from machine import Pin, I2C
import time

# ==========================================
# ESP32 + HW-395 + VEML7700
# Automatic gain control
# ==========================================

I2C_SDA = 21
I2C_SCL = 22
I2C_FREQ = 100000

VEML7700_ADDR = 0x10

ALS_CONFIG = 0x00
ALS_DATA = 0x04
WHITE_DATA = 0x05

INTEGRATION_TIME = 100

# Vishay Application Note 84323
# Resolutie in lux/count bij 100 ms
RESOLUTION_TABLE = {
    0.125: 0.5376,  # Gain 1/8
    0.25:  0.2688,  # Gain 1/4
    1.0:   0.0672,  # Gain 1
    2.0:   0.0336   # Gain 2
}

# Kalibratie op basis van UT383 bij 1021 lux:
# VEML = 1111 lux
# UT383 = 1021 lux
CALIBRATION_FACTOR = 1021 / 1111

GAINS = [
    (2, 0.125, "1/8"),
    (3, 0.25,  "1/4"),
    (0, 1.0,   "1"),
    (1, 2.0,   "2")
]

# Gain switching thresholds
RAW_LOW = 1500
RAW_HIGH = 4000

gain_index = 0

i2c = I2C(
    0,
    scl=Pin(I2C_SCL),
    sda=Pin(I2C_SDA),
    freq=I2C_FREQ
)


def read_register(register):
    data = i2c.readfrom_mem(
        VEML7700_ADDR,
        register,
        2
    )
    return data[0] | (data[1] << 8)


def write_register(register, value):
    i2c.writeto_mem(
        VEML7700_ADDR,
        register,
        value.to_bytes(2, "little")
    )


# ==========================================
# DYNAMIC REFERENCE RESOLUTION
# ==========================================
def get_resolution(index):
    gain = GAINS[index][1]
    # Basisresolutie uit Vishay-tabel bij 100 ms
    reference = RESOLUTION_TABLE[gain]
    # Aanpassen aan integratietijd
    resolution = reference * (100 / INTEGRATION_TIME)
    return resolution


# ==========================================
# SENSOR CONFIGURATION
# ==========================================

def set_gain(index):

    global gain_index

    gain_index = index

    gain_code, gain, gain_name = GAINS[index]

    # IT = 100 ms, sensor enabled
    config = gain_code << 11

    write_register(ALS_CONFIG, config)

    # Wait for a fresh measurement
    time.sleep_ms(INTEGRATION_TIME + 150)

    return gain


def init_sensor():

    set_gain(gain_index)

    print("Configuration:", hex(read_register(ALS_CONFIG)))


# ==========================================
# VISHAY LUX CORRECTION
# ==========================================

def calculate_lux(raw, index):
    resolution = get_resolution(index)
    # Lineaire luxberekening
    lux_raw = raw * resolution
    # Kalibratie tegenover UT383
    lux = lux_raw * CALIBRATION_FACTOR
    return lux, resolution


# ==========================================
# AUTOMATIC GAIN CONTROL
# ==========================================

def read_light():
    global gain_index
    raw = read_register(ALS_DATA)
    old_gain = gain_index

    if raw < RAW_LOW and gain_index < len(GAINS) - 1:
        gain_index += 1
    elif raw > RAW_HIGH and gain_index > 0:
        gain_index -= 1
    if gain_index != old_gain:
        print(
            "Changing gain:",
            GAINS[old_gain][2],
            "->",
            GAINS[gain_index][2]
        )
        set_gain(gain_index)
        # Read a fresh sample with the new gain
        raw = read_register(ALS_DATA)

    white = read_register(WHITE_DATA)
    lux, resolution = calculate_lux(raw, gain_index)
    return raw, white, lux, resolution


# ==========================================
# MAIN
# ==========================================
print()
print("ESP32 VEML7700 AUTO GAIN")
print("========================")

devices = i2c.scan()
print("I2C devices:", [hex(d) for d in devices])

if VEML7700_ADDR not in devices:
    print("ERROR: VEML7700 not found!")

else:
    init_sensor()
    print("Sensor initialized")
    print("Integration:", INTEGRATION_TIME, "ms")
    print("========================")

    while True:
        try:
            raw, white, lux_linear, resolution = read_light()

            print("ALS raw        :", raw)
            print("WHITE raw      :", white)
            print("Gain           :", GAINS[gain_index][2])
            print("Resolution     :", resolution)
            print("Lux linear     : {:.2f}".format(lux_linear))

            if raw > 60000:
                print("WARNING: Sensor near saturation!")

            print("------------------------")

        except Exception as e:

            print("Measurement error:", e)

        time.sleep_ms(200)
