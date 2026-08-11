#!/usr/bin/env python3
"""
Livello 2b — estrazione della documentazione dai frame Figma.

Ogni componente ha DUE frame affiancati, e servono entrambi:

  Purpose & Usage   perche' esiste, quando usarlo, anti-pattern di SCELTA
                    "Nome pattern" + "1.1 How and when to use it (Do)"
                    "1.N Anti-pattern (Don't)" -> Rule / Why it's wrong / Use instead

  Behavior          come si comporta, anti-pattern di COMPOSIZIONE
                    "template behavior" + le sezioni per piattaforma:
                    Interactive elements / Position / Animation / Size /
                    Conditional logic / Copy & truncation
                    piu' coppie Do / Don't con mockup e didascalia

TRE ACCORGIMENTI, ognuno costato un errore trovato sul campo:

 1. gli APOSTROFI vanno normalizzati: Figma usa quello tipografico (U+2019) e
    un confronto letterale su "Don't" fallisce in silenzio;

 2. sotto UNA intestazione di anti-pattern possono stare PIU' terzine
    Rule / Why it's wrong / Use instead. La prima versione ne leggeva una
    sola, e su Button Icon trovava 1 anti-pattern invece di 8;

 3. la DIDASCALIA di un Do/Don't sta a profondita' MINORE del mockup: e' il
    solo modo per non confondere la spiegazione col testo finto dentro lo
    screenshot. Cercarla per posizione fissa non funziona.

  python tools/extract_docs.py <slug> [pagina]
  python tools/extract_docs.py button Button
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "contracts"
B2C = "QWM2EhgZmv2KKcqI0315fx"

# Figma usa l'apostrofo tipografico, il codice quello dritto.
AP = re.compile("[\u2018\u2019\u02BC\u00B4`]")
norm = lambda s: AP.sub("'", s or "")                                   # noqa: E731
chiave = lambda s: re.sub(r"[^a-z0-9]", "", norm(s).lower())            # noqa: E731

HEAD_DO = re.compile(r"^\d+\.\d+\s+How and when to use it", re.I)
HEAD_ANTI = re.compile(r"^\d+\.\d+\s+Anti-pattern", re.I)
USED_IN = re.compile(r"^In which component", re.I)
ETICHETTE = {"rule": "scenario", "why it's wrong": "reason", "use instead": "alternative"}

SPEC = re.compile(r"^(Interactive elements|Position|Animation|Size|Conditional logic|"
                  r"Copy & truncation|Copy|States?)\s*:?$", re.I)
PIATTAFORMA = re.compile(r"^(iOS Liquid Glass|iOS / Android|iOS|Android|Mobile|Desktop)([\s/]|$)", re.I)
E_DO = lambda s: re.match(r"^do$", s, re.I) is not None                 # noqa: E731
E_DONT = lambda s: re.match(r"^don'?t$", s, re.I) is not None           # noqa: E731


def trova_per_nome(radice, regex):
    """Il primo nodo il cui nome combacia."""
    trovato = [None]

    def w(n):
        if trovato[0] is not None:
            return
        if regex.search(n.get("name") or ""):
            trovato[0] = n
            return
        for c in n.get("children") or []:
            w(c)

    w(radice)
    return trovato[0]


def primo_testo(nodo):
    trovato = [None]

    def w(n):
        if trovato[0] is not None:
            return
        if n.get("type") == "TEXT" and (n.get("characters") or "").strip():
            trovato[0] = n["characters"].strip()
            return
        for c in n.get("children") or []:
            w(c)

    w(nodo or {})
    return trovato[0]


def testi(radice):
    """TEXT con la PROFONDITA': serve a separare didascalia e mockup."""
    fuori = []

    def w(n, d):
        if n.get("type") == "TEXT" and (n.get("characters") or "").strip():
            fuori.append({"t": norm(n["characters"].strip()), "d": d})
        for c in n.get("children") or []:
            w(c, d + 1)

    w(radice, 0)
    return fuori


def leggi_purpose(doc):
    T = testi(doc)
    t = [x["t"] for x in T]

    frame_nome = trova_per_nome(doc, re.compile(r"^Nome pattern$", re.I))
    nome = primo_testo(frame_nome) if frame_nome else None
    if not nome:
        h = next((i for i, x in enumerate(t) if HEAD_DO.search(x) or HEAD_ANTI.search(x)), -1)
        nome = t[h - 1] if h > 0 else None

    dos, antis = [], []
    i = 0
    while i < len(t):
        if HEAD_DO.search(t[i]):
            # Fra la descrizione e "In which component…" c'e' il contenuto finto
            # dei mockup: la posizione non e' fissa, va cercata l'etichetta.
            usati, j = [], i + 2
            while j < len(t) and not HEAD_DO.search(t[j]) and not HEAD_ANTI.search(t[j]) \
                    and not USED_IN.search(t[j]):
                j += 1
            if j < len(t) and USED_IN.search(t[j]):
                j += 1
                while j < len(t) and not HEAD_DO.search(t[j]) and not HEAD_ANTI.search(t[j]):
                    usati.append(t[j])
                    j += 1
            dos.append({"section": re.match(r"^\d+\.\d+", t[i]).group(0),
                        "description": t[i + 1] if i + 1 < len(t) else "",
                        "usedIn": usati})
            i = j
        elif HEAD_ANTI.search(t[i]):
            # Sotto UNA intestazione possono stare PIU' terzine: ogni "Rule"
            # apre un anti-pattern nuovo.
            base = re.match(r"^\d+\.\d+", t[i]).group(0)
            j, n, cur = i + 1, 0, None

            def chiudi(c):
                if c and c.get("scenario"):
                    antis.append(c)

            while j < len(t) and not HEAD_DO.search(t[j]) and not HEAD_ANTI.search(t[j]):
                k = ETICHETTE.get(t[j].lower())
                if k == "scenario" and j + 1 < len(t):
                    chiudi(cur)
                    cur = {"section": f"{base}.{n}" if n else base,
                           "origin": "purpose", "scenario": t[j + 1]}
                    n += 1
                    j += 2
                elif k and cur and j + 1 < len(t):
                    cur[k] = t[j + 1]
                    j += 2
                else:
                    j += 1
            chiudi(cur)
            i = j
        else:
            i += 1
    return {"name": nome, "dos": dos, "antis": antis}


def leggi_behavior(doc):
    T = testi(doc)
    frame_nome = trova_per_nome(doc, re.compile(r"^template behavior$", re.I))
    nome = primo_testo(frame_nome) if frame_nome else None

    spec, piattaforma = {}, None
    i = 0
    while i < len(T):
        if PIATTAFORMA.search(T[i]["t"]) and len(T[i]["t"]) < 30:
            piattaforma = T[i]["t"]
            i += 1
            continue
        m = SPEC.match(T[i]["t"])
        if m and i + 1 < len(T):
            # camelCase vero: "Copy & truncation" -> copyAndTruncation
            parole = [w for w in re.split(r"\s+", m.group(1).replace("&", " and ")) if w]
            k = parole[0].lower() + "".join(w[0].upper() + w[1:].lower() for w in parole[1:])
            spec.setdefault(piattaforma or "default", {})[k] = T[i + 1]["t"]
            i += 1
        i += 1

    # La didascalia e' il primo TEXT a profondita' <= all'etichetta, prima
    # dell'etichetta successiva. Il mockup sta piu' in fondo e viene saltato.
    coppie = []
    for i in range(len(T)):
        e_do, e_dont = E_DO(T[i]["t"]), E_DONT(T[i]["t"])
        if not e_do and not e_dont:
            continue
        didascalia = None
        for j in range(i + 1, len(T)):
            if E_DO(T[j]["t"]) or E_DONT(T[j]["t"]):
                break
            if T[j]["d"] <= T[i]["d"]:
                didascalia = T[j]["t"]
                break
        if didascalia:
            coppie.append({"kind": "do" if e_do else "dont", "caption": didascalia})
    return {"name": nome, "spec": spec, "pairs": coppie}


def ordina(o):
    if isinstance(o, list):
        return [ordina(x) for x in o]
    if isinstance(o, dict):
        return {k: ordina(o[k]) for k in sorted(o)}
    return o


def main(argv):
    resto = [a for a in argv if not a.startswith("--")]
    slug = resto[0] if resto else "button"
    filtro = resto[1] if len(resto) > 1 else None

    censimento = ROOT / "data" / "figma-pages.json"
    if not censimento.exists():
        sys.exit("\n  Manca data/figma-pages.json. Eseguire prima il censimento delle pagine.\n")
    pagine = json.loads(censimento.read_text(encoding="utf-8"))["b2c"]["pages"]

    frames = []
    for p in pagine:
        if not p.get("docFrames"):
            continue
        if filtro and filtro.lower() not in (p.get("label") or "").lower():
            continue
        for fr in p.get("frames") or []:
            frames.append({**fr, "page": p.get("label")})

    print(f"> {len(frames)} frame da leggere" + (f' sulla pagina "{filtro}"' if filtro else "") + "\n")

    f = Figma()
    purposes, behaviors = [], []
    for fr in frames:
        doc = list(f.get(f"files/{B2C}/nodes?ids={fr['id']}")["nodes"].values())[0]["document"]
        if re.search(r"purpose", fr.get("name") or "", re.I):
            p = leggi_purpose(doc)
            purposes.append({**fr, **p})
            print(f"   Purpose   {(p['name'] or '—')[:16]:<16} {len(p['dos'])} do  {len(p['antis'])} anti")
        elif re.search(r"behavior", fr.get("name") or "", re.I):
            b = leggi_behavior(doc)
            behaviors.append({**fr, **b})
            n = sum(len(o) for o in b["spec"].values())
            nd = sum(1 for x in b["pairs"] if x["kind"] == "do")
            nn = sum(1 for x in b["pairs"] if x["kind"] == "dont")
            print(f"   Behavior  {(b['name'] or '—')[:16]:<16} {n} spec  {nd} do / {nn} don't")

    def scegli(arr):
        k = chiave(slug)
        return (next((x for x in arr if chiave(x.get("name")) == k), None)
                or next((x for x in arr if k in chiave(x.get("name"))), None))

    P, B = scegli(purposes), scegli(behaviors)

    intento = {
        "id": f"ds.{slug}",
        "componentName": (P or {}).get("name") or (B or {}).get("name"),
        "purpose": ((P or {}).get("dos") or [{}])[0].get("description") if P else None,
        "usedIn": [u for d in ((P or {}).get("dos") or []) for u in d.get("usedIn", [])],
        "commonPatterns": (
            [{"origin": "purpose", "section": d["section"], "description": d["description"]}
             for d in ((P or {}).get("dos") or [])]
            + [{"origin": "behavior", "section": f"B.do.{i + 1}", "description": p["caption"]}
               for i, p in enumerate([x for x in ((B or {}).get("pairs") or []) if x["kind"] == "do"])]
        ),
        "antiPatterns": (
            list((P or {}).get("antis") or [])
            + [{"origin": "behavior", "section": f"B.dont.{i + 1}", "scenario": p["caption"]}
               for i, p in enumerate([x for x in ((B or {}).get("pairs") or []) if x["kind"] == "dont"])]
        ),
        "behavior": (B or {}).get("spec") or {},
        "_source": {
            "ds": "b2c", "fileKey": B2C,
            "purposeFrame": {"id": P["id"], "page": P["page"]} if P else None,
            "behaviorFrame": {"id": B["id"], "page": B["page"]} if B else None,
            "confidence": "human-authored",
        },
    }

    meta = ROOT / "components" / slug / "docs" / "metadata.json"
    if not meta.exists():
        meta = Path("C:/Users/simon/Downloads/ds-cross-app") / "components" / slug / "docs" / "metadata.json"
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        intento["_reproducibility"] = {
            "antiPatterns": {"figma": len(intento["antiPatterns"]),
                             "metadata": len((m.get("usage") or {}).get("antiPatterns") or [])},
            "commonPatterns": {"figma": len(intento["commonPatterns"]),
                               "metadata": len((m.get("usage") or {}).get("commonPatterns") or [])},
            "behaviorKeys": {"figma": sum(len(o) for o in intento["behavior"].values()),
                             "metadata": len((m.get("behavior") or {}).get("interactions") or {})},
            "contentBlock": {"figma": 1 if any(o.get("copyAndTruncation") for o in intento["behavior"].values()) else 0,
                             "metadata": len(m.get("content") or {})},
        }

    cartella = USCITA / slug
    cartella.mkdir(parents=True, exist_ok=True)
    scrivi_json(cartella / "intent.json", ordina(intento))

    L = "-" * 72
    print(f"\n{L}\n  INTENTO UNIFICATO - {intento['componentName']}\n{L}")
    print(f"\n> PURPOSE\n   {(intento['purpose'] or '—')[:150]}...")
    print("\n> BEHAVIOR")
    for plat, o in intento["behavior"].items():
        print(f"   [{plat}]")
        for k, v in o.items():
            print(f"      {k:<22} {str(v)[:74]}...".replace("\n", " "))
    print(f"\n> ANTI-PATTERN  {len(intento['antiPatterns'])}")
    for a in intento["antiPatterns"]:
        print(f"   [{a.get('origin')}] {str(a.get('scenario') or '')[:80]}")
    print(f"\n> PATTERN D'USO  {len(intento['commonPatterns'])}")
    if intento.get("_reproducibility"):
        print("\n> RIPRODUCIBILITA'   Figma  vs  metadata.json scritto a mano")
        for k, v in intento["_reproducibility"].items():
            print(f"   {k:<16} {str(v['figma']):>3}  vs {str(v['metadata']):>3}")
    print(f"\nOK  data/contracts/{slug}/intent.json\n{L}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
