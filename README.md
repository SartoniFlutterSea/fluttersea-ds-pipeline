# fluttersea-ds-ai

Estrae il **Design System Cross-App** da Figma verso JSON strutturati, e ne
pubblica la documentazione come sito statico.

Il design system è mobile-native (iOS, Android, iOS Liquid Glass): qui non ci
sono componenti da renderizzare in un browser, ma la loro descrizione letta
direttamente dai file Figma.

## Cosa produce

Tre artefatti per componente, una cartella ciascuno, in `data/contracts/<slug>/`:

| File | Contenuto | Cambia quando |
|---|---|---|
| `contract.json` | property, token, dimensioni, testi | si modifica il componente |
| `intent.json` | scopo, anti-pattern, comportamento | si modifica la documentazione |
| `figma.json` | dove sta in Figma, per piattaforma, stato della pagina | un nodo si sposta |

Sono separati perché hanno ritmi diversi: il contratto cambia a ogni
pubblicazione, l'ancoraggio quasi mai.

## Struttura

```
tools/          gli script di estrazione
config/         quali file Figma leggere, come interpretare i marcatori di stato
data/           gli artefatti estratti, versionati
storybook/      il sito di documentazione, generato da data/
scripts/        generazione delle storie
docs/           come funziona l'importazione e la gestione dei dati
```

`data/` è versionato di proposito: gli artefatti sono il prodotto della
pipeline, e vederli in diff è il modo per capire cosa è cambiato in Figma.

## Uso

```bash
npm install
export FIGMA_TOKEN=figd_...        # oppure copiare .env.example in .env.local

node tools/scan-files.mjs                          # censimento delle pagine
node tools/build-contract.mjs <slug> <nodeId> b2c  # i fatti fisici
node tools/build-anchor.mjs   <slug> <nodeId> b2c  # l'ancoraggio
node tools/extract-docs.mjs   <slug> <purposeId> <behaviorId>   # la documentazione

npm run storybook          # il sito in locale
npm run build-storybook    # il sito statico
```

### Il `ds` va sempre indicato

I due design system condividono gli identificativi dei nodi, perché il file
B2B è stato duplicato dal B2C. Lo stesso `nodeId` su file diversi restituisce
componenti diversi: `5473:10855` è un Button da 90 varianti su B2C e da 120 su
B2B. Senza specificare il `ds` si documenta il componente sbagliato, e nulla lo
segnala.

## Stato

Estratti finora: `button`, `button-icon`, `fab`. I componenti documentati in
Figma sono molti di più; la pagina *Stato dell'estrazione* del sito misura
quanto è coperto.

### Limiti noti

- **FAB non produce token né dimensioni.** L'estrattore misura i token sulla
  size di riferimento; FAB non ha un asse `size`, quindi non misura nulla e non
  avvisa. Vale per ogni componente senza quell'asse.
- **I nodi per piattaforma** vengono letti da una documentazione esterna scritta
  a mano, quando disponibile. Andrebbero ricavati da Figma.
- **Il formato della documentazione non è uno solo.** Oltre a `Purpose & Usage`
  + `Behavior`, in Figma esiste un formato più vecchio con frame `Do & don't`
  che l'estrattore non legge ancora.
