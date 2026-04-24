---
title: Memory
aliases: [MEMORY]
tags: [claude-memory, MEMORY]
categoria: MEMORY
sincronizado: 2026-04-19T05:26:18
---

# Memória do Sistema Stemmia Forense

## Perfil e comunicação
- [user_perfil.md](user_perfil.md) — Dados pessoais, neurodivergência, estilo de aprendizado
- [user_empresas.md](user_empresas.md) — Empresas da família (Stemmia, Clínica Minas, Minas Assistencial)
- [feedback_comunicacao.md](feedback_comunicacao.md) — Regras: direto, mínimo, sem perguntas
- [feedback_sem_fricao.md](feedback_sem_fricao.md) — Executar sem discutir, sem analogias
- [feedback_mesa_limpa.md](feedback_mesa_limpa.md) — NUNCA criar arquivos na raiz do Desktop
- [feedback_sintese_sessao.md](feedback_sintese_sessao.md) — Salvar síntese antes de compactar contexto
- [feedback_linguagem_fingida.md](feedback_linguagem_fingida.md) — PROIBIDO linguagem fingida/humanizada, tom seco sempre
- [feedback_resposta_curta_autismo.md](feedback_resposta_curta_autismo.md) — Resposta mínima 3 linhas, sem tabelas/analogias (sobrecarga sensorial)
- [feedback_explicar_termos.md](feedback_explicar_termos.md) — Sempre explicar termos técnicos, usuário esquece entre sessões
- [feedback_explicar_simples_exemplo.md](feedback_explicar_simples_exemplo.md) — Termo técnico SEM exemplo concreto = atraso. Sempre 1 frase + exemplo visual + por que importa
- [feedback_ortografia.md](feedback_ortografia.md) — SEMPRE acentuação correta, NUNCA escrever sem acentos
- [feedback_nunca_perguntar.md](feedback_nunca_perguntar.md) — NUNCA perguntar "quer que eu faça?" quando ação já foi pedida
- [feedback_no_computer_use.md](feedback_no_computer_use.md) — NUNCA usar computer-use sem autorização explícita

- [feedback_sync_upload.md](feedback_sync_upload.md) — SEMPRE subir PDFs/HTMLs pro site via FTP + atualizar Planner

- [feedback_pje_windows.md](feedback_pje_windows.md) — PJe SÓ no Windows/Parallels, NUNCA Mac Chrome
- [reference_executar_windows_parallels.md](reference_executar_windows_parallels.md) — `open -a "Parallels Desktop" arquivo.bat` executa no Windows sem computer-use

## Feedback operacional (como trabalhar)
- [feedback_hooks_sobrecarga.md](feedback_hooks_sobrecarga.md) — Hooks excessivos degradam performance, manter 7 essenciais (revisado 16/abr)
- [feedback_agent_teams.md](feedback_agent_teams.md) — Agent Teams (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) é essencial
- [feedback_progresso_real.md](feedback_progresso_real.md) — SEMPRE mostrar % de progresso real em tarefas longas
- [feedback_continuidade_sessao.md](feedback_continuidade_sessao.md) — Ler diário antes de qualquer ação
- [feedback_documentacao_fluxos.md](feedback_documentacao_fluxos.md) — Documentar fluxos antes de executar
- [feedback_nao_decidir_sozinho.md](feedback_nao_decidir_sozinho.md) — Ler fluxo existente antes de criar novo
- [feedback_processar_casos_reais.md](feedback_processar_casos_reais.md) — Prioridade: casos reais > infraestrutura
- [feedback_sem_perguntas.md](feedback_sem_perguntas.md) — Extrair do contexto e executar
- [feedback_plugins.md](feedback_plugins.md) — Documentar plugins ao instalar/criar
- [feedback_planos_completos.md](feedback_planos_completos.md) — Planos: decidir e fazer, sem perguntas triviais
- [feedback_otimizar_tempo.md](feedback_otimizar_tempo.md) — Velocidade máxima: paralelo sempre, gastar tokens > gastar tempo
- [feedback_n8n_mentira.md](feedback_n8n_mentira.md) — NUNCA dizer que nao pode usar N8N, MCP funciona
- [feedback_lentidao_startup.md](feedback_lentidao_startup.md) — Lentidao no inicio irrita, agir primeiro
- [feedback_tudo_opus.md](feedback_tudo_opus.md) — Tudo Opus, NUNCA sugerir trocar modelo por agente
- [feedback_parar_configurar.md](feedback_parar_configurar.md) — Parar de configurar, usar para trabalho real
- [feedback_verificar_antes_declarar.md](feedback_verificar_antes_declarar.md) — NUNCA dizer "feito" sem output de verificação comprovada
- [feedback_max_2_retries.md](feedback_max_2_retries.md) — Falhou 2x = mudar estratégia, diagnosticar causa raiz
- [feedback_nunca_rm_rf.md](feedback_nunca_rm_rf.md) — NUNCA rm -rf, usar mv /tmp/ como padrão seguro
- [feedback_estrutura_pastas.md](feedback_estrutura_pastas.md) — SEMPRE criar pasta estruturada + README mestre detalhado em projeto novo

## Plugins instalados
- [reference_ruflo.md](reference_ruflo.md) — Ruflo v3.5.51: orquestrador de swarms, memória, 98 agents, 30 skills, MCP
- [reference_mcps_juridicos.md](reference_mcps_juridicos.md) — MCP Brasil (326 tools), PJe MCP, escavador, busca-processos-judiciais

## Projeto Dexter (hub central perícias)
- [project_dexter.md](project_dexter.md) — STEMMIA Dexter: hub reorganizado, bot novo, monitor movimentações

## Ultraplan fix (16/abr/2026)
- [project_ultraplan_fix.md](project_ultraplan_fix.md) — GitHub remote + hook auto-sync + fix symlink CLAUDE.md

## Unificação STEMMIA (17/abr/2026)
- [project_unificacao_stemmia.md](project_unificacao_stemmia.md) — Plano-mestre 12 tarefas: unificar captação→laudo no Dexter + Fluxo D novo + banco SQLite de aprendizado contínuo

## Otimização de tokens
- [reference_guia_tokens.md](reference_guia_tokens.md) — Guia completo em STEMMIA Dexter (4 níveis, 7 scripts, cronograma 6 dias)

## Referências-raiz
- [reference_n8n_server.md](reference_n8n_server.md) — Servidor N8N self-hosted (https://n8n.srv19105.nvhm.cloud)
- Hub principal: ~/Desktop/STEMMIA Dexter/ (reorganizado 07/abr/2026)
- Pasta sistema: ~/Desktop/STEMMIA — SISTEMA COMPLETO/
- Diário: ~/Desktop/STEMMIA — SISTEMA COMPLETO/DIARIO-DO-SISTEMA.md
- Índice geral: ~/Desktop/ANALISADOR FINAL/Analisa Processual Completa/07-metodos/00-INDICE-GERAL.md
- [reference_ftp_deploy.md](reference_ftp_deploy.md) — FTP deploy (senha atualizada 16/mar/2026)
- [reference_gemini_key.md](reference_gemini_key.md) — Chave Gemini + IDs workflows N8N
- [reference_plan_mode.md](reference_plan_mode.md) — Pasta de projetos Plan Mode

## Projeto Fenix (PRIORIDADE MAXIMA)
- [project_fenix.md](project_fenix.md) — Reorganizacao profissional: rotina, usar ferramentas existentes, processar casos reais
- [feedback_fenix_foco.md](feedback_fenix_foco.md) — NUNCA criar infra nova, cada sessao = 1 processo resolvido

## Download PJe (FUNCIONANDO desde 13/abr/2026)
- [project_download_pje_139.md](project_download_pje_139.md) — Fluxo COMPLETO: Selenium + Chrome debug 9223 + perfil isolado. Detalhado.
- [project_pje_erros_log.md](project_pje_erros_log.md) — Log de TODOS os erros de cada execução do script PJe
- [project_comunica_pje.md](project_comunica_pje.md) — Cadastro PENDENTE no Comunica PJe (CNJ) para intimações centralizadas

## Monitor de Movimentações (14/abr/2026)
- [project_monitor_ativacao.md](project_monitor_ativacao.md) — Plano: ativar DataJud cron + Comunica PJe + hub.py
- [project_monitor_fontes.md](project_monitor_fontes.md) — MONITOR-FONTES: orquestrador 5 fontes + dashboard + Telegram + launchd 3x/dia (17/abr/2026)

## Reorganização de Ferramentas (14/abr/2026)
- [project_reorganizacao_ferramentas.md](project_reorganizacao_ferramentas.md) — Centralizar scripts no Dexter + docs padronizadas + Obsidian + relatório no site

## Projetos ativos
- [project_clinica_minas.md](project_clinica_minas.md) — Sistema Clínica Minas (fase requisitos)
- [project_automacoes.md](project_automacoes.md) — Monitor publicações, OpenClaw, bot Telegram
- [project_n8n_analise_pericial.md](project_n8n_analise_pericial.md) — Pipeline análise pericial (local OK, N8N cloud bloqueado)
- [project_pesquisador_produtos.md](project_pesquisador_produtos.md) — Workflow N8N pesquisador multi-loja
- [project_banco_dados_2.md](project_banco_dados_2.md) — Banco de Dados 2.0 (Direito/Medicina/Perícia/TI — 155 pastas, vazio)

## Referências de contato
- [reference_email_pericial.md](reference_email_pericial.md) — Email pericial: perito@drjesus.com.br (NÃO recebe intimações)

## Compras e pesquisas
- [feedback_salvar_busca.md](feedback_salvar_busca.md) — "salva essa busca" → salvar em ~/Desktop/Compras Apartamento/{categoria}/

## Contexto pessoal
- [project_pai_falecimento.md](project_pai_falecimento.md) — Pai faleceu 11/fev/2026, sobrecarga
- [project_apartamento_gv.md](project_apartamento_gv.md) — Mudança de apartamento GV

## Sistema Anti-Mentira (17/abr/2026)
- [reference_anti_mentira.md](reference_anti_mentira.md) — Hooks que bloqueiam claims sem verificação + capturam frustração + destilam erros em novas memórias

## Incidente recuperação 19/abr/2026
- [project_claude_revolucao.md](project_claude_revolucao.md) — PASTA MESTRE ~/Desktop/CLAUDE REVOLUÇÃO/ (16 arquivos, 290KB). Documenta TUDO do sistema.
- [feedback_mapeamento_habilidades.md](feedback_mapeamento_habilidades.md) — Atualizar MAPEAMENTO-HABILIDADES.md a cada sessão com evidências novas. ZERO bajulação.
- [project_recuperacao_19abr2026.md](project_recuperacao_19abr2026.md) — Diagnóstico+recuperação. Time Machine OFF causou perda. Skills intactas, settings.json restaurar.
- [feedback_nao_oferecer_limpeza.md](feedback_nao_oferecer_limpeza.md) — PROIBIDO oferecer limpar/reorganizar sem palavra LIMPAR-LIBERADO. Causou perda de dias.
- [feedback_avisar_recursos_existentes.md](feedback_avisar_recursos_existentes.md) — ANTES de propor criar X, buscar se X já existe. Caso jsonl: meses pedindo o que já existia.
- [reference_obsidian_notion.md](reference_obsidian_notion.md) — Obsidian (local MD) vs Notion (cloud). Recomendação: Obsidian para prática pericial.
- [project_camada_seguranca_planner.md](project_camada_seguranca_planner.md) — PENDENTE: proteger /teste/backup-claude/ com .htaccess + auth + noindex.

## Sistema (atualizado 16/abr/2026)
- 85 agentes, 17 MCPs, 7 hooks, 25 plugins, 98+ scripts, Claude Code v2.1.112, Opus 4.7
- Docs offline: ~/Desktop/última tentativa/docs-claude-code/ (20 páginas)
- Telegram: @stemmiapericia_bot (chat_id: 8397602236)
- Permissões: Bash(*), Edit(*), Write(*), WebFetch(*), WebSearch — ZERO fricção
