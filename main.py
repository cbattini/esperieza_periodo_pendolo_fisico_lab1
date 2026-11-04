import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

""" LETTURA DATI """

# COSTANTI
L = 525.500 * 2
SIGMA_L = 1.0 # incertezza sulla lunghezza dell'asta misurata col metro (mm)
G = 9.805

# colonne: 0 = numero misura, 1 = braccio, 2 = numero periodi, 3 = periodo*N, 4: errore_d

# opzioni per ogni lettura
opz = dict(delimiter=',', usecols=(0, 1, 2, 3, 4))

# d1
dati_d1 = np.loadtxt('d1.txt', **opz)
dati_d2 = np.loadtxt('d2.txt', **opz)
dati_d3 = np.loadtxt('d3.txt', **opz)
dati_d4 = np.loadtxt('d4.txt', **opz)
dati_d5 = np.loadtxt('d5.txt', **opz)

""" ANALISI DATI """

def errore_standard(valori, valore_medio):
    return np.sqrt(np.sum((valori - valore_medio)**2) / (len(valori) * (len(valori) - 1)))

# tabella con colonne: 0 = numero misura, 1 = braccio, 2 = numero periodi, 3 = periodo, 4: errore_d, 5: errore_standard_T
def analisi_dati(d):
    d[:, 3] = d[:, 3]/d[:, 2] # dividiamo T*N/N = T
    periodi = d[:, 3]

    # colonne: 0 = numero misura, 1 = braccio, 2 = numero periodi, 3 = periodo, 4: errore_d

    # calcoliamo l'errore del periodo usando la deviazione standard
    valore_medio_periodo = np.mean(periodi)

    errore_standard_d = errore_standard(periodi, valore_medio_periodo)

    d = np.column_stack((d, np.full(len(d), np.sqrt(0.001**2 + round(errore_standard_d, 4)**2))))

    # colonne: 0 = numero misura, 1 = braccio, 2 = numero periodi, 3 = periodo, 4: errore_d, 5: errore_standard_T
        
    return d

def modello_periodo(d, l):
    # l = lunghezza dell'asta (parametro libero del fit)
    return 2 * np.pi * np.sqrt(((l**2)/12 + d**2) / (G * 1000 * d)) # G*1000: da m/s^2 a mm/s^2 (l e d sono in mm)

d1_analizzato = analisi_dati(dati_d1)
d2_analizzato = analisi_dati(dati_d2)
d3_analizzato = analisi_dati(dati_d3)
d4_analizzato = analisi_dati(dati_d4)
d5_analizzato = analisi_dati(dati_d5)

d = [d1_analizzato[:, 1][0], d2_analizzato[:, 1][0], d3_analizzato[:, 1][0], d4_analizzato[:, 1][0], d5_analizzato[:, 1][0]]
t = [np.mean(d1_analizzato[:, 3]), np.mean(d2_analizzato[:, 3]), np.mean(d3_analizzato[:, 3]), np.mean(d4_analizzato[:, 3]), np.mean(d5_analizzato[:, 3])]
sigma_d = [d1_analizzato[:, 4][0], d2_analizzato[:, 4][0], d3_analizzato[:, 4][0], d4_analizzato[:, 4][0], d5_analizzato[:, 4][0]]
sigma_t = [d1_analizzato[:, 5][0], d2_analizzato[:, 5][0], d3_analizzato[:, 5][0], d4_analizzato[:, 5][0], d5_analizzato[:, 5][0]]


d = np.array(d)
t = np.array(t)
sigma_d = np.array(sigma_d)
sigma_T = np.array(sigma_t)

""" FIT """
# l è l'unico parametro libero -> G costante, d variabile scelta, T variabile dipendente da d
# quindi con il fit cerco l

parametri, covarianza = curve_fit(modello_periodo, d, t, p0=[L], sigma=sigma_T, absolute_sigma=True)

l_fit = parametri[0] # trovo il valore del parametro libero che meglio approssima le misure 
sigma_l = np.sqrt(covarianza[0, 0])

residui = t - modello_periodo(d, l_fit)

# Confronto tra l di best-fit e l misurata: compatibilità in unità di sigma
compatibilita = abs(l_fit - L) / np.sqrt(sigma_l**2 + SIGMA_L**2)

""" TABELLE """
# Per ogni tabella stampo una versione leggibile a schermo e una pronta per LaTeX

def stampa_tabella(titolo, intestazioni, righe, intestazioni_latex=None):
    larghezze = [max(len(str(x)) for x in col) for col in zip(intestazioni, *righe)]
    print(f'\n=== {titolo} ===')
    print('  '.join(str(h).rjust(w) for h, w in zip(intestazioni, larghezze)))
    print('  '.join('-' * w for w in larghezze))
    for r in righe:
        print('  '.join(str(x).rjust(w) for x, w in zip(r, larghezze)))

    # versione LaTeX: i valori "a ± b" diventano "$a \pm b$"
    def cella_latex(x):
        x = str(x)
        return f'${x.replace("±", r"\pm")}$' if '±' in x else x

    intestazioni_latex = intestazioni_latex or intestazioni
    print('\n% LaTeX')
    print('\\begin{tabular}{' + 'c' * len(intestazioni) + '}')
    print('\\hline')
    print(' & '.join(intestazioni_latex) + r' \\')
    print('\\hline')
    for r in righe:
        print(' & '.join(cella_latex(x) for x in r) + r' \\')
    print('\\hline')
    print('\\end{tabular}')

# 1) Misure singole per ogni d
analizzati = [d1_analizzato, d2_analizzato, d3_analizzato, d4_analizzato, d5_analizzato]
for i, dati in enumerate(analizzati):
    righe = []
    for riga in dati:
        n, N, T_singolo = int(riga[0]), int(riga[2]), riga[3]
        righe.append([n, N, f'{T_singolo * N:.2f}', f'{T_singolo:.3f}'])
    stampa_tabella(f'Misure d{i+1} = ({d[i]:.1f} ± {sigma_d[i]:.1f}) mm',
                   ['#', 'N', 'N*T [s]', 'T [s]'], righe,
                   ['\\#', '$N$', '$NT$ [s]', '$T$ [s]'])

# 2) Riepilogo: valori medi, errori e residui
righe = []
for i in range(len(d)):
    righe.append([f'd{i+1}', f'{d[i]:.1f} ± {sigma_d[i]:.1f}', f'{t[i]:.4f} ± {sigma_T[i]:.4f}',
                  f'{residui[i] * 1000:+.1f}'])
stampa_tabella('Riepilogo', ['', 'd [mm]', 'T [s]', 'residuo [ms]'], righe,
               ['', '$d$ [mm]', '$T$ [s]', 'residuo [ms]'])

# 3) Risultato del fit e confronto con la misura diretta
stampa_tabella('Confronto lunghezza asta', ['', 'l [mm]'],
               [['best-fit', f'{l_fit:.1f} ± {sigma_l:.1f}'],
                ['misurata', f'{L:.1f} ± {SIGMA_L:.1f}']],
               ['', '$l$ [mm]'])
print(f'\nCompatibilità |l_fit - l_mis| / sqrt(sigma_fit^2 + sigma_mis^2) = {compatibilita:.2f} sigma')

""" GRAFICO """

# Grafico fit e residui
fig, (ax_fit, ax_res) = plt.subplots(2, 1, sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))

# Fit
d_grid = np.linspace(0.8 * d.min(), 1.05 * d.max(), 500)
colori = plt.cm.tab10(np.arange(len(d)))
for i in range(len(d)):
    ax_fit.errorbar(d[i], t[i], xerr=sigma_d[i], yerr=sigma_T[i], fmt='x', color=colori[i],
                    label=f'$d_{i+1}$ = {d[i]:.1f} mm')
ax_fit.plot(d_grid, modello_periodo(d_grid, l_fit), color='black', label=f'Fit: l = {l_fit:.1f} ± {sigma_l:.1f} mm')
ax_fit.plot(d_grid, modello_periodo(d_grid, L), color='grey', ls='--', label=f'Modello con l misurata = {L:.0f} ± {SIGMA_L:.0f} mm')
ax_fit.set_title('T in funzione di d')
ax_fit.set_ylabel('T [s]')
ax_fit.legend()

# Residui
for i in range(len(d)):
    ax_res.errorbar(d[i], residui[i], yerr=sigma_T[i], fmt='x', color=colori[i])
ax_res.axhline(0, color='black')
ax_res.set_xlabel('d [mm]')
ax_res.set_ylabel('Residui [s]')

# Dispersione delle misure: scarto di ogni T dalla media del suo gruppo
fig_disp, ax_disp = plt.subplots()

for i, dati in enumerate(analizzati):
    scarti = (dati[:, 3] - t[i]) * 1000 # in ms
    ax_disp.plot(np.full(len(scarti), i), scarti,'o', color=colori[i], alpha=0.6, markersize=5)
    ax_disp.errorbar(i, 0, yerr=sigma_T[i] * 1000, fmt='_', color='black', capsize=6, markersize=20)
ax_disp.axhline(0, color='grey', lw=0.8)
ax_disp.set_xticks(range(len(d)), [f'$d_{i+1}$ = {d[i]:.1f} mm' for i in range(len(d))], rotation=20)
ax_disp.set_ylabel(r'$T_i - \bar{T}$ [ms]')
ax_disp.set_title(r'Dispersione delle misure di T (barra nera = $\sigma_T$ della media)')
fig_disp.tight_layout()

plt.show()
