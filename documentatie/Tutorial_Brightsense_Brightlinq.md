# 2.1 BrightLinq (server)

## 2.1.1 Startup

Volg onderstaande stappen om de BrightLinq-server op te starten en de compatibiliteit met de microcontroller te testen.

1. Open het project **BrightLinq** in een IDE naar keuze, zoals PyCharm, Visual Studio Code of Thonny.
2. Controleer of Python geïnstalleerd is:

   ```bash
   python --version
   ```

3. Maak een virtuele Python-omgeving aan en activeer deze.
4. Installeer de vereiste dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start de server:

   ```bash
   python main.py
   ```

6. Open de API-documentatie via [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Hier kunnen de beschikbare endpoints worden bekeken en getest.

De server is klaar voor gebruik wanneer de documentatie bereikbaar is en de API correct reageert.

## 2.1.2 API – EmLinQ v1

De BrightLinq-server biedt een REST API voor communicatie met embedded apparaten. De API is gedocumenteerd volgens de OpenAPI 3.1-specificatie.

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OpenAPI-specificatie:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

### HealthController (`/v1/health`)

Controleert de beschikbaarheid en status van de server.

| Methode | Endpoint | Beschrijving |
|---|---|---|
| GET | `/v1/health` | Controleert of de server bereikbaar is. |
| GET | `/v1/health-details` | Geeft gedetailleerde statusinformatie. |

### MqttController (`/v1/mqtt`)

Beheert het publiceren van gegevens en commando's via MQTT.

| Methode | Endpoint | Beschrijving |
|---|---|---|
| POST | `/v1/mqtt/publish` | Publiceert gegevens via MQTT. |
| POST | `/v1/mqtt/publish-cqs` | Publiceert een command-querybericht. |

### Discovery (`/v1/discovery`)

Zoekt naar beschikbare apparaten en geeft verbonden apparaten weer.

| Methode | Endpoint | Beschrijving |
|---|---|---|
| GET | `/v1/discovery/scan` | Start een nieuwe zoekopdracht naar apparaten. |
| GET | `/v1/discovery/list` | Geeft de verbonden apparaten weer. |

### Device (`/v1/device`)

Biedt endpoints om apparaten uit te lezen, aan te sturen en te identificeren. Afhankelijk van de methode voert de microcontroller een actie uit en stuurt de server een antwoord terug.

Om een ander type testbench, zoals Brightsense, toe te voegen, moet de API indien nodig worden uitgebreid of aangepast.

| Methode | Endpoint | Beschrijving |
|---|---|---|
| GET | `/v1/device/{device_id}/get` | Leest gegevens van een apparaat uit. |
| POST | `/v1/device/{device_id}/set` | Wijzigt gegevens van een apparaat. |
| GET | `/v1/device/{device_id}/list` | Geeft de beschikbare apparaatgegevens weer. |
| GET | `/v1/device/{device_id}/whois` | Activeert de status-led van het apparaat om het te identificeren. |

### Schemas

De API-documentatie bevat schemas voor request- en responsegegevens, waaronder `Device`, `DiscoveryListResponse`, `DiscoveryScanResponse` en `MqttPublishRequest`. Daarnaast zijn er schemas voor HTTP- en validatiefouten.

Deze schemas beschrijven de verwachte gegevensstructuur en helpen bij het correct opbouwen van API-verzoeken.

---

# 2.2 Brightsense (client/microcontrollers)

## 2.2.1 Startup

1. Download de MicroPython-firmware die geschikt is voor de ESP32.
2. Open het project **Brightsense** in een IDE naar keuze, zoals PyCharm, Visual Studio Code of Thonny.
3. Flash de MicroPython-firmware op de ESP32.
4. Stel de interpreter van de IDE in op de MicroPython-interpreter van de ESP32.
5. Kopieer de benodigde Python-bestanden naar de microcontroller. Kopieer `main.py` tijdens het debuggen bij voorkeur niet naar de microcontroller, omdat deze automatisch wordt uitgevoerd bij het opstarten. Dit kan het testen en debuggen bemoeilijken.
6. Voer `main.py` uit op de verbonden microcontroller vanuit de IDE.

## 2.2.2 Structuur van het basisproject

- **`configuration.py`**: bevat de configuratie van de gebruikte peripherals, zoals GPIO-pinnen en sensoren.
- **`main.py`**: initialiseert de peripherals en voegt deze op basis van `configuration.py` toe aan het device.
- **`framework/device.py`**: beheert de MQTT-communicatie, device-identiteit, topics en de lijst `self._peripherals`, met peripherals zoals leds, relais en e-paperdisplays.
- **`framework/*module.py`**: bevat drivers voor aansturingsmodules, zoals relais, NeoPixels en e-paperdisplays.
- **`framework/*sensor.py`**: bevat drivers voor sensoren, zoals RGB-kleursensoren en lichtsensoren.

## 2.2.3 Wat aanpassen voor een nieuwe testbench?

| Bestand | Aanpassen? | Wanneer? |
|---|---|---|
| `configuration.py` | Ja | Bij een andere boardconfiguratie, GPIO-pinnen, kanalen of peripherals. |
| `main.py` | Meestal | Wanneer nieuwe modulenamen of initialisatieprocedures nodig zijn. |
| `framework/device.py` | Idealiter niet | Alleen wanneer de algemene device- of MQTT-functionaliteit moet veranderen. |
| Nieuwe `framework/*module.py`- of `framework/*sensor.py`-bestanden | Vaak | Wanneer de sensor of controlemodule niet door een bestaande module wordt ondersteund. |
| `lib/` | Soms | Wanneer de nieuwe hardware een extra driver of bibliotheek nodig heeft. |

