#!/usr/bin/env python3
"""
Mappa i componenti documentati in ds-cross-app sui nodi Figma reali.

Risponde a: dei file Figma censiti, quali corrispondono davvero ai componenti
che abbiamo documentato, e ogni componente dove vive esattamente.

I metadata.json della knowledge base dichiarano `figmaNodeIds` per piattaforma,
ma NON dicono in quale file stanno. E gli identificativi non bastano a dedurlo:
i file condividono gli id, perche' il B2B e' un duplicato del B2C. Qui ogni
nodo viene cercato in tutti i file candidati e si registra dove risponde
davvero, con il nome che ha li' dentro.

Le richieste sono raggruppate: /v1/files/{key}/nodes accetta piu' id in una
chiamata sola, quindi bastano poche chiamate per file invece di una per nodo.

  python tools/map_components.py [--kb=PERCORSO]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "mappa-componenti.json"
RAPPORTO = ROOT / "docs" / "componenti-figma.md"
KB_PREDEFINITA = Path("C:/Users/simon/Downloads/ds-cross-app")
A_GRUPPI = 40


def candidati():
    """I file in cui cercare: prima i semi, poi le librerie note dal censimento."""
    ordine = []
    cfg = json.loads((ROOT / "config" / "figma-files.json").read_text(encoding="utf-8"))
    for v in cfg["files"].values():
        ordine.append((v["fileKey"], v["name"]))

    inv = ROOT / "data" / "figma-inventory.json"
    if inv.exists():
        dati = json.loads(inv.read_text(encoding="utf-8"))
        for k, v in dati.get("files", {}).items():
            if k not in {x[0] for x in ordine}:
                ordine.append((k, v.get("name") or k))
    return ordine


def leggi_kb(kb: Path):
    """Slug -> {piattaforma: nodeId} dai metadata.json della knowledge base."""
    fuori = {}
    base = kb / "components"
    if not base.exists():
        return fuori
    for cartella in sorted(p for p in base.iterdir() if p.is_dir()):
        f = cartella / "docs" / "metadata.json"
        if not f.exists():
            continue
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        nodi = {k: v for k, v in (m.get("figmaNodeIds") or {}).items() if isinstance(v, str)}
        fuori[cartella.name] = {
            "nodi": nodi,
            "nome": (m.get("component") or {}).get("name") or cartella.name,
            "stato": m.get("status"),
        }
    return fuori


def main(argv):
    kb = KB_PREDEFINITA
    for a in argv:
        if a.startswith("--kb="):
            kb = Path(a.split("=", 1)[1])

    componenti = leggi_kb(kb)
    if not componenti:
        print(f"\n  Nessun metadata.json trovato in {kb / 'components'}\n")
        return 1

    # tutti i nodi distinti, e chi li reclama
    reclami = {}
    for slug, c in componenti.items():
        for piattaforma, nodo in c["nodi"].items():
            reclami.setdefault(nodo.replace("-", ":"), []).append((slug, piattaforma))

    nodi = sorted(reclami)
    files = candidati()
    print(f"\n  {len(componenti)} componenti · {len(nodi)} nodi distinti · {len(files)} file candidati\n")

    f = Figma()
    # nodo -> [(fileKey, nomeFile, nomeNodo, tipo)]
    dove = {n: [] for n in nodi}

    for chiave, nome_file in files:
        trovati = 0
        for i in range(0, len(nodi), A_GRUPPI):
            gruppo = nodi[i : i + A_GRUPPI]
            dati, err = f.prova(f"files/{chiave}/nodes?ids={','.join(gruppo)}")
            if err:
                print(f"    ✖ {nome_file}: {err}")
                break
            for nodo_id, voce in (dati.get("nodes") or {}).items():
                if not voce or not voce.get("document"):
                    continue
                doc = voce["document"]
                dove[nodo_id].append(
                    {"fileKey": chiave, "file": nome_file, "nodo": doc.get("name"), "tipo": doc.get("type")}
                )
                trovati += 1
        print(f"    {trovati:>4} nodi risolti in  {nome_file}")

    # ── esito per componente ─────────────────────────────────────────────────
    esiti = {}
    for slug, c in sorted(componenti.items()):
        per_piattaforma = {}
        for piattaforma, nodo in c["nodi"].items():
            n = nodo.replace("-", ":")
            per_piattaforma[piattaforma] = {"nodeId": n, "trovatoIn": dove.get(n, [])}
        risolti = [p for p, v in per_piattaforma.items() if v["trovatoIn"]]
        ambigui = [p for p, v in per_piattaforma.items() if len(v["trovatoIn"]) > 1]
        totali = len(per_piattaforma)
        if totali == 0:
            classe = "senza nodi"       # il metadata non dichiara alcun nodo
        elif len(risolti) == totali:
            classe = "completo"
        elif len(risolti) == 0:
            classe = "irrisolto"        # nodi dichiarati, nessuno risponde
        else:
            classe = "parziale"
        esiti[slug] = {
            "nome": c["nome"],
            "stato": c["stato"],
            "piattaforme": per_piattaforma,
            "risolte": len(risolti),
            "totali": totali,
            "classe": classe,
            "ambiguo": bool(ambigui),
        }

    # quali file servono davvero ai componenti documentati
    uso = {}
    for e in esiti.values():
        for v in e["piattaforme"].values():
            for t in v["trovatoIn"]:
                uso.setdefault(t["fileKey"], {"file": t["file"], "nodi": 0})["nodi"] += 1

    scrivi_json(USCITA, {"componenti": esiti, "fileUsati": uso, "totali": {
        "componenti": len(esiti),
        "nodiDistinti": len(nodi),
        "completi": sum(1 for e in esiti.values() if e["classe"] == "completo"),
        "parziali": sum(1 for e in esiti.values() if e["classe"] == "parziale"),
        "senzaNodi": sum(1 for e in esiti.values() if e["classe"] == "senza nodi"),
        "irrisolti": sum(1 for e in esiti.values() if e["classe"] == "irrisolto"),
        "ambigui": sum(1 for e in esiti.values() if e["ambiguo"]),
        "chiamate": f.chiamate,
    }})

    # ── rapporto leggibile ───────────────────────────────────────────────────
    completi = [s for s, e in esiti.items() if e["classe"] == "completo"]
    parziali = [s for s, e in esiti.items() if e["classe"] == "parziale"]
    senza = [s for s, e in esiti.items() if e["classe"] == "senza nodi"]
    irrisolti = [s for s, e in esiti.items() if e["classe"] == "irrisolto"]
    ambigui = [s for s, e in esiti.items() if e["ambiguo"]]

    r = [
        "# Componenti documentati e nodi Figma",
        "",
        f"Mappatura dei {len(esiti)} componenti di `ds-cross-app` sui nodi Figma reali.",
        "",
        "I `metadata.json` dichiarano gli identificativi dei nodi ma non il file che",
        "li contiene, e l'identificativo da solo non basta a dedurlo: i file",
        "condividono gli id. Qui ogni nodo e' stato cercato in tutti i file candidati.",
        "",
        "## Esito",
        "",
        "| | Componenti |",
        "|---|---|",
        f"| risolti su tutte le piattaforme | {len(completi)} |",
        f"| risolti solo in parte | {len(parziali)} |",
        f"| non risolti (nodi dichiarati, nessuno risponde) | {len(irrisolti)} |",
        f"| senza nodi dichiarati nel metadata | {len(senza)} |",
        f"| ambigui (lo stesso nodo in piu' file) | {len(ambigui)} |",
        "",
        "## File Figma effettivamente usati dai componenti documentati",
        "",
        "| File | Nodi |",
        "|---|---|",
    ]
    for k, v in sorted(uso.items(), key=lambda x: -x[1]["nodi"]):
        r.append(f"| {v['file']} | {v['nodi']} |")

    if irrisolti:
        r += ["", "## Non risolti", "",
              "Il nodo dichiarato non risponde in nessun file candidato: e' stato",
              "spostato, cancellato, oppure vive in un file che non abbiamo.", ""]
        for s in irrisolti:
            nodi_s = ", ".join(v["nodeId"] for v in esiti[s]["piattaforme"].values())
            r.append(f"- **{esiti[s]['nome']}** (`{s}`) · {nodi_s}")

    if ambigui:
        r += ["", "## Ambigui", "",
              "Lo stesso identificativo risponde in piu' file, con componenti diversi.", ""]
        for s in ambigui:
            r.append(f"- **{esiti[s]['nome']}** (`{s}`)")
            for p, v in esiti[s]["piattaforme"].items():
                if len(v["trovatoIn"]) > 1:
                    for t in v["trovatoIn"]:
                        r.append(f"  - {p} · `{v['nodeId']}` → «{t['nodo']}» in {t['file']}")

    r += ["", "## Tutti i componenti", ""]
    for s, e in sorted(esiti.items()):
        primo = next((t for v in e["piattaforme"].values() for t in v["trovatoIn"]), None)
        dove_txt = primo["file"] if primo else "⚠️ non risolto"
        r.append(f"- **{e['nome']}** (`{s}`) · {e['risolte']}/{e['totali']} piattaforme · {dove_txt}")

    RAPPORTO.parent.mkdir(parents=True, exist_ok=True)
    RAPPORTO.write_text("\n".join(r) + "\n", encoding="utf-8")

    linea = "─" * 64
    print(f"\n{linea}")
    print(f"  componenti          {len(esiti)}")
    print(f"  risolti del tutto   {len(completi)}")
    print(f"  risolti in parte    {len(parziali)}")
    print(f"  non risolti         {len(irrisolti)}")
    print(f"  senza nodi          {len(senza)}")
    print(f"  ambigui             {len(ambigui)}")
    print(f"\n  FILE USATI DAI COMPONENTI DOCUMENTATI")
    for k, v in sorted(uso.items(), key=lambda x: -x[1]["nodi"]):
        print(f"    {v['nodi']:>4} nodi  {v['file']}")
    print(f"\n  chiamate API {f.chiamate}")
    print(f"  scritto data/{USCITA.name}")
    print(f"          docs/{RAPPORTO.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
