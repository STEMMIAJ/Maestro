"""JobLogger — logging JSON estruturado + captura de falhas com schema do db/falhas.json.

Endereça:
- BUGS.md (todos): observabilidade pobre, prints soltos
- INDEX.md fluxo: "Falha nova → registrar em casos-reais/REGISTRO.md"

Base: ~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/06-TEMPLATES/script-cli-typer-com-logging.py

Saída:
1. Console legível: [HH:MM:SS] LEVEL mensagem
2. JSONL rotativo (10MB×5): ~/Desktop/_MESA/40-CLAUDE/logs-pje/{script}.jsonl
3. Falhas com ref_falhas_json: vão pro JSONL com ID já catalogado
4. Falhas SEM ref (NOVAS): também append em casos-reais/REGISTRO.md no formato esperado
"""
from __future__ import annotations
import hashlib
import json
import logging
import logging.handlers
import sys
import traceback as _tb
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / "Desktop/_MESA/40-CLAUDE/logs-pje"
JSONL_FALHAS = LOG_DIR / "falhas-runtime.jsonl"
REGISTRO_MD = (
    Path.home()
    / "Desktop/_MESA/01-ATIVO/PYTHON-BASE/03-FALHAS-SOLUCOES/casos-reais/REGISTRO.md"
)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        d = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra_data", None)
        if isinstance(extra, dict):
            d.update(extra)
        if record.exc_info:
            d["exc"] = self.formatException(record.exc_info)
        return json.dumps(d, ensure_ascii=False)


class JobLogger:
    """Logger por script. Não compartilha state global entre instâncias."""

    def __init__(self, script: str, level: str = "INFO") -> None:
        self.script = script
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._configurar(level)

    def _configurar(self, level: str) -> None:
        self.log = logging.getLogger(self.script)
        self.log.setLevel(level)
        self.log.handlers.clear()
        self.log.propagate = False
        # console
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)-5s %(message)s", datefmt="%H:%M:%S"
            )
        )
        self.log.addHandler(ch)
        # JSONL rotativo
        fh = logging.handlers.RotatingFileHandler(
            LOG_DIR / f"{self.script}.jsonl",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        fh.setFormatter(_JsonFormatter())
        self.log.addHandler(fh)

    # ---- níveis padrão (proxy) ----
    def info(self, msg, *args, **kw) -> None:
        self.log.info(msg, *args, **kw)

    def aviso(self, msg, *args, **kw) -> None:
        self.log.warning(msg, *args, **kw)

    def erro(self, msg, *args, **kw) -> None:
        self.log.error(msg, *args, **kw)

    def debug(self, msg, *args, **kw) -> None:
        self.log.debug(msg, *args, **kw)

    # ---- captura estruturada (schema falhas.json) ----
    def captura_falha(
        self,
        *,
        tecnologia: str,
        categoria: str,
        sintoma: str,
        contexto: dict | None = None,
        ref_falhas_json: str | None = None,
        exc: BaseException | None = None,
        severidade: str = "alta",
    ) -> str:
        """Registra uma falha estruturada.

        Args:
            tecnologia: 'playwright' | 'selenium' | 'cdp' | 'requests' | 'geral'
            categoria:  'selector' | 'timeout' | 'sessao' | 'download' | ...
            sintoma:    primeira linha do erro (literal). NÃO inferir.
            contexto:   {cnj, url, linha, args, ...} — qualquer dict serializável.
            ref_falhas_json: ID já catalogado (ex 'PJE-007'). Se None: marca NOVA.
            exc: exceção opcional (vai pro traceback).
            severidade: 'bloqueador' | 'alta' | 'media' | 'baixa'.

        Returns:
            hash_dedupe (8 hex) do (tecnologia|categoria|sintoma).
        """
        sintoma_clean = (sintoma or "").splitlines()[0][:300]
        h = hashlib.sha256(
            f"{tecnologia}|{categoria}|{sintoma_clean}".encode("utf-8")
        ).hexdigest()[:8]
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "id_provisorio": ref_falhas_json or f"NEW-{h}",
            "tecnologia": tecnologia,
            "categoria": categoria,
            "sintoma": sintoma_clean,
            "severidade": severidade,
            "contexto": {"script": self.script, **(contexto or {})},
            "ja_catalogada": ref_falhas_json is not None,
            "traceback": (
                "".join(_tb.format_exception(type(exc), exc, exc.__traceback__))
                if exc
                else None
            ),
            "hash_dedupe": h,
        }
        # 1. JSONL append-only (sempre)
        with JSONL_FALHAS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # 2. Console
        self.log.error(
            "FALHA[%s] %s/%s: %s",
            entry["id_provisorio"],
            tecnologia,
            categoria,
            sintoma_clean,
        )
        # 3. NOVA → agrega em REGISTRO.md
        if not ref_falhas_json:
            self._agregar_registro(entry)
        return h

    @staticmethod
    def _agregar_registro(e: dict) -> None:
        try:
            REGISTRO_MD.parent.mkdir(parents=True, exist_ok=True)
            ctx = e["contexto"]
            bloco = (
                f"\n### {datetime.now().strftime('%Y-%m-%d')} — "
                f"[{e['tecnologia']}] {e['sintoma'][:80]}\n"
                f"- **Script:** `{ctx.get('script','-')}` "
                f"(cnj={ctx.get('cnj','-')})\n"
                f"- **Sintoma:** `{e['sintoma']}`\n"
                f"- **Causa raiz:** _a investigar (hash {e['hash_dedupe']})_\n"
                f"- **Fix:** _a registrar_\n"
                f"- **Virou entrada em falhas.json?** não\n"
            )
            with REGISTRO_MD.open("a", encoding="utf-8") as f:
                f.write(bloco)
        except Exception:
            # Logger NUNCA pode quebrar o script principal.
            pass


def get_logger(script: str) -> JobLogger:
    return JobLogger(script)
