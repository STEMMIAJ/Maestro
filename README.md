# STEMMIA Dexter

Repositorio central do sistema pericial do Dr. Jesus Eduardo Noleto de Oliveira.
Hub unico para gestao de 74+ processos judiciais, pericias medicas, peticoes, laudos e automacoes.

**CRM:** ativo | **Funcao:** perito judicial nomeado | **Especialidade:** pericias medicas judiciais

---

## Inicio rapido de sessao

```
1. Ler MEMORIA.md         → quem sou, prioridades, locais
2. Ler 00-CONTROLE/AGORA.md → foco atual, estado, bloqueios
3. Ler DECISOES.md         → decisoes tomadas (evitar retrabalho)
4. Ler ROTINA.md           → sequencia diaria padrao
5. Trabalhar.
```

Regra absoluta: processos judiciais reais antes de qualquer configuracao, site ou estetica.

---

## Estrutura de pastas

```
STEMMIA Dexter/
├── 00-CONTROLE/              # Estado atual, indices, prompts operacionais
│   ├── AGORA.md              # Foco da sessao atual
│   ├── indices/              # Indices gerados automaticamente
│   └── PROCESSOS-BAIXADOS-*.md
│
├── agents/                   # Definicoes de agentes Claude
│   ├── clusters/             # Grupos: analise, pesquisa, redacao, roteiro, verificacao
│   └── orquestradores/       # Orquestradores de fluxo
│
├── AUTOMACAO/                # Automacoes e monitoramento
│   ├── n8n/                  # Workflows N8N exportados
│   ├── FONTES-MONITORAMENTO.md
│   ├── FLUXOS-N8N.md
│   ├── MEUS-PROCESSOS.md
│   ├── MAPA-AUTOMACAO.html
│   └── PROGRESSO.html
│
├── BANCO-DADOS/              # Bases de conhecimento
│   ├── casos-clinicos/
│   ├── DIREITO/              # 23 subdiretorios tematicos
│   ├── MEDICINA/             # 59 subdiretorios por especialidade
│   ├── PERICIA/              # Protocolos, escalas, tabelas
│   ├── TI e IA/              # Notas sobre ferramentas e automacao
│   ├── GERAL/                # Banco Geral (1,5 GB, ex-ANALISADOR FINAL)
│   └── BANCO-GERAL-LINK      # Atalho interno -> ./GERAL
│
├── PYTHON-BASE/              # Base de conhecimento Python (ex-_MESA/01-ATIVO)
│   ├── 03-FALHAS-SOLUCOES/   # falhas.json com 90+ entradas
│   ├── 06-TEMPLATES/         # templates prontos
│   ├── _INDICE-CONSULTAVEL.md       # gerado automaticamente
│   └── _RELATORIO-CRESCIMENTO.html  # dashboard
│
├── CONVERSAS/                # Transcricoes uteis
│   ├── claude-code/
│   └── codex/
│
├── data/                     # Dados operacionais
│   ├── banco-geral/
│   ├── bases-dados/
│   ├── inbox/
│   ├── processos/
│   └── saida/
│
├── DOCS/                     # Documentacao do sistema
│   ├── docs-offline/         # Docs Claude Code offline (20 paginas)
│   ├── guias/
│   ├── pesquisas/
│   ├── MIGRACAO.md           # Guia de migracao de scripts
│   ├── FLUXOS.md             # Fluxos operacionais documentados
│   └── GUIA-MCPs.md          # Resumo dos MCPs instalados
│
├── FERRAMENTAS/              # Ferramentas especializadas
│   ├── analisador-novo/      # Analisador processual v2
│   ├── analisador-ultra/     # Analisador com IA
│   ├── analise-nova/
│   ├── juridicas/            # Ferramentas juridicas especificas
│   ├── openclaw/             # Pesquisa jurisprudencia OpenClaw
│   ├── openclaw-config/      # Configuracao do OpenClaw
│   ├── pesquisador-honorarios/ # Pesquisa e dashboard de honorarios
│   ├── CIF-CHECKLIST.html    # Checklist CIF interativo
│   ├── CIF-IFBrM.html       # Indice funcional brasileiro modificado
│   ├── CIF-WHODAS.html       # WHODAS 2.0 interativo
│   └── MEEM-interativo.html  # Mini exame do estado mental
│
├── GITs/                     # Repositorios git
│   └── cowork-pericia/
│
├── hooks/                    # Hooks do Claude Code (local)
│
├── INBOX/                    # Entrada de conteudo externo
│   └── instagram/            # Links e prints do Instagram
│
├── memoria/                  # Memoria persistente
│   ├── base-conhecimento/
│   ├── conversas/
│   └── feedback/
│
├── MODELOS/                  # Templates de documentos
│   ├── peticoes-antigas/
│   └── peticoes-formais/
│
├── MODELOS PETICOES PLACEHOLDERS/  # Templates com variaveis
│   ├── aceite/
│   ├── agendamento/
│   ├── disponibilidade/
│   ├── esclarecimentos/
│   ├── escusa/
│   ├── proposta/
│   ├── prorrogacao/
│   └── requisicao/
│
├── MUTIRAO/                  # Mutiroes periciais
│   ├── escalas/
│   ├── processos/
│   ├── referencias/
│   ├── roteiros-gerados/
│   └── templates/
│
├── Mutirao Conselheiro Pena/  # Mutirao especifico
│
├── n8n/                      # Workflows N8N (destino migracao)
│
├── painel/                   # Dashboard web
│   └── assets/
│
├── PERICIA FINAL/            # Pipeline completo de pericia
│   ├── dados_brutos/         # Dados AJ, AJG, DataJud, DJe, PJe
│   ├── dados_normalizados/
│   ├── docs/
│   ├── downloads/
│   ├── fases/                # Fases do pipeline
│   ├── logs/
│   ├── output/               # Saida consolidada
│   ├── scripts/              # 18 scripts especificos
│   └── templates/
│
├── PROCESSOS -> ~/Desktop/ANALISADOR FINAL/processos/  (SYMLINK)
├── PROCESSOS-PENDENTES/      # Downloads pendentes, PDFs soltos
│
├── referencias/              # Material de referencia
│   ├── checklist/
│   ├── escalas/
│   ├── protocolos/
│   └── tabelas/
│
├── RELATORIOS/               # Relatorios gerados
│   ├── pdfs/
│   └── screenshots/
│
├── SCRIPTS -> ~/Desktop/ANALISADOR FINAL/scripts/  (SYMLINK)
│
├── SESSOES/                  # Registros de sessoes de trabalho
│
├── skills/                   # Skills do Claude Code (local)
│
├── src/                      # Codigo-fonte (destino migracao)
│   ├── honorarios/
│   ├── jurisprudencia/
│   ├── peticoes/
│   ├── pipeline/
│   │   └── verificadores/
│   ├── pje/
│   └── utils/
│
├── templates/                # Templates padronizados
│   ├── laudo/
│   ├── peticao/
│   ├── relatorio/
│   └── roteiro/
│
├── _arquivo/                 # Pastas inativas (25+ itens arquivados)
│
├── CLAUDE.md                 # Instrucoes para Claude Code
├── CODEX.md                  # Instrucoes para Codex
├── DECISOES.md               # Registro de decisoes tomadas
├── INVENTARIO.md             # Inventario completo do sistema
├── MEMORIA.md                # Contexto do usuario e prioridades
└── ROTINA.md                 # Rotina diaria padrao
```

---

## Scripts principais

Os scripts ficam em `~/Desktop/ANALISADOR FINAL/scripts/` (57 scripts Python), acessiveis via symlink `SCRIPTS/`.

### Triagem e organizacao

| Script | Funcao |
|--------|--------|
| `scanner_processos.py` | Varre pasta de PDFs e identifica processos por CNJ |
| `padronizar_pastas.py` | Organiza processos na estrutura CNJ padrao |
| `classificar_documento.py` | Classifica tipo de documento (peticao, sentenca, laudo etc) |
| `classificar_acao.py` | Identifica tipo de acao (civel, trabalhista etc) |
| `detectar_urgencia.py` | Gera URGENCIA.json com nivel de prioridade |
| `inbox_processor.py` | Processa PDFs novos da INBOX |

### Extracao e analise

| Script | Funcao |
|--------|--------|
| `pipeline_analise.py` | Pipeline completo de 7 etapas de analise processual |
| `extrair_partes.py` | Extrai partes do processo (autor, reu, perito etc) |
| `extrair_quesitos.py` | Extrai quesitos periciais do texto |
| `resumir_fatos.py` | Resume fatos relevantes do processo |
| `sequencia_cronologica.py` | Monta linha do tempo do processo |
| `triagem_complexidade.py` | Avalia complexidade da pericia |
| `localizar_nomeacao.py` | Localiza ato de nomeacao do perito |

### Peticoes e laudos

| Script | Funcao |
|--------|--------|
| `gerar_peticao.py` | Gera peticao a partir de template + dados do processo |
| `gerar_aceite_rapido.py` | Gera aceite de nomeacao simplificado |
| `gerar_aceites_lote.py` | Gera aceites em lote para multiplos processos |
| `gerar_checklist.py` | Gera checklist pericial por tipo de acao |
| `gerar_mutirao.py` | Gera roteiro para mutirao pericial |
| `laudo_pipeline.py` | Pipeline de geracao de laudo |
| `md_para_pdf.py` | Converte Markdown para PDF |
| `md_para_xml_peticao.py` | Converte Markdown para XML de peticao PJe |

### Honorarios

| Script | Funcao |
|--------|--------|
| `calcular_honorarios.py` | Calcula honorarios periciais |
| `verificar_proposta.py` | Verifica proposta de honorarios |

### Monitoramento

| Script | Funcao |
|--------|--------|
| `monitor.py` | Monitor geral de publicacoes |
| `monitorar_movimentacao.py` | Monitora movimentacoes processuais |
| `deadline_monitor.py` | Monitora prazos e alerta vencimentos |
| `briefing_diario.py` | Gera briefing diario de pendencias |
| `notificar_telegram.py` | Envia notificacoes via Telegram |

### Consultas externas

| Script | Funcao |
|--------|--------|
| `consultar_aj.py` | Consulta Assistencia Judiciaria |
| `consultar_ajg.py` | Consulta Assistencia Judiciaria Gratuita |
| `sincronizar_aj_pje.py` | Sincroniza dados AJ com PJe |
| `pje_standalone.py` | Acesso standalone ao PJe |
| `descobrir_processos.py` | Descobre processos novos via DataJud |

### Administracao

| Script | Funcao |
|--------|--------|
| `orquestrador_noturno.py` | Roda tarefas automaticas a noite |
| `auditar_sistema.py` | Audita integridade do sistema |
| `gestor-processos.py` | Interface de gestao de processos |
| `deploy_site.py` | Deploy do site via FTP |
| `relatorio_semanal.py` | Gera relatorio semanal |
| `gerar_guia_comandos.py` | Gera guia de comandos apos criar skill/agente |

---

## Dependencias

```bash
# Sistema
Python 3.10+
pdftotext (poppler-utils)
tesseract-ocr
jq

# Python
pip install click rich selenium requests beautifulsoup4 pdfplumber

# Opcional
chromedriver (para PJe via Selenium)
```

---

## Acesso pelo Windows (Parallels)

```
\\Mac\Home\Desktop\STEMMIA Dexter\
```

PJe so funciona no Windows/Parallels com Chrome debug porta 9223 e perfil isolado.

---

## Contagem do sistema

- **Processos ativos:** 74+
- **Scripts Python:** 57 (ANALISADOR FINAL) + 18 (PERICIA FINAL)
- **Agentes Claude:** 85
- **MCPs configurados:** 17+
- **Workflows N8N:** 4 exportados
- **Templates de peticao:** 8 tipos com placeholders
- **Bases de dados:** Direito (23), Medicina (59), Pericia, TI/IA
- **Ferramentas interativas:** CIF-CHECKLIST, CIF-IFBrM, CIF-WHODAS, MEEM

---

## Arquivos de controle

| Arquivo | Funcao |
|---------|--------|
| `MEMORIA.md` | Quem sou, como trabalho, prioridades |
| `DECISOES.md` | Registro de toda decisao tomada |
| `ROTINA.md` | Sequencia diaria padrao |
| `00-CONTROLE/AGORA.md` | Estado atual e foco da sessao |
| `INVENTARIO.md` | Mapa completo de pastas e symlinks |
| `CLAUDE.md` | Instrucoes para Claude Code |
| `CODEX.md` | Instrucoes para Codex |
