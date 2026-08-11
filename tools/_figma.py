"""
Client Figma condiviso: radice del progetto, token, chiamate con ritentativi.

Nella versione JavaScript i ritentativi c'erano in un solo script su quattro, e
i timeout intermittenti dell'API interrompevano a meta' una passata da otto
minuti. Qui la logica sta in un posto solo, cosi' non puo' divergere.

Il token si cerca in quest'ordine:
  1. FIGMA_TOKEN_FULL / FIGMA_ACCESS_TOKEN / FIGMA_TOKEN nell'ambiente
  2. il file indicato da FIGMA_ENV_FILE
  3. credentials.env, poi .env.local, nella radice del progetto
"""
from __future__ import annotations

import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import requests

# La console Windows usa cp1252 e va in errore sui caratteri non latini,
# che nei nomi dei file Figma abbondano (emoji, accenti, simboli).
for _flusso in (sys.stdout, sys.stderr):
    if getattr(_flusso, "encoding", "").lower() not in ("utf-8", "utf8"):
        try:
            _flusso.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.figma.com/v1/"

NOMI = ("FIGMA_TOKEN_FULL", "FIGMA_ACCESS_TOKEN", "FIGMA_TOKEN")


def _da_file(percorso: Path) -> str | None:
    try:
        testo = percorso.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    for nome in NOMI:
        m = re.search(rf"^\s*{nome}\s*=\s*(.+)$", testo, re.M)
        if m:
            valore = m.group(1).strip().strip("\"'")
            if valore:
                return valore
    return None


def _trova_token() -> str:
    for nome in NOMI:
        v = os.environ.get(nome, "").strip()
        if v:
            return v
    candidati = [os.environ.get("FIGMA_ENV_FILE"), ROOT / "credentials.env", ROOT / ".env.local"]
    for c in candidati:
        if not c:
            continue
        t = _da_file(Path(c))
        if t:
            return t
    sys.exit(
        "\n  Token Figma non trovato. Cercato in:\n"
        "    variabili d'ambiente  FIGMA_TOKEN_FULL, FIGMA_ACCESS_TOKEN, FIGMA_TOKEN\n"
        "    il file indicato da   FIGMA_ENV_FILE\n"
        "    credentials.env e .env.local nella radice del progetto\n"
    )


TOKEN = _trova_token()


class ErroreFigma(Exception):
    """Errore non ritentabile: il chiamante decide se fermarsi o registrarlo."""

    def __init__(self, stato: int, url: str, corpo: str = ""):
        self.stato, self.url, self.corpo = stato, url, corpo
        super().__init__(f"HTTP {stato} su {url}")


class Figma:
    """
    Il limite di frequenza di Figma e' la causa piu' comune di fallimento su
    passate lunghe. Con 12 richieste in parallelo, 36 file su 113 hanno
    risposto 429 e i ritentativi si arrendevano dopo ~25 secondi complessivi.
    Ora l'attesa cresce in modo esponenziale, rispetta l'intestazione
    Retry-After quando c'e', e il parallelismo predefinito e' piu' prudente.
    """

    def __init__(self, tentativi: int = 6, timeout: int = 90):
        self.tentativi, self.timeout = tentativi, timeout
        self.chiamate = 0
        self.attese = 0          # secondi passati ad aspettare per 429/5xx
        # Distanza minima fra due richieste, misurata su tutto il client: il
        # solo limitare il parallelismo non basta, perche' richieste veloci in
        # sequenza raggiungono lo stesso il limite.
        self._passo = 0.35
        self._ultima = 0.0
        self._lucchetto = threading.Lock()
        self.s = requests.Session()
        self.s.headers["X-Figma-Token"] = TOKEN

    def get(self, percorso: str) -> dict[str, Any]:
        ultimo: Exception | None = None
        for i in range(1, self.tentativi + 1):
            try:
                with self._lucchetto:
                    ritardo = self._passo - (time.monotonic() - self._ultima)
                    if ritardo > 0:
                        time.sleep(ritardo)
                    self._ultima = time.monotonic()
                self.chiamate += 1
                r = self.s.get(BASE + percorso, timeout=self.timeout)
                if r.ok:
                    return r.json()
                # 429 e 5xx sono transitori: si riprova con attesa crescente
                if r.status_code == 429 or r.status_code >= 500:
                    ultimo = ErroreFigma(r.status_code, percorso, r.text[:200])
                    # Figma indica quanto aspettare: se lo dice, gli si crede.
                    suggerita = r.headers.get("Retry-After")
                    if suggerita and suggerita.isdigit():
                        attesa = min(int(suggerita), 120)
                    else:
                        attesa = min(2 ** i + (5 if r.status_code == 429 else 0), 90)
                    self.attese += attesa
                    time.sleep(attesa)
                    continue
                raise ErroreFigma(r.status_code, percorso, r.text[:200])
            except requests.RequestException as e:
                ultimo = e
                if i < self.tentativi:
                    time.sleep(2.5 * i)
        raise ultimo if ultimo else ErroreFigma(0, percorso)

    def prova(self, percorso: str) -> tuple[dict[str, Any] | None, str | None]:
        """Come get, ma restituisce l'errore invece di sollevarlo."""
        try:
            return self.get(percorso), None
        except ErroreFigma as e:
            return None, f"HTTP {e.stato}"
        except Exception as e:  # rete, timeout
            return None, str(e)[:80]

    def in_parallelo(self, elementi: Sequence, lavoro: Callable, quanti: int = 4) -> list:
        """Poche richieste alla volta: l'API risponde 429 se la si sommerge."""
        with ThreadPoolExecutor(max_workers=quanti) as ex:
            return list(ex.map(lavoro, elementi))


def _serializzabile(o: Any) -> Any:
    """
    ijson restituisce i numeri come Decimal, che json non sa scrivere.
    Si arrotondano anche a due cifre: l'output deve essere CANONICO, cosi' due
    estrazioni identiche producono file identici e ogni differenza in revisione
    e' un cambiamento vero.
    """
    from decimal import Decimal

    if isinstance(o, Decimal):
        f = float(o)
        return int(f) if f.is_integer() else round(f, 2)
    raise TypeError(f"non serializzabile: {type(o).__name__}")


def scrivi_json(percorso: Path, dati: Any) -> None:
    """
    Output canonico: chiavi ordinate, numeri arrotondati, nessuna data dentro.

    I fine riga sono forzati a LF. Senza, su Windows Python traduce a CRLF e
    lo stesso artefatto risulta diverso a seconda della piattaforma: la
    pipeline girera' su Linux in CI, e OGNI file apparirebbe modificato.
    """
    import json

    percorso.parent.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(dati, indent=2, ensure_ascii=False, sort_keys=True,
                       default=_serializzabile) + chr(10)
    with open(percorso, "w", encoding="utf-8", newline=chr(10)) as fh:
        fh.write(testo)
