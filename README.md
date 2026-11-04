# Pendolo fisico: analisi dati

Codice di analisi per la relazione di laboratorio sul pendolo fisico (LAB1).
L'esperienza misura il periodo di oscillazione di un'asta sospesa a distanze
diverse dal centro di massa. Il fit delle misure ricava la lunghezza dell'asta,
che viene poi confrontata con quella misurata direttamente.

**Risultato con i dati attuali:**

| Lunghezza dell'asta | `l` [mm]       |
| ------------------- | -------------- |
| Dal fit             | 1053.6 ± 0.7   |
| Misurata col metro  | 1051.0 ± 1.0   |

La differenza tra i due valori è pari a **2.17 σ**.

## Avvio rapido

Serve Python 3.12 o successivo (il codice è stato eseguito con Python 3.14.6).
Dalla cartella del progetto:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Lo script va lanciato da questa cartella, perché legge i file `d1.txt`…`d5.txt`
con percorsi relativi.

## Cosa produce

**Sul terminale**, ogni tabella in versione leggibile e in versione LaTeX
(`tabular`, da incollare nella relazione):

1. le misure singole per ciascuna distanza `d`
2. il riepilogo con `d`, `T` medio, incertezze e residui del fit
3. il confronto tra `l` di best-fit e `l` misurata, seguito dalla compatibilità

**In due finestre grafiche:**

1. `T` in funzione di `d`, con la curva di fit, il modello calcolato con la `l`
   misurata e, sotto, i residui
2. la dispersione delle singole misure di `T` attorno alla media di ogni gruppo

I grafici non vengono salvati su file: si possono esportare dalla finestra di
Matplotlib. Il terminale resta occupato finché le finestre sono aperte.

Per salvare le tabelle su file senza aprire i grafici:

```bash
MPLBACKEND=Agg python main.py > risultati.txt
```

In questo caso Matplotlib può stampare un avviso sul backend non interattivo,
che si può ignorare.

## File del progetto

| File               | Contenuto                                                    |
| ------------------ | ------------------------------------------------------------ |
| `main.py`          | Lettura dei dati, analisi, fit, tabelle e grafici            |
| `d1.txt`…`d5.txt`  | Misure del periodo, un file per ogni distanza `d`            |
| `misure.md`        | Significato delle colonne e calcolo di `d` e delle incertezze |
| `considerazioni.md` | Appunti sulle ipotesi: massa uniforme, centro di massa, angolo |
| `requirements.txt` | Versioni esatte delle dipendenze Python                      |

## Modello fisico

Per un'asta omogenea di lunghezza `l`, sospesa a distanza `d` dal centro di massa
e in regime di piccole oscillazioni, il periodo è:

```
T(d) = 2π · sqrt( (l²/12 + d²) / (g · d) )
```

`T` ha un minimo per `d = l/√12`, circa 303 mm per quest'asta. Per questo le
misure scendono fino a `d3` e poi risalgono.

Il modello si basa su due ipotesi, motivate in `considerazioni.md`:

- **Massa uniforme:** i 10 fori hanno un'area totale pari a circa l'1.1% di
  quella dell'asta e, a parità di spessore e densità, rimuovono la stessa
  frazione di volume e di massa. I fori sono spostati verso un lato, quindi il
  centro di massa si sposta di circa 0.3 mm (stima): `delta = 24 mm · 0.0112 = 0.3 mm`. Lo
  scarto è minore di `σ_d = 0.5 mm e 1.2 mm`, quindi si assume che il centro di massa coincida con
  il centro dell'asta.
- **Piccole oscillazioni:** la correzione al periodo resta sotto l'incertezza
  del cronometro se `θ < 23°`. L'angolo di lancio misurato è di circa 16°.

## Dati

Ogni file `dN.txt` è un CSV con una riga di intestazione e queste colonne:

| Colonna    | Significato                              | Unità |
| ---------- | ---------------------------------------- | ----- |
| `#`        | Numero della misura                      | -     |
| `d`        | Distanza tra perno e centro di massa     | mm    |
| `N`        | Numero di periodi cronometrati           | -     |
| `T*N`      | Tempo totale degli `N` periodi           | s     |
| `errore_d` | Incertezza su `d`                        | mm    |

Le cinque distanze, calcolate in `misure.md`, sono:

| File     | `d` [mm]      | Misure | Strumento per la distanza dal bordo |
| -------- | ------------- | ------ | ----------------------------------- |
| `d1.txt` | 482.3 ± 0.5   | 6      | Calibro ventesimale                 |
| `d2.txt` | 375.2 ± 0.5   | 5      | Calibro ventesimale                 |
| `d3.txt` | 276.1 ± 1.2   | 5      | Metro                               |
| `d4.txt` | 176.0 ± 1.2   | 5      | Metro                               |
| `d5.txt` | 75.1 ± 1.2    | 5      | Metro                               |

## Analisi

1. **Periodo singolo:** `T = (T*N) / N` per ogni misura.
2. **Periodo medio:** media delle misure di ogni gruppo.
3. **Incertezza sul periodo:** errore standard della media sommato in quadratura
   alla risoluzione del cronometro sul singolo periodo (0.01 s / 10 = 0.001 s):
   ```
   σ_T = sqrt( 0.001² + σ_media² )
   ```
4. **Fit:** `scipy.optimize.curve_fit` con `l` come unico parametro libero, pesato
   con `σ_T` (`absolute_sigma=True`). `g = 9.805 m/s²` è fissato.
5. **Compatibilità** con la lunghezza misurata (`1051 ± 1` mm):
   ```
   λ = |l_fit − l_mis| / sqrt( σ_fit² + σ_mis² )
   ```

### Risultati per distanza

| `d` [mm]    | `T` [s]         | Residuo [ms] |
| ----------- | --------------- | ------------ |
| 482.3 ± 0.5 | 1.6385 ± 0.0044 | −9.0         |
| 375.2 ± 0.5 | 1.5782 ± 0.0029 | −4.0         |
| 276.1 ± 1.2 | 1.5722 ± 0.0022 | +3.5         |
| 176.0 ± 1.2 | 1.6826 ± 0.0024 | +1.8         |
| 75.1 ± 1.2  | 2.2934 ± 0.0016 | −0.5         |

## Limiti da tenere presenti

- **`σ_d` non entra nel fit:** il fit usa solo `σ_T`. L'incertezza su `d` compare
  soltanto nelle tabelle e nelle barre d'errore del grafico.
- **`N = 10` è presupposto:** il termine 0.001 s è scritto direttamente in
  `main.py`. Se cambi `N`, va aggiornato a mano.
- **Cinque file fissi:** per aggiungere una distanza non basta creare un nuovo
  file `d6.txt`: vanno modificate anche le liste in `main.py`.
- **Riproducibilità numerica:** i risultati riportati qui non si aggiornano da
  soli. Se cambi i dati, rilancia lo script e aggiorna questo file.
