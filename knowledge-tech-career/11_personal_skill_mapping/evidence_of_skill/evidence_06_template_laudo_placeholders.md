---
titulo: Gerador de laudo por template com substituição de placeholders a partir de FICHA.json
tipo: evidencia
dominio: Automação doc.
subtopico: templates + placeholder replacement
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/Desktop/STEMMIA Dexter/src/automacoes/usar_template_pericia.py
---

## Descrição
Script que aplica template de laudo pericial (acidente-trabalho, securitario-invalidez, INSS),
lê `FICHA.json` ao lado do arquivo de saída, substitui placeholders `{{CHAVE}}` com os dados,
mantém intactos placeholders não preenchidos e lista quais campos ficaram pendentes. CNJ passado
via CLI sobrescreve o do FICHA. Salva em `~/Desktop/_MESA/10-PERICIA/laudos/{CNJ}/laudo.md`
conforme regra MESA LIMPA.

## Arquivo real
`/Users/jesus/Desktop/STEMMIA Dexter/src/automacoes/usar_template_pericia.py`
(templates em `~/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/formatos-laudo/`)

## Habilidade demonstrada
- `Automação doc.templates + placeholder` — 3 (regex unicode + fallback limpo)
- `Python.sintaxe básica` — 2
- `Perícia.laudo médico-legal` — 4 (os 3 tipos cobrem o grosso do volume pericial)
- `Python.pytest / testes` — 0 (sem teste — oportunidade)

## Trecho relevante
```python
TEMPLATES_ROOT = Path.home() / "Desktop" / "_MESA" / "10-PERICIA" / "templates-reaproveitaveis"

TIPO_MAP = {
    "acidente": "formatos-laudo/acidente-trabalho.md",
    "securitario": "formatos-laudo/securitario-invalidez.md",
    "inss": "formatos-laudo/inss.md",
}

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")

def substituir(conteudo: str, dados: dict):
    nao_preenchidos = set()
    def repl(m):
        chave = m.group(1)
        if chave in dados and dados[chave] not in (None, ""):
            return str(dados[chave])
        nao_preenchidos.add(chave)
        return m.group(0)  # mantem placeholder
    novo = PLACEHOLDER_RE.sub(repl, conteudo)
    return novo, sorted(nao_preenchidos)
```

## Data
2026-04-19 (ver `project_pericias_reaproveitaveis.md` na MEMORY).

## Validação externa
**Média** — em uso. Integrado ao pipeline `/perícia [CNJ]` do hub. FICHA.json já padronizada em
vários processos reais.

## Limitações conhecidas
- Não valida tipos (tudo vira string): uma IDADE como int passa; FICHA com campo faltante vira placeholder visível.
- Não gera DOCX/PDF — só Markdown (conversão em outro script).
- INSS ainda marcado como "a criar" no docstring — verificar se existe hoje.
- Sem suite pytest.
