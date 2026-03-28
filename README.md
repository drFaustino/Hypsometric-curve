# Hypsometric Curve (QGIS 4 / Qt6)

**Hypsometric Curve** e' un plugin per QGIS 4 che calcola e visualizza la curva ipsometrica di un bacino idrografico a partire da un modello digitale di elevazione (DEM) e da un poligono che ne delimita l’area.

Il plugin e' stato progettato per essere:
- **scientificamente rigoroso**
- **estremamente veloce** (rasterizzazione GDAL con `ALL_TOUCHED=TRUE`)
- **modulare e manutenibile**
- **compatibile con QGIS 4 + Qt6**
- **editoriale e didattico**, ideale per analisi geomorfologiche, idrologiche e geologiche.

---

## Funzionalita' principali

- Calcolo della **curva ipsometrica** (h/H vs a/A)
- Calcolo di:
  - **h_min**, **h_max**
  - **h_med** (quota media del bacino)
  - **HI – Hypsometric Integral**
  - **aree parziali e cumulative**
- Rasterizzazione del bacino tramite **GDAL** (massima velocita')
- Supporto completo a **Qt6** e **QGIS 4**
- Grafico interattivo con:
  - colore personalizzabile
  - proiezione del punto HI sulla curva
  - griglia e layout ottimizzato
- Esportazione:
  - tabella in **CSV**
  - grafico in **PNG/JPG**
- Architettura modulare:
  - `core/` per la logica scientifica
  - `gui/` per l’interfaccia
  - `resources/` per icone e traduzioni

---

## Struttura del progetto
hypsometric_curve/
│
├── init.py
├── hypsometric_curve.py
│
├── gui/
│   ├── hypsometric_curve_dialog.py
│   └── hypsometric_curve_dialog_base.ui
│
├── core/
│   ├── raster_utils.py
│   ├── calculations.py
│   ├── graph_utils.py
│   └── table_utils.py
│
├── resources/
│   ├── resources.qrc
│   └── resources_rc.py
│
└── i18n/
└── hypsometric_curve_it.qm

---

##  Installazione

1. Copiare la cartella `hypsometric_curve/` nella directory dei plugin di QGIS:
   
   **Windows**
   C:\Users\<utente>\AppData\Roaming\QGIS\QGIS4\profiles\default\python\plugins\

2. Avviare QGIS 4.
3. Aprire **Plugin → Gestisci e installa plugin**.
4. Attivare **Hypsometric Curve**.

---

## Utilizzo

1. Caricare un **DEM** e un **poligono** del bacino.
2. Aprire il plugin da:
- **Plugins → Hypsometric Curve**
- oppure dalla toolbar.
3. Selezionare:
- DEM
- banda
- poligono del bacino
- numero di classi
4. Premere **Calcola**.
5. Esportare:
- tabella (CSV)
- grafico (PNG/JPG)

---

## Requisiti

- **QGIS 4.x**
- **Qt6**
- **GDAL ≥ 3.4**
- **NumPy**
- **Matplotlib**

---

## Metodologia

La curva ipsometrica viene calcolata secondo la definizione classica:

- **a/A** = area cumulativa normalizzata
- **h/H** = quota cumulativa normalizzata

L’**Hypsometric Integral (HI)** è calcolato come:

\[
HI = \frac{\bar{h} - h_{\min}}{h_{\max} - h_{\min}}
\]

dove \(\bar{h}\) è la quota media del bacino.

La rasterizzazione del bacino avviene tramite:
gdal.RasterizeLayer(..., options=["ALL_TOUCHED=TRUE"])

garantendo una maschera continua e accurata.

---

## Validazione

Il plugin è stato testato con:

- DEM SRTM 30 m
- DEM LiDAR 1 m
- Bacini di dimensioni variabili (0.5–500 km²)
- Sistemi di riferimento UTM e nazionali

---

## Autore

**Dr. Geol. Faustino Cetraro**  
Scientific communicator & editorial architect  
Email: *geol-faustino@libero.it*

---

## Licenza

Rilasciato sotto licenza **GNU GPL v2 o successiva**.

---

## Contributi

Contributi, segnalazioni e miglioramenti sono benvenuti.  
Aprire una *issue* o una *pull request* nel repository.



