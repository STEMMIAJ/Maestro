# Quem faz o quê

Divisão de responsabilidade por ator. Regra: se sair dessa lista, **é manual e é teu problema**.

## 1. VOCÊ (humano, Dr. Jesus)

1. Logar em AJ TJMG, AJG CJF, PJe TJMG, PJe TRF6 (tudo que exige certificado ou senha).
2. Resolver captcha (TJMG jurisprudência: 1ª vez; depois a sessão fica salva).
3. Marcar processo na aba PUSH do PJe e escrever cidade+vara na observação **antes** de acionar download.
4. Ler o processo e decidir conclusão pericial (CID, incapacidade, nexo, DII/DID).
5. Aprovar/rejeitar valor de proposta de honorários, petição final, laudo final.
6. Assinar PDF no PJeOffice (fora do escopo automático).
7. Dizer `LIMPAR-LIBERADO` quando autorizar exclusão de arquivos.

## 2. CLAUDE CODE (sessão atual, você falando comigo)

1. Ler pastas, descrever estrutura, atualizar arquivos .md.
2. Criar/ajustar scripts Python que **não envolvem login nem captcha**.
3. Rodar pipelines já existentes (análise de PDFs já baixados, geração de petição a partir de FICHA).
4. Indexar FICHA.json no banco local (`indexer_ficha.py`).
5. Consultar MCPs (context7, brlaw, sentry, PubMed) para pesquisa.
6. Manter a CENTRAL-DE-FLUXOS-MAESTRO atualizada.
7. **Nunca** empurrar pro GitHub sem pedido explícito.

## 3. COWORK (`~/Desktop/STEMMIA Dexter/cowork/`)

1. Biblioteca de templates de petição (em `02-BIBLIOTECA/`).
2. Motor `aplicar_template.py` que recebe FICHA.json + TEMPLATE.md e gera petição preenchida.
3. Pipelines documentados (`04-PIPELINES/*.md`) — servem como mapa, nem todos têm todos os agentes prontos.
4. Escopo: **1 processo por vez**. Não é para lote.

## 4. OPENCLAW (futuro, hoje congelado)

1. Rodar cron noturno (quando destravado): coletar jurisprudência pública, atualizar bases, refazer índices.
2. Tarefas que **não dependem de login** (scraping público estável).
3. **Hoje = 0% ativo.** Cron vazio, 0 agentes. Ignorar até destravar explicitamente.

## 5. GITHUB (STEMMIAJ/Maestro)

1. Versionar scripts, templates e estes .md de fluxo.
2. **Não guardar segredo sensível** (tokens Telegram, senhas PJe, cookies).
3. Hoje: hook automático empurra `conversations/` pro `main` sem revisão. **A auditar.**
4. Branches órfãs pendentes: `feat/003-openclaw-daemon`, `doc/008-peticoes-catalogo`.

## Conflitos atuais

- Agentes paralelos colidiram em 24/abr (commit de petições na branch do OpenClaw). **Resolver manualmente depois.**
- PERFIL-ESTILO.json (88KB, 68 petições analisadas) está no iCloud, **não plugado em nenhum script**. Decisão pendente: copiar local ou descartar.

## Regra única

Antes de fazer algo novo, perguntar: **quem era para fazer isso?** Se for humano e eu tentar automatizar login/captcha, paro. Se for Claude Code e você tentar fazer manualmente, me pede.
