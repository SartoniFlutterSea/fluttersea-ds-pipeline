#!/usr/bin/env python3
"""
Unisce i grafi per file in uno solo, calcola la topologia e produce l'albero.

La distinzione atomo/molecola/organismo NON si ricava dai nomi ma dal grafo:
un componente che non usa altri componenti e' un atomo, uno che usa atomi e'
una molecola, uno che usa molecole e' un organismo. E' una proprieta'
topologica, piu' affidabile di qualsiasi convenzione di naming.

  python tools/build_graph.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, scrivi_json  # noqa: E402
import _grafo as G  # noqa: E402

CARTELLA = ROOT / "data" / "grafo"
ALBERO = ROOT / "docs" / "grafo-figma.md"


def main():
    files = sorted((CARTELLA / "file").glob("*.json"))
    if not files:
        sys.exit("\n  Nessun grafo per file. Eseguire prima tools/graph_file.py\n")

    g = G.Grafo()
    copertura = {}
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        parziale = G.Grafo()
        parziale.nodi = d["nodi"]
        parziale.archi = {(a["da"], a["tipo"], a["a"]): a for a in d["archi"]}
        parziale.irrisolti = d.get("irrisolti") or []
        g.unisci(parziale)
        f = next(v for v in d["nodi"].values() if v["tipo"] == "file")
        copertura[d["fileKey"]] = {"nome": f.get("nome"), **(f.get("_letto") or {})}

    g.calcola_profondita()
    r = g.riepilogo()

    scrivi_json(CARTELLA / "nodi.json", g.nodi)
    scrivi_json(CARTELLA / "archi.json", [dict(v) for v in g.archi.values()])
    scrivi_json(CARTELLA / "riepilogo.json", {"riepilogo": r, "copertura": copertura})

    # ── albero leggibile ─────────────────────────────────────────────────────
    per_file = {}
    for n in g.nodi.values():
        if n["tipo"] == "file":
            per_file.setdefault(n.get("fileKey"), {"info": n, "tipi": {}})
    for n in g.nodi.values():
        fk = n.get("file")
        if fk in per_file and n["tipo"] != "file":
            per_file[fk]["tipi"][n["tipo"]] = per_file[fk]["tipi"].get(n["tipo"], 0) + 1

    # dipendenze fra file, dagli archi che attraversano il confine
    fra_file = {}
    for a in g.archi.values():
        fd = a.get("fileDestinazione")
        da = g.nodi.get(a["da"], {}).get("file") or g.nodi.get(a["da"], {}).get("fileKey")
        if fd and da and fd != da:
            fra_file[(da, fd)] = fra_file.get((da, fd), 0) + a["occorrenze"]

    nome = lambda fk: (per_file.get(fk, {}).get("info", {}) or {}).get("nome") or fk

    righe = [
        "# Grafo dei dati Figma", "",
        f"{r['nodi']:,} nodi · {r['archi']:,} archi · {r['irrisolti']:,} riferimenti irrisolti".replace(",", "."),
        "",
        "Identita' dei nodi: `fig:{file}:{nodo}` per i nodi, `comp:{chiave}` per i",
        "componenti pubblicati, `var:` e `sty:` per variabili e stili. Team e progetto",
        "sono **attributi**, non parte dell'identificativo: un file spostato di",
        "progetto non deve generare un nodo duplicato.", "",
        "## Tipologie di nodo", "", "| Tipo | Nodi |", "|---|---|",
    ]
    righe += [f"| {k} | {v:,} |".replace(",", ".") for k, v in r["perTipo"].items()]
    righe += ["", "## Tipi di arco", "", "| Tipo | Archi |", "|---|---|"]
    righe += [f"| {k} | {v:,} |".replace(",", ".") for k, v in r["perArco"].items()]

    righe += ["", "## Dipendenze fra file", "",
              "Archi che attraversano il confine di un file, con quante volte ricorrono.", ""]
    for (a, b), n in sorted(fra_file.items(), key=lambda x: -x[1]):
        righe.append(f"- **{nome(a)}** → **{nome(b)}** · {n:,} riferimenti".replace(",", "."))

    righe += ["", "## Albero per file", ""]
    for fk, d in sorted(per_file.items(), key=lambda x: -sum(x[1]["tipi"].values())):
        i = d["info"]
        c = copertura.get(fk, {})
        righe.append(f"### {i.get('nome')}")
        righe.append("")
        righe.append(f"`{fk}` · letto in modo **{c.get('modo', '?')}** · "
                     f"{c.get('nodi', 0):,} nodi Figma".replace(",", "."))
        if c.get("senzaManifest"):
            righe.append("")
            righe.append(f"> ⚠️ {c['senzaManifest']:,} istanze non attribuite: il file supera il limite".replace(",", ".")
                         + " della lettura completa e il ripiego per pagina non restituisce i manifest.")
        righe.append("")
        for t, n in sorted(d["tipi"].items(), key=lambda x: -x[1]):
            righe.append(f"- {t}: **{n:,}**".replace(",", "."))
        righe.append("")

    ALBERO.parent.mkdir(parents=True, exist_ok=True)
    ALBERO.write_text("\n".join(righe) + "\n", encoding="utf-8")

    linea = "─" * 64
    print(f"\n{linea}")
    print(f"  nodi   {r['nodi']:,}".replace(",", "."))
    print(f"  archi  {r['archi']:,}".replace(",", "."))
    print(f"  irrisolti {r['irrisolti']:,}".replace(",", "."))
    print("\n  PER TIPO")
    for k, v in r["perTipo"].items():
        print(f"    {k:<20}{v:,}".replace(",", "."))
    print("\n  PER ARCO")
    for k, v in r["perArco"].items():
        print(f"    {k:<20}{v:,}".replace(",", "."))
    print(f"\n  scritto data/grafo/nodi.json · archi.json · riepilogo.json")
    print(f"          docs/{ALBERO.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
