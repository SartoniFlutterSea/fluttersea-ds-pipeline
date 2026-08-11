#!/usr/bin/env python3
"""
Strato leggero: cosa ogni file OFFRE.

Cinque chiamate per file, ~5 secondi, ~5 MB:
  ?depth=1            le pagine
  /components         i componenti pubblicati, con la loro CHIAVE
  /component_sets     i set pubblicati
  /styles             gli stili pubblicati
  /variables/local    le variabili, con i loro alias

Il risultato e' l'INDICE GLOBALE `chiave -> file`. Serve a rendere gratuite le
risoluzioni: senza, ogni riferimento a un componente esterno costa una chiamata
a /v1/components/{key}. Con l'indice in memoria, zero.

Nota: /components restituisce i soli componenti PUBBLICATI, non tutti quelli
presenti nel file (1.496 su 2.358 per Cross App). E' esattamente cio' che serve:
solo un componente pubblicato puo' essere consumato da un altro file.

  python tools/index_keys.py [--quanti=N] [--daccapo] [--perimetro]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "grafo" / "indice.json"


def perimetro_ds():
    """Gli 8 file del design system: i semi piu' le librerie gia' scoperte."""
    chiavi = []
    cfg = json.loads((ROOT / "config" / "figma-files.json").read_text(encoding="utf-8"))
    chiavi += [v["fileKey"] for v in cfg["files"].values()]
    inv = ROOT / "data" / "figma-inventory.json"
    if inv.exists():
        chiavi += list(json.loads(inv.read_text(encoding="utf-8")).get("files", {}))
    return sorted(set(chiavi))


def tutti_i_file():
    p = ROOT / "data" / "figma-censimento.json"
    if not p.exists():
        return perimetro_ds()
    return sorted(json.loads(p.read_text(encoding="utf-8"))["files"])


def leggi_file(f: Figma, chiave: str) -> dict:
    """Le cinque chiamate leggere su un file. Ogni errore e' registrato, non solleva."""
    esito = {"fileKey": chiave, "errori": {}}

    meta, err = f.prova(f"files/{chiave}?depth=1")
    if err:
        esito["errori"]["file"] = err
        return esito
    esito["nome"] = meta.get("name")
    esito["lastModified"] = meta.get("lastModified")
    esito["versione"] = meta.get("version")
    esito["pagine"] = [
        {"id": p.get("id"), "nome": p.get("name")}
        for p in (meta.get("document", {}).get("children") or [])
    ]

    for endpoint, campo in (("components", "componenti"), ("component_sets", "set"), ("styles", "stili")):
        dati, err = f.prova(f"files/{chiave}/{endpoint}")
        if err:
            esito["errori"][endpoint] = err
            esito[campo] = []
            continue
        voci = (dati.get("meta") or {}).get(endpoint) or []
        esito[campo] = [
            {
                "key": v.get("key"),
                "nodeId": v.get("node_id"),
                "nome": v.get("name"),
                "descrizione": (v.get("description") or "") or None,
                "pagina": ((v.get("containing_frame") or {}).get("pageName")),
                "aggiornato": v.get("updated_at"),
                "tipoStile": v.get("style_type"),
            }
            for v in voci
            if v.get("key")
        ]

    var, err = f.prova(f"files/{chiave}/variables/local")
    if err:
        esito["errori"]["variables"] = err
        esito["variabili"] = []
        return esito

    meta_v = var.get("meta") or {}
    collezioni = meta_v.get("variableCollections") or {}
    variabili = []
    for v in (meta_v.get("variables") or {}).values():
        if not v.get("key"):
            continue
        col = collezioni.get(v.get("variableCollectionId")) or {}
        alias = []
        letterali = 0
        for modo, valore in (v.get("valuesByMode") or {}).items():
            if isinstance(valore, dict) and valore.get("type") == "VARIABLE_ALIAS":
                rif = str(valore.get("id") or "")
                # "VariableID:<chiave>/<idLocale>" significa variabile importata
                esterna = "/" in rif
                alias.append({
                    "modo": modo,
                    "verso": rif,
                    "chiaveVerso": rif.replace("VariableID:", "").split("/")[0] if esterna else None,
                    "esterno": esterna,
                })
            else:
                letterali += 1
        variabili.append({
            "key": v["key"],
            "id": v.get("id"),
            "nome": v.get("name"),
            "tipo": v.get("resolvedType"),
            "collezione": col.get("name"),
            "modi": [m.get("name") for m in (col.get("modes") or [])],
            "alias": alias,
            "letterali": letterali,
        })
    esito["variabili"] = variabili
    return esito


def main(argv):
    quanti = 3
    for a in argv:
        if a.startswith("--quanti="):
            quanti = int(a.split("=")[1])

    espliciti = [a for a in argv if not a.startswith("--")]
    if espliciti:
        # file indicati a mano: quelli scoperti da resolve_keys non stanno nel
        # censimento, ma indicizzarli rende risolvibili i loro componenti
        chiavi = espliciti
    else:
        chiavi = perimetro_ds() if "--perimetro" in argv else tutti_i_file()

    precedenti = {}
    if USCITA.exists() and "--daccapo" not in argv:
        try:
            precedenti = json.loads(USCITA.read_text(encoding="utf-8")).get("files", {})
        except (OSError, json.JSONDecodeError):
            precedenti = {}
    riusciti = {k: v for k, v in precedenti.items() if not v.get("errori", {}).get("file")}

    mancanti = [k for k in chiavi if k not in riusciti]
    if riusciti:
        print(f"  {len(riusciti)} gia' indicizzati")
    print(f"  {len(mancanti)} da indicizzare, {quanti} in parallelo\n")

    f = Figma()
    fatti = [0]

    def lavora(chiave):
        r = leggi_file(f, chiave)
        fatti[0] += 1
        if fatti[0] % 10 == 0:
            print(f"    {fatti[0]}/{len(mancanti)}...", flush=True)
        return chiave, r

    files = dict(riusciti)
    if mancanti:
        files.update(dict(f.in_parallelo(mancanti, lavora, quanti)))

    # ── indice globale: chiave -> file ───────────────────────────────────────
    comp, var, sty = {}, {}, {}
    for k, v in files.items():
        for c in v.get("componenti") or []:
            comp[c["key"]] = {"file": k, "nodeId": c["nodeId"], "nome": c["nome"]}
        for c in v.get("set") or []:
            comp[c["key"]] = {"file": k, "nodeId": c["nodeId"], "nome": c["nome"], "set": True}
        for s in v.get("stili") or []:
            sty[s["key"]] = {"file": k, "nodeId": s["nodeId"], "nome": s["nome"]}
        for x in v.get("variabili") or []:
            var[x["key"]] = {"file": k, "id": x["id"], "nome": x["nome"]}

    scrivi_json(USCITA, {
        "totali": {
            "file": len(files),
            "componenti": len(comp),
            "stili": len(sty),
            "variabili": len(var),
            "chiamate": f.chiamate,
        },
        "indiceComponenti": comp,
        "indiceStili": sty,
        "indiceVariabili": var,
        "files": files,
    })

    linea = "─" * 64
    print(f"\n{linea}")
    print(f"  file indicizzati    {len(files)}")
    print(f"  componenti          {len(comp)}")
    print(f"  stili               {len(sty)}")
    print(f"  variabili           {len(var)}")
    errori = {k: v["errori"] for k, v in files.items() if v.get("errori")}
    if errori:
        print(f"\n  con errori          {len(errori)}")
        for k, e in list(errori.items())[:6]:
            print(f"    {(files[k].get('nome') or k)[:34]:<36}{e}")
    print(f"\n  chiamate API {f.chiamate}")
    print(f"  scritto data/grafo/{USCITA.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
