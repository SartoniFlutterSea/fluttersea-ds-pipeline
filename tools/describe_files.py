#!/usr/bin/env python3
"""
Apre in parallelo ogni file del censimento e ne descrive il contenuto.

Una chiamata per file (?depth=1): restituisce nome, data di modifica e l'elenco
delle PAGINE. Non serve scendere piu' a fondo per capire cos'e' un file: i nomi
delle pagine lo dicono gia'.

La descrizione e' DERIVATA, mai inventata: conta le pagine, riconosce i
marcatori di stato nei nomi, e cerca un vocabolario di componenti noti. Se le
prove non bastano, il file viene segnato come non classificato invece di
indovinare.

  python tools/describe_files.py [--quanti=N]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _figma import ROOT, Figma, scrivi_json  # noqa: E402

USCITA = ROOT / "data" / "figma-descrizioni.json"
ALBERO = ROOT / "docs" / "figma-mappa.md"

# I marcatori che i designer mettono nei nomi delle pagine.
MARCATORI = {
    "\U0001F7E2": "fatto",
    "\U0001F534": "in corso",
    "❌": "assente",
    "❓": "da decidere",
    "❖": "sezione",
    "⚠": "non modificare",
    "➡": "template",
    "\U0001F6A7": "in lavorazione",
}

# Vocabolario: se molte pagine si chiamano cosi', il file contiene componenti.
COMPONENTI = {
    "button", "card", "badge", "avatar", "chip", "input", "checkbox", "radio", "toggle",
    "modal", "sheet", "toast", "alert", "banner", "accordion", "tab", "tabs", "navbar",
    "header", "footer", "divider", "icon", "icons", "list", "table", "tooltip", "dropdown",
    "select", "slider", "stepper", "spinner", "loader", "progress", "pagination",
    "breadcrumb", "menu", "search", "hero", "carousel", "grid", "link", "counter",
    "quicklink", "segmented", "textfield", "typography", "color", "colors", "spacing",
    "elevation", "shadow", "radius", "token", "tokens", "foundation", "foundations",
}
STRUTTURA = {
    "cover", "thumbnail", "about", "changelog", "documentation", "index", "intro",
    "guidelines", "release", "template", "archive", "playground", "profile",
}

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF☀-➿⬀-⯿️■-◿←-⇿]"
)


def pulisci(nome):
    return EMOJI.sub("", nome or "").strip(" -–—_·").strip()


def classifica(nome_file, pagine):
    """Restituisce (categoria, motivi). I motivi sono le prove effettivamente usate."""
    n = (nome_file or "").lower()
    puliti = [pulisci(p).lower() for p in pagine]
    parole = set()
    for p in puliti:
        parole.update(w for w in re.split(r"[^a-z]+", p) if w)

    comp = len(parole & COMPONENTI)
    strut = len(parole & STRUTTURA)

    if "(copy)" in n or "copia" in n:
        return "copia", ["il nome contiene «Copy»"]
    if re.search(r"\btest\b|test ai|playground", n):
        return "prova", ["il nome indica una prova"]
    if re.search(r"archiv", n):
        return "archivio", ["il nome indica un archivio"]
    if re.search(r"librar|foundation|asset|utilit", n):
        return "libreria", ["il nome indica una libreria"]
    if re.search(r"ui kit|ui-kit|styleguide|design system|\bds[ _]", n):
        motivi = ["il nome indica un design system"]
        if comp >= 5:
            motivi.append(str(comp) + " pagine con nomi di componenti")
        return "design-system", motivi
    if comp >= 8:
        return "design-system", [str(comp) + " pagine con nomi di componenti"]
    if re.search(r"manual|documentaz|handoff|template", n):
        return "documentazione", ["il nome indica documentazione"]
    if re.search(r"mappatur|analisi|verificar|flow", n):
        return "analisi", ["il nome indica un lavoro di analisi"]
    if comp >= 3:
        return "componenti", [str(comp) + " pagine con nomi di componenti"]
    if strut and len(pagine) <= 3:
        return "scheletro", ["poche pagine, solo di struttura"]
    return "non classificato", [str(len(pagine)) + " pagine, nessun segnale riconoscibile"]


def descrivi(pagine, categoria, motivi):
    """Frase costruita solo su fatti misurati."""
    parti = [str(len(pagine)) + (" pagina" if len(pagine) == 1 else " pagine")]

    conteggi = {}
    for p in pagine:
        for m in EMOJI.findall(p or ""):
            if m in MARCATORI:
                conteggi[m] = conteggi.get(m, 0) + 1
    if conteggi:
        dettaglio = ", ".join(
            str(v) + " " + MARCATORI[k] for k, v in sorted(conteggi.items(), key=lambda x: -x[1])
        )
        parti.append("di cui " + dettaglio)

    campione = [pulisci(p) for p in pagine if pulisci(p)][:4]
    if campione:
        parti.append("fra cui " + ", ".join(campione))

    frase = ". ".join(parti) + "."
    if motivi:
        frase += " Classificato «" + categoria + "»: " + motivi[0] + "."
    return frase


def main(argv):
    quanti = 2
    for a in argv:
        if a.startswith("--quanti="):
            quanti = int(a.split("=")[1])

    percorso = ROOT / "data" / "figma-censimento.json"
    if not percorso.exists():
        print("\n  Manca il censimento. Eseguire prima list_files, discover_files, merge_inventory.\n")
        return 1

    censimento = json.loads(percorso.read_text(encoding="utf-8"))
    # Ripartenza: il limite di frequenza di Figma fa fallire una parte dei file
    # a ogni passata. Rileggere quelli gia' riusciti sprecherebbe chiamate e
    # rialzerebbe il limite. Si riprende solo cio' che manca, cosi' rieseguire
    # lo script converge invece di ricominciare da zero.
    precedenti = {}
    if USCITA.exists() and "--daccapo" not in argv:
        try:
            precedenti = json.loads(USCITA.read_text(encoding="utf-8")).get("files", {})
        except (OSError, json.JSONDecodeError):
            precedenti = {}
    riusciti = {k: v for k, v in precedenti.items() if not v.get("errore")}

    chiavi = [k for k in sorted(censimento["files"]) if k not in riusciti]
    if riusciti:
        print("  " + str(len(riusciti)) + " gia' letti nelle passate precedenti")
    print("  " + str(len(chiavi)) + " da leggere ora, " + str(quanti) + " in parallelo")
    print()

    f = Figma()
    fatti = [0]

    def analizza(chiave):
        dati, err = f.prova("files/" + chiave + "?depth=1")
        fatti[0] += 1
        if fatti[0] % 20 == 0:
            print("    " + str(fatti[0]) + "/" + str(len(chiavi)) + "...", flush=True)
        base = dict(censimento["files"][chiave])
        if err:
            base.update(
                errore=err,
                categoria="non leggibile",
                pagine=[],
                numPagine=0,
                descrizione="Non leggibile: " + err
                + ". Il file risulta nel censimento ma l'accesso e' negato, oppure e' stato rimosso.",
            )
            return chiave, base
        pagine = [p.get("name", "") for p in (dati.get("document", {}).get("children") or [])]
        cat, motivi = classifica(dati.get("name") or base.get("nome"), pagine)
        base.update(
            nome=dati.get("name") or base.get("nome"),
            lastModified=dati.get("lastModified") or base.get("lastModified"),
            versione=dati.get("version"),
            pagine=pagine,
            numPagine=len(pagine),
            categoria=cat,
            descrizione=descrivi(pagine, cat, motivi),
        )
        return chiave, base

    risultati = dict(riusciti)
    risultati.update(dict(f.in_parallelo(chiavi, analizza, quanti)) if chiavi else {})
    scrivi_json(USCITA, {"totali": {"file": len(risultati), "chiamate": f.chiamate}, "files": risultati})

    # ── albero indentato in markdown ─────────────────────────────────────────
    per_gruppo = {}
    for v in risultati.values():
        per_gruppo.setdefault((v.get("team") or "(fuori dai progetti visibili)",
                               v.get("progetto") or "—"), []).append(v)

    cats = {}
    for v in risultati.values():
        cats[v["categoria"]] = cats.get(v["categoria"], 0) + 1

    righe = [
        "# Mappa dei file Figma",
        "",
        str(len(risultati)) + " file, aperti uno per uno.",
        "",
        "Ogni descrizione e' **derivata dai nomi delle pagine**, non scritta a mano:",
        "conta le pagine, riconosce i marcatori di stato, cerca un vocabolario di",
        "componenti noti. Dove le prove non bastano il file resta *non classificato*",
        "invece di essere indovinato.",
        "",
        "## Per categoria",
        "",
        "| Categoria | File |",
        "|---|---|",
    ]
    righe += ["| " + k + " | " + str(v) + " |" for k, v in sorted(cats.items(), key=lambda x: -x[1])]
    righe += ["", "## Albero", ""]

    for chiave_gruppo in sorted(per_gruppo):
        team, prog = chiave_gruppo
        righe.append("### " + team + " / " + prog)
        righe.append("")
        for v in sorted(per_gruppo[chiave_gruppo], key=lambda x: (x.get("nome") or "").lower()):
            data = (v.get("lastModified") or "")[:10]
            righe.append("- **" + (v.get("nome") or "?") + "** · `" + v["categoria"] + "` · " + data)
            righe.append("  - " + v["descrizione"])
            righe.append("  - `" + v["key"] + "`")
        righe.append("")

    ALBERO.parent.mkdir(parents=True, exist_ok=True)
    ALBERO.write_text("\n".join(righe) + "\n", encoding="utf-8")

    linea = "─" * 62
    print("\n" + linea)
    for k, v in sorted(cats.items(), key=lambda x: -x[1]):
        print("  " + k.ljust(20) + str(v))
    print("\n  chiamate API " + str(f.chiamate))
    print("  scritto data/" + USCITA.name)
    print("          docs/" + ALBERO.name + "\n" + linea + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
