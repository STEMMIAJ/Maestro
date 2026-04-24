# FLUXO 01 — Captura de processos

## Objetivo

Saber quais processos caíram para o perito **antes** de o prazo estourar. Fonte varia: AJ TJMG, AJG CJF, PJe TJMG direto, DJEN (CNJ), Comunica PJe.

## Passos (como funciona hoje)

1. Abrir navegador (Chrome ou Safari) e logar no **AJ TJMG** (https://www.tjmg.jus.br/... auxílio judicial).
2. Abrir navegador e logar no **AJG CJF** (https://www.cjf.jus.br/... auxílio justiça gratuita — Justiça Federal).
3. Rodar script que identifica processos novos e extrai a lista.
4. Cruzar lista com banco local (FICHA.json existentes) para saber o que é novo.

## PROBLEMA PJe

A maior parte das nomeações **chega pelo PJe direto**, não aparece no AJ/AJG. Tentativas existentes:

- **DJEN (CNJ)** — Diário de Justiça Eletrônico Nacional, cobre publicações de todos tribunais.
- **DataJud (CNJ)** — API pública com movimentações processuais.
- **Comunica PJe (CNJ)** — notificações centralizadas (cadastro ainda pendente do Dr. Jesus).

Esses 3 estão parcialmente implementados mas **não consolidados num único script rodante**.

## Ideias existentes (não consolidadas)

- Cruzar DJEN + DataJud + Comunica PJe num orquestrador único.
- Filtrar só por nomeações do Dr. Jesus usando nome + CRM.
- Notificar via Telegram quando CNJ novo aparecer.

## SCRIPTS EXISTENTES

### Núcleo AJ / AJG
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/pje/consultar_aj.py` | Consulta AJ TJMG | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/consultar_ajg.py` | Consulta AJG CJF | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/sincronizar_aj_pje.py` | Cruza AJ com PJe | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/aj_tjmg.py` | Adapter AJ TJMG (novo monitor) | RASCUNHO (deferred) |
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/ajg_cjf.py` | Adapter AJG CJF (novo monitor) | RASCUNHO (deferred) |
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/exemplos-reais/exemplo-2-monitor-pericial/adapters/aj_tjmg.py` | Exemplo consolidado AJ TJMG | DUVIDOSO (exemplo) |
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/aj_jt.py` | Adapter AJ Justiça do Trabalho | RASCUNHO (deferred) |

### DJEN / DataJud / Comunica PJe
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/djen.py` | Fonte DJEN no monitor novo | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/monitor-publicacoes/dje_tjmg.py` | DJE TJMG (estadual) | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/jurisprudencia/utils/datajud_api.py` | Cliente DataJud (CNJ) | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/datajud_client.py` | Outro cliente DataJud | DUVIDOSO (tem `_analise-erros/ERROS-datajud_client.py.md`) |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/02-INTEGRACAO-DATAJUD/comunica_pje.py` | Comunica PJe legado | DUVIDOSO (legado) |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta/descobrir_processos.py` | Descobre processos novos | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/jurisprudencia/descobrir_processos.py` | Variante na pasta jurisprudência | DUVIDOSO |

### Monitor consolidado (projeto novo 22/abr/2026)
| Caminho | O que faz |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/` | Pasta inteira do monitor async novo. Lê DJEN + filtro homônimo (irmão). Handoff em `04-docs/HANDOFF.md` |

## O que está FUNCIONANDO hoje

- Consultar AJ TJMG e AJG CJF manualmente via `consultar_aj.py` / `consultar_ajg.py` (stemmia-forense).
- Ler DJEN via `dje_tjmg.py`.
- Consultar DataJud via `datajud_api.py` (stemmia-forense/jurisprudencia).

## O que está PARCIAL

- Monitor novo (pasta `monitor-processos-novo-2026-04-22/`) — código em pé mas adapters AJ/AJG marcados `_deferred/`.
- Comunica PJe — só legado, nunca integrado.

## O que é só IDEIA

- Orquestrador único cruzando 5 fontes.
- Notificação Telegram no momento da nomeação.
- Cadastro Dr. Jesus no Comunica PJe (pendência do humano).

## Próximos passos possíveis (NÃO EXECUTAR AGORA)

1. Ativar adapters `_deferred/aj_tjmg.py` + `ajg_cjf.py` do monitor novo.
2. Consolidar descobrir_processos.py (tem 2 versões divergentes).
3. Auditar `datajud_client.py` contra os erros em `_analise-erros/`.
4. Dr. Jesus se cadastra no Comunica PJe (fora do Claude Code).
