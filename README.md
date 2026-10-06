# Light-Colour-Led-Testbench

Geautomatiseerde ESP32‑testbank om lichtsterkte, RGB‑kleur en de werking van een Philips Hue‑bewegingssensor te testen.  
Resultaten worden live weergegeven op een ingebouwd schermpje met grafieken en simpele scores.

## Doel

- **Lamp‑test:**  
  Een Hue‑lamp (of andere lichtbron) wordt door verschillende kleuren en wit‑/warmlicht gestuurd.  
  Een kleursensor meet helderheid per kleur en kleuraccuraatheid. Resultaten worden in grafieken getoond.

- **Bewegingstest:**  
  Een mechanisch element beweegt 10× voor een Philips Hue‑bewegingssensor.  
  De ESP32 controleert via de Hue Bridge of de sensor elke beweging detecteert en toont een score **X/10**.

Alles wordt aangestuurd door een ESP32 met MicroPython.

---

## Gebruik

### Lamp‑test

1. Draai de lamp in de houder van de testbank.
2. Sluit de behuizing (donkere meetkamer).
3. Druk op **“Start lamp‑test”**.

De testbank:

- Stuurt de lamp automatisch door een vaste reeks:
  - Rood, groen, blauw, cyaan, magenta, geel
  - Warm wit, neutraal wit, koud wit
  - Uit
- Meet bij elke stap met een TCS34725‑kleursensor:
  - R, G, B, clear (helderheid)
- Toont op het scherm:
  - Grafieken van helderheid per kleur (R/G/B over de teststappen)
  - Kleuraccuraatheid (vergelijking verwachte vs. gemeten R/G/B‑verhouding)
  - Optioneel een samenvattende score (bijv. “Kleuraccuraatheid: 87 %”)

---

### Bewegingstest

1. Monteer de Philips Hue‑bewegingssensor op de voorziene plek.
2. Zorg dat het bewegingselement (bijv. servo met vlagje) vrij kan bewegen.
3. Druk op **“Start bewegingstest”**.

De testbank:

- Beweegt 10× een object voor de sensor (vast patroon).
- Vraagt na elke beweging via de Hue Bridge API:
  - `state.presence` (gedetecteerd ja/nee)
  - Optioneel `state.lightlevel`
- Telt hoeveel keer de sensor correct reageerde.
- Toont op het scherm:
  - Tijdens de test: “Getest: 3/10”, “Gedetecteerd: 2/10”
  - Na afloop: **“Score: 8/10”** (en eventueel een korte kwalificatie)

---

## Hardware (kern)

- ESP32 (MicroPython)
- TCS34725 kleursensor (I²C)
- Klein display (TFT of OLED)
- 2–3 drukknoppen:
  - “Start lamp‑test”
  - “Start bewegingstest”
  - Optioneel: “Mode / Dashboard”
- Philips Hue Bridge + Hue lamp + Hue bewegingssensor
- Optioneel: servo/motor voor bewegingstest

---

## Software (op ESP32)

- `main.py` – hoofdloop, knoppen, modus‑keuze
- `light_test.py` – lamp‑testreeks, sensor uitlezen, grafieken
- `motion_test.py` – 10× beweging, Hue API uitlezen, X/10 score
- `dashboard.py` – overzichtsscherm met laatste resultaten
- `hue_api.py` – HTTP‑communicatie met Hue Bridge
- `sensors/tcs34725.py` – driver voor de kleursensor

---

## Resultaten

- **Lamp‑test:**
  - Grafieken van helderheid per kleur (R/G/B)
  - Kleuraccuraatheid (verwachting vs. meting)
  - Optioneel samenvattende scores

- **Bewegingstest:**
  - Eenvoudige, duidelijke score **X/10**
  - Optioneel kwalificatie (zeer goed / goed / matig / slecht)

---

## Opmerkingen

- Alle communicatie met lamp en bewegingssensor verloopt via de Hue Bridge API (HTTP over Wi‑Fi).
- De testbank evalueert het systeemgedrag: “Bij beweging detecteert de sensor dit wel/niet betrouwbaar?”
- Het project is modulair: extra sensoren, tests of een webinterface kunnen later eenvoudig worden toegevoegd.
