#!/usr/bin/env python3
"""
Scopre i file Figma seguendo i riferimenti fra componenti.

Serve perche' l'inventario dei team vede solo i progetti accessibili: DS B2B
sta in un progetto negato e non comparirebbe. Qui si parte dai file noti, si
legge il manifest dei componenti e per ogni chiave si risale al file d'origine
con /v1/components/{key}.

Il risultato e' un grafo: chi dipende da chi, e tramite quale componente.

  python tools/discover_files.py [--depth=N] [fileKey ...]
"""
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "figma-inventory.json"


def main(argv: list[str]) -> int:
    salti_max = 3
    for a in argv:
        if a.startswith("--depth="):
            salti_max = int(a.split("=")[1])
    semi = [a for a in argv if not a.startswith("--")]
    if not semi:
        cfg = json.loads((ROOT / "config" / "figma-files.json").read_text(encoding="utf-8"))
        semi = [v["fileKey"] for v in cfg["files"].values()]

    f = Figma()
    files: dict[str, dict] = {}
    archi: list[dict] = []
    coda = deque((k, 0) for k in semi)
    visti = set(semi)

    print(f"\n  semi: {len(semi)}   profondità massima: {salti_max}\n")

    while coda:
        chiave, salto = coda.popleft()
        meta, err = f.prova(f"files/{chiave}?depth=1")
        nome = f"({err})" if err else meta.get("name", "?")
        files[chiave] = {
            "name": nome,
            "lastModified": None if err else meta.get("lastModified"),
            "hop": salto,
            "role": "seme" if salto == 0 else "libreria",
        }
        print(f"{'  ' * salto}▸ {nome}   {chiave}")
        if err or salto >= salti_max:
            continue

        # il manifest dei componenti richiede depth>=3: con depth=1 e' vuoto
        albero, err = f.prova(f"files/{chiave}?depth=3")
        if err:
            print(f"{'  ' * salto}    ✖ manifest: {err}")
            continue

        comps = {}
        for sorgente in ("components", "componentSets"):
            for nodo_id, c in (albero.get(sorgente) or {}).items():
                if c.get("key"):
                    comps[c["key"]] = c.get("name", "")

        print(f"{'  ' * salto}    {len(comps)} componenti da risolvere… ", end="", flush=True)

        def risolvi(item):
            ck, cnome = item
            r, e = f.prova(f"components/{ck}")
            if e or not r:
                return None
            fk = (r.get("meta") or {}).get("file_key")
            return None if not fk or fk == chiave else (fk, ck, cnome)

        trovati: dict[str, int] = {}
        for esito in f.in_parallelo(list(comps.items()), risolvi):
            if not esito:
                continue
            fk, ck, cnome = esito
            trovati[fk] = trovati.get(fk, 0) + 1
            archi.append({"from": chiave, "to": fk, "componentKey": ck, "componentName": cnome})

        print(f"{len(trovati)} file collegati")
        for fk in trovati:
            if fk not in visti:
                visti.add(fk)
                coda.append((fk, salto + 1))

    inventario = {
        "seeds": semi,
        "maxHops": salti_max,
        "files": files,
        "edges": sorted(archi, key=lambda e: (e["from"], e["to"], e["componentKey"])),
        "totals": {"files": len(files), "edges": len(archi), "apiCalls": f.chiamate},
    }
    scrivi_json(USCITA, inventario)

    linea = "─" * 66
    print(f"\n{linea}")
    print(f"  file scoperti  {len(files)}")
    print(f"  collegamenti   {len(archi)}")
    print(f"  chiamate API   {f.chiamate}")
    for k, v in sorted(files.items(), key=lambda x: x[1]["hop"]):
        print(f"   {v['hop']}  {v['name'][:34]:<34}  {k}")
    print(f"\n  scritto data/{USCITA.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
