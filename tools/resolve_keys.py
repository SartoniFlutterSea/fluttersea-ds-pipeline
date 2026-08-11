#!/usr/bin/env python3
"""
Risolve le chiavi di componente che l'indice non conosce, e scopre i file da
cui vengono.

PERCHE' SERVE
L'indice copre i file del censimento. Ma il manifest di Cross App dichiara 507
componenti `remote=True`, e 315 hanno chiavi che nessun file censito pubblica:
vengono da librerie che non abbiamo mai visto. `/v1/components/{key}` restituisce
`meta.file_key`, quindi ogni chiave ignota e' un indizio verso un file nuovo.

E' lo stesso meccanismo di discover_files, ma applicato alle chiavi rimaste
scoperte invece che a tutti i componenti: molte meno chiamate, e mirate.

CACHE
`chiave -> file` non cambia mai. Si salva su disco e si riusa: la seconda
esecuzione non ripete nulla.

  python tools/resolve_keys.py [--quanti=N]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

CARTELLA = ROOT / "data" / "grafo"
CACHE = CARTELLA / "cache-chiavi.json"


def chiavi_irrisolte() -> dict[str, list[str]]:
    """Chiave -> i file che la citano, dai grafi gia' prodotti."""
    fuori: dict[str, list[str]] = {}
    d = CARTELLA / "file"
    if not d.exists():
        return fuori
    for p in sorted(d.glob("*.json")):
        g = json.loads(p.read_text(encoding="utf-8"))
        for x in g.get("irrisolti") or []:
            if x.get("tipo") == "componente" and x.get("chiave"):
                fuori.setdefault(x["chiave"], []).append(g["fileKey"])
    return fuori


def main(argv):
    quanti = 3
    for a in argv:
        if a.startswith("--quanti="):
            quanti = int(a.split("=")[1])

    cache = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text(encoding="utf-8")).get("chiavi", {})
        except (OSError, json.JSONDecodeError):
            cache = {}

    tutte = chiavi_irrisolte()
    mancanti = [k for k in tutte if k not in cache]
    print(f"\n  {len(tutte)} chiavi irrisolte · {len(cache)} già in cache · {len(mancanti)} da risolvere\n")
    if not mancanti:
        print("  Nulla da fare.\n")
        return 0

    f = Figma()
    fatti = [0]

    def risolvi(chiave):
        r, err = f.prova(f"components/{chiave}")
        fatti[0] += 1
        if fatti[0] % 25 == 0:
            print(f"    {fatti[0]}/{len(mancanti)}...", flush=True)
        if err:
            return chiave, {"errore": err}
        meta = r.get("meta") or {}
        return chiave, {
            "file": meta.get("file_key"),
            "nodeId": meta.get("node_id"),
            "nome": meta.get("name"),
        }

    cache.update(dict(f.in_parallelo(mancanti, risolvi, quanti)))

    # ── quali file emergono ──────────────────────────────────────────────────
    indice = json.loads((CARTELLA / "indice.json").read_text(encoding="utf-8"))
    noti = set(indice.get("files") or {})
    nuovi: dict[str, int] = {}
    errori = 0
    for k, v in cache.items():
        if v.get("errore"):
            errori += 1
            continue
        fk = v.get("file")
        if fk and fk not in noti:
            nuovi[fk] = nuovi.get(fk, 0) + 1

    scrivi_json(CACHE, {
        "totali": {"chiavi": len(cache), "fileNuovi": len(nuovi), "errori": errori},
        "fileNuovi": nuovi,
        "chiavi": cache,
    })

    linea = "─" * 64
    print(f"\n{linea}")
    print(f"  chiavi risolte      {len(cache) - errori}")
    print(f"  non risolvibili     {errori}")
    print(f"\n  FILE MAI VISTI PRIMA: {len(nuovi)}")
    if nuovi:
        g = Figma()
        for fk, quante in sorted(nuovi.items(), key=lambda x: -x[1]):
            meta, err = g.prova(f"files/{fk}?depth=1")
            nome = f"({err})" if err else meta.get("name")
            print(f"    {quante:>4} componenti  {str(nome)[:40]:<42}{fk}")
    print(f"\n  chiamate API {f.chiamate}")
    print(f"  scritto data/grafo/{CACHE.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
