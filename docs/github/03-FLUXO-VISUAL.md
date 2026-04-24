# Fluxo Visual — o ciclo completo de uma sessão

> Um diagrama que mostra literalmente o que acontece do início ao fim. Imprima se quiser.

## A sessão em 1 figura (texto visual)

```
╔═══════════════════════════════════════════════════════════════╗
║                      ABRIR SESSÃO                             ║
╚═══════════════════════════════════════════════════════════════╝
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  1. cd Maestro/                      │
         │  2. bash scripts/status.sh           │
         │  3. Ler 4 arquivos-base              │
         │     (CHARTER, RULES, WORKFLOW, DOD)  │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  4. gh issue list --state open       │
         │  5. Escolher UMA issue (#N)          │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  6. git checkout -b feat/N-slug      │
         │     (criar branch paralela)          │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  7. Implementar (editar arquivos)    │
         │  8. git add + commit (repetir)       │
         │                                      │
         │  A cada passo útil: novo commit.     │
         │  Commits são foto do progresso.      │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  9. Rodar teste                      │
         │     Copiar output no terminal        │
         └──────────────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
              TESTE OK            TESTE RUIM
                  │                   │
                  │                   ▼
                  │         ┌──────────────────┐
                  │         │ voltar passo 7   │
                  │         │ (corrigir)       │
                  │         └──────────────────┘
                  ▼
         ┌──────────────────────────────────────┐
         │ 10. Atualizar CHANGELOG.md           │
         │ 11. git push origin feat/N-slug      │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │ 12. gh pr create --fill              │
         │     (abrir Pull Request)             │
         │                                      │
         │ Corpo do PR:                         │
         │ - Closes #N                          │
         │ - output de teste em ```             │
         │ - checklist DOD 5/5 marcado          │
         └──────────────────────────────────────┘
                            │
                            ▼
            ╔═══════════════════════════════╗
            ║   GITHUB ACTIONS (porteiro)   ║
            ║   enforce-dod.yml roda aqui   ║
            ║                               ║
            ║   ✓ Closes #N?                ║
            ║   ✓ CHANGELOG atualizado?     ║
            ║   ✓ Output em bloco?          ║
            ║   ✓ DOD 5/5 marcados?         ║
            ║   ✓ Scripts bash OK?          ║
            ╚═══════════════════════════════╝
                            │
                  ┌─────────┴─────────┐
                  │                   │
              TUDO VERDE         FALTA ALGO
                  │                   │
                  │                   ▼
                  │         ┌──────────────────┐
                  │         │ GitHub mostra    │
                  │         │ o que falta      │
                  │         │ → voltar passo 7 │
                  │         └──────────────────┘
                  ▼
         ┌──────────────────────────────────────┐
         │ 13. gh pr merge --squash             │
         │     (mergear o PR)                   │
         │     Issue #N fecha automaticamente   │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │ 14. bash scripts/finalize.sh         │
         │     (cria handoff)                   │
         │ 15. Preencher handoff com:           │
         │     - Issue trabalhada               │
         │     - Estado (DONE)                  │
         │     - Próximo passo                  │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │ 16. git add + commit + push final    │
         └──────────────────────────────────────┘
                            │
                            ▼
╔═══════════════════════════════════════════════════════════════╗
║                    FIM DA SESSÃO                              ║
║  Você pode fechar o Claude. Tudo salvo. Histórico imutável.   ║
╚═══════════════════════════════════════════════════════════════╝
```

## Se você só lembra de 1 coisa

```
ABRIR = bash scripts/status.sh
FECHAR = bash scripts/finalize.sh + git push
```

Se rodar esses 2 comandos, 80% do fluxo acontece automaticamente.

## Situações-exceção

### "Travei"
```
git status
# se mostrar vermelho/bagunça → não mexer, cola aqui
# se mostrar 'nothing to commit' → você está limpo, pode fechar
```

### "Não sei em que estado estou"
```
bash scripts/status.sh
# mostra: branch, último commit, issues abertas, último handoff
```

### "Quero ver o histórico"
```
git log --oneline -20
# 20 últimos commits
```

### "Quero ver o que mudou desde a última foto"
```
git diff
# mostra linha por linha o que está diferente
```

### "Meu Mac morreu, estou em outro"
```
git clone https://github.com/STEMMIAJ/Maestro.git
cd Maestro
# tudo aqui. mesma coisa.
```

## Por que esse fluxo funciona pra TEA+TDAH

- **Externaliza memória**: arquivo substitui "o que eu tinha que lembrar"
- **Binário**: cada passo é SIM ou NÃO, sem zona cinza
- **Rastreável**: qualquer momento você vê onde parou
- **Imperdível**: commit + push = backup automático
- **Reversível**: Git nunca apaga, só acrescenta. Erro tem volta.

Não precisa entender os detalhes. Precisa seguir os 16 passos. O arquivo lembra por você.
