#!/usr/bin/env python3
"""
Elenca i file Figma partendo dagli identificativi dei team.

L'API non ha un endpoint "tutti i miei file": il percorso obbligato e'
  team -> /v1/teams/{id}/projects -> /v1/projects/{id}/files
e i team non sono ricavabili dall'API, stanno nell'URL di Figma.

Attenzione: un progetto vuoto e un progetto a cui non si ha accesso
restituiscono entrambi una lista vuota. L'API non li distingue.

  python tools/list_files.py <teamId> [<teamId> ...]
  python tools/list_files.py --progetto=<projectId> [...]

Il secondo serve quando si conosce l'URL di un progetto ma non il team che lo
contiene: e' il caso di DS B2B, che vive in un progetto di commessa fuori dal
workspace dei design system.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "figma-teams-inventory.json"


def main(argv: list[str]) -> int:
    team_ids = [a for a in argv if not a.startswith("--")]
    progetti_sciolti = [a.split("=", 1)[1] for a in argv if a.startswith("--progetto=")]
    if not team_ids and not progetti_sciolti:
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

    # Progetti indicati direttamente, senza passare dal team.
    if progetti_sciolti:
        sciolti = {"id": None, "name": "(progetti indicati a mano)", "projects": []}
        for pid in progetti_sciolti:
            fl, err = f.prova(f"projects/{pid}/files")
            if err:
                print()
                print(f"▸ progetto {pid}  ✖ {err}")
                inventario["errors"].append({"projectId": pid, "error": err})
                continue
            files = [
                {"key": x["key"], "name": x["name"], "lastModified": x.get("last_modified")}
                for x in (fl.get("files") or [])
            ]
            nome = fl.get("name") or pid
            sciolti["projects"].append({"id": pid, "name": nome, "files": files})
            inventario["totals"]["projects"] += 1
            inventario["totals"]["files"] += len(files)
            print()
            print(f"▸ progetto {pid}  \"{nome}\"  ·  {len(files)} file")
        if sciolti["projects"]:
            inventario["teams"].append(sciolti)

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
    raise SystemExit(main(sys.argv[1:]))
