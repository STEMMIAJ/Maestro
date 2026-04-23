---
titulo: Aliases úteis para rotina pericial
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: medio
tempo_leitura_min: 3
---

# Aliases úteis — rotina pericial

Alias = apelido curto para comando longo. Editar `~/.zshrc`, adicionar as linhas abaixo, recarregar com `source ~/.zshrc`.

## Navegação rápida
```bash
alias pericia='cd ~/Desktop/STEMMIA\ Dexter'
alias mesa='cd ~/Desktop/_MESA'
alias laudos='cd ~/Desktop/_MESA/10-PERICIA/laudos'
alias scripts='cd ~/Desktop/STEMMIA\ Dexter/src/automacoes'
alias hooks='cd ~/Desktop/STEMMIA\ Dexter/src/hooks'
alias docs='cd ~/Desktop/STEMMIA\ Dexter/DOCS'
```

## Listagem
```bash
alias ll='ls -lhG'         # detalhado + colorido
alias la='ls -lahG'        # inclui ocultos
alias lt='ls -lhtG'        # ordem por data (mais recente primeiro)
```

## Git
```bash
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --decorate -20'
alias gd='git diff'
```

## Python / venv
```bash
alias venv='source .venv/bin/activate'
alias py='python3'
alias pipf='pip freeze > requirements.txt'
```

## Perícia — ações comuns
```bash
# rodar monitor de movimentações
alias monitor='cd ~/Desktop/STEMMIA\ Dexter/src/automacoes && source .venv/bin/activate && python3 monitorar_movimentacao.py'

# abrir mapa mestre do sistema
alias mapa='cat ~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md | less'

# últimas execuções do monitor
alias logmon='tail -f ~/Desktop/STEMMIA\ Dexter/src/automacoes/logs/monitor-*.log'
```

## Funções (quando alias não basta)
Alias não aceita argumento. Função aceita.

```bash
# cria pasta nova e entra
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# busca processo no pericia por parte do nome
buscar_proc() {
    find ~/Desktop/_MESA/10-PERICIA/processos -iname "*$1*"
}
```

Uso: `buscar_proc silva` → lista tudo com "silva" no nome.

## Recarregar sem reiniciar terminal
```bash
source ~/.zshrc
```

## Testar sem salvar
Rodar `alias x='comando longo'` no terminal atual — vive só nessa sessão.
