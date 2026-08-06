# Import dati — da dove vengono, e come si prendono

Cosa abbiamo accertato interrogando direttamente l'API Figma, il 5 agosto 2026,
con il token già presente in `b2b-ui-kit/.env.local`.

Tutto ciò che segue è **verificato con una chiamata**, non dedotto.

---

## 1. Il grafo dei file Figma

Non c'è un file solo. Ce n'è uno **condiviso a monte** e uno per design system.

```
              ❖ Antares Foundations
              S8U9Li374QCzYEtwFBnaaX
              1.614 variabili pubblicate
              la palette assoluta: #BED62F, le scale numeriche
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
   🏗️ DS B2B                        📱 Design System Cross App
   AFsC1fNp7mYe6Qm4l2Cfin           QWM2EhgZmv2KKcqI0315fx
   2.076 variabili locali           1.515 variabili pubblicate
   1.594 pubblicate
```

**I due DS non si importano a vicenda.** Il file B2C copre **0** dei 519
riferimenti esterni del B2B: entrambi attingono allo stesso strato di fondo. La
condivisione dei 742 token che avevamo misurato sui nomi ha quindi una causa
strutturale, non una coincidenza di naming.

### Le altre librerie a monte del B2B

Ricavate risalendo dalle chiavi delle entità importate
(`/v1/components/{key}` → `meta.file_key`):

| fileKey | Nome | Variabili | Copre |
|---|---|---|---|
| `S8U9Li374QCzYEtwFBnaaX` | **❖ Antares Foundations** | 1.614 | **459 / 519** |
| `V1QcyELlWtJTnfrjrRJrfR` | Library MySisal Business (EVO 2025) | 117 | 11 / 519 |
| `FUrJB3g2FMvTEuRjHk4p6r` | 🛠️ Design utilities | 0 | 0 |
| `KUB9MGjJGlYw0nJOjXz1au` | 🖌️ Graphic Assets library | 0 | 0 |

**470 su 519 coperte.** Le 49 restanti vengono da una libreria che il fetch a
profondità 3 non ha raggiunto: si trovano aumentando la profondità.

> `❖ Antares Foundations` si chiama **letteralmente** come il pacchetto che
> l'architettura target ipotizzava di dover creare (`@antares/foundations`).
> Non è da costruire: esiste, ha un fileKey, ed è leggibile.

---

## 2. La struttura interna di un file DS

Le collezioni del file B2B, con i loro **modi** — che sono le dimensioni di
variazione:

| Collezione | Variabili | Modi |
|---|---|---|
| `component` | 1.495 + 31 | Mode 1 *(nessuna variazione)* |
| `theme` | 193 | **light, dark** |
| `primitive` | 67 + 33 | Value *(le scale dimensionali, locali)* |
| `typography` | 68 | Mode 1 |
| `brand` | 43 | **sisal, snai, pokerstars, eloterie, millipiyango, mdjs, dbox, sisalBusiness** |
| `device` | 28 | **desktop, mobile** |
| `os` | 5 | **ios, android** |
| `Foundations` | 28 + 3 + 1 | Light |
| `Tokens` | 25 + 5 + 2 | Default |
| `Layout direction` | 1 | **western, middle eastern** |
| `.generosity` | 41 | Mode 1 |

Due osservazioni operative:

- La collezione `brand` ha modi per **`dbox`** e **`sisalBusiness`**, e c'è una collezione **`os` con `ios`/`android`**: lo stesso file porta dimensioni di prodotti diversi, mobile incluso.
- **I nomi di collezione sono duplicati** — `component` ×2, `primitive` ×2, `Foundations` ×3, `Tokens` ×3, `brand` ×2. Identificare un livello dal nome non è affidabile: serve una mappa esplicita `collectionId → livello`.

---

## 3. La catena degli alias

Misurata su tutti i valori di tutte le variabili del file B2B:

```
alias interni al file        :     90
alias verso librerie esterne :  2.314   ← 519 chiavi distinte
valori letterali             :    217
profondità massima           :      3 salti (dentro il file)
cicli                        :      0
```

**L'88% dei valori è un alias**, e quasi tutti escono dal file. Un esempio
tracciato per intero:

```
button/color/brand/primary/bg/default          collezione "component"
  → color/bg/action/brand/primary/default      collezione "theme",  modo light
    → brand/primary/200                        collezione "brand",  modo sisal
      → VariableID:3fea8220…/498:304           ❖ Antares Foundations
```

Quattro livelli. Il CSS committato contiene solo il valore finale: **la catena
esiste, ma viene appiattita in fase di export.**

Le dimensioni invece si risolvono **dentro** il file, perché la scala è nella
collezione `primitive` locale:

```
button/size/md/height → size/40 (primitive, Value) → 40
```

---

## 4. Cosa permette il token attuale

Verificato una chiamata alla volta sul file B2B.

| Endpoint | Esito | Serve a |
|---|---|---|
| `/v1/files/{key}/nodes?ids=` | ✅ | property table, geometria, `boundVariables` |
| `/v1/files/{key}/variables/local` | ✅ | le variabili definite nel file |
| `/v1/files/{key}/variables/published` | ✅ | le variabili che il file pubblica |
| `/v1/images/{key}?ids=&format=png` | ✅ | export PNG per il diff visivo |
| `/v1/files/{key}?depth=N` | ✅ | manifest di componenti e stili |
| `/v1/components/{key}` · `/v1/styles/{key}` | ✅ | **risalire al file di origine** (`meta.file_key`) |
| `/v1/me` | ❌ 403 | irrilevante — è solo uno scope mancante |

Il 403 su `/v1/me` **non** significa token scaduto: è limitato negli scope. Per
tutto ciò che serve funziona.

### Due avvertenze

**`depth=1` svuota i manifest.** I dizionari `components` e `styles` della
risposta si popolano in base ai nodi effettivamente restituiti: con `depth=1` si
ottiene solo il livello canvas e i manifest tornano vuoti. Serve `depth=3` o più
per vedere le entità importate.

**Le variabili importate non sono in `variables/local`.** Hanno id in forma
`VariableID:<variableKey>/<localId>` — lo slash è il segnale. Per risolverle
serve `variables/published` **del file a monte**, e mappare per `key`.

*(Correzione a un'ipotesi precedente: quegli hash sono chiavi di **variabile**,
non di **file**. Interrogarli come fileKey restituisce 404.)*

---

## 5. Come si estrae, livello per livello

| Livello | Sorgente | Chiamata | Unità |
|---|---|---|---|
| **0 · Fondazioni** | `❖ Antares Foundations` | `variables/published` | il file |
| **1 · Semantica** | il file del DS | `variables/local` + risoluzione modi | il file |
| **2 · Componente** | il nodo `COMPONENT_SET` | `nodes?ids=` | il nodo |
| **2b · Intento** | i frame `Purpose & Usage` / `Behavior` | `nodes?ids=` | il frame |
| **2c · Riferimento visivo** | il nodo | `images?ids=&format=png` | il nodo |
| **3 · Pagina** | i frame di documentazione del pattern | `nodes?ids=` | il frame |
| **4 · Flusso** | le connessioni di prototipo | `nodes` → `interactions` | il flusso |

### I frame di documentazione: misurati, e i due DS non si somigliano

Il template `Purpose & Usage` + `Behavior` descritto in `SCHEMA.md` §5 **esiste ed
è usato**. Ma la copertura è opposta nei due file:

| | 📱 Cross App (B2C) | 🏗️ DS B2B |
|---|---|---|
| Pagine | 84 | 65 |
| **Pagine con documentazione** | **27** | **7** |
| Frame totali | **72** | 19 |
| Di cui su componenti veri | ~25 | **1** (Page Footer) |

Nel B2C la pagina `Button` ha **8 frame**: è da lì che vengono gli anti-pattern
dei `metadata.json`. Nel B2B i frame stanno quasi tutti su pagine di *pattern di
prodotto* (`PAF Card`, `PAF Header`, `PAF Modal`) e su un `DOC Playground`.

**Conseguenza operativa**: il livello 2b si estrae dal B2C, non dal B2B. Per il
B2B l'intento va preso dai `DESIGN.md` (sottili: 23 righe per il Button, zero
anti-pattern) oppure adottato dal B2C con una decisione esplicita.

### La struttura del frame, verificata

```
FRAME "Purpose & Usage"
  Section Header      tag "For designer" · titolo · Documentation Alert
  Body
    "Nome pattern"                          → a quale componente si riferisce
    "1.1 How and when to use it (Do ✅)"     → commonPatterns[]
        <testo>
        "In which component / template / flow is it used?"  → usedIn[]
    "1.N Anti-pattern (Don't ❌)"            → antiPatterns[]
        "Rule"            → scenario
        "Why it's wrong"  → reason
        "Use instead"     → alternative
```

**Una pagina ospita più componenti.** La pagina `Button` del B2C documenta `FAB`,
`Button Square` e `Button`: il match va fatto sul campo *Nome pattern*, mai sul
nome della pagina.

**L'estrazione è riproducibile.** Eseguita sul `FAB`, restituisce **5 anti-pattern
su 5**, nello stesso ordine di quelli scritti a mano in
`components/fab/docs/metadata.json`. Il processo descritto in `HANDOFF.md` è
quindi automatizzabile — non è un'ipotesi, è misurato.

L'unico scostamento: Figma ha **1** blocco *Do*, il metadata ne ha **3**
`commonPatterns`. Chi ha compilato il JSON ha espanso una sezione in tre — è
arricchimento oltre la sorgente, e quella parte **non** è riproducibile.

### Lo stato vive nel nome della pagina

Entrambi i file usano emoji nel nome della pagina come marcatore di avanzamento,
con **due convenzioni diverse**:

| DS | Marcatori | Significato |
|---|---|---|
| B2C | 🟢 × 51 | completato |
| B2B | 🔴 × 3 · ❌ × 5 · ❓ × 1 | in lavorazione · non esiste · da decidere |
| entrambi | ❖ | pagina-sezione, non un componente |

È un dato di copertura che oggi non legge nessuno. La mappa marcatore → stato è
dichiarata in `design2code/config/figma-status.json`: **non si deduce dal
simbolo**, perché le due convenzioni sono incompatibili (nel B2C il verde marca
ciò che è fatto, nel B2B i marcatori segnalano solo i problemi).

Coincidenza degna di nota: `Checkbox` e `Dropdown` sono 🔴 in Figma **e** sono i
due componenti privi di `DESIGN.md` e `CHANGELOG.md` in codice. I due stati
concordano per caso, perché nessuno dei due sistemi legge l'altro.

### Il vincolo di ordine

**Il livello 0 va estratto per primo.** Senza la palette risolta, l'88% dei
valori del livello 1 resta un alias non risolvibile — ed è esattamente il motivo
per cui il primo tentativo di export si è fermato al 17% di corrispondenza col
CSS committato.

### La discovery dei node id

Oggi è **manuale**: gli id vengono copiati dai link Figma e annotati a mano nelle
request. È automatizzabile camminando l'albero del file e raccogliendo i nodi di
tipo `COMPONENT_SET`, ma non è ancora scritto.

---

## 6. Cosa resta da procurare

| # | Cosa | Perché |
|---|---|---|
| 1 | **Service account Figma** | oggi il token è in un `.env.local` personale: in CI non esiste |
| 2 | **Il fileKey della libreria delle 49 chiavi restanti** | si trova con un fetch più profondo |
| 3 | **Mappa `collectionId → livello`** | i nomi di collezione sono duplicati (§2) |
| 4 | **Quanto sono compilati i frame di documentazione** | mai misurato: determina se il livello 2b ha una sorgente |
| 5 | **Quanto i file sono prototipati** | determina se il livello 4 si estrae o si dichiara |

Nessuno di questi blocca l'estrazione dei livelli 0, 1 e 2: quelli si possono
fare oggi.
