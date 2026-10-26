# Light-Colour-Led-Testbench

Geautomatiseerde ESP32-testbank om lichtsterkte, kleur en de werking van een Philips Hue-bewegingssensor te testen.
De resultaten worden live getoond op een ingebouwd schermpje met waarden, grafieken en simpele scores.

## Doel

- **Lamp-test:**
  Een Hue-lamp (of andere lichtbron) wordt door verschillende kleuren en wit-/warmlicht gestuurd.
  Een spectraalsensor (AS7341) meet de kleur en een luxsensor (BH1750) meet de lichtsterkte.
  Zo wordt gecontroleerd of de lamp de gevraagde kleur en helderheid ook echt geeft.

- **Bewegingstest:**
  Een servo beweegt 10× een warm voorwerp of plaatje voor een Philips Hue-bewegingssensor.
  De ESP32 controleert via de Hue Bridge of de sensor elke beweging detecteert en toont een score **X/10**.

Alles wordt aangestuurd door een ESP32 met MicroPython. De lamp wordt getest in een donkere meetruimte (een grote kartonnen doos, binnenin zwart gemaakt).

---

## Gebruik

> De knopbediening hieronder is een voorstel voor de hardware met één drukknop. Pas ze aan als je code anders werkt.

De testbank heeft **één drukknop** (GPIO27, interne pull-up):

- **Korte druk:** wisselt van weergave of modus (kleur / lux / bewegingstest).
- **Lange druk:** start de test van de gekozen modus.

De status-LED licht op terwijl een meting bezig is.

### Lamp-test

1. Draai de Hue-lamp in de E27-fitting in de doos.
2. Sluit de doos (donkere meetkamer).
3. Kies de lamp-test en start ze met een lange druk.

De testbank:

- Stuurt de lamp via de Hue Bridge door een vaste reeks:
  - Rood, groen, blauw, cyaan, magenta, geel
  - Warm wit, neutraal wit, koud wit
  - Uit
- Meet bij elke stap:
  - **AS7341:** spectrum (8 zichtbare banden, clear en NIR) voor de kleur
  - **BH1750:** lichtsterkte in lux
- Toont op het scherm:
  - Gemeten lux per stap en de kleurwaarde (RGB/hex)
  - Grafiek van helderheid per kleur over de teststappen
  - Kleuraccuraatheid: vergelijking van de verwachte en de gemeten kleurverhoudingen
  - Optioneel een samenvattende score (bijv. "Kleuraccuraatheid: 87 %")

De AS7341 kan verzadigen op een lamp van 1100 lm op korte afstand. Zorg daarom voor voldoende afstand, een diffusor (karton) en pas indien nodig de integratietijd aan.

---

### Bewegingstest

1. Monteer de Philips Hue-bewegingssensor op de voorziene plek (3D-geprinte houder).
2. Zorg dat de servo met het plaatje vrij kan bewegen.
3. Kies de bewegingstest en start ze met een lange druk.

De testbank:

- Beweegt 10× een plaatje voor een warmtebron (vast patroon) of beweegt een warm voorwerp voor de sensor.
- Vraagt na elke beweging via de Hue Bridge API of de sensor beweging heeft gezien (`presence` bij de v1-API, `motion` bij de v2-API).
- Telt hoeveel keer de sensor correct reageerde.
- Toont op het scherm:
  - Tijdens de test: "Getest: 3/10", "Gedetecteerd: 2/10"
  - Na afloop: **"Score: 8/10"** (en eventueel een korte kwalificatie)

**Belangrijk:** de sensor is een PIR-sensor. Hij reageert op een verandering in warmte, niet op een voorwerp met dezelfde temperatuur als de omgeving. Gebruik daarom een warmtebron: een warmtematje dat vastligt terwijl de servo een plaatje ervoor langs beweegt, of een handwarmer op de servoarm. Houd er rekening mee dat de sensor na een detectie een korte wachttijd heeft; die bepaalt hoe snel je hem na elkaar kunt triggeren.

---

## Hardware

**Elektronica:**

- ESP32 DevKit V1 (30-pin, MicroPython)
- AS7341 spectraalsensor (I²C, adres 0x39), Adafruit-bordje
- BH1750 luxsensor (I²C, adres 0x23), Adafruit-bordje
- 1,3" IPS-display 240×240, ST7789 (SPI, 3,3 V)
- 1 drukknop (GPIO27) en een status-LED met weerstand van 330 Ω
- SG90-servo (5 V, PWM)
- Voeding: gsm-lader 5 V (minstens 1 A) en een micro-USB-datakabel
- Buffercondensator 1000 µF / 35 V en 3 keramische condensatoren van 100 nF voor ontkoppeling
- Breadboard 830 punten, jumperdraden en Dupont-kabels

**Hue-systeem:**

- Philips Hue Bridge (v2)
- Philips Hue-kleurlamp (E27, 1100 lm)
- Philips Hue Motion Sensor (binnen)
- E27-fitting met snoer, schakelaar en stekker (kant-en-klaar, niet zelf aan 230 V wiren)

**Opstelling:**

- Grote kartonnen doos, binnenin zwart (donkere meetkamer, met ventilatie)
- 3D-geprinte houders voor de sensoren, het display, de servo en de bewegingssensor
- Warmtematje (of handwarmer) als warmtebron voor de bewegingstest

Het volledige overzicht met aantallen, prijzen, leveranciers en alternatieven staat in de BOM (Excel).

---

## Aansluitingen

- **I²C (AS7341 en BH1750):** SDA GPIO21, SCL GPIO22. Beide sensoren voeden op 3,3 V.
- **Display (ST7789):** SPI, 3,3 V. Het backlight kan tijdens de lichtmeting gedimd of uitgeschakeld worden, omdat het de meting verstoort.
- **Drukknop:** GPIO27 naar GND.
- **Status-LED:** een vrije GPIO via 330 Ω. De LED en het display zijn lichtbronnen: schaduw de sensoren af.
- **Servo:** voeding op VIN (5 V), niet op 3,3 V. Massa gemeenschappelijk met de ESP32. De 1000 µF-condensator staat op de 5 V-rail bij de servo.

---

## Software (op ESP32)

- `main.py`: hoofdloop, knop, modus-keuze
- `light_test.py`: lamp-testreeks, sensoren uitlezen, grafieken
- `motion_test.py`: 10× beweging, Hue API uitlezen, X/10 score
- `dashboard.py`: overzichtsscherm met laatste resultaten
- `hue_api.py`: HTTP-communicatie met de Hue Bridge
- `sensors/as7341.py`: driver voor de spectraalsensor
- `sensors/bh1750.py`: driver voor de luxsensor
- `display.py`: aansturing van het ST7789-display
- `servo.py`: aansturing van de servo

> Pas deze lijst aan de echte structuur van de repository aan.

---

## Resultaten

- **Lamp-test:**
  - Lux en kleur per stap
  - Grafieken van helderheid per kleur
  - Kleuraccuraatheid (verwachting vs. meting)
  - Optioneel samenvattende scores

- **Bewegingstest:**
  - Eenvoudige, duidelijke score **X/10**
  - Optioneel kwalificatie (zeer goed / goed / matig / slecht)
  - Optioneel de reactietijd en het kortste interval waarmee de sensor opnieuw triggert

---

## Opmerkingen

- Alle communicatie met lamp en bewegingssensor verloopt via de Hue Bridge API (HTTP over Wi-Fi). De ESP32 en de Bridge moeten op hetzelfde netwerk zitten; de ESP32 gebruikt 2,4 GHz Wi-Fi.
- De testbank evalueert het systeemgedrag: "Bij beweging detecteert de sensor dit wel/niet betrouwbaar?"
- De meetgegevens kunnen ook naar het Brightsense-platform verstuurd worden (MQTT vanaf de ESP32), als dat in de opdracht zit.
- Het project is modulair: extra sensoren, tests of een webinterface kunnen later eenvoudig worden toegevoegd.
- Zonder Hue Motion Sensor vervalt de bewegingstest (en dus de servo en het warmtematje). De lamp-test blijft werken.
