#!/usr/bin/env python3
"""
detectar_habilidade_nova.py

Standalone. Le os JSONLs dos ultimos N dias (default 7), extrai padroes
de novos comandos / conceitos usados pelo usuario, compara com o
MAPEAMENTO-HABILIDADES.md e SUGERE atualizacoes (nao aplica).

Saida:
  - JSON em stdout
  - Arquivo MD para revisao em
    ~/Desktop/_MESA/40-CLAUDE/sugestoes-mapeamento/sugestao-{YYYY-MM-DD}.md

Uso:
  python3 detectar_habilidade_nova.py [--dias 7] [--min-freq 2]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
PROJECT_DIR = HOME / ".claude" / "projects" / "-Users-jesus"
MAPEAMENTO = HOME / "Desktop" / "CLAUDE REVOLUÇÃO" / "PERFIL" / "MAPEAMENTO-HABILIDADES.md"
SAIDA_DIR = HOME / "Desktop" / "_MESA" / "40-CLAUDE" / "sugestoes-mapeamento"

# Termos tecnicos candidatos (CLI tools, libs, conceitos)
RE_SLASH = re.compile(r"(/[a-zA-Z][\w\-:]+)")
RE_BACKTICK = re.compile(r"`([a-zA-Z][\w\-\./:]{2,40})`")
RE_PIPE_CMD = re.compile(r"\b(npx?|pnpm|yarn|pip3?|brew|gh|git|docker|kubectl|"
                         r"playwright|selenium|jq|curl|ffmpeg|sqlite3|sed|awk)\s+([a-z][\w\-]+)")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--min-freq", type=int, default=2)
    return ap.parse_args()


def jsonls_recentes(dias: int) -> list[Path]:
    cutoff = (datetime.now() - timedelta(days=dias)).timestamp()
    return [p for p in PROJECT_DIR.glob("*.jsonl") if p.stat().st_mtime >= cutoff]


def extrair_texto_usuario(p: Path) -> str:
    buf = []
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                try:
                    obj = json.loads(linha)
                except Exception:
                    continue
                msg = obj.get("message") or obj
                if not isinstance(msg, dict):
                    continue
                if msg.get("role") not in ("user",) and obj.get("type") != "user":
                    continue
                c = msg.get("content")
                if isinstance(c, str):
                    buf.append(c)
                elif isinstance(c, list):
                    for it in c:
                        if isinstance(it, dict) and isinstance(it.get("text"), str):
                            buf.append(it["text"])
    except Exception:
        pass
    return "\n".join(buf)


def coletar_termos(texto: str) -> Counter:
    c = Counter()
    for m in RE_SLASH.findall(texto):
        c[("slash", m)] += 1
    for m in RE_BACKTICK.findall(texto):
        c[("backtick", m)] += 1
    for tool, sub in RE_PIPE_CMD.findall(texto):
        c[("cli", f"{tool} {sub}")] += 1
    return c


def termos_no_mapeamento() -> set[str]:
    if not MAPEAMENTO.exists():
        return set()
    txt = MAPEAMENTO.read_text(encoding="utf-8", errors="ignore")
    return {m.lower() for m in re.findall(r"`([^`]+)`", txt)}


def main() -> int:
    args = parse_args()
    arquivos = jsonls_recentes(args.dias)
    if not arquivos:
        print(json.dumps({"status": "vazio", "dias": args.dias, "sugestoes": []},
                         ensure_ascii=False, indent=2))
        return 0
    contagem = Counter()
    for p in arquivos:
        txt = extrair_texto_usuario(p)
        contagem.update(coletar_termos(txt))
    ja_mapeados = termos_no_mapeamento()
    sugestoes = []
    for (cat, termo), freq in contagem.most_common():
        if freq < args.min_freq:
            continue
        if termo.lower() in ja_mapeados:
            continue
        sugestoes.append({"categoria": cat, "termo": termo, "frequencia": freq})
    out = {
        "status": "ok",
        "dias_analisados": args.dias,
        "arquivos": len(arquivos),
        "min_freq": args.min_freq,
        "total_sugestoes": len(sugestoes),
        "sugestoes": sugestoes[:100],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    try:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        data = datetime.now().strftime("%Y-%m-%d")
        f = SAIDA_DIR / f"sugestao-{data}.md"
        linhas = [f"# Sugestoes de atualizacao do MAPEAMENTO-HABILIDADES",
                  f"Gerado: {datetime.now().isoformat(timespec='seconds')}",
                  f"Janela: ultimos {args.dias} dias  | arquivos: {len(arquivos)}",
                  f"Min frequencia: {args.min_freq}",
                  "",
                  f"## {len(sugestoes)} candidato(s) novo(s)",
                  ""]
        for s in sugestoes[:100]:
            linhas.append(f"- [{s['categoria']}] `{s['termo']}` x{s['frequencia']}")
        f.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print(f"\n# arquivo md: {f}", file=sys.stderr)
    except Exception as e:
        print(f"# erro md: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
