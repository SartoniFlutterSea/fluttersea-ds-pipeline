"""
Verifica che il nodo scaricato sia davvero il componente chiesto.

Serve perche' i due file Figma condividono gli identificativi: il B2B e' un
duplicato del B2C, quindi lo stesso nodeId esiste in entrambi e restituisce
componenti diversi senza che nulla lo segnali. Senza questo controllo,
`build_contract.py checkbox 5473-10855` scrive tranquillamente le 90 varianti
di Button dentro il contratto di Checkbox.

Il confronto e' sull'INSIEME delle parole, non sulla stringa: lo slug
`button-icon` corrisponde legittimamente al nodo "Icon Button".
"""
from __future__ import annotations

import re
import sys


def _parole(s: str) -> set[str]:
    return {p for p in re.split(r"[^a-z0-9]+", str(s or "").lower()) if p}


def verifica_nodo(slug: str, nome_nodo: str, ds: str = "?", node_id: str = "?",
                  forza: bool = False) -> None:
    a, b = _parole(slug), _parole(nome_nodo)
    comuni = len(a & b)
    if comuni and comuni >= min(len(a), len(b)):
        return

    messaggio = "\n".join([
        "",
        "  ✖ Il nodo non corrisponde al componente chiesto.",
        "",
        f"      slug richiesto   {slug}",
        f'      nodo ottenuto    "{nome_nodo}"   ({ds} · {node_id})',
        "",
        "    I due file Figma condividono gli identificativi: lo stesso nodeId",
        "    esiste in entrambi e restituisce componenti diversi. Controllare il",
        "    ds, oppure il nodeId.",
        "",
        "    Se la differenza è voluta, ripetere con --forza in fondo.",
        "",
    ])
    if forza:
        print(messaggio.replace("✖", "⚠"), file=sys.stderr)
        return
    sys.exit(messaggio)
