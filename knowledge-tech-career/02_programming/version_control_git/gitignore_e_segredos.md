---
titulo: .gitignore e segredos
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 4
---

# .gitignore e segredos

## `.gitignore` — arquivos que o Git ignora
Arquivo de texto na raiz do repo, uma regra por linha. Git nunca adiciona nem mostra esses arquivos como modificados.

### Criar
```bash
touch .gitignore
```

### Sintaxe
```gitignore
# comentário começa com #

# padrão simples — ignora em qualquer pasta
*.log
.DS_Store

# pasta inteira
.venv/
node_modules/
__pycache__/

# só na raiz (começa com /)
/config.local.json

# exceção (precede com !)
*.pdf
!templates/*.pdf       # não ignora PDFs de templates
```

## O que SEMPRE ignorar

### Segredos e credenciais
```gitignore
.env
.env.*
*.key
*.pem
*.p12
*.pfx
credentials.json
secrets.yaml
```

### Ambiente Python
```gitignore
.venv/
venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
```

### Sistema / editor
```gitignore
.DS_Store           # Mac
Thumbs.db           # Windows
*.swp               # Vim
.idea/              # PyCharm
.vscode/            # VS Code (opcional — às vezes vale commitar parte)
```

### Logs e dados locais
```gitignore
logs/
*.log
*.sqlite
*.db
```

## Exemplo pericial — `.gitignore` realista
Para projeto Python do monitor de movimentações:
```gitignore
# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/

# Segredos
.env
*.key
*.pem
config/credenciais.json

# Dados locais (não são código)
logs/
dados/
downloads-pje/
*.sqlite

# Sistema
.DS_Store

# Saídas geradas
laudos_gerados/
```

## Por que nunca commitar segredo
Git **guarda histórico para sempre**. Commit de chave API + push → chave está pública no GitHub, mesmo que você delete no commit seguinte.

Bots varrem GitHub em segundos procurando:
- `AWS_ACCESS_KEY`
- `API_KEY=...`
- `senha="..."`
- Chaves privadas `-----BEGIN RSA PRIVATE KEY-----`

Resultado: cobrança de mil dólares em AWS em 1 hora, ou acesso indevido ao PJe.

## Se commitou segredo
1. **Trocar a chave imediatamente** no serviço. Não adianta só apagar do Git.
2. Remover do histórico: `git filter-repo` ou BFG Repo-Cleaner.
3. `git push --force` (com cautela).
4. Verificar se não vazou via git log público.

## Padrão recomendado — arquivo `.env`
```bash
# .env (IGNORADO pelo Git)
DATAJUD_API_KEY=abc123
PJE_CPF=000.000.000-00
PJE_SENHA=senha-secreta
```

No código Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["DATAJUD_API_KEY"]
```

Commitar `.env.example` (sem valores reais) para documentar quais variáveis existem:
```bash
# .env.example (COMMITADO)
DATAJUD_API_KEY=
PJE_CPF=
PJE_SENHA=
```

## Checagem rápida
Antes de `git push` num repo novo:
```bash
git ls-files | grep -Ei "(env|key|pem|credential|secret|senha)"
```
Se retornar algo → revisar. Nunca empurrar sem certeza.
