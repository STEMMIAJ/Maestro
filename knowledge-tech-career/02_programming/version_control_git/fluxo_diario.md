---
titulo: Fluxo diário com Git
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Fluxo diário com Git

Rotina mínima: **status → add → commit → push**. Repetir ao longo do dia.

## 1. Começar o dia — `git pull`
Antes de editar qualquer coisa, sincronizar com o remote.
```bash
git pull origin main
```

Por que importa: se colaborador (ou você mesmo, de outra máquina) empurrou algo, você começa do ponto correto. Sem pull → conflito certo depois.

## 2. Ver o que mudou — `git status`
A cada mudança significativa, rodar:
```bash
git status
```

Saída típica:
```
On branch main
Changes not staged for commit:
  modified:   src/extrator.py
Untracked files:
  novo_modulo.py
```

Lê: "editei `extrator.py`, criei `novo_modulo.py`, ainda não staged".

## 3. Ver o diff — `git diff`
Antes de commitar, olhar o que está indo.
```bash
git diff                    # mudanças não staged
git diff --staged           # mudanças que vão no commit
git diff src/extrator.py    # só um arquivo
```

Por que importa: pega typo, debug print esquecido, chave API coladinha sem querer. **Sempre olhar antes de commitar.**

## 4. Staging — `git add`
```bash
git add src/extrator.py             # um arquivo
git add src/                         # pasta inteira
git add -p                           # interativo — escolhe pedaços
git add .                            # tudo na pasta atual (cuidado)
```

Preferir nome específico a `git add .` — evita commitar lixo por acidente (`.DS_Store`, `*.pyc`).

## 5. Commit — `git commit`
```bash
git commit -m "adiciona extrator de CID-10"
```

Mensagem boa:
- Imperativo presente: "adiciona", "corrige", "remove" (não "adicionei").
- Resume o **por quê** em uma linha.
- Detalhes longos vão na segunda linha em diante (abrir editor com `git commit` sem `-m`).

Exemplo pericial:
```
corrige fuso horario em data de movimentacao DJEN

DataJud retorna em UTC, display precisa America/Sao_Paulo.
Antes: movimentacao de 22:00 aparecia dia seguinte.
```

## 6. Push — `git push`
```bash
git push origin main
```

Envia seus commits locais para o remote. Outros veem a partir daí.

Push atômico: se falhar por rejeição (remote tem commit que você não tem), **parar**, `git pull --rebase`, resolver conflitos se houver, tentar de novo.

## Quando fazer cada coisa

| Situação | Ação |
|---|---|
| Comecei a trabalhar | `git pull` |
| Acabei uma feature completa | `add` + `commit` + `push` |
| Salvar progresso parcial | `add` + `commit` (sem push) |
| Trocar de contexto, trabalho inacabado | `git stash` (ver emergências) |
| Ver se mudei algo | `git status` |
| Conferir antes de commitar | `git diff --staged` |
| Puxar atualização do time | `git pull --rebase` |

## Commits atômicos
Um commit = uma ideia. Se você precisa escrever "e também" na mensagem, são 2 commits.

Ruim: `"adiciona extrator + corrige bug de fuso + atualiza README"`.
Bom: três commits separados.

Benefício: `git revert <commit>` desfaz uma coisa só; `git log --grep="fuso"` acha a correção rápido.

## Regra anti-lambança
1. Nunca editar direto na main em projeto sério → usar branch.
2. Pull antes de começar. Push ao terminar.
3. Nunca commit com terminal num estado que você não entende (`git status` incompreensível = pare, peça ajuda).
