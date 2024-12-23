# Hypsometric curve 
## plugin QGIS
### versione 0.1, richiesto min. QGIS v. 3.x

Calcola la **curva ipsometrica** di un bacino idrografico da un layer DEM del terreno e dalla definizione del perimetro del bacino, ottenuto da un layer vettoriale contenente il poligono che ne delimita i confini. È possibile scegliere il numero di banda per le quote altimetriche del terreno e definire il numero di classi degli intervalli di quota altimetrica per suddividere l'area del bacino stesso. Come risultato, vengono calcolate la quota minima, massima e media all'interno del poligono del bacino, l'area totale e il valore dell'integrale ipsometrico. Inoltre, viene disegnato il grafico della curva ipsometrica, con i relativi valori calcolati riportati in una tabella. È possibile salvare sia il grafico in formato immagine che la tabella dei valori in un file CSV o TXT.

Per il funzionamento del plugin è richiesto l'uso delle librerie **numpy**, **matplotlib**, **pyplot** e **csv**.

## Interfaccia del plugin
L'interfaccia del plugin è semplice e intuitiva, progettata per agevolare l'analisi del bacino idrografico. È organizzata in tre menu principali:

**Selezione del layer raster (DEM)**: permette di scegliere il layer raster contenente il Modello Digitale di Elevazione (DEM).

**Scelta della banda**: consente di specificare il numero della banda da utilizzare nel calcolo.

**Selezione del layer vettoriale**: serve per indicare il layer vettoriale che contiene il poligono delimitante il bacino idrografico.

Oltre ai menu principali, l'interfaccia include un controllo dedicato alla definizione del numero di intervalli di quota da considerare all'interno dei confini del bacino.

> **Risultati**

L'elaborazione restituisce i seguenti risultati:

- Quota minima, massima e media all'interno del poligono che delimita il bacino.
- Area totale del bacino.
- Valore dell'integrale ipsometrico.

**Funzionalità aggiuntive**

Il plugin genera automaticamente il grafico della curva ipsometrica, i cui valori calcolati vengono anche riportati in una tabella consultabile. È possibile esportare i risultati grazie a due opzioni di salvataggio:

- Il grafico può essere salvato come immagine in vari formati.
- La tabella dei valori può essere esportata in un file CSV o TXT per ulteriori analisi.

L'interfaccia è progettata per garantire un flusso di lavoro semplice ed efficace, combinando visualizzazione e analisi dei dati in modo pratico.

![img_2](https://github.com/user-attachments/assets/d801172e-eb46-4b0f-84f4-83e2f16cffb8)

> **Note importanti**

Per eseguire i calcoli in modo accurato, è fondamentale utilizzare un **sistema di riferimento proiettato** (ad esempio, il sistema UTM). Questo garantisce che le misure, sia delle quote altimetriche del terreno che delle aree, siano corrette e coerenti.

Inoltre, è essenziale che **entrambi i layer** coinvolti nell'analisi, ovvero il *layer raster del DEM* e il *layer vettoriale* contenente il poligono del bacino, **siano nello stesso sistema di riferimento proiettato**.

L'adozione di un **CRS proiettato** consente di lavorare in unità metriche, migliorando la precisione delle analisi e garantendo che le aree e le altezze siano calcolate correttamente rispetto alla superficie terrestre.
