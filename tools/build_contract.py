#!/usr/bin/env python3
"""
Livello 2 — contratto di componente, estratto da Figma.

La sorgente e' la property table reale piu' la geometria dei nodi, non la PROSA
della descrizione: ricavare gli assi dal testo sbagliava default e ordine.

Due principi:
 · OUTPUT CANONICO — chiavi ordinate, float arrotondati, nessun timestamp
   dentro l'artefatto: ogni diff e' un cambiamento vero, mai rumore.
 · NON PROMETTE PIU' DI QUANTO HA MISURATO — ogni sezione dichiara su quante
   varianti e' stata verificata.

Il file Figma NON e' scritto qui dentro: i due DS condividono gli id dei nodi,
quindi lo stesso nodeId su file diversi restituisce componenti diversi. Il ds
va indicato, e un controllo verifica che il nodo sia quello atteso.

  python tools/build_contract.py <slug> <nodeId> [ds] [--forza]
  python tools/build_contract.py button 5473-10855 b2c
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402
from _guardia import verifica_nodo  # noqa: E402

USCITA = ROOT / "data" / "contracts"


def arrotonda(n):
    """
    Come `Math.round(n*100)/100` in JavaScript, che scrive 40 e non 40.0.
    Serve perche' gli artefatti gia' prodotti vanno riprodotti identici.
    """
    if not isinstance(n, (int, float)) or isinstance(n, bool):
        return n
    v = round(float(n) * 100) / 100
    return int(v) if float(v).is_integer() else v


def pulisci(nome: str) -> str:
    """«Show left icon#5615:73» → «Show left icon»"""
    return str(nome).split("#")[0].strip()


def camel(nome: str) -> str:
    parti = [p for p in re.split(r"[\s_-]+", pulisci(nome)) if p]
    if not parti:
        return ""
    return parti[0].lower() + "".join(p[0].upper() + p[1:] for p in parti[1:])


def combinazione(nome: str) -> dict:
    """«Size=md, State=Default» → {Size: md, State: Default}"""
    fuori = {}
    for pezzo in str(nome).split(","):
        parti = [x.strip() for x in pezzo.split("=")]
        if len(parti) == 2:
            fuori[parti[0]] = parti[1]
    return fuori


def ordina(o):
    """Forma canonica: chiavi in ordine, ricorsivo. Gli array mantengono l'ordine."""
    if isinstance(o, list):
        return [ordina(x) for x in o]
    if isinstance(o, dict):
        return {k: ordina(o[k]) for k in sorted(o)}
    return o


def superfici(nodo, nome_var):
    """I colori legati a variabili: sfondo, bordo, testo, icona."""
    fuori = {}
    bv = nodo.get("boundVariables") or {}
    fills = nodo.get("fills") or []
    strokes = nodo.get("strokes") or []
    riempimento = ((fills[0] if fills else {}).get("boundVariables") or {}).get("color", {}).get("id")
    bordo = ((strokes[0] if strokes else {}).get("boundVariables") or {}).get("color", {}).get("id")
    if riempimento:
        fuori["bg"] = nome_var(riempimento)
    if bordo:
        fuori["border"] = nome_var(bordo)

    def scendi(n):
        for c in n.get("children") or []:
            cf = ((c.get("fills") or [{}])[0].get("boundVariables") or {}).get("color", {}).get("id")
            if cf:
                if c.get("type") == "TEXT" and "text" not in fuori:
                    fuori["text"] = nome_var(cf)
                elif "icon" not in fuori:
                    fuori["icon"] = nome_var(cf)
            scendi(c)

    scendi(nodo)
    if bv.get("strokeWeight"):
        fuori["_borderWidth"] = nome_var(bv["strokeWeight"]["id"])
    return fuori


def geometria(nodo, nome_var):
    """Spaziature e raggi legati a variabili, piu' l'altezza misurata."""
    bv = nodo.get("boundVariables") or {}
    g = {}
    mappa = {"paddingTop": "paddingVertical", "paddingLeft": "paddingHorizontal",
             "itemSpacing": "gap", "strokeWeight": "borderWidth"}
    for k, etichetta in mappa.items():
        if bv.get(k):
            g[etichetta] = nome_var(bv[k]["id"])
    raggio = bv.get("topLeftRadius") or bv.get("bottomLeftRadius")
    if raggio:
        g["borderRadius"] = nome_var(raggio["id"])
    riquadro = nodo.get("absoluteBoundingBox") or {}
    g["_measured"] = {"height": arrotonda(riquadro.get("height")), "layout": nodo.get("layoutMode")}
    return g


def main(argv):
    slug = next((a for a in argv if not a.startswith("--")), "button")
    resto = [a for a in argv if not a.startswith("--")]
    node_id = resto[1] if len(resto) > 1 else "5473-10855"
    cfg = json.loads((ROOT / "config" / "figma-files.json").read_text(encoding="utf-8"))
    ds = resto[2] if len(resto) > 2 else cfg["default"]
    if ds not in cfg["files"]:
        sys.exit(f'\n  ✖ ds sconosciuto: "{ds}" — attesi: {", ".join(cfg["files"])}\n')
    chiave_file = cfg["files"][ds]["fileKey"]

    f = Figma()

    # variabileId → nome, per tradurre i boundVariables
    vmeta = f.get(f"files/{chiave_file}/variables/local")["meta"]
    variabili = vmeta.get("variables") or {}
    nome_var = lambda i: (variabili.get(i) or {}).get("name")  # noqa: E731

    nodi = f.get(f"files/{chiave_file}/nodes?ids={node_id}")
    doc = list(nodi["nodes"].values())[0]["document"]
    verifica_nodo(slug, doc.get("name"), ds=ds, node_id=node_id, forza="--forza" in argv)
    varianti = doc.get("children") or []

    # ── 1. Assi: dalla property table, non dalla prosa ──────────────────────
    defs = doc.get("componentPropertyDefinitions") or {}
    assi, booleani, testi, scambi = [], [], [], []
    for nome_grezzo, d in defs.items():
        voce = {"figmaProperty": pulisci(nome_grezzo), "name": camel(nome_grezzo)}
        if d.get("type") == "VARIANT":
            assi.append({**voce, "values": sorted(d.get("variantOptions") or [])})
        elif d.get("type") == "BOOLEAN":
            booleani.append({**voce, "default": d.get("defaultValue")})
        elif d.get("type") == "TEXT":
            testi.append({**voce, "default": d.get("defaultValue")})
        else:
            scambi.append({**voce, "type": d.get("type")})

    # ── 2. Il default: la PRIMA variante del set e' il riferimento di Figma ──
    prima = combinazione(varianti[0]["name"]) if varianti else {}

    trova = lambda r: next((a for a in assi if re.search(r, a["name"], re.I)), None)  # noqa: E731
    asse_size = trova("size")
    asse_aspetto = trova("appear")
    asse_gerarchia = trova("hierarch")
    asse_stato = trova("state")

    # ── 3. Sizing e token: dai boundVariables dei nodi variante ─────────────
    sizing, token = {}, {}
    da_size = da_token = 0
    for v in varianti:
        combo = combinazione(v.get("name", ""))
        sz = combo.get(asse_size["figmaProperty"]) if asse_size else None
        if sz and sz not in sizing:
            sizing[sz] = geometria(v, nome_var)
            da_size += 1

        if asse_aspetto and asse_gerarchia and asse_stato:
            a = combo.get(asse_aspetto["figmaProperty"])
            g = combo.get(asse_gerarchia["figmaProperty"])
            st = combo.get(asse_stato["figmaProperty"])
            if a is None or g is None or not st:
                continue
            # solo dalla size di riferimento, per non moltiplicare
            if asse_size and combo.get(asse_size["figmaProperty"]) != prima.get(asse_size["figmaProperty"]):
                continue
            token.setdefault(f"{a}/{g}", {})[st] = superfici(v, nome_var)
            da_token += 1

    n_size = len(asse_size["values"]) if asse_size else 0
    combinazioni_attese = (
        (len(asse_aspetto["values"]) if asse_aspetto else 0)
        * (len(asse_gerarchia["values"]) if asse_gerarchia else 0)
        * (len(asse_stato["values"]) if asse_stato else 0)
    )

    contratto = {
        "id": f"ds.{slug}",
        "name": doc.get("name"),
        "source": {"ds": ds, "fileKey": chiave_file, "fileName": cfg["files"][ds]["name"],
                   "nodeId": node_id, "nodeType": doc.get("type")},
        "props": [{
            "name": a["name"],
            "figmaProperty": a["figmaProperty"],
            "values": a["values"],
            "default": prima.get(a["figmaProperty"]),
            "_source": {"values": "figma", "order": "figma-alphabetical", "default": "figma-first-variant"},
        } for a in assi],
        "booleans": booleani, "texts": testi, "swaps": scambi,
        "sizing": sizing, "tokens": token,
        "_coverage": {
            "variants": len(varianti),
            "sizingMeasuredOn": f"{da_size}/{n_size} size",
            "tokensMeasuredOn": f"{da_token} combinazioni su {combinazioni_attese}",
            "note": "I token sono misurati sulla sola size di riferimento: le superfici non variano con la size.",
        },
    }

    cartella = USCITA / slug
    cartella.mkdir(parents=True, exist_ok=True)
    scrivi_json(cartella / "contract.json", ordina(contratto))

    L = "─" * 70
    print(f"\n{L}\n  CONTRATTO da Figma — {doc.get('name')}\n{L}")
    print(f"\n▸ NODO      {doc.get('type')} · {len(varianti)} varianti")
    print("\n▸ ASSI      (dalla property table, non dalla prosa)")
    for a in assi:
        print(f"   {a['name']:<12} figma=\"{a['figmaProperty']}\"  default={prima.get(a['figmaProperty']) or '—'}")
        print(f"      {' | '.join(a['values'])}")
    if booleani:
        print("\n▸ BOOLEAN   " + ", ".join(f"{b['name']}={b['default']}" for b in booleani))
    if testi:
        print("▸ TEXT      " + ", ".join(f"{t['name']}=\"{t['default']}\"" for t in testi))
    if scambi:
        print("▸ SWAP      " + ", ".join(s["name"] for s in scambi))
    print(f"\n▸ SIZING    {', '.join(sizing)}")
    for k, g in sizing.items():
        legami = " · ".join(f"{x}={t}" for x, t in g.items() if not x.startswith("_")) or "(nessun binding)"
        print(f"   {k}: {legami}  [h={g['_measured']['height']}]")
    print(f"\n▸ TOKEN     {len(token)} combinazioni appearance/hierarchy")
    print(f"\n▸ COPERTURA {json.dumps(contratto['_coverage'], ensure_ascii=False)}")
    print(f"\n✅ scritto data/contracts/{slug}/contract.json\n{L}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
