# Sessão 2026-04-19 — Unificação fluxos PJe + Skill automática

## Pedido do Dr. Jesus (transcrito)
Unificar descobrir/baixar/incluir em pasta canônica ~/Desktop/STEMMIA Dexter/src/pje/.
Separar processos PERITO vs PARTE via blacklist Consulta Pública TJMG.
Criar skill /novo-fluxo + hook PostToolUse Write.
Corrigir loop infinito do baixar_push_pje.py.
Proativizar dedup em incluir_push.py.
READMEs por blocos lógicos.
Relatório diário + bot Telegram.
Salvar sessão inteira.

## Estado inicial (problemas identificados)
1. descobrir_processos.py retornava 160 CNJs misturando PERITO + PARTE
2. baixar_push_pje.py entrava em loop infinito baixando 7× o mesmo CNJ (dedup falho — hash PJe ≠ {CNJ}.pdf)
3. incluir_push.py travava em duplicatas (verificação reativa)
4. Fluxos espalhados em 5 pastas sem fonte da verdade
5. Sem documentação por blocos
6. Ultraplan timeout 90min — abandonado

## Decisões tomadas
- Filtro perito: auxiliaresDaJustica=PERITO + blacklist via Consulta Pública TJMG
- Pasta canônica: ~/Desktop/STEMMIA Dexter/src/pje/ — nada deletado
- Skill + hook PostToolUse Write (5 AND-conditions anti-token-waste)
- README blocos lógicos (não literal linha-por-linha)
- Nada de Ultraplan — execução direta via Agent Teams paralelos

## Arquivos criados (19/abr/2026)
- src/pje/config/config_pje.py — 5413 bytes
- src/pje/descoberta/fontes/consulta_publica_tjmg.py — 6020 bytes
- src/pje/descoberta/core/filtro_perito.py — 6561 bytes
- src/pje/descoberta/blacklist_manual.txt — 519 bytes (vazio, Dr. Jesus popula manualmente)
- __init__.py em config/, descoberta/, descoberta/fontes/, descoberta/core/

## Arquivos modificados
- src/pje/download/baixar_push_pje.py — fix loop infinito via _DEDUP_INDEX persistente (~linhas 84-113)

## Bloqueios identificados
- Consulta Pública TJMG é JSF/Seam com ViewState — GET simples retorna só placeholder
- Workaround: blacklist_manual.txt onde Dr. Jesus cola CNJs copiados do form web

## Pendências pós-sessão (Dr. Jesus valida)
- Popular blacklist_manual.txt com CNJs da Consulta Pública TJMG
- Rodar descoberta e validar 3 CSVs (PERITO/INDETERMINADO/PARTE)
- Testar download com --limit 3 para confirmar fix dedup
- Criar ~/.credenciais-cnj.json com senha PJe (para AJ/AJG full)
- Decidir busca semântica: A local / B Supabase / C keywords (recomendação: C)
- Confirmar modelo relatório (recomendação: C Markdown + A Telegram)

## Pontos abertos
1. Nome do modo fracionado: REFINO-7 / ATELIÊ / DESTILAÇÃO
2. Libs polimento (tqdm+rich+tenacity+pydantic) hoje ou depois?
3. renomear_cidades.py: gerar lista de variações hoje ou sessão futura?
