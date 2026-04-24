# Opcoes de banco de dados — inicial (qualitativo)

Gerado em 2026-04-22. Sem custos. So comparacao direcional.

## Cenario de uso
- Guardar FICHA.json de cada processo (metadados, sem PII sensivel).
- Guardar tarefas do Maestro (espelho opcional).
- Alimentar dashboard publico stemmia.com.br com metricas agregadas.
- Receber logs de cron (opcional).

## Opcoes

### 1) Supabase
Pros:
- Postgres gerenciado + Auth + Storage.
- SDK para Next.js / Astro simples.
- Row Level Security para proteger dados de pacientes.
- Dashboard web proprio.
Contras:
- Dependencia externa.
- Plano free tem limites (RESEARCH).
- Egresso caro em escala.
Integracao com Telegram: via webhook ou polling Python.
Integracao com dashboard: nativa.
Dificuldade de manter sozinho: baixa.

### 2) SQLite local + export para site
Pros:
- Zero custo.
- Backup = copiar arquivo.
- Ja cabe no fluxo atual.
Contras:
- Nao multi-usuario.
- Dashboard precisa ler DB -> gera arquivo JSON para site (publicar por git ou rsync).
- Sem auth nativa.
Integracao: gerar JSON estatico, site consome.
Dificuldade: baixissima.

### 3) Postgres self-hosted (VPS)
Pros:
- Controle total.
- Pode encriptar em repouso.
Contras:
- Manutencao (patches, backups).
- Hardening obrigatorio.
- Custo de VPS.
Dificuldade: alta.

### 4) JSON files + indexacao (baseline)
Pros:
- Ja funciona (FICHA.json existe).
- Git versiona.
Contras:
- Busca limitada.
- Nao escala alem de ~1000 processos.
Dificuldade: zero.

## Topologia hibrida sugerida (se adotar Supabase)
- Local: JSON files + SQLite opcional.
- Remoto: Supabase Postgres com subset agregado (sem PII).
- Backup: dump periodico -> area restrita em stemmia.com.br.

## Backup local + no site
- Local: `_arquivo/backups/maestro_<data>/` (diario).
- No site: `stemmia.com.br/_backups/` (area protegida por .htaccess ou basic auth) — RESEARCH se a hospedagem permite.
- Cifrar com gpg simetrico antes de upload.

## O que depende de pesquisa futura (RESEARCH)
- Limites do Supabase free tier em 2026.
- Se hospedagem do stemmia.com.br suporta area privada com auth.
- Compliance (dados pericia, LGPD).

## Recomendacao provisoria (para validar)
Comecar com opcao 4 (JSON) + opcao 2 (SQLite) em paralelo. Migrar para Supabase quando dashboard exigir queries dinamicas.
