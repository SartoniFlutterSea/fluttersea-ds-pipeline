#!/usr/bin/env python3
"""
Classifica ogni PAGINA dei file del perimetro.

Un file di design system non e' omogeneo: contiene pagine che pubblicano
componenti, pagine di fondamenta con i soli token, sezioni, separatori, guide,
aree di lavoro in corso e archivi. Trattarle allo stesso modo produce i numeri
gonfiati che abbiamo gia' visto: in DS B2B una sola pagina di lavoro vale il
68% del file.

IL SEGNALE PRINCIPALE
Una pagina che PUBBLICA componenti e' una fonte; una che li consuma soltanto e'
un'area di lavoro. Lo dice `containing_frame.pageName` di /v1/files/{key}/components,
che costa una chiamata per file.

Gli altri segnali vengono dal nome, che i designer usano come convenzione:
i marcatori di stato, il prefisso di sezione, i separatori fatti di trattini.

  python tools/classify_pages.py [--tutti]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "pagine.json"
RAPPORTO = ROOT / "docs" / "pagine.md"

PERIMETRO = [
    "QWM2EhgZmv2KKcqI0315fx", "AFsC1fNp7mYe6Qm4l2Cfin", "S8U9Li374QCzYEtwFBnaaX",
    "KUB9MGjJGlYw0nJOjXz1au", "V1QcyELlWtJTnfrjrRJrfR", "AaT6MvmrhxgPLQjWt1qGDj",
    "FUrJB3g2FMvTEuRjHk4p6r",
]

SEPARATORE = re.compile(r"^[\s\-–—_·.]*$")
# ⚠️ Le sezioni non usano tutte lo stesso marcatore: ❖ in Cross App e B2B,
# ma ↴ in DS WEB GLOBAL e MySisal. Riconoscerne uno solo lasciava 20 sezioni
# classificate come ambigue.
SEZIONE = re.compile(r"^\s*❖|↴\s*$")
FONDAMENTA = re.compile(
    r"colors?|tokens?|typograph|elevation|spacing|margin|radius|shadow|grid|icon set|"
    r"primitive|semantic|breakpoint|immagin|images?|foundation", re.I)
GUIDA = re.compile(
    r"tutorial|guide|how to|use dev|user stor|template documentaz|getting started|changelog|"
    r"read\s*me|decision tree|documentation|content loading|use a |set a[n ]|check right", re.I)
LAVORO = re.compile(
    r"playground|updates|test|discovery|wip|work in progress|draft|bozza|analisi|mappatur|"
    r"da fare|da aggiungere|da ordinare|backup|piano |ready for dev", re.I)
ARCHIVIO = re.compile(r"archiv|archive|legacy|old|deprecat", re.I)
STRUTTURA = re.compile(r"^\s*(thumbnail|cover|about|profile|index)\s*$", re.I)


def classifica(nome: str, pubblicati: int, marcatori: str) -> tuple[str, str]:
    """(classe, motivo). Il motivo e' la prova usata, non una supposizione."""
    n = nome or ""
    if SEPARATORE.match(n):
        return "separatore", "il nome è solo trattini o spazi"
    if SEZIONE.search(n):
        return "sezione", "marcatore di sezione (❖ oppure ↴)"
    if STRUTTURA.match(n):
        return "struttura", "pagina di servizio del file"
    if ARCHIVIO.search(n):
        return "archivio", "il nome indica materiale archiviato"
    if "🚧" in marcatori:
        return "lavoro", "marcata 🚧 in corso"
    if LAVORO.search(n):
        return "lavoro", "il nome indica un'area di lavoro"
    if GUIDA.search(n):
        return "guida", "il nome indica una guida o un template"
    if FONDAMENTA.search(n):
        return "fondamenta", "il nome indica token o fondamenta"
    if pubblicati:
        return "componenti", f"pubblica {pubblicati} componenti"
    if "🟢" in marcatori or "✅" in marcatori:
        return "anomalia", "marcata come fatta ma non pubblica nulla"
    return "senza componenti", "non pubblica nulla e nessun segnale nel nome"


def main(argv):
    idx = json.loads((ROOT / "data" / "grafo" / "indice.json").read_text(encoding="utf-8"))
    chiavi = list(idx["files"]) if "--tutti" in argv else PERIMETRO

    risultato, conteggi = {}, Counter()
    for k in chiavi:
        v = idx["files"].get(k) or {}
        if not v.get("pagine"):
            continue
        pub = Counter()
        for c in (v.get("componenti") or []) + (v.get("set") or []):
            if c.get("pagina"):
                pub[c["pagina"]] += 1

        pagine = []
        for p in v["pagine"]:
            nome = p.get("nome") or ""
            marcatori = "".join(ch for ch in nome if ord(ch) > 0x2000)
            cls, motivo = classifica(nome, pub.get(nome, 0), marcatori)
            conteggi[cls] += 1
            pagine.append({
                "id": p.get("id"), "nome": nome, "classe": cls, "motivo": motivo,
                "componentiPubblicati": pub.get(nome, 0),
            })
        risultato[k] = {"nome": v.get("nome"), "pagine": pagine}

    scrivi_json(USCITA, {"totali": dict(conteggi), "files": risultato})

    # ── rapporto ────────────────────────────────────────────────────────────
    ORDINE = ["componenti", "fondamenta", "guida", "lavoro", "archivio", "anomalia",
              "sezione", "separatore", "struttura", "senza componenti"]
    r = ["# Pagine, classificate", "",
         "Un file di design system non è omogeneo. Qui ogni pagina è classificata",
         "dal segnale più forte disponibile: **pubblica componenti o no**, più le",
         "convenzioni di nome che i designer usano già.", "",
         "| Classe | Pagine | Cosa farne |", "|---|---|---|"]
    COSA = {
        "componenti": "**estrarre**: sono le fonti",
        "fondamenta": "**estrarre**: qui vivono i token",
        "guida": "documentazione per persone, non per il sistema",
        "lavoro": "**escludere** dal perimetro, censire a parte",
        "archivio": "**escludere**",
        "sezione": "solo struttura dell'elenco",
        "separatore": "solo struttura dell'elenco",
        "struttura": "servizio del file",
        "anomalia": "**da chiedere**: marcata fatta, ma non pubblica",
        "senza componenti": "**da guardare**: né fonte né lavoro dichiarato",
    }
    for c in ORDINE:
        if conteggi.get(c):
            r.append(f"| {c} | {conteggi[c]} | {COSA[c]} |")

    for c in ORDINE:
        righe = [(f["nome"], p) for f in risultato.values() for p in f["pagine"] if p["classe"] == c]
        if not righe or c in ("separatore", "sezione", "struttura"):
            continue
        r += ["", f"## {c} · {len(righe)}", ""]
        for nome_file, p in sorted(righe, key=lambda x: -x[1]["componentiPubblicati"])[:40]:
            n = f" · {p['componentiPubblicati']} componenti" if p["componentiPubblicati"] else ""
            r.append(f"- **{p['nome'] or '(senza nome)'}** — {nome_file}{n}")
        if len(righe) > 40:
            r.append(f"- … altre {len(righe)-40}")

    RAPPORTO.parent.mkdir(parents=True, exist_ok=True)
    RAPPORTO.write_text("\n".join(r) + "\n", encoding="utf-8")

    linea = "─" * 60
    print(f"\n{linea}")
    for c in ORDINE:
        if conteggi.get(c):
            print(f"  {c:<20}{conteggi[c]:>5}   {COSA[c].replace('**','')}")
    print(f"\n  totale pagine {sum(conteggi.values())}")
    print(f"  scritto data/{USCITA.name} · docs/{RAPPORTO.name}\n{linea}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
