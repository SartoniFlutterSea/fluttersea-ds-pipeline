#!/usr/bin/env python3
"""
Elenca i file Figma partendo dagli identificativi dei team.

L'API non ha un endpoint "tutti i miei file": il percorso obbligato e'
  team -> /v1/teams/{id}/projects -> /v1/projects/{id}/files
e i team non sono ricavabili dall'API, stanno nell'URL di Figma.

Attenzione: un progetto vuoto e un progetto a cui non si ha accesso
restituiscono entrambi una lista vuota. L'API non li distingue.

  python tools/list_files.py <teamId> [<teamId> ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "figma-teams-inventory.json"


def main(team_ids: list[str]) -> int:
    if not team_ids:
        print(
            "\n  Serve almeno un identificativo di team.\n"
            "    python tools/list_files.py <teamId> [<teamId> ...]\n\n"
            "  Dove trovarlo: apri il team su Figma e guarda l'URL.\n"
            "    https://www.figma.com/files/<org>/team/1234567890123456789\n"
            "                                          ^^^^^^^^^^^^^^^^^^^\n"
        )
        return 1

    f = Figma()
    inventario = {"teams": [], "totals": {"projects": 0, "files": 0}, "errors": []}

    for tid in team_ids:
        print(f"\n▸ team {tid}  ", end="")
        dati, err = f.prova(f"teams/{tid}/projects")
        if err:
            print(f"✖ {err}")
            inventario["errors"].append({"teamId": tid, "error": err})
            continue

        nome = dati.get("name") or "—"
        progetti = dati.get("projects") or []
        print(f'"{nome}"  ·  {len(progetti)} progetti')
        team = {"id": tid, "name": nome, "projects": []}

        for p in progetti:
            fl, err = f.prova(f"projects/{p['id']}/files")
            if err:
                print(f"    ✖ progetto {p['name']}: {err}")
                inventario["errors"].append({"projectId": p["id"], "name": p["name"], "error": err})
                continue
            files = [
                {"key": x["key"], "name": x["name"], "lastModified": x.get("last_modified")}
                for x in (fl.get("files") or [])
            ]
            team["projects"].append({"id": p["id"], "name": p["name"], "files": files})
            inventario["totals"]["projects"] += 1
            inventario["totals"]["files"] += len(files)
            print(f"    {len(files):>3} file  {p['name']}")

        inventario["teams"].append(team)

    scrivi_json(USCITA, inventario)
    linea = "─" * 64
    print(f"\n{linea}")
    print(f"  team {len(inventario['teams'])} · progetti {inventario['totals']['projects']} · file {inventario['totals']['files']}")
    if inventario["errors"]:
        print(f"  ⚠️  {len(inventario['errors'])} errori, registrati nell'inventario")
    print(f"  chiamate API {f.chiamate}")
    print(f"  scritto data/{USCITA.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main([a for a in sys.argv[1:] if not a.startswith("--")]))
