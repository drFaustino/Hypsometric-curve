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

## Teoria implementata

La curva ispometrica, o ipsografica, rappresenta la distribuzione delle quote altimetriche all'interno di un bacino idrografico. Essa viene tracciata in relazione alla proporzione tra l'altezza totale e l'area complessiva del bacino. Le fasce altimetriche sono disposte in ordine decrescente, dalla quota massima a quella minima. La curva fornisce informazioni cruciali sulla distribuzione dell'area in funzione delle diverse altezze all'interno del bacino. L'altezza media hmed del bacino è calcolata come:

![imgform1](https://github.com/user-attachments/assets/554f1d6b-34cb-4399-baf2-ea4a799c8884)

dove A è l'area totale del bacino idrografico, h è l'altezza, che varia in funzione della posizione lungo il bacino (ad esempio, la quota a diverse altitudini), dA rappresenta l'elemento infinitesimo di area che corrisponde a un intervallo di altezza 
h. 

### Spiegazione della formula
La formula calcola la media delle altezze del bacino idrografico, tenendo conto non solo delle altezze stesse, ma anche della distribuzione spaziale di queste altezze nel bacino.

- **Integrazione dell'altezza lungo l'area del bacino**: Questa espressione somma (o integra) le altezze h su tutta l'area del bacino, ponderando ciascuna altezza per la porzione di area a cui corrisponde.
- **Il significato del termine h⋅dA**: La quantità h⋅dA rappresenta il contributo all'altezza totale dato da una piccola area dA in cui l'altezza è h.
- **L'integrale da 0 ad A**: Somma tutti i contributi delle diverse altezze su tutta l'area del bacino. In pratica, l'integrale calcola il totale delle "altezze ponderate" lungo l'intero bacino.
- **Divisione per A**: Dopo aver calcolato la somma delle altezze ponderate, questa viene divisa per l'area totale A. Ciò serve a ottenere la media delle altezze lungo l'area, considerando appunto il peso che ogni intervallo di altezza ha in relazione all'area che occupa.

### Integrale ispometrico HI
L'integrale è definito come l'area sotto la curva ipsometrica calcolato nel seguente modo (Keller e Pinter, 2002):

![imgform2](https://github.com/user-attachments/assets/0bcbf5fb-a907-4677-b821-7b50d0dd1b04)

dove hmed è l'atezza media calcolata, hmax e hmin soni rispettivamente l'altezza massima e minima all'interno del bacino idrografico. Hi varia da 0, per regioni fortemente erose, a 1 per regioni leggermente erose (Pedrera et al. 2009).

## Aggiornamento - versione 0.2

In questa versione sono state implementate diverse nuove funzionalità per migliorare l'interattività e l'usabilità dell'applicazione. Tra le principali novità:

- **Assegnazione del colore alla curva ipsometrica**: È possibile personalizzare il colore della curva utilizzando il pulsante Colore. Questo permette di modificare l'aspetto grafico del grafico in modo semplice e immediato.
- **Aggiornamento del grafico senza ricalcolo**: Dopo aver assegnato un colore alla curva, il grafico viene aggiornato dinamicamente senza la necessità di ricalcolare i dati. Questa funzionalità garantisce maggiore efficienza e una migliore esperienza d'uso.
- **Visualizzazione di informazioni utili**: Sono state aggiunte funzionalità per visualizzare dettagli significativi come l'indice HI (Hypsometric Index) e altri dati correlati, direttamente sul grafico, offrendo una rappresentazione più chiara e completa.

Grazie a queste nuove caratteristiche, l'applicazione risulta più versatile e intuitiva, rispondendo meglio alle esigenze degli utenti.

![fig_3](https://github.com/user-attachments/assets/b4ce74eb-aaa0-4aee-9c9e-4fb5af563797)

Nuova interfaccia con l'aggiunta di ulteriori informazioni e la possibilità di cambiare il colore alla curva

![fig_4](https://github.com/user-attachments/assets/1b6d72cc-6de7-4b2b-a459-17460ec23791)

La scheda Tabella mostra i valori calcolati con la possibilità di salvarsli su file

![fig_5](https://github.com/user-attachments/assets/c0d7ebfd-cd2a-48b1-bc3b-4f919945719b)

La scheda Informazioni riporta la definizione delle varie caratteristiche calcolate.

