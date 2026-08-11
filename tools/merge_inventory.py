#!/usr/bin/env python3
"""
Unisce i due censimenti. Nessuno dei due basta da solo: l'inventario dei team
non vede i progetti negati, il crawler non vede i file scollegati.
Registra anche COME ogni file e' stato visto.

  python tools/merge_inventory.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "figma-censimento.json"


def leggi(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    T = leggi(ROOT / "data" / "figma-teams-inventory.json")
    R = leggi(ROOT / "data" / "figma-inventory.json")
    if not T and not R:
        print("\n  ✖ nessun censimento da unire. Eseguire prima list_files e discover_files.\n")
        return 1

    files: dict[str, dict] = {}

    for t in (T or {}).get("teams", []):
        for p in t["projects"]:
            for f in p["files"]:
                v = files.setdefault(f["key"], {"key": f["key"], "visto": []})
                v.update(nome=f["name"], team=t["name"], progetto=p["name"],
                         lastModified=f.get("lastModified"))
                v["visto"].append("progetto")

    for k, f in (R or {}).get("files", {}).items():
        v = files.setdefault(k, {"key": k, "visto": []})
        v.setdefault("nome", f.get("name"))
        v.setdefault("lastModified", f.get("lastModified"))
        v["dipendenza"] = "seme" if f.get("hop") == 0 else "libreria"
        v["visto"].append("riferimento")

    solo_rif = [f for f in files.values() if "progetto" not in f["visto"]]
    out = {
        "totali": {
            "file": len(files),
            "daProgetti": sum("progetto" in f["visto"] for f in files.values()),
            "daRiferimenti": sum("riferimento" in f["visto"] for f in files.values()),
            "soloRiferimenti": len(solo_rif),
        },
        "progettiNegati": [{"progetto": e.get("name") or e.get("teamId"), "errore": e["error"]}
                           for e in (T or {}).get("errors", [])],
        "files": files,
    }
    scrivi_json(USCITA, out)

    linea = "─" * 62
    print(f"\n{linea}")
    for k, v in out["totali"].items():
        print(f"  {k:<20} {v}")
    for f in solo_rif:
        print(f"     {(f.get('nome') or '?')[:32]:<32}{f['key']}   ← invisibile nei progetti")
    for p in out["progettiNegati"]:
        print(f"     {p['progetto']}  {p['errore']}")
    print(f"\n  scritto data/{USCITA.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
