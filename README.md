# Light-Colour-Led-Testbench

Automated testbench to measure and visualize light intensity and RGB colour of LEDs, screens and other light sources.  
Special focus on testing a Philips Hue lamp and a Philips Hue motion sensor, with results shown on a small display with graphs.

## Goal

Build a compact, ESP32‑based testbench that can:

- Measure light intensity and colour (R/G/B) of various light sources using a colour sensor.
- Automatically control a Philips Hue lamp via the Hue Bridge API.
- Test and visualize the behaviour of a Philips Hue motion sensor.
- Show live data and graphs on a small local display.

All controlled by an ESP32 running MicroPython.

## Features (planned)

### 1. Motion Sensor Test Mode

Test the Philips Hue motion sensor independently.

- Read from Hue Bridge API:
  - `state.presence` (motion detected yes/no)
  - `state.lightlevel` (sensor light level)
- Optionally read local light sensor (TCS34725) for comparison.
- Display on screen:
  - Current presence status
  - Current light level
  - Time‑based graph (last 30–60 s) of presence and/or light level
- Buttons:
  - Start/Stop measurement (reset buffer)
  - Back to dashboard

Optional automation:
- Small servo or motor to move an object in front of the sensor for repeatable motion patterns.

---

### 2. Light / Colour Test Mode

Test lamps and other light sources (e.g. Philips Hue lamp).

- Control Hue lamp via Hue Bridge API:
  - On/off
  - Brightness
  - Colour (xy or hue/sat)
- Measure with local colour sensor (TCS34725):
  - R, G, B, clear (intensity)
- Display on screen:
  - Current lamp settings (colour + brightness)
  - Measured R/G/B/clear values (numeric)
  - Graph over time / test steps:
    - Intensity (clear channel)
    - Or separate R, G, B lines
- Buttons:
  - Run full test (predefined sequence of colours/brightness levels)
  - Single step (test one specific setting)

---

### 3. Dashboard Mode

Overview screen with key metrics and mini‑graphs.

- Show latest values:
  - Motion sensor: presence, lightlevel
  - Light sensor: R, G, B, clear
- Mini graphs:
  - Presence over time (last ~30 s)
  - R/G/B or intensity over time (last ~30 s)
- System status:
  - Wi‑Fi connected (yes/no)
  - Hue Bridge reachable (yes/no)
- Buttons:
  - Navigate to Motion Sensor Test
  - Navigate to Light / Colour Test

---

## Hardware (planned)

- **Microcontroller**
  - ESP32 (e.g. DOIT ESP32 DevKit v1 or similar)

- **Light / colour sensor**
  - TCS34725 (I²C)  
    - Measures R, G, B, clear (intensity)

- **Display**
  - Option A: 1.3"–1.8" TFT (ST7735 / ILI9341, SPI)  
  - Option B: 0.96" OLED (SSD1306, I²C)  
  - Used for menus, numeric values and simple line graphs.

- **Buttons**
  - 2–3 push buttons:
    - MODE: switch between Dashboard / Motion Test / Light Test
    - START/STOP: start or reset a measurement
    - BACK / STEP: context‑dependent navigation

- **Philips Hue ecosystem**
  - Philips Hue Bridge (v2/v3)
  - Philips Hue lamp (device under test)
  - Philips Hue motion sensor (device under test)

- **Optional**
  - Servo (SG90) or small motor + driver to simulate motion in front of the Hue motion sensor.
  - Additional lux sensor (e.g. BH1750) for independent lux reference.

---

## Software architecture (planned)

Firmware on ESP32 in MicroPython.

### Main structure

- `main.py`
  - Initialize hardware:
    - I²C (TCS34725, optional OLED)
    - SPI (if using TFT)
    - Buttons
    - Wi‑Fi
  - Main loop:
    - Read buttons
    - Update current mode:
      - 0: Dashboard
      - 1: Motion Sensor Test
      - 2: Light / Colour Test
    - Call corresponding screen/logic function

- `motion_test.py`
  - `fetch_motion_sensor_state()` – read from Hue API
  - `run_motion_test(display, buffer)` – main test loop
  - Maintain ring buffer for last N samples (presence, lightlevel)
  - Draw:
    - Current status text
    - Line graph of presence/lightlevel over time

- `light_test.py`
  - `set_lamp_colour(bri, xy/hue_sat)` – send command to Hue lamp
  - `read_light_sensor()` – read R/G/B/clear from TCS34725
  - `run_light_test(display, buffer)` – step through colours/brightness
  - Draw:
    - Current lamp settings
    - Measured R/G/B/clear values
    - Graph of intensity or R/G/B over time/steps

- `dashboard.py`
  - `show_dashboard(display, motion_buffer, light_buffer)`
  - Show:
    - Latest motion sensor values
    - Latest light sensor values
    - Mini graphs
    - Wi‑Fi & Bridge status

- `hue_api.py`
  - HTTP wrappers for Hue Bridge:
    - `get_sensor_state(sensor_id)`
    - `set_light_state(light_id, **kwargs)`
  - Handle:
    - Wi‑Fi connection
    - API username/token
    - Error handling (Bridge unreachable, etc.)

### Display & graphs

- Use a MicroPython display library depending on screen:
  - ST7735 / ILI9341 for TFT
  - SSD1306 for OLED
- Custom simple graph function:
  - X‑axis: time or step index
  - Y‑axis: mapped sensor value to pixel height
  - Multiple lines for R, G, B if needed

---

## User workflow

1. Power on the ESP32 testbench.
2. Use **MODE** button to switch between:
   - Dashboard
   - Motion Sensor Test
   - Light / Colour Test
3. In **Motion Sensor Test**:
   - Press **START** to begin logging.
   - Move in front of the Hue motion sensor (or let servo move).
   - Watch live presence status and graph on the display.
4. In **Light / Colour Test**:
   - Press **RUN TEST** to execute a predefined sequence of lamp colours/brightness.
   - Or use **STEP** to test a single setting.
   - Watch measured R/G/B/clear values and graphs.
5. Use **Dashboard** for a quick overview of both sensors and system status.

---

## Future extensions (optional)

- Log all measurements to SD card or send to a PC/server for deeper analysis.
- Web interface on ESP32 or external dashboard (e.g. on Raspberry Pi).
- More advanced colour metrics (derived from R/G/B, e.g. approximate colour temperature).
- Automated motion patterns with servo control and configurable profiles.
- Support for additional light sources (other smart bulbs, screens, etc.).

---

## Repo structure (planned)

```text
Light-Colour-Led-Testbench/
├─ README.md
├─ docs/
│  └─ hardware_plan.md
├─ firmware/
│  ├─ main.py
│  ├─ motion_test.py
│  ├─ light_test.py
│  ├─ dashboard.py
│  ├─ hue_api.py
│  └─ sensors/
│     └─ tcs34725.py
└─ hardware/
   ├─ wiring_diagram.png
   └─ bom.md
```

---

## Notes

- All communication with the Philips Hue lamp and motion sensor goes through the Hue Bridge API (HTTP over Wi‑Fi).
- The local colour sensor (TCS34725) is used for independent measurement of light intensity and RGB content.
- The project is designed to be modular: additional sensors, displays or test modes can be added later without restructuring everything.
