#!/usr/bin/env python3
"""
Livello 2 — figma.json: l'ANCORAGGIO.

E' l'input dell'estrazione, non il suo output: serve per sapere cosa andare a
prendere. Per questo e' un file a se' e non un blocco dentro contract.json:
cambia solo quando un nodo si sposta, mentre il contratto cambia a ogni
pubblicazione.

Censisce anche i frame di documentazione presenti nel file.

⚠️ La ricerca dei frame usa `depth=3`, che e' una trappola nota: la
documentazione piu' annidata non viene vista, e il risultato sembra «nessuna
documentazione» invece di «non ho cercato abbastanza». Il censimento vero lo fa
`classify_pages.py`; qui il dato resta come indicazione, non come misura.

  python tools/build_anchor.py <slug> <nodeId> [ds] [--forza]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402
from _guardia import verifica_nodo  # noqa: E402

USCITA = ROOT / "data" / "contracts"

DOC_RE = re.compile(r"purpose|usage|behavior|behaviour|anatomy|do\s*&|don'?t|guideline|spec|documentation|linee guida", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u25A0-\u25FF]")


def main(argv):
    resto = [a for a in argv if not a.startswith("--")]
    slug = resto[0] if resto else "button"
    node_id = resto[1] if len(resto) > 1 else "5473-10855"
    cfg = json.loads((ROOT / "config" / "figma-files.json").read_text(encoding="utf-8"))
    ds = resto[2] if len(resto) > 2 else cfg["default"]
    if ds not in cfg["files"]:
        sys.exit(f'\n  ✖ ds sconosciuto: "{ds}" — attesi: {", ".join(cfg["files"])}\n')
    chiave_file = cfg["files"][ds]["fileKey"]

    # Su B2C un componente ha un nodo per piattaforma: si leggono dal metadata
    # della knowledge base, se esiste. Su B2B la piattaforma e' una sola.
    nodi_piattaforma = {"default": node_id}
    try:
        m = json.loads((Path("C:/Users/simon/Downloads/ds-cross-app") / "components" / slug
                        / "docs" / "metadata.json").read_text(encoding="utf-8"))
        if m.get("figmaNodeIds") and ds == "b2c":
            plat = {k: v for k, v in m["figmaNodeIds"].items() if k != "propertyTable"}
            if plat:
                nodi_piattaforma = plat
    except (OSError, json.JSONDecodeError):
        pass

    f = Figma()
    nodi = f.get(f"files/{chiave_file}/nodes?ids={node_id}")
    doc = list(nodi["nodes"].values())[0]["document"]
    verifica_nodo(slug, doc.get("name"), ds=ds, node_id=node_id, forza="--forza" in argv)

    file_meta = f.get(f"files/{chiave_file}?depth=3")
    canvases = (file_meta.get("document") or {}).get("children") or []

    per_pagina = []
    for c in canvases:
        colpi = []

        def scendi(ns):
            for n in ns or []:
                if DOC_RE.search(n.get("name") or ""):
                    colpi.append({"id": n.get("id"), "name": n.get("name"), "type": n.get("type")})
                scendi(n.get("children"))

        scendi(c.get("children"))
        per_pagina.append({"page": c.get("name"), "id": c.get("id"),
                           "children": len(c.get("children") or []), "docFrames": colpi})

    # ── lo stato, dal marcatore nel nome della pagina ────────────────────────
    stato_cfg = json.loads((ROOT / "config" / "figma-status.json").read_text(encoding="utf-8"))
    voluto = node_id.replace("-", ":")

    def contiene(c):
        trovato = [False]

        def w(ns):
            for n in ns or []:
                if n.get("id") == voluto:
                    trovato[0] = True
                w(n.get("children"))

        w(c.get("children"))
        return trovato[0]

    pagina = next((c for c in canvases if contiene(c)), None)
    if pagina is None:
        # depth=3 puo' non arrivare al nodo: si rilegge piu' a fondo
        profondo = f.get(f"files/{chiave_file}?depth=5")
        pagina = next((c for c in (profondo.get("document") or {}).get("children") or []
                       if contiene(c)), None)

    marcatore = ""
    if pagina:
        visti = []
        for m in EMOJI.findall(pagina.get("name") or ""):
            if m not in visti:
                visti.append(m)
        marcatore = "".join(visti)
    mappa = stato_cfg.get("b2b" if re.search(r"DS B2B", file_meta.get("name") or "") else "b2c") or {}

    ancoraggio = {
        "id": f"ds.{slug}",
        "fileKey": chiave_file,
        "fileName": file_meta.get("name"),
        "ds": ds,
        "nodes": nodi_piattaforma,
        "nodeType": doc.get("type"),
        "nodeName": doc.get("name"),
        "variantCount": len(doc.get("children") or []),
        "parts": {},
        "page": ({
            "id": pagina.get("id"),
            "name": pagina.get("name"),
            "label": EMOJI.sub("", pagina.get("name") or "").strip(),
            "marker": marcatore or None,
            "status": (mappa.get(marcatore, "unknown") if marcatore else None),
        } if pagina else None),
        "documentation": [{"page": p["page"], "frames": p["docFrames"]}
                          for p in per_pagina if p["docFrames"]],
        "lastModified": file_meta.get("lastModified"),
    }

    cartella = USCITA / slug
    cartella.mkdir(parents=True, exist_ok=True)
    scrivi_json(cartella / "figma.json", ancoraggio)

    L = "─" * 70
    print(f"\n{L}\n  ANCORAGGIO — {doc.get('name')}\n{L}")
    print(f'\n   file      "{file_meta.get("name")}"  {chiave_file}')
    print(f"   nodo      {node_id}  {doc.get('type')}  ·  {ancoraggio['variantCount']} varianti")
    print(f"   modificato {file_meta.get('lastModified')}")
    totale = sum(len(p["docFrames"]) for p in per_pagina)
    print(f"\n▸ PAGINE DEL FILE ({len(canvases)})   frame di doc trovati: {totale}")
    for p in per_pagina:
        if p["docFrames"]:
            print(f"   {len(p['docFrames']):>3} frame  {p['page']}")
    if not totale:
        print("   ⚠️  nessun frame con nomi tipo Purpose / Usage / Behavior / Anatomy")
    print(f"\n✅ scritto data/contracts/{slug}/figma.json\n{L}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
