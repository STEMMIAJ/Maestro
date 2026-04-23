---
titulo: Scripts do projeto — convenções
tipo: readme_tecnico
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# 14_automation/scripts

Convenção para scripts Python que suportam este repositório. **Esta pasta contém specs, não código.** Código real vive em `~/Desktop/STEMMIA Dexter/src/automacoes/` (alias `~/stemmia-forense/automacoes/`) para manter o repo de conhecimento leve e versionável.

## Regras

- **Python 3.11+**, stdlib primeiro; dependências externas justificadas no spec.
- **Um arquivo = um propósito**. Nome em `snake_case.py`, verbo no início (`ingest_`, `index_`, `validate_`, `refresh_`).
- **Idempotente**. Rodar 2x = mesmo resultado ou no-op.
- **Dry-run por padrão**. `--apply` para efeito. `--verbose` para log detalhado.
- **Zero efeito colateral em raw**. Jamais editar `16_inbox/raw_*/`.
- **Saída estruturada**. Log JSONL em `13_reports/automation_logs/YYYY-MM-DD_<script>.jsonl`.
- **Falhas Python**: consultar `~/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json` antes de escrever; citar IDs como `# ref: PW-012`.

## Anatomia esperada

```python
#!/usr/bin/env python3
"""
<spec one-liner>
Ref spec: 14_automation/scripts/<nome>_spec.md
"""
from __future__ import annotations
import argparse, json, logging, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[...]  # ate knowledge-tech-career/

def main(argv: list[str] | None = None) -> int:
    ...

if __name__ == "__main__":
    raise SystemExit(main())
```

## Contrato CLI mínimo

| Flag | Significado |
|---|---|
| `--dry-run` (default) | só imprime o que faria |
| `--apply` | executa escrita |
| `--since YYYY-MM-DD` | janela temporal |
| `--verbose` | log DEBUG |
| `--output <path>` | override destino relatório |

## Specs presentes

- `skill_mapping_pipeline_spec.md`
- `knowledge_refresh_pipeline_spec.md`
- `source_validation_pipeline_spec.md`

## Não-objetivos

- Não rodar como serviço longo aqui. Scheduling fica no launchd/`CronCreate`, não no script.
- Não duplicar lógica já existente no Dexter — importar de `~/stemmia-forense/automacoes/`.
