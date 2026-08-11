# API Figma usate

Riferimento di cosa il sistema chiede a Figma, quanto costa, e cosa non usa.

> **Tutte le chiamate del codice sono in lettura.** Verificato riga per riga:
> non esiste una `POST`, `PUT`, `PATCH` o `DELETE` verso i file.
>
> ⚠️ **Ma il token non è a sola lettura.** Vedi [Scope del token](#scope-del-token):
> possiede permessi di scrittura su variabili, commenti, Code Connect e dev
> resources. La garanzia sta nel codice, non nel permesso.

---

## Autenticazione

Un token passato nell'intestazione:

```
X-Figma-Token: <token>
```

Il token arriva dall'ambiente (`FIGMA_TOKEN`), come lo passa la CI, con
`.env.local` come ripiego locale. Non compare mai nel codice né in repo.

### Scope del token

Ricavati dalla risposta di `/v1/me`, che li elenca nell'errore.

| Lettura | Scrittura |
|---|---|
| `file_content:read` | ⚠️ `file_variables:write` |
| `file_metadata:read` | ⚠️ `file_comments:write` |
| `file_versions:read` | ⚠️ `file_code_connect:write` |
| `file_comments:read` | ⚠️ `file_dev_resources:write` |
| `file_variables:read` | |
| `library_content:read` · `library_assets:read` · `library_analytics:read` | |
| `team_library_content:read` · `file_dev_resources:read` | |

⚠️ `file_variables:write` consente di **modificare le variabili**, cioè i token
del design system. Il nostro codice non lo fa, ma un token con quel permesso in
un file `.env` è un rischio da conoscere.

**Assenti:** `current_user:read` (perciò `/v1/me` risponde `403`) e ogni scope
sui webhook.

---

## I file letti

| | Chiave | Nome |
|---|---|---|
| `b2c` | `QWM2EhgZmv2KKcqI0315fx` | 📱 Design System Cross App |
| `b2b` | `AFsC1fNp7mYe6Qm4l2Cfin` | 🏗️ DS B2B |

Le librerie di variabili (Antares Foundations, Library MySisal) si raggiungono
seguendo i rimandi, non sono configurate direttamente.

⚠️ **I due file condividono gli identificativi dei nodi**, perché il B2B è stato
duplicato dal B2C. Lo stesso `nodeId` restituisce componenti diversi. Il file va
sempre indicato esplicitamente. Vedi
[modulo 1 dell'architettura](architettura/01-raccolta-input.md).

---

## Gli endpoint in uso

### `GET /v1/files/{key}`

Senza parametri restituisce anche `lastModified`, che è tutto ciò che serve per
sapere se vale la pena leggere il resto.

```
uso      rilevare se qualcosa è cambiato
costo    < 1 s
```

### `GET /v1/files/{key}?depth=N`

L'albero del file fino a `N` livelli: pagine, componenti, nomi, stati.

```
uso      censimento delle pagine, ricerca dei frame di documentazione
costo    ~40 s con depth=3
```

⚠️ **`depth` è una trappola.** Con `depth=3` la documentazione che sta a cinque,
sei o sette livelli **non viene vista**, e il risultato sembra «nessuna
documentazione» invece di «non ho cercato abbastanza». È il caso reale che ha
fatto risultare privi di documentazione componenti che invece ce l'hanno.

⚠️ Con `depth=1` i manifesti di componenti e stili tornano **vuoti**: se servono,
occorre almeno `depth=3`.

### `GET /v1/files/{key}/nodes?ids=…`

Un nodo per intero, **senza limite di profondità**. È il modo giusto per leggere
un componente o un frame di documentazione.

```
uso      varianti, geometria, tabella delle proprietà, testi della doc
costo    ~2 s per nodo
```

### `GET /v1/files/{key}/variables/local`

Il catalogo delle variabili del file, con le catene di rimandi.

```
uso      risolvere i token
costo    ~3 s per file
```

Le variabili importate da altre librerie si riconoscono dal formato
dell'identificativo, e per risolverle serve leggere anche il file d'origine:
**1.853 salti fra file** su 2.076 variabili.

---

## Chi usa cosa

```
scan-files       files?depth=3                       censimento pagine
build-anchor     files?depth=3 · depth=5 · nodes     dove sta il componente
build-contract   nodes · variables/local             proprietà, token, dimensioni
extract-docs     nodes                               scopo, anti-pattern, comportamento
resolve-tokens   variables/local                     catalogo e valori risolti
```

---

## Tempi misurati

Su chiamate reali ai file di produzione, non stimati.

| Operazione | Durata |
|---|---|
| Rilevare un cambiamento | **< 1 s** |
| Tutte le variabili di un file | **~3 s** |
| Albero del file (`depth=3`) | **~40 s** |
| Un nodo | **~2 s** |
| Un componente completo | **~5 s** |
| Passata su tutti i componenti | **8-10 min** |

---

## Gestione degli errori

⚠️ **Lacuna nota: solo `extract-docs.mjs` ritenta.**

| Script | Ritentativi | Timeout |
|---|---|---|
| `extract-docs` | ✅ 4 tentativi, attesa crescente | ✅ 90 s |
| `build-contract` | ❌ | ❌ |
| `build-anchor` | ❌ | ❌ |
| `scan-files` | ❌ | ❌ |
| `resolve-tokens` | da verificare | da verificare |

Gli altri falliscono al primo errore di rete. Durante lo sviluppo si sono
verificati **timeout intermittenti** dell'API Figma, quindi non è un rischio
teorico: una passata completa da otto minuti può interrompersi a metà.

Il comportamento corretto, già implementato in `extract-docs`, è ritentare su
`429` e sui codici `5xx` con attesa crescente, e imporre un timeout esplicito.
Portarlo negli altri è parte dell'attività **2** (*rendere affidabile
l'estrazione*).

---

## Endpoint previsti, non ancora in uso

| Endpoint | Per cosa | Stato |
|---|---|---|
| `GET /v1/images` | immagini dei componenti nelle pagine del sito | attività **4** |
| `GET /v1/files/{key}/variables/published` | variabili pubblicate invece che di lavoro | da valutare |
| `POST /v2/webhooks` | avvisi immediati invece del controllo periodico | ⛔ **403** |

Il `403` sui webhook è la ragione per cui l'attività **12** è bloccata: il token
attuale è a scopo limitato. È anche **l'unica chiamata in scrittura** che il
sistema userebbe mai, e serve solo a registrare *«avvisami quando cambia»*: non
tocca il contenuto dei file.

---

## Cosa il sistema non fa

- **Non scrive su Figma.** Nessuna chiamata `POST`, `PUT`, `PATCH` o `DELETE`
  verso i file, verificato riga per riga sul codice.
- **Non legge i commenti**, né i dati degli utenti.
- **Non accede a file diversi** da quelli configurati e da quelli raggiunti
  seguendo i rimandi delle variabili.

⚠️ Notare la formulazione: *non fa*, non *non può*. Il token ha permessi di
scrittura su variabili, commenti, Code Connect e dev resources. Chi volesse la
garanzia a livello di permesso, e non di codice, deve chiedere un token con i
soli scope in lettura.
