"""
Modello del grafo: identita' dei nodi, tipi di arco, tipologie di dato.

IDENTITA'
Team e progetto NON entrano nell'identificativo. Un file puo' essere spostato
fra progetti e la sua chiave non cambia: un'identita' che li contenesse
diventerebbe instabile e produrrebbe nodi duplicati al primo riordino. In piu'
il censimento dei progetti e' incompleto per costruzione, due progetti su 23
rispondono 403.

Team e progetto restano ATTRIBUTI del nodo file, agganciati dal censimento
quando disponibili. Il percorso leggibile team/progetto/file:nodo si ricava con
una giunzione.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── identita' ────────────────────────────────────────────────────────────────

def id_file(file_key: str) -> str:
    return f"file:{file_key}"


def id_nodo(file_key: str, node_id: str) -> str:
    """Un nodo dentro un file. Unico in tutto Figma."""
    return f"fig:{file_key}:{node_id}"


def id_componente(chiave: str) -> str:
    """Componente pubblicato. Resta valido anche se il nodo si sposta."""
    return f"comp:{chiave}"


def id_variabile(chiave: str) -> str:
    return f"var:{chiave}"


def id_stile(chiave: str) -> str:
    return f"sty:{chiave}"


# ── tipologie di dato ────────────────────────────────────────────────────────
# Ognuna ha un segnale misurabile. Dove il segnale manca il nodo resta
# "non classificato" invece di essere indovinato.

TIPI = (
    "file",
    "pagina",
    "sezione",
    "token",            # variabile con valore letterale
    "alias-locale",     # alias verso una variabile dello stesso file
    "alias-esterno",    # alias verso un altro file
    "stile",
    "atomo",            # componente che non contiene istanze di altri componenti
    "molecola",         # contiene istanze di atomi
    "organismo",        # contiene istanze di molecole
    "componente",       # componente la cui profondita' non e' ancora calcolata
    "schermata",        # frame a dimensione di dispositivo, fuori da un componente
    "flusso",           # schermate collegate da transizioni di prototipo
    "documentazione",   # frame di documentazione accanto ai componenti
    "non classificato",
)

# Larghezze tipiche dei dispositivi: un frame cosi' largo, fuori da un
# componente, e' una schermata e non un elemento di interfaccia.
LARGHEZZE_DISPOSITIVO = {320, 360, 375, 390, 393, 412, 414, 428, 430, 768, 834, 1024, 1280, 1440, 1920}

# Nomi dei frame di documentazione, dai template usati dai designer.
import re  # noqa: E402

DOC_RE = re.compile(r"purpose\s*&?\s*usage|behaviou?r|anatomy|do\s*&\s*don|don'?t|guideline|spec\b", re.I)


# ── tipi di arco ─────────────────────────────────────────────────────────────

ARCHI = (
    "istanza-di",    # nodo INSTANCE  -> componente
    "alias-di",      # variabile      -> variabile
    "usa-token",     # nodo           -> variabile
    "usa-stile",     # nodo           -> stile
    "contiene",      # contenitore    -> figlio
    "pubblica",      # file           -> componente/stile/variabile che offre
    "transizione",   # frame          -> frame (prototipo)
)


@dataclass
class Grafo:
    """
    Contenitore con deduplica. I nodi sono unici per identificativo, gli archi
    per la terna (da, tipo, a): lo stesso riferimento ripetuto mille volte in
    un file produce un arco solo, con il conteggio delle occorrenze.
    """

    nodi: dict[str, dict[str, Any]] = field(default_factory=dict)
    archi: dict[tuple[str, str, str], dict[str, Any]] = field(default_factory=dict)
    # riferimenti che non si e' saputo risolvere, per dichiarare i buchi
    irrisolti: list[dict[str, Any]] = field(default_factory=list)

    def nodo(self, ident: str, tipo: str, **attributi) -> dict[str, Any]:
        n = self.nodi.get(ident)
        if n is None:
            n = {"id": ident, "tipo": tipo}
            self.nodi[ident] = n
        # un tipo piu' preciso sostituisce uno generico, mai il contrario
        if tipo != "non classificato" and n["tipo"] in ("non classificato", "componente"):
            n["tipo"] = tipo
        for k, v in attributi.items():
            if v is not None and (k not in n or n[k] in (None, "", [], {})):
                n[k] = v
        return n

    def arco(self, da: str, tipo: str, a: str, **prove) -> None:
        chiave = (da, tipo, a)
        e = self.archi.get(chiave)
        if e is None:
            e = {"da": da, "tipo": tipo, "a": a, "occorrenze": 0}
            self.archi[chiave] = e
        e["occorrenze"] += 1
        for k, v in prove.items():
            if v is not None and k not in e:
                e[k] = v

    def irrisolto(self, **dettagli) -> None:
        self.irrisolti.append(dettagli)

    def unisci(self, altro: "Grafo") -> None:
        for ident, n in altro.nodi.items():
            mio = self.nodi.get(ident)
            if mio is None:
                self.nodi[ident] = n
            else:
                if n["tipo"] != "non classificato" and mio["tipo"] in ("non classificato", "componente"):
                    mio["tipo"] = n["tipo"]
                for k, v in n.items():
                    if k not in mio and v is not None:
                        mio[k] = v
        for chiave, e in altro.archi.items():
            mio = self.archi.get(chiave)
            if mio is None:
                self.archi[chiave] = e
            else:
                mio["occorrenze"] += e["occorrenze"]
        self.irrisolti.extend(altro.irrisolti)

    # ── calcolo topologico: atomo / molecola / organismo ─────────────────────

    def calcola_profondita(self) -> dict[str, int]:
        """
        La distinzione atomo/molecola/organismo si ricava dal GRAFO, non dai
        nomi: un componente che non usa altri componenti e' un atomo, uno che
        usa atomi e' una molecola, uno che usa molecole e' un organismo.

        Si calcola sulla chiusura degli archi `istanza-di`, con protezione
        contro i cicli (un componente che, per errore, contiene se stesso).
        """
        # `da` E' gia' l'identificativo del componente che contiene l'istanza:
        # gli archi istanza-di partono da comp:{chiave}, non dal file, tranne
        # quando l'istanza sta fuori da qualsiasi componente.
        usa: dict[str, set[str]] = {}
        for (da, tipo, a) in self.archi:
            if tipo == "istanza-di" and da.startswith("comp:"):
                usa.setdefault(da, set()).add(a)

        profondita: dict[str, int] = {}
        in_corso: set[str] = set()

        def calcola(ident: str) -> int:
            if ident in profondita:
                return profondita[ident]
            if ident in in_corso:      # ciclo: si dichiara e si tronca
                return 0
            in_corso.add(ident)
            figli = usa.get(ident, ())
            p = 0 if not figli else 1 + max(calcola(f) for f in figli)
            in_corso.discard(ident)
            profondita[ident] = p
            return p

        for ident in list(self.nodi):
            if self.nodi[ident]["tipo"] in ("atomo", "molecola", "organismo", "componente"):
                p = calcola(ident)
                self.nodi[ident]["profondita"] = p
                self.nodi[ident]["tipo"] = "atomo" if p == 0 else "molecola" if p == 1 else "organismo"
        return profondita

    def riepilogo(self) -> dict[str, Any]:
        per_tipo: dict[str, int] = {}
        for n in self.nodi.values():
            per_tipo[n["tipo"]] = per_tipo.get(n["tipo"], 0) + 1
        per_arco: dict[str, int] = {}
        for (_, tipo, _) in self.archi:
            per_arco[tipo] = per_arco.get(tipo, 0) + 1
        return {
            "nodi": len(self.nodi),
            "archi": len(self.archi),
            "irrisolti": len(self.irrisolti),
            "perTipo": dict(sorted(per_tipo.items(), key=lambda x: -x[1])),
            "perArco": dict(sorted(per_arco.items(), key=lambda x: -x[1])),
        }


def classifica_frame(nome: str, larghezza: float | None, dentro_componente: bool) -> str:
    """Tipologia di un FRAME, dai soli segnali misurabili."""
    if DOC_RE.search(nome or ""):
        return "documentazione"
    if not dentro_componente and larghezza and int(round(larghezza)) in LARGHEZZE_DISPOSITIVO:
        return "schermata"
    return "non classificato"
