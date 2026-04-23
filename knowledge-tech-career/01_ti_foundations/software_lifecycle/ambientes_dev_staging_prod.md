---
titulo: "Ambientes dev, staging e produção"
bloco: "01_ti_foundations/software_lifecycle"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 4
---

# Ambientes dev, staging e produção

Software maduro roda em cópias isoladas chamadas *ambientes*. Separar reduz risco de corromper dados reais ao experimentar.

## Dev (desenvolvimento)

Ambiente onde o código está sendo escrito e testado pelo autor.

- **Onde**: máquina do próprio desenvolvedor (seu Mac).
- **Dados**: falsos ou anonimizados; banco local pequeno.
- **Estabilidade**: baixa — quebra esperada, faz parte do trabalho.
- **Acesso**: só o dev.
- **Exemplo no Dexter**: rodar `monitorar_movimentacao.py` apontando para banco SQLite de teste em `/tmp/`.

## Staging (homologação)

Réplica fiel de produção, porém isolada, usada para validação final antes de soltar ao usuário real.

- **Onde**: servidor idêntico ao de produção (mesmo SO, mesma versão de Python, mesma config).
- **Dados**: cópia mascarada de produção ou dados sintéticos realistas.
- **Estabilidade**: alta — se quebrar em staging, não vai para prod.
- **Acesso**: devs, QA, stakeholders internos.
- **Finalidade**: descobrir bug que só aparece com dado real e carga real (integração com API externa, performance, migração de banco).

## Produção (prod)

Ambiente acessado por usuários finais. Dados reais, consequências reais.

- **Onde**: infra definitiva (VPS, cloud, data center).
- **Dados**: reais, sob LGPD, com backup e criptografia.
- **Estabilidade**: máxima — indisponibilidade significa cliente irritado, prejuízo, eventual ação judicial.
- **Acesso**: restrito; alterações só via pipeline auditado.
- **Exemplo no Dexter**: `stemmia.com.br`, VPS `srv19105` do N8N, Planner em uso pelo escritório.

## Variantes intermediárias

- **Test / CI** — ambiente efêmero criado pelo pipeline para rodar testes automatizados.
- **QA** — dedicado a analistas de qualidade; entre dev e staging.
- **Preview / review app** — um ambiente por pull request, destruído ao *merge*. Vercel, Netlify fazem isso automaticamente.

## Por que separar

1. **Proteção de dados reais** — não testar migração destrutiva em cima do banco do Planner.
2. **Isolamento de falha** — bug em dev não derruba cliente.
3. **Reprodutibilidade** — diferença dev vs prod revela config implícita ("funciona na minha máquina").
4. **Segurança** — credenciais diferentes; vazamento de chave dev não compromete prod.
5. **Conformidade** — LGPD exige segregação de ambiente de teste com dado pessoal.

## Variáveis por ambiente

Configuração varia, código é o mesmo. Armazenar em variável de ambiente (`.env`):

```
# dev
DATABASE_URL=sqlite:///tmp/laudos_dev.db
DATAJUD_API_KEY=chave_sandbox
LOG_LEVEL=DEBUG

# prod
DATABASE_URL=postgres://user:senha@srv19105/laudos_prod
DATAJUD_API_KEY=chave_real
LOG_LEVEL=WARNING
```

Nunca commitar `.env`. Sempre ter `.env.example` no repositório.

## Fluxo típico

```
código → dev → CI/testes → staging → aprovação → prod
```

Promoção entre ambientes é automatizada (pipeline) e auditável (log de deploy).

## Por que importa para o perito

- **Perícia em incidente de produção** (indisponibilidade de e-commerce) frequentemente revela deploy direto do dev para prod, sem staging — falha de processo.
- **Vazamento de dados de staging** ainda é vazamento se o dado não foi devidamente mascarado; LGPD se aplica.
- **Seu próprio Dexter**: banco de treino do modelo pericial deve ficar separado do banco real de casos; misturar contamina experimentos.

## Referências

- The Twelve-Factor App — 12factor.net/config.
