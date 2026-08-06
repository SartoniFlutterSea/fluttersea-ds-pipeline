# Attività previste

> Ricavate dalle decisioni aperte e dai limiti noti dei
> [cinque moduli di architettura](architettura/README.md).
>
> **Le colonne `Ordine` e `Stima` sono da compilare.** Questo documento è fatto
> per essere modificato: le attività sono descritte per risultato, non per
> passaggi tecnici, così che l'ordine si possa decidere senza entrare nel codice.

**🎯** serve al primo obiettivo: design-to-code provato e Storybook consultabile
**⛔** dipende da una decisione o da un accesso che non controlliamo

---

## Fondamenta

| | Attività | Produce | Ordine | Stima |
|---|---|---|---|---|
| **1** 🎯 | **Validare l'architettura col team** | I cinque moduli rivisti, obiezioni raccolte, impianto confermato o corretto | | |
| **2** 🎯 | **Rendere affidabile l'estrazione** | Nessun dato esce vuoto o sbagliato in silenzio | | |
| **3** 🎯 | **Estendere l'estrazione a tutti i componenti** | Da 3 a circa 51, con tutti i formati di documentazione letti | | |

**La 2 precede la 3.** Sono tre difetti già incontrati, tutti della stessa
famiglia: producono un risultato plausibile invece di un errore.

- un componente senza asse dimensionale genera un contratto valido ma vuoto
- la scansione si ferma a tre livelli e dà per assente documentazione che sta a sei
- tre script su quattro non ritentano: un timeout di rete interrompe la passata

Estendere prima di chiuderli significa produrre cinquantuno artefatti sbagliati
invece di tre.

---

## Storybook consultabile

| | Attività | Produce | Ordine | Stima |
|---|---|---|---|---|
| **4** 🎯 | **Pubblicare il sito** | Un link che i designer aprono, con l'accesso deciso | | |
| **5** | **Anteprima per ogni proposta** | Un indirizzo che mostra la modifica prima di approvarla | | |

⚠️ **GitHub Pages non è utilizzabile.** Verificato con tre prove: due account
diversi, e una repository con dentro un solo file HTML. Tutte bloccate nello
stesso stato. È un guasto lato GitHub, documentato dal 25 luglio senza risposta
ufficiale.

Un servizio di ospitalità alternativo chiude la **4**, porta dentro la **5**, e
risolve anche la domanda sulla visibilità. Mezz'ora di configurazione contro
un'attesa senza data.

---

## Design-to-code

| | Attività | Produce | Ordine | Stima |
|---|---|---|---|---|
| **6** 🎯 | **Portare il generatore sul design system giusto** | Genera dal contratto mobile, non da quello web | | |
| **7** 🎯 ⛔ | **Generare un componente su richiesta e misurarlo** | Si sa quanto spesso il generato è corretto | | |
| **8** 🎯 | **Confronto visivo dentro la proposta** | Un designer approva guardando, non leggendo codice | | |
| **9** ⛔ | **Definire da dove arriva il comportamento** | La parte che il contratto non può contenere ha una fonte | | |

La **6** è più grande di quanto sembri: il generatore è stato provato contro il
Button web da 120 varianti, mentre quello mobile ne ha 90 con proprietà diverse.
Non è un adattamento, è rifare il confronto.

La **7** è bloccata dall'accesso alla repository del team, senza il quale manca
il metro di giudizio.

---

## Automazione e controllo

| | Attività | Produce | Ordine | Stima |
|---|---|---|---|---|
| **10** | **Automatizzare il ciclo Figma verso proposta** | Una modifica in Figma apre da sola una proposta verificata | | |
| **11** ⛔ | **Definire approvazioni e responsabilità** | Ogni proposta arriva a chi ne risponde | | |
| **12** ⛔ | **Avvisi immediati da Figma** | Da «entro un quarto d'ora» a «in pochi secondi» | | |

⚠️ **La 12 non blocca nulla.** Il controllo periodico funziona già con gli
accessi che abbiamo. È il tipo di richiesta che finisce in cima alle liste
quando può stare in fondo.

---

## Dati e interfaccia

| | Attività | Produce | Ordine | Stima |
|---|---|---|---|---|
| **13** | **Decidere la gestione dei dati** | Dove vivono i valori dei brand, che fine fa la documentazione scritta a mano, quali brand estrarre | | |
| **14** | **Decidere se i designer useranno GitHub** | Determina se serve costruire un'interfaccia, e quindi un servizio | | |

La **14** è la più sottovalutata. Generare, modificare una proposta e approvare
sono tre azioni che **GitHub già offre**: la revisione di una proposta *è*
l'approvazione modificabile.

```
i designer usano GitHub?

  sì   →  nessuna interfaccia da costruire, nessun servizio, si parte oggi
  no   →  serve un'interfaccia, e allora serve anche un endpoint
```

Il costo non è l'endpoint, che è mezza giornata. È l'interfaccia: settimane per
rifare qualcosa che esiste già. Conviene misurare se i designer si bloccano
davvero, e dove, prima di costruirla.

---

## Cosa dipende da altri

| Attività | Serve | Da chi |
|---|---|---|
| **4** | che GitHub risolva, oppure un host alternativo | GitHub, oppure noi |
| **7** | accesso alla repository del team | IT |
| **9** | da dove arriva il comportamento dei componenti | design system team |
| **11** | chi possiede quali componenti | design system team |
| **12** | utenza di servizio Figma | amministratore Figma |

Sono cinque su quattordici. **Portarle in riunione come richieste esplicite, con
nome e impatto, vale più di qualsiasi affinamento delle stime.**

---

## Cosa è già fatto

Non sono attività da pianificare, ma servono a capire da dove si parte.

```
✅  estrazione funzionante           3 componenti, tre artefatti ciascuno
✅  94% dei token risolti            confrontati col codice esistente
✅  sito compilato e verificato      63 pagine in 20 secondi
✅  architettura documentata         cinque moduli con diagrammi
✅  riferimento delle API Figma      endpoint, tempi, trappole
✅  controllo di coerenza            impedisce di estrarre il componente sbagliato
```

---

## Cosa resta fuori, e perché

| | Perché non ora |
|---|---|
| **Generazione automatica a ogni modifica** | Prima serve la **7**: automatizzare senza sapere quanto è affidabile produce lavoro invece di risparmiarlo |
| **Il design system B2B** | Stessa pipeline, dati separati. È una scelta di prodotto, non un'estensione tecnica |
| **Flussi, stato, dati** | Non stanno in Figma. Richiedono una fonte diversa e un modulo di architettura ancora da scrivere |
| **Altri brand e temi** | Estrarli è meccanico, ma raddoppia i dati senza un uso immediato. Rientra nella **13** |
