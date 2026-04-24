# Maestro — CLAUDE.md (contrato com o agente)

> Este arquivo é lido pelo Claude Code ao entrar em `~/Desktop/STEMMIA Dexter/Maestro/`.
> Obedecer literalmente.

## Ordem obrigatória ao iniciar QUALQUER tarefa

1. `cat CHARTER.md RULES.md WORKFLOW.md DEFINITION_OF_DONE.md` — reler as 4 bases
2. `bash scripts/status.sh` — ver estado atual
3. `gh issue list --state open` — escolher 1 issue
4. Seguir os 13 passos do WORKFLOW.md

## Proibido (zero exceção)

- Criar arquivo fora de `Maestro/`
- Executar `rm`, `rm -rf`, `mv para /tmp` sem `LIMPAR-LIBERADO` na mensagem do usuário
- Dizer "feito", "pronto", "rodando", "concluído" sem output colado
- Perguntar "quer que eu faça?" — decidir ou parar
- Pular qualquer passo do WORKFLOW.md
- Implementar decisão grande sem ADR aprovado

## Obrigatório (zero exceção)

- Toda tarefa começa escolhendo 1 issue aberta
- Toda alteração vira commit imediato
- Todo fim de sessão escreve handoff
- Todo push bem-sucedido registrado no CHANGELOG
- Toda falha 2x consecutivas vira issue `blocker` e para

## Comandos canônicos

```bash
# Abrir sessão
bash scripts/status.sh

# Sincronizar com remote
bash scripts/sync.sh

# Encerrar sessão (cria handoff)
bash scripts/finalize.sh
```

## Usuário

Dr. Jesus, perito médico judicial, TEA+TDAH.
Respostas: máx 3 linhas entre ações. Zero bajulação. Zero motivacional.
Termo técnico → 1 frase + exemplo concreto.

## Se em dúvida

PARAR. Escrever 1 pergunta objetiva. Não "tentar".
