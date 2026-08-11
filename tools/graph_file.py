#!/usr/bin/env python3
"""
Strato pesante: cosa un file USA, con granularita' di componente.

Una lettura completa (160 MB, 55 s per Cross App) parsificata A EVENTI con
ijson: i 139.897 nodi non finiscono mai tutti in memoria insieme. Si tiene solo
la PILA del percorso corrente, profonda quanto l'annidamento.

PERCHE' NON BASTA QUALCOSA DI PIU' LEGGERO, misurato:
  ?depth=3     5,4 MB   manifest incompleto:   105 componenti su 2.358
  ?depth=8    64,8 MB   ancora incompleto:   1.745 su 2.358
  /nodes?ids=  per pagina, ma NON restituisce i manifest (verificato: 0)

Il manifest `components` e' indispensabile: un nodo INSTANCE porta un
`componentId` che e' un identificativo di NODO, non una chiave. Solo il
manifest traduce quel nodo nella chiave con cui risalire al file d'origine.

  python tools/graph_file.py <fileKey> [...] [--forza]
"""
import json
import sys
import time
from pathlib import Path

import ijson
import requests

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, TOKEN, scrivi_json  # noqa: E402
import _grafo as G  # noqa: E402

CARTELLA = ROOT / "data" / "grafo" / "file"
INDICE = ROOT / "data" / "grafo" / "indice.json"

# Campi del nodo che interessano. Tutto il resto si scarta appena letto.
CAMPI = {"id", "name", "type", "componentId", "transitionNodeID"}
CONTENITORI = {"COMPONENT", "COMPONENT_SET"}


def carica_cache():
    """Risoluzioni gia' fatte da resolve_keys: chiave -> file. Non cambiano mai."""
    p = ROOT / "data" / "grafo" / "cache-chiavi.json"
    if not p.exists():
        return {}
    try:
        c = json.loads(p.read_text(encoding="utf-8")).get("chiavi", {})
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in c.items() if v.get("file")}


def carica_indice():
    if not INDICE.exists():
        sys.exit("\n  Manca data/grafo/indice.json. Eseguire prima tools/index_keys.py\n")
    return json.loads(INDICE.read_text(encoding="utf-8"))


def attraversa(file_key: str, su_nodo, su_manifest, indice=None):
    """
    Scarica e attraversa senza materializzare.

    `document` e' la PRIMA chiave del JSON (verificato), quindi lo streaming non
    puo' fermarsi prima: va letto tutto. Ma si tiene solo la pila corrente.

    Sono nodi soltanto le mappe sotto un array `children`: cosi' `fills.item`,
    `effects.item` e simili non vengono scambiati per nodi.

    ⚠️ Oltre una certa dimensione Figma rifiuta la lettura completa con
    «Request too large» (misurato su Library MySisal e DS WEB GLOBAL, mentre
    Cross App a 160 MB e DS B2B a 307.913 nodi passano). In quel caso si ripiega
    su una lettura per pagina, che pero' NON restituisce i manifest: il
    ripiego lo dichiara al chiamante, che ne terra' conto nella copertura.
    """
    esito = _intero(file_key, su_nodo, su_manifest)
    if esito == "troppo-grande":
        return _per_pagina(file_key, su_nodo, su_manifest, indice)
    return esito


def _per_pagina(file_key: str, su_nodo, su_manifest, indice):
    """Ripiego: una pagina alla volta. Manifest solo dai componenti pubblicati."""
    info = ((indice or {}).get("files") or {}).get(file_key, {})
    for c in (info.get("componenti") or []) + (info.get("set") or []):
        if c.get("nodeId") and c.get("key"):
            su_manifest("components", {"_nodeId": c["nodeId"], "key": c["key"],
                                       "name": c.get("nome"), "remote": False})

    pagine = [p["id"] for p in (info.get("pagine") or []) if p.get("id")]
    for pid in pagine:
        url = f"https://api.figma.com/v1/files/{file_key}/nodes?ids={pid}"
        with requests.get(url, headers={"X-Figma-Token": TOKEN}, stream=True, timeout=900) as r:
            if not r.ok:
                continue
            r.raw.decode_content = True
            _eventi(ijson.parse(r.raw), su_nodo, su_manifest, radice="nodes")
    return "per-pagina"


def _intero(file_key: str, su_nodo, su_manifest):
    url = f"https://api.figma.com/v1/files/{file_key}"
    with requests.get(url, headers={"X-Figma-Token": TOKEN}, stream=True, timeout=1800) as r:
        if r.status_code == 400:
            # il corpo va letto QUI: dopo la chiusura del flusso non c'e' piu'
            corpo = r.raw.read(400).decode("utf8", "replace")
            if "too large" in corpo.lower():
                return "troppo-grande"
            raise requests.HTTPError(f"HTTP 400 — {corpo[:160]}", response=r)
        r.raise_for_status()
        r.raw.decode_content = True
        _eventi(ijson.parse(r.raw), su_nodo, su_manifest, radice="document")
    return "intero"


def _eventi(parser, su_nodo, su_manifest, radice: str):
        pila = []
        manifest_in_corso = None
        voce = {}

        for prefisso, evento, valore in parser:
            # ── manifest di primo livello ────────────────────────────────────
            if evento == "start_map" and prefisso in ("components", "componentSets", "styles"):
                manifest_in_corso = prefisso
                continue
            if manifest_in_corso:
                if prefisso == manifest_in_corso and evento == "end_map":
                    manifest_in_corso = None
                    continue
                resto = prefisso[len(manifest_in_corso) + 1 :] if prefisso.startswith(manifest_in_corso + ".") else ""
                if resto and "." not in resto:
                    if evento == "start_map":
                        voce = {"_nodeId": resto}
                    elif evento == "end_map":
                        su_manifest(manifest_in_corso, voce)
                        voce = {}
                elif resto and evento in ("string", "number", "boolean"):
                    campo = resto.split(".", 1)[1]
                    if "." not in campo:
                        voce[campo] = valore
                continue

            # ── albero del documento ─────────────────────────────────────────
            # lettura intera:    document...
            # lettura per pagina: nodes.<id>.document...
            if radice == "document":
                if not prefisso.startswith("document"):
                    continue
                e_nodo = prefisso == "document" or prefisso.endswith(".children.item")
            else:
                if ".document" not in prefisso:
                    continue
                e_nodo = prefisso.endswith(".document") or prefisso.endswith(".children.item")

            if evento == "start_map" and e_nodo:
                pila.append({"_p": prefisso})
                continue

            if evento == "end_map" and e_nodo and pila and pila[-1]["_p"] == prefisso:
                su_nodo(pila.pop(), pila)
                continue

            if pila and evento in ("string", "number", "boolean"):
                p = pila[-1]["_p"]
                if prefisso.startswith(p + "."):
                    campo = prefisso[len(p) + 1 :]
                    if campo in CAMPI:
                        pila[-1][campo] = valore
                    elif campo == "absoluteBoundingBox.width":
                        pila[-1]["larghezza"] = valore


def analizza(file_key: str, indice: dict) -> tuple[G.Grafo, dict]:
    g = G.Grafo()
    idx_comp = indice.get("indiceComponenti", {})
    idx_var = indice.get("indiceVariabili", {})
    cache = carica_cache()
    info = (indice.get("files") or {}).get(file_key, {})
    id_f = G.id_file(file_key)

    g.nodo(id_f, "file", fileKey=file_key, nome=info.get("nome") or file_key,
           team=info.get("team"), progetto=info.get("progetto"),
           lastModified=info.get("lastModified"))

    per_nodo: dict[str, dict] = {}          # nodeId -> {key, name}

    def su_manifest(_quale, voce):
        nid, k = voce.get("_nodeId"), voce.get("key")
        if nid and k:
            # `remote` distingue un componente di QUESTO file da uno importato
            # da una libreria. Senza, un componente locale non pubblicato
            # sembrerebbe un riferimento esterno irrisolto.
            per_nodo[nid] = {"key": k, "nome": voce.get("name"),
                             "remote": bool(voce.get("remote")),
                             # se c'e', questo componente e' una VARIANTE di un set
                             "set": voce.get("componentSetId")}

    conta = {"nodi": 0, "istanze": 0, "senzaManifest": 0, "esterne": 0, "interne": 0,
             "localiNonPubblicati": 0, "esterneIgnote": 0,
             "schermate": 0, "documentazione": 0, "transizioni": 0}

    # ⚠️ `document` precede i manifest nel JSON: durante l'attraversamento
    # `per_nodo` e' ancora vuoto. Si accumula e si risolve DOPO, quando il
    # manifest e' completo. Si conservano solo tuple leggere, non i nodi.
    varianti: dict[str, int] = {}                              # chiave del set -> quante varianti
    visti_componenti: list[tuple[str, str, str | None]] = []   # (nodeId, nome, antenatoNodeId)
    visti_istanze: list[tuple[str | None, str]] = []           # (antenatoNodeId, componentId)

    def su_nodo(nodo, pila):
        conta["nodi"] += 1
        tipo = nodo.get("type")
        nome = nodo.get("name") or ""
        nid = nodo.get("id")

        # il componente antenato piu' vicino: e' lui che "usa" cio' che contiene.
        # Si identifica per nodeId, perche' la chiave non e' ancora nota.
        antenato = None
        for f in reversed(pila):
            if f.get("type") in CONTENITORI and f.get("id"):
                antenato = f["id"]
                break

        if tipo in CONTENITORI and nid:
            visti_componenti.append((nid, nome, antenato))

        if tipo == "INSTANCE" and nodo.get("componentId"):
            conta["istanze"] += 1
            visti_istanze.append((antenato, nodo["componentId"]))

        # schermate e documentazione: solo fuori da un componente
        if tipo == "FRAME" and nid:
            # pila = [documento, pagina] quando il frame sta sulla pagina
            classe = G.classifica_frame(nome, nodo.get("larghezza"), bool(antenato),
                                        sulla_pagina=len(pila) == 2)
            if classe == "schermata":
                conta["schermate"] += 1
                g.nodo(G.id_nodo(file_key, nid), "schermata", file=file_key, nome=nome,
                       larghezza=nodo.get("larghezza"))
                g.arco(id_f, "contiene", G.id_nodo(file_key, nid))
            elif classe == "documentazione":
                conta["documentazione"] += 1
                g.nodo(G.id_nodo(file_key, nid), "documentazione", file=file_key, nome=nome)
                g.arco(id_f, "contiene", G.id_nodo(file_key, nid))

        if nodo.get("transitionNodeID") and nid:
            conta["transizioni"] += 1
            g.arco(G.id_nodo(file_key, nid), "transizione",
                   G.id_nodo(file_key, nodo["transitionNodeID"]))

    t0 = time.time()
    modo = attraversa(file_key, su_nodo, su_manifest, indice)
    durata = time.time() - t0

    # ── risoluzione, ora che il manifest c'e' ────────────────────────────────
    def chiave_di(node_id):
        """
        La chiave dell'unita' significativa. Una COMPONENT che appartiene a un
        COMPONENT_SET e' una VARIANTE, non un componente a se': Button ha 90
        combinazioni di varianti, e contarle una per una gonfiava il totale di
        2,6 volte. L'unita' e' il set; le varianti diventano un suo attributo.
        """
        voce = per_nodo.get(node_id)
        if not voce:
            return None
        sid = voce.get("set")
        if sid:
            padre = per_nodo.get(sid)
            if padre:
                varianti[padre["key"]] = varianti.get(padre["key"], 0) + 1
                return padre["key"]
        return voce["key"]

    for nid, nome, antenato in visti_componenti:
        voce = per_nodo.get(nid)
        if voce and voce.get("set"):
            continue                      # e' una variante: conta il set, non lei
        k = chiave_di(nid)
        if not k:
            continue                      # componente non pubblicato: non e' un nodo del grafo
        g.nodo(G.id_componente(k), "componente", file=file_key, nodeId=nid, nome=nome)
        g.arco(id_f, "pubblica", G.id_componente(k))
        ka = chiave_di(antenato) if antenato else None
        if ka:
            g.arco(G.id_componente(ka), "contiene", G.id_componente(k))

    for antenato, cid in visti_istanze:
        voce = per_nodo.get(cid)
        if not voce:
            conta["senzaManifest"] += 1
            continue
        chiave = voce["key"]
        bersaglio = G.id_componente(chiave)
        ka = chiave_di(antenato) if antenato else None
        da = G.id_componente(ka) if ka else id_f

        # dove vive il componente: indice, poi cache delle risoluzioni, poi
        # il campo `remote` del manifest come ultima parola
        dest = idx_comp.get(chiave) or cache.get(chiave)
        origine = (dest or {}).get("file")

        if origine and origine != file_key:
            conta["esterne"] += 1
            g.nodo(bersaglio, "componente", file=origine, nome=(dest or {}).get("nome"))
            g.arco(da, "istanza-di", bersaglio, fileDestinazione=origine)
        elif origine:
            conta["interne"] += 1
            g.arco(da, "istanza-di", bersaglio, fileDestinazione=file_key)
        elif not voce["remote"]:
            # componente di questo file, mai pubblicato come libreria: e' locale,
            # non un riferimento mancante
            conta["localiNonPubblicati"] += 1
            g.nodo(bersaglio, "componente", file=file_key, nome=voce.get("nome"), pubblicato=False)
            g.arco(da, "istanza-di", bersaglio, fileDestinazione=file_key)
        else:
            conta["esterneIgnote"] += 1
            g.irrisolto(tipo="componente", da=da, chiave=chiave, nodo=cid, remoto=True)

    # ── stili e variabili, dallo strato leggero ──────────────────────────────
    for s in info.get("stili") or []:
        g.nodo(G.id_stile(s["key"]), "stile", file=file_key, nodeId=s.get("nodeId"), nome=s.get("nome"))
        g.arco(id_f, "pubblica", G.id_stile(s["key"]))

    for v in info.get("variabili") or []:
        ident = G.id_variabile(v["key"])
        esterni = [a for a in v.get("alias") or [] if a.get("esterno")]
        locali = [a for a in v.get("alias") or [] if not a.get("esterno")]
        g.nodo(ident, "alias-esterno" if esterni else "alias-locale" if locali else "token",
               file=file_key, nome=v.get("nome"), tipoValore=v.get("tipo"), collezione=v.get("collezione"))
        g.arco(id_f, "pubblica", ident)
        for a in esterni:
            ck = a.get("chiaveVerso")
            dest = idx_var.get(ck)
            if dest:
                g.arco(ident, "alias-di", G.id_variabile(ck), fileDestinazione=dest["file"])
            else:
                g.irrisolto(tipo="variabile", da=ident, chiave=ck, modo=a.get("modo"))

    for k, n_var in varianti.items():
        nodo = g.nodi.get(G.id_componente(k))
        if nodo:
            nodo["varianti"] = max(nodo.get("varianti", 0), n_var)
    conta["setConVarianti"] = len(varianti)
    conta["modo"] = modo
    conta["manifest"] = len(per_nodo)
    conta["secondi"] = round(durata, 1)
    g.nodi[id_f]["_letto"] = conta
    return g, conta


def main(argv):
    chiavi = [a for a in argv if not a.startswith("--")]
    if not chiavi:
        sys.exit("\n  python tools/graph_file.py <fileKey> [<fileKey> ...] [--forza]\n")

    indice = carica_indice()
    CARTELLA.mkdir(parents=True, exist_ok=True)

    for k in chiavi:
        uscita = CARTELLA / f"{k}.json"
        if uscita.exists() and "--forza" not in argv:
            print(f"  già fatto, si salta: {k}   (--forza per rifarlo)")
            continue
        nome = ((indice.get("files") or {}).get(k) or {}).get("nome") or k
        print(f"\n▸ {nome}   {k}", flush=True)
        try:
            g, c = analizza(k, indice)
        except requests.RequestException as e:
            print(f"    ✖ {str(e)[:120]}")
            continue
        r = g.riepilogo()
        print(f"    {c['nodi']} nodi in {c['secondi']}s  ·  manifest {c['manifest']}")
        print(f"    istanze {c['istanze']}  →  esterne {c['esterne']} · interne {c['interne']}"
              f" · locali non pubblicati {c['localiNonPubblicati']} · esterne ignote {c['esterneIgnote']}")
        print(f"    schermate {c['schermate']} · documentazione {c['documentazione']}"
              f" · transizioni {c['transizioni']}")
        print(f"    grafo: {r['nodi']} nodi, {r['archi']} archi, {r['irrisolti']} irrisolti")
        scrivi_json(uscita, {
            "fileKey": k,
            "riepilogo": r,
            "nodi": g.nodi,
            "archi": [dict(v) for v in g.archi.values()],
            "irrisolti": g.irrisolti,
        })
        print(f"    scritto data/grafo/file/{k}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
