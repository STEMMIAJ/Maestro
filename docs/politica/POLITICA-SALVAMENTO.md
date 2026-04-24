# Política de Salvamento — regras de QUANDO salvar

> Vale para Claude (agente) e para Dr. Jesus. Ordem: RULES.md > esta política.

## 1. Gatilhos obrigatórios de COMMIT

Commit acontece **imediatamente** em qualquer um destes eventos:

| Gatilho | Exemplo | Mensagem-padrão |
|---|---|---|
| Arquivo novo criado e útil | Novo script funcional | `feat(<escopo>): adicionar <nome>` |
| Bug corrigido | Script parou de falhar | `fix(<escopo>): corrigir <o que>` |
| Refactor concluído | Reorganização de código | `refactor(<escopo>): <descrição>` |
| Doc criada ou alterada | Novo .md | `doc(<escopo>): adicionar <título>` |
| ADR aprovado | Decisão grande documentada | `doc(adr): ADR-NNNN <título>` |
| Handoff preenchido | Fim de sessão | `chore(handoff): sessão YYYY-MM-DD` |
| Configuração alterada | Settings, env, gitignore | `chore(config): <o que>` |
| Teste criado ou ajustado | tests/*.py | `test(<escopo>): <o que cobre>` |

**Regra de bolso:** se a mudança é **útil por si só**, já é hora de commitar. Não espere "terminar a issue toda".

## 2. Gatilhos obrigatórios de PUSH

Push acontece em qualquer um destes eventos:

| Gatilho | Por quê |
|---|---|
| Fim de cada sessão | Trabalho não pode ficar só no Mac |
| Antes de pausa > 30 min | Pode acontecer algo na sua ausência |
| Antes de mudança arriscada | Backup antes de experimentar |
| Após commit em branch de PR | Actions só roda com push |
| Sempre que o WORKFLOW pedir (passo 11/16) | Sem exceção |

**Regra de bolso:** duvidou se deve pushar? Pushe.

## 3. O que NUNCA se comita

- `.env`, `secrets.json`, chaves, certificados `.pem`, `.key` — pre-commit bloqueia
- Senhas em texto plano — revisar antes
- Backups `.tar.gz`, `.zip` gigantes — usar git-lfs ou pasta `.tmp/` no gitignore
- Arquivos de log grandes — `logs/*.log` está no gitignore
- `node_modules/`, `__pycache__/`, `.venv/` — já no gitignore
- PDFs de processos judiciais com dados de paciente — estão em pastas separadas, não no repo

## 4. Granularidade de commits — nem muito pequeno, nem muito grande

**Ruim (muito pequeno):**
```
a1b2c3d doc: corrigir typo
b2c3d4e doc: corrigir outro typo
c3d4e5f doc: corrigir mais um
```
Melhor juntar em 1 commit: `doc: corrigir typos em X.md`

**Ruim (muito grande):**
```
xyz789a feat: implementar tudo do pipeline, corrigir bugs, adicionar docs, refatorar cron
```
Quebrar em 4 commits separados.

**Bom (tamanho certo):**
- 1 mudança lógica = 1 commit
- Entre 5 e 200 linhas alteradas em média
- Mensagem explica PORQUÊ, não o QUÊ

## 5. Quando NÃO fazer Pull Request

Commit direto em `main` permitido SÓ em:
- Bootstrap inicial (já feito, não mais)
- Correção de typo em `.md` da raiz (README, CHANGELOG)
- Adição de handoff ao final de sessão
- Para TUDO o mais: PR obrigatório

## 6. Frequência mínima (anti-abandono)

Se passarem 3 dias sem commit no repo, sistema entra em alerta (TODO: cron futuro). Motivo: projeto esfriando = projeto morrendo. Regra humana: **ao menos 1 commit a cada 72h durante semana de trabalho.**

Se você está de férias/doente, escreve isso num handoff `PAUSED` e o cronômetro não conta.

## 7. Política por tipo de arquivo

| Tipo | Regra |
|---|---|
| Código (`.py`, `.sh`) | Commit com teste junto ou commit seguinte adiciona teste |
| Doc (`.md`) | Commit livre, sem teste |
| Config (`.json`, `.yml`) | Commit + teste manual com output colado no PR |
| Dados de teste (`tests/fixtures/`) | Commit livre |
| Dados reais (PDFs, FICHAs) | NÃO commitar — ficam fora do repo |

## 8. Ordem de precedência em conflito de regra

```
Pedido explícito do usuário com "QUEBRAR-REGRA-N"
           >
RULES.md
           >
POLITICA-SALVAMENTO.md (este arquivo)
           >
WORKFLOW.md
           >
Hábito comum
```

Se o Claude violar, você escreve `PARAR. Ler POLITICA-SALVAMENTO.md. Qual regra?`

## 9. Push automático? (por que NÃO)

Teve tentação de fazer push automático a cada commit. Decidido: **não**.

Motivos:
- Push triggers GitHub Actions (custo de recursos)
- Commit "no meio" do trabalho não deve ir público
- Força disciplina de pensar "este é ponto bom de sincronizar?"

**Exceção futura:** um cron pode fazer push 1x/hora se houver commits locais atrasados. Issue separada pra considerar.

## 10. Resumo em 1 parágrafo

Commite SEMPRE que algo útil foi concluído. Pushe SEMPRE no fim de sessão + antes de pausa longa + quando o workflow mandar. Nunca comite segredos. Nunca force-push em main. PR pra tudo que não seja typo/handoff. Se tiver dúvida: commit+push e seguir em frente.
