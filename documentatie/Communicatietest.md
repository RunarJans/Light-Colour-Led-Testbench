# Communicatietest Brightsense (ESP32 + laptop-server)

Met deze test controleer je of je ESP32 het MQTT-protocol van Brightsense (BrightLinQ) spreekt.
Je gebruikt twee scripts:

| Script | Draait op | Rol |
|---|---|---|
| `test_device.py` | ESP32 (via Thonny) | Nep-lichtsensor die zich gedraagt als een Brightsense-device |
| `laptop_server.py` | Laptop (via cmd) | Nep-server die scant, commando's stuurt en antwoorden toont |

Thuis praten ze via de publieke broker `broker.hivemq.com`. Bij Brightsense wissel je enkel van profiel.
Iedereen kan op die publieke broker meelezen, dus stuur er geen gevoelige data over.

---

## 1. Wat moet je aanpassen?

### In `test_device.py` (ESP32)
| Wat | Waar | Thuis (test) | Bij Brightsense |
|---|---|---|---|
| `PROFIEL` | bovenaan | `"thuis"` | `"brightlinq"` |
| Wifi-wachtwoord | profiel `thuis`, `"password"` | wachtwoord van je eigen wifi invullen | niet nodig (`brightlinq`) |
| Broker | profiel `brightlinq`, `"server"` | niet nodig | IP-adres van `brightlinq.local` invullen |
| `DEVICE_TYPE` | onder de profielen | `"TEST_ESP32_LUX"` | eventueel `Configuration.BOARD_SENSE_LUX_RGB_1` |
| `prefix` | profiel `thuis` | `"mijn-test/"` (mag je veranderen) | blijft `""` (leeg) |

### In `laptop_server.py` (laptop)
| Wat | Waar | Waarde |
|---|---|---|
| `PREFIX` | bovenaan | moet **exact gelijk** zijn aan `prefix` van profiel `thuis` in `test_device.py` |
| `BROKER` | bovenaan | `broker.hivemq.com` (niet wijzigen) |

Wil je een uniek prefix (omdat de broker publiek is)? Verander `mijn-test/` op beide plaatsen naar bijvoorbeeld `mijn-test-4821/`.

De laptop heeft geen wifi-instellingen nodig. Hij gebruikt je gewone internetverbinding.

---

## 2. Voorbereiding (eenmalig)

### Op de ESP32
1. Sluit de ESP32 aan via USB.
2. Thonny: **Run -> Configure interpreter -> MicroPython (ESP32)** en kies je poort (bv. COM7).
3. Open **View -> Files**.
4. Upload via rechtermuisknop -> **Upload to /** deze vier dingen vanuit `C:\pad\naar\python-brightsense-develop`:
   - map `lib`
   - map `framework`
   - map `model`
   - bestand `configuration.py`
5. Upload **niet** `main.py`. Dat draait bij elke opstart automatisch en crasht op Pico-pinnen (`invalid pin`).
6. Maak een nieuw bestand `test_device.py` (zie code onderaan) en sla het op op **This computer** in dezelfde map.

### Op de laptop
1. Open cmd in de projectmap: typ `cmd` in de adresbalk van Verkenner en druk Enter.
2. Installeer paho-mqtt in Python 3.11 (de Python van MinGW heeft geen pip, 3.14 is een alfaversie):

```
C:\Python311\python.exe -m pip install -U paho-mqtt
```

   Staat pip er niet? Voer eerst uit: `C:\Python311\python.exe -m ensurepip --upgrade`
3. Maak `laptop_server.py` (zie code onderaan):

```
notepad laptop_server.py
```

   Sla op met **Opslaan als type: Alle bestanden**, anders wordt het `laptop_server.py.txt`.

---

## 3. Thuis testen

### Stap 1: ESP32 starten
1. Open `test_device.py` in Thonny. Controleer: `PROFIEL = "thuis"` en wachtwoord ingevuld.
2. Klik op de rode **Stop**-knop en daarna op **Run**.
3. Wacht tot dit verschijnt:

```
Wifi OK, IP: ... MAC: ...
subscribing to mijn-test/broadcast/cmd
subscribing to mijn-test/<id>/cmd
Broadcasting {"client_id": ..., "method": "discovery.register", ...}
Listening for messages!
```

### Stap 2: laptop-server starten
Typ in cmd:

```
C:\Python311\python.exe laptop_server.py
```

Stoppen doe je met **Ctrl+C**.

### Stap 3: resultaat controleren
**In cmd (laptop):**

```
MQTT verbonden met broker.hivemq.com - resultaat: Success
SCAN: {...}
DEVICE GEVONDEN: <id> | type TEST_ESP32_LUX | ip ... | via discovery.scan
>>> Testreeks start voor <id>
COMMANDO naar mijn-test/<id>/cmd : {...}
ANTWOORD op device.list ... status 200 OK
ANTWOORD op device.get ... status 200 OK
ANTWOORD op device.set ... status 200 OK
ANTWOORD op device.get ... status 404 Channel "5" not found
PUSH van <id> -> {...}
```

**In Thonny (ESP32):** `ONTVANGEN op ...`, `GET reply`, `SET reply`, `LIST reply`, `PUSH reply` en `>>> WHOIS ontvangen`.

### Wat de testreeks controleert
| Commando | Verwacht |
|---|---|
| `device.list` | status 200, lijst met de sensor |
| `device.get` kanaal 0 | status 200, sensordata |
| `device.set` | status 200, `interval` en `polling` veranderen |
| `device.get` kanaal 5 | status 404 `Channel "5" not found` |
| `device.whois` | geen antwoord, de ESP32 toont `WHOIS ontvangen` |
| pushes | elke 5 seconden zolang `polling` aan staat |

---

## 4. Testen met het echte Brightsense-systeem

Je hebt `laptop_server.py` hier niet nodig. Hun eigen server neemt die rol over.

1. Verbind je **pc** met wifi `BrightLinQ` (wachtwoord `brightlinq`).
2. Zoek het IP van de broker in cmd:

```
ping brightlinq.local
```

   Noteer het IP tussen de blokhaken. Een ESP32 kan `.local`-namen meestal niet omzetten, dus je gebruikt het IP.
3. Verbind je pc eventueel terug met je gewone netwerk. De ESP32 verbindt zelf met `BrightLinQ`.
4. In `test_device.py`:
   - zet `PROFIEL = "brightlinq"`
   - vul bij profiel `brightlinq` het IP in bij `"server"`
   - overweeg `DEVICE_TYPE = Configuration.BOARD_SENSE_LUX_RGB_1`
5. Klik op **Stop** en daarna op **Run**.
6. Controleer dat `Wifi OK` verschijnt en daarna `Connected successfully to MQTT server`, en kijk bij Brightsense of het device verschijnt.

Het prefix is dan leeg, dus je gebruikt precies hun topics: `<id>/cmd`, `<id>/rsp`, `broadcast/cmd` en `broadcast/rsp`.

---

## 5. Problemen oplossen

| Fout | Oplossing |
|---|---|
| `Wifi Internal State Error` | Druk op EN/RESET van de ESP32 en start opnieuw |
| `Wifi verbinden mislukt` | Naam of wachtwoord fout, of geen 2.4 GHz netwerk |
| `ImportError: no module named 'framework'` | `framework`, `lib`, `model` of `configuration.py` staat niet op de ESP32 |
| `invalid pin` | Je draait `main.py` van Brightsense (Pico-pinnen). Gebruik `test_device.py` |
| `OSError -202` / "Kan broker niet omzetten" | Gebruik een IP-adres in plaats van `brightlinq.local` |
| Laptop toont geen `DEVICE GEVONDEN` | `PREFIX` verschilt tussen laptop en ESP32, of de ESP32 draait niet |
| `'python' is not recognized` / `No module named 'pip'` | Gebruik `C:\Python311\python.exe` |
| `no attribute 'CallbackAPIVersion'` | `C:\Python311\python.exe -m pip install -U paho-mqtt` |
| `can't open file laptop_server.py` | Bestand heet `.py.txt` of staat in een andere map (controleer met `dir`) |
| Poort bezet in Thonny | Klik op Stop, of sluit andere programma's die COM7 gebruiken |

---

## 6. Beperkingen

- Dit is een nepsensor met een verzonnen waarde. Er is geen echte VEML7700 of RGB-sensor aangesloten.
- `device.whois` laat op een echt bord de status-LED knipperen. In de test wordt alleen een tekst getoond.
- Het `epoch`-veld is de interne klok van de ESP32 zonder NTP, net als het originele framework (`ntp disabled`).
- Of de echte Brightsense-server het device accepteert, zie je pas bij hen (type, kanalen).

---

## 7. Volledige code: `test_device.py` (ESP32)

```python
import network
import time
import ujson
import ubinascii
import machine
import socket
from lib.umqttsimple import MQTTClient
from framework.mqttmethods import MQTTMethods
from model.broadcastregistrationmodel import BroadcastRegistrationModel
from configuration import Configuration

# ============================================================
#  ENIGE PLEK DIE JE MOET AANPASSEN
# ============================================================
PROFIEL = "thuis"      # "thuis" of "brightlinq"

PROFIELEN = {
    "thuis": {
        "ssid": "JOUW_WIFI",
        "password": "JOUW_WACHTWOORD",
        "server": "broker.hivemq.com",
        "prefix": "mijn-test/",   # voorkomt botsing op de publieke broker
    },
    "brightlinq": {
        "ssid": "BrightLinQ",
        "password": "brightlinq",
        "server": "192.168.X.X",     # IP van brightlinq.local invullen
        "prefix": "",                # leeg = exact de topics van Brightsense
    },
}
# ============================================================

P = PROFIELEN[PROFIEL]
SSID = P["ssid"]
PASSWORD = P["password"]
SERVER = P["server"]
PREFIX = P["prefix"]

DEVICE_NAME = "Test lichtsensor ESP32"
DEVICE_TYPE = "TEST_ESP32_LUX"   # evt. Configuration.BOARD_SENSE_LUX_RGB_1

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC_RSP = PREFIX + CLIENT_ID.decode() + "/rsp"
TOPIC_CMD = PREFIX + CLIENT_ID.decode() + "/cmd"
BROADCAST_CMD = PREFIX + "broadcast/cmd"
BROADCAST_RSP = PREFIX + "broadcast/rsp"

KNOWN_CHANNELS = [0]

mac = ""
ip = ""
client = None


# ---------------- Nepsensor (zelfde gedrag als LightSensor) ----------------
class FakeLightSensor:
    TYPE = "LightSensorModule"

    def __init__(self, channel):
        self._channel = channel
        self._interval = 5
        self._polling = False
        self._last_message = 0
        self._last_status = 200
        self._last_status_message = "OK"
        self._has_error = False

    def get_status(self):
        return {"status": self._last_status,
                "message": self._last_status_message,
                "has_error": self._has_error}

    def _value(self):
        return 100 + int(time.time()) % 50

    def to_device_list(self):
        return {
            "type": self.TYPE,
            "channel": self._channel,
            "value": self._value(),
            "interval": self._interval,
            "polling": self._polling,
        }

    def _to_dict(self, client_id, method, message_id):
        return {
            "client_id": client_id,
            "method": method,
            "message_id": message_id,
            "data": self.to_device_list(),
            "epoch": time.time(),
            "status": self._last_status,
            "message": self._last_status_message,
        }

    def _to_error_dict(self, client_id, method, message_id):
        return {
            "client_id": client_id,
            "method": method,
            "message_id": message_id,
            "epoch": time.time(),
            "status": self._last_status,
            "message": self._last_status_message,
        }

    def main_task(self, topic, mqtt_client, client_id):
        if (time.time() - self._last_message) > self._interval:
            if self._polling:
                result = ujson.dumps(
                    self._to_dict(client_id, MQTTMethods.DEVICE_PUSH, "NA"))
                print("PUSH reply " + result)
                mqtt_client.publish(topic, result)
            self._last_message = time.time()

    def handle_message(self, obj, topic, mqtt_client):
        method = obj["method"]
        message_id = obj.get("message_id", "")
        channel = obj.get("channel", Configuration.DEFAULT_CHANNEL)
        message_client_id = obj["client_id"]

        if channel != self._channel:
            return

        if method == MQTTMethods.DEVICE_GET:
            result = ujson.dumps(
                self._to_dict(message_client_id, method, message_id))
            print("GET reply " + result)
            mqtt_client.publish(topic, result)

        if method == MQTTMethods.DEVICE_SET:
            try:
                data = obj["data"]
                self._interval = data.get("interval", self._interval)
                self._polling = data.get("polling", self._polling)
                result = ujson.dumps(
                    self._to_dict(message_client_id, method, message_id))
                print("SET reply " + result)
                mqtt_client.publish(topic, result)
            except Exception as e:
                self._last_status = 500
                self._last_status_message = str(e)
                self._has_error = True
                result = ujson.dumps(
                    self._to_error_dict(message_client_id, method, message_id))
                print("SET error reply " + result)
                mqtt_client.publish(topic, result)


sensor = FakeLightSensor(0)


# ---------------- Wifi ----------------
def reset_wifi():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.disconnect()
    except OSError:
        pass
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)
    return wlan


def connect_wifi():
    global mac, ip
    for poging in range(1, 4):
        print("Verbinden met wifi:", SSID, "(poging", poging, "van 3)")
        try:
            wlan = reset_wifi()
            wlan.connect(SSID, PASSWORD)
        except OSError as e:
            print("Wifi fout:", e)
            time.sleep(2)
            continue

        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > 15:
                break
            time.sleep(0.5)

        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            mac = ubinascii.hexlify(wlan.config("mac"), ":").decode()
            print("Wifi OK, IP:", ip, "MAC:", mac)
            return

        print("Niet verbonden, status:", wlan.status())

    raise RuntimeError("Wifi verbinden mislukt (naam, wachtwoord, 2.4 GHz, bereik?)")


# ---------------- MQTT ----------------
def broadcast(method):
    model = BroadcastRegistrationModel(
        CLIENT_ID.decode(), ip, mac, DEVICE_TYPE, method)
    print("Broadcasting " + model.toJSON())
    client.publish(BROADCAST_RSP, model.toJSON())


def post_error(topic, method, message_id, status, message):
    error_message = {
        "client_id": CLIENT_ID.decode(),
        "method": method,
        "message_id": message_id,
        "epoch": time.time(),
        "status": status,
        "message": message,
    }
    payload = ujson.dumps(error_message)
    print(payload)
    client.publish(topic, payload)


def list_device(obj):
    response = {
        "client_id": obj["client_id"],
        "method": obj["method"],
        "message_id": obj.get("message_id", ""),
        "data": [sensor.to_device_list()],
        "epoch": time.time(),
        "status": 200,
        "message": "OK",
    }
    payload = ujson.dumps(response)
    print("LIST reply " + payload)
    client.publish(TOPIC_RSP, payload)


def on_message(tpc, msg):
    topic, message = tpc.decode(), msg.decode()
    print("ONTVANGEN op", topic, ":", message)

    try:
        obj = ujson.loads(message)
        method = obj["method"]
    except Exception as e:
        print("Ongeldig bericht:", e)
        return

    message_id = obj.get("message_id", "")

    if topic == TOPIC_CMD and method == MQTTMethods.DEVICE_LIST:
        list_device(obj)

    elif topic == TOPIC_CMD and method == MQTTMethods.DEVICE_WHOIS:
        print(">>> WHOIS ontvangen: hier zou de status-LED knipperen")

    elif topic == TOPIC_CMD:
        channel = obj.get("channel", Configuration.DEFAULT_CHANNEL)
        if channel not in KNOWN_CHANNELS:
            post_error(TOPIC_RSP, method, message_id, 404,
                       'Channel "' + str(channel) + '" not found')
        else:
            sensor.handle_message(obj, TOPIC_RSP, client)

    elif topic == BROADCAST_CMD:
        if method == MQTTMethods.DISCOVERY_SCAN:
            broadcast(MQTTMethods.DISCOVERY_SCAN)

    else:
        print("Geen implementatie voor", topic, method)


def check_server():
    try:
        socket.getaddrinfo(SERVER, 1883)
    except OSError as e:
        print("Kan broker '" + SERVER + "' niet omzetten naar een IP:", e)
        print("Gebruik het IP-adres in plaats van de naam (.local werkt niet op ESP32).")
        raise


def connect_mqtt():
    global client
    check_server()
    print("Verbinden met MQTT-broker:", SERVER)
    client = MQTTClient(CLIENT_ID, SERVER, port=1883)
    client.set_callback(on_message)

    gelukt = False
    fout = None
    for poging in range(3):
        try:
            client.connect()
            gelukt = True
            break
        except Exception as e:
            fout = e
            print("Broker niet bereikbaar:", e)
            time.sleep(3)
    if not gelukt:
        raise Exception("Verbinden met MQTT-broker mislukt: " + str(fout))

    for topic in (BROADCAST_CMD, TOPIC_CMD):
        print("subscribing to " + topic)
        client.subscribe(topic)

    print("Client id:", CLIENT_ID.decode())
    print("Notifying server")
    broadcast(MQTTMethods.DISCOVERY_REGISTER)
    print("Connected successfully to MQTT server")


# ---------------- Start ----------------
print("Profiel:", PROFIEL, "| framework", Configuration.FRAMEWORK_VERSION)
connect_wifi()
connect_mqtt()
print("Listening for messages!")

while True:
    try:
        client.check_msg()
        sensor.main_task(TOPIC_RSP, client, CLIENT_ID.decode())
        time.sleep(0.1)
    except OSError as e:
        print("Verbinding verbroken:", e, "- opnieuw verbinden")
        time.sleep(3)
        try:
            connect_wifi()
            connect_mqtt()
        except Exception as e2:
            print("Herverbinden mislukt:", e2)
```

---

## 8. Volledige code: `laptop_server.py` (cmd)

```python
import json
import threading
import time

import paho.mqtt.client as mqtt

# ============================================================
#  MOET GELIJK ZIJN AAN HET PROFIEL OP ESP32 A
# ============================================================
BROKER = "broker.hivemq.com"
PORT = 1883
PREFIX = "mijn-test/"
# ============================================================

CLIENT_ID = "laptop-server-" + str(int(time.time()))
BROADCAST_CMD = PREFIX + "broadcast/cmd"
BROADCAST_RSP = PREFIX + "broadcast/rsp"
RSP_FILTER = PREFIX + "+/rsp"      # alle devices, ook broadcast/rsp

COMMAND_INTERVAL = 6   # seconden tussen commando's
SCAN_INTERVAL = 10     # seconden tussen scans zolang er geen device is

# Testreeks die om de beurt naar het ontdekte device gaat
COMMANDS = [
    {"method": "device.list"},
    {"method": "device.get", "channel": 0},
    {"method": "device.set", "channel": 0, "data": {"interval": 5, "polling": True}},
    {"method": "device.whois"},
    {"method": "device.get", "channel": 5},   # bestaat niet: fout 404 verwacht
    {"method": "device.set", "channel": 0, "data": {"interval": 10, "polling": True}},
    {"method": "device.set", "channel": 0, "data": {"interval": 5, "polling": False}},
]

target = None
lock = threading.Lock()


def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT verbonden met", BROKER, "- resultaat:", reason_code)
    client.subscribe(RSP_FILTER)
    print("Luisteren op:", RSP_FILTER)


def on_message(client, userdata, msg):
    global target
    topic = msg.topic
    try:
        obj = json.loads(msg.payload.decode())
    except Exception:
        print("ONTVANGEN (geen JSON) op", topic, ":", msg.payload)
        return

    method = obj.get("method")

    if topic == BROADCAST_RSP:
        print("DEVICE GEVONDEN:", obj.get("client_id"),
              "| type", obj.get("type"),
              "| ip", obj.get("ip"),
              "| versie", obj.get("version"),
              "| via", method)
        with lock:
            if target is None:
                target = obj.get("client_id")
                print(">>> Testreeks start voor", target)

    elif method == "device.push":
        print("PUSH van", obj.get("client_id"), "->", obj.get("data"))

    else:
        print("ANTWOORD op", method, "(id", obj.get("message_id"), ") status",
              obj.get("status"), obj.get("message"), "->", obj.get("data"))


def send_scan(client):
    payload = json.dumps({
        "client_id": CLIENT_ID,
        "method": "discovery.scan",
        "message_id": "scan-" + str(int(time.time())),
    })
    print("SCAN:", payload)
    client.publish(BROADCAST_CMD, payload)


def send_command(client, teller):
    cmd = dict(COMMANDS[teller % len(COMMANDS)])
    cmd["client_id"] = CLIENT_ID
    cmd["message_id"] = "cmd-" + str(teller + 1)
    topic = PREFIX + target + "/cmd"
    payload = json.dumps(cmd)
    print("COMMANDO naar", topic, ":", payload)
    client.publish(topic, payload)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

time.sleep(1)
send_scan(client)

teller = 0
laatste_cmd = 0
laatste_scan = time.time()

try:
    while True:
        with lock:
            huidig = target

        if huidig is None:
            if time.time() - laatste_scan >= SCAN_INTERVAL:
                send_scan(client)
                laatste_scan = time.time()
        elif time.time() - laatste_cmd >= COMMAND_INTERVAL:
            send_command(client, teller)
            teller += 1
            laatste_cmd = time.time()

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Gestopt.")
    client.loop_stop()
    client.disconnect()
```
