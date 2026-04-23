---
titulo: Geração de laudo com template
bloco: 09_legal_medical_integration
tipo: receita
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 5
---

# Geração de laudo com template

## Pipeline canônico

`ficha.json` → template markdown com placeholders → substituição → markdown final → PDF.

Cada etapa tem ferramenta padrão, alternativas, trade-off.

## 1. Template markdown com placeholders

Arquivo `.md` com variáveis `{{campo}}`. Ex.:

```markdown
# Laudo Pericial Médico

**Processo**: {{processo.cnj}}
**Vara**: {{processo.vara}}
**Perito**: {{perito.nome}} — {{perito.crm}}
**Data do exame**: {{exame.data}}

## Identificação
{{identificacao.texto}}

## Anamnese
### Queixa principal
{{anamnese.queixa_principal}}

### História da doença atual
{{anamnese.historia_doenca_atual}}

## Exame físico
{{exame_fisico.geral}}

### Testes específicos
{{#each exame_fisico.testes_especificos}}
- **{{this.nome}}**: {{this.resultado}}
{{/each}}

## Exames complementares
{{#each exames_complementares}}
### {{this.tipo}} ({{this.data}})
{{this.resultado}}
Fonte: peça {{this.fonte_peca}}, página {{this.pagina}}.
{{/each}}

## Discussão
{{discussao}}

## Conclusão
{{conclusao}}

**CID principal**: {{cid_principal}}

## Respostas aos quesitos
{{#each respostas_quesitos}}
### Quesito {{this.numero}} ({{this.autor}})
> {{this.texto_literal}}

**Resposta**: {{this.resposta}}

{{/each}}

---
{{perito.nome}}
CRM: {{perito.crm}}
{{local}}, {{data_entrega}}
```

Engines de template:

- **Jinja2** (Python): sintaxe `{{ var }}` + `{% for %}`. Pythônico, muito flexível.
- **Handlebars** (JS/Python port): `{{#each}}`, `{{#if}}`. Leve.
- **Mustache**: mais simples, sem lógica. Seguro.
- **Mako / Chameleon**: Python alternativas.

Para Dexter: Jinja2. Já é padrão em Python, suporte a macros, filtros customizados.

## 2. Substituição via script Python

```python
from jinja2 import Environment, FileSystemLoader
import json
from pathlib import Path

env = Environment(loader=FileSystemLoader("templates/"))
env.trim_blocks = True
env.lstrip_blocks = True

template = env.get_template("laudo_base.md")

ficha = json.loads(Path("dados/processos/5001234.../ficha.json").read_text())

md = template.render(**ficha)
Path("saida/laudo.md").write_text(md)
```

Script existente no Dexter: `~/stemmia-forense/automacoes/usar_template_pericia.py` (ver `project_pericias_reaproveitaveis.md`).

## 3. Validação pós-substituição

Antes de converter para PDF:

- Nenhum placeholder ficou sem substituir (regex `\{\{.*?\}\}` → alerta).
- Nenhuma seção ficou vazia (se vazia por dado ausente, marcar `[NÃO CONSTA]` explicitamente).
- Nenhum campo com "null" ou "None" em texto visível (sintoma de bug no render).

## 4. Conversão markdown → PDF

Três opções consolidadas:

### Pandoc

```bash
pandoc laudo.md -o laudo.pdf --pdf-engine=xelatex \
  --template=tmpl-abnt.tex \
  -V mainfont="Times New Roman" \
  -V fontsize=12pt \
  -V geometry:margin=2.5cm
```

**Forte**: layout profissional, ABNT, LaTeX sob o capô, controle fino.
**Fraco**: exige LaTeX instalado, curva de aprendizado no template.

### WeasyPrint

Converte HTML+CSS em PDF. Fluxo: markdown → HTML (via `markdown` lib) → WeasyPrint → PDF.

```python
import markdown, weasyprint
html = markdown.markdown(md, extensions=["tables", "toc"])
html_completo = f"<html><head><link rel='stylesheet' href='laudo.css'></head><body>{html}</body></html>"
weasyprint.HTML(string=html_completo, base_url=".").write_pdf("laudo.pdf")
```

**Forte**: CSS padrão, visual rápido de iterar, bom para laudo "moderno".
**Fraco**: renderização CSS próxima do browser mas não 100% compatível; performance média.

### ReportLab

API programática; você "desenha" o PDF. Controle total, mas código verboso.

**Forte**: layouts com gráficos, tabelas complexas, assinatura digital embutida, formulários.
**Fraco**: verbosidade; não parte de markdown.

### Recomendação para Dexter

- Laudo padrão → Pandoc com template ABNT.
- Laudo com visual customizado (infográfico, figura) → WeasyPrint + CSS.
- Laudo com formulário preenchível / gráficos dinâmicos → ReportLab.

## 5. Assinatura digital

PDF gerado é assinado com certificado ICP-Brasil:

- Ferramenta oficial: **PJe Office Pro** (JAR em `~/.pjeoffice-pro/` — **NÃO MOVER**, path hardcoded; regra CLAUDE.md).
- Alternativas: Adobe Acrobat, iText (PyPDF2 + cryptography), Assina BR (gov.br).
- Hash do PDF + certificado gera PAdES / CAdES.
- Assinatura invalida se PDF muda depois — garantir que laudo está final antes de assinar.

## 6. Rastreabilidade embutida

Inserir no PDF (metadata ou rodapé):

- Hash SHA-256 do PDF.
- ID do laudo (LAU-2026-xxxx).
- Timestamp de geração (UTC).
- Versão do template usado.
- Git commit da ficha.json que alimentou o render.

Ver `auditability_traceability/rastreabilidade_de_laudo.md`.

## Erros comuns

- Placeholder restante no PDF final → script validador obrigatório.
- Aspas curvas/retas misturadas → filtro de normalização no Jinja.
- Acento quebrado → UTF-8 em todas as etapas.
- Quebra de página no meio de tabela → CSS `page-break-inside: avoid`.
- Template não versionado → laudo muda comportamento sem rastro.

## Referências

- Jinja2 docs.
- Pandoc manual (templates LaTeX).
- WeasyPrint docs.
- ReportLab user guide.
- Script do Dexter: `~/stemmia-forense/automacoes/usar_template_pericia.py`.
