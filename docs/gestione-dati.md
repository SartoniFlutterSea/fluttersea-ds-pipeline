# Gestione dati — come sono strutturati, e chi li possiede

Come organizzare i dati del design system, ricavato da ciò che l'analisi di Figma
ha mostrato (`import-dati.md`).

La tesi in una riga: **i livelli non li dobbiamo inventare — esistono già in
Figma, con dei nomi.** La struttura giusta li rispecchia, così la pipeline è una
proiezione e non una traduzione.

---

## 1. Il criterio: il livello è ciò che fa variare

Non è una scelta di gusto. Le collezioni Figma hanno **modi**, e i modi *sono* le
dimensioni di variazione. Da lì la regola:

> **Un dato appartiene al livello più basso che non varia.**
> Cambia col brand → livello brand. Cambia col tema → livello theme. Non cambia
> con niente ed è un valore assoluto → primitive. Non cambia con niente ma
> referenzia altro → component.

È un criterio **verificabile**: dato un token nuovo, si guarda su quali modi ha
valori diversi e il livello si deduce. Non serve discuterne.

---

## 2. I livelli

```
┌─ 0 · FONDAZIONI ────────────────────────── condiviso, un file solo ─┐
│  la palette assoluta e le scale — #BED62F, size/40                   │
│  ❖ Antares Foundations · 1.614 variabili · varia per: NIENTE         │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌─ 1 · SEMANTICA ─────────────┴──────────────────────── per design system ─┐
│  brand   43 × 8 modi     quale voce della palette per questo brand        │
│  theme  193 × 2 modi     quale ruolo semantico (bg/action/primary)        │
│  device  28 × 2 modi     desktop / mobile                                 │
│  os       5 × 2 modi     ios / android                                    │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
┌─ 2 · COMPONENTE ────────────┴──────────────────────── per design system ─┐
│  contratto: variants · sizing · tokens · anatomia · stati · semantica     │
│  1.526 token di componente — solo alias, non variano                      │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
┌─ 3 · PAGINA ────────────────┴─┐   ┌─ 4 · FLUSSO ──────────────────────┐
│  slot · componenti ammessi     │   │  stati · transizioni · guardie     │
│  regole quantitative           │   │                                    │
└────────────────────────────────┘   └────────────────────────────────────┘

     ⟂ REGOLE          vincoli verificabili, con `appliesTo` dichiarato
     ⟂ CAMBIAMENTI     eventi con il perché, indicizzati sul tempo
```

I due livelli con `⟂` sono **ortogonali**: attraversano tutti gli altri, e per
questo non stanno dentro nessuno.

---

## 3. Dove cade la linea condiviso / locale

Questo **corregge** l'architettura target ereditata, che collocava la giuntura fra
*semantic* e *component*. I dati la mettono più in basso.

| Livello | Condiviso | Evidenza |
|---|---|---|
| **0 · fondazioni** | ✅ **sì, già oggi** | è un file separato che entrambi i DS importano |
| **1a · brand** | 🟡 **da decidere** | ogni DS ha la *sua* collezione `brand`, con gli **stessi 8 brand** |
| **1b · theme, device, os** | ❌ per DS | la semantica appartiene al prodotto |
| **2 · componente** | ❌ per DS | |
| **3 · pagina, 4 · flusso** | ❌ per DS | |
| **⟂ regole** | 🟡 **misto** | ~12 su 42 sono vincoli sull'artefatto e sono condivisibili |

**La riga gialla del brand è la domanda aperta più concreta.** Se le due
collezioni mappano gli stessi 8 brand sulla stessa palette, sono la stessa cosa
scritta due volte, e sarebbero il secondo strato da promuovere a condiviso. Si
verifica con una chiamata.

---

## 4. Un valore di token non è una coppia nome → valore

È una **funzione di cinque dimensioni**:

```
valore = f(token, brand, tema, device, os, direzione)
```

Modellarlo come mappa piatta significa perdere la variazione o duplicare il
catalogo per ogni combinazione. La forma giusta separa due cose:

```
GRAFO      il token come entità: id, livello, tipo, aliasOf, deprecato
           → identità e relazioni, poche migliaia di archi

TABELLA    (token, brand, tema, device, os) → valore
           → ~18k righe, nessuna traversata da fare
```

È la separazione già decisa in `design/06` (D11), ora con il numero corretto di
dimensioni: cinque, non due.

**Corollario**: `resolved/` è **derivato**. Si ricostruisce risolvendo la catena
dal livello 0 in su, quindi non va scritto a mano e non deve stare in Git.

---

## 5. La disposizione sul disco

```
tokens/
├── foundations.json            ← livello 0, dal file condiviso — una volta per tutti i DS
├── collections.json            ← mappa collectionId → livello  (vedi §7)
├── tokens.json                 ← catalogo: id, livello, tipo, aliasOf, deprecato
└── resolved/                   ← DERIVATO, fuori da Git
    ├── sisal.light.desktop.json
    └── snai.dark.mobile.json

components/<id>/
├── component.json              ← livello 2: contratto
├── figma.json                  ← ancoraggio: fileKey + nodi
└── changelog.md                ← generato

pages/<id>/     composition.json · pattern.md          ← livello 3
flows/<id>/     flow.json · flow.md                    ← livello 4
rules/<id>.json                                        ← ⟂ regole
```

Regola trasversale: **cartelle piatte, gerarchia nei dati.** Il raggruppamento è
un campo (`family`, `layer`), mai un livello di cartella — è ciò che ha reso
invisibili 8 componenti in `ds-cross-app`.

---

## 6. Chi scrive cosa

| Livello | Sorgente | Scritto da | In Git |
|---|---|---|---|
| 0 · fondazioni | Figma Variables (file condiviso) | **macchina** | ✅ catalogo |
| 1 · semantica | Figma Variables (file DS) | **macchina** | ✅ catalogo |
| — valori risolti | derivati dalla catena | **macchina** | ❌ artefatto |
| 2 · contratto | property table + geometria + binding | **macchina** | ✅ |
| 2 · intento (purpose, anti-pattern) | frame di documentazione, o redazione | **umano** | ✅ |
| 3 · pagina | UX | **umano** | ✅ |
| 4 · flusso | prototipo Figma → bozza, poi UX | misto | ✅ |
| ⟂ regole | DS team | **umano** | ✅ |
| ⟂ cambiamenti | diff dei fatti + il perché all'evento | misto | ✅ generato |

**Un solo writer per campo.** È la condizione che ha retto ovunque nelle due repo
e che è mancata in tutti e tre i casi di divergenza misurati.

---

## 7. Due problemi di igiene da chiudere subito

**I nomi delle collezioni sono duplicati.** Nel file B2B: `component` ×2,
`primitive` ×2, `Foundations` ×3, `Tokens` ×3, `brand` ×2. Un livello dedotto dal
*nome* non è affidabile.

→ Serve `tokens/collections.json`, una mappa esplicita `collectionId → livello`
dichiarata a mano una volta e verificata in CI. È la prima cosa che il collector
deve leggere.

**Esiste una collezione `.generosity` (41 variabili)** il cui nome suggerisce un
esperimento. Va classificata o esclusa esplicitamente: un collector che la
ingerisce silenziosamente porta dentro dati che nessuno rivendica.

---

## 8. Perché questa struttura e non un'altra

Tre proprietà, tutte conseguenza del §1:

**È verificabile.** Il livello di un token si deduce dai modi su cui varia. Un
token classificato male è un errore rilevabile, non un'opinione.

**È una proiezione, non una traduzione.** Rispecchiando le collezioni Figma, la
pipeline non deve reinterpretare niente: quando i designer aggiungono un modo — un
brand nuovo, una piattaforma — la struttura lo assorbe senza modifiche al modello.

**Isola il condiviso in un punto solo.** Il livello 0 è già un file separato con
un nome proprio. Governarlo significa governare una dipendenza esistente, non
crearne una nuova — che è l'unica forma di condivisione praticabile fra sei
aziende senza autorità centrale.
