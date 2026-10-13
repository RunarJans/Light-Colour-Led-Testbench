# Onderdelenlijst — ESP32 Hue/RGB-lamptester

| Onderdeel | Aantal | Functie | Opmerking |
|---|---:|---|---|
| ESP32 DevKit V1, 30-pin | 1 | Besturing, Wi-Fi, Hue-status uitlezen, sensoren en display aansturen | 3,3 V-logica |
| AS7341 kleur-/spectraalsensor | 1 | Meet kleur en spectrum van de lamp | I2C, adres 0x39 |
| BH1750 / GY-302 luxsensor | 1 | Meet lichtintensiteit in lux | I2C, adres 0x23 |
| 1,3" ST7789 TFT-display, 240x240 | 1 | Toont kleur, hex/RGB en lux | SPI, 3,3 V |
| Tactile push button, 6x6 mm | 1 | Wisselt tussen kleur- en luxweergave | GPIO27 naar GND, interne pull-up |
| LED | 1 | Statusweergave | Bijvoorbeeld: meting bezig |
| Weerstand 330 ohm | 1 | Stroombeperking status-LED | 1/4 W |
| 5 V USB-voedingsadapter, min. 2 A | 1 | Voedt ESP32, display en sensoren | Via USB of VIN |
| Micro-USB-datakabel | 1 | Programmeren en voeden | Moet data ondersteunen |
| E27-lampsnoer met EU-stekker en schakelaar | 1 | Voedt de Hue-lamp rechtstreeks | Kant-en-klaar, geen relais nodig |
| Philips Hue-kleurlamp, E27 | 1 | Te testen lamp | Kleur en helderheid instelbaar |
| Zwart karton, vilt of verf | 1 | Eenvoudige donkere meetopstelling | Vermindert omgevingslicht en reflecties |
| Dubbelzijdige tape of hot glue | 1 | Sensoren en display bevestigen | Tijdelijke of vaste montage |
| DC Motor | 1 | Bewegingstest |  |
| Optioneel: condensator 100 nF | 3 | Ontkoppeling voedingsrail | Dicht bij modules plaatsen |
| Optioneel: condensator 470 uF, 10 V | 1 | Buffer bij Wi-Fi-pieken | Voorkomt mogelijke brownout-resets |
