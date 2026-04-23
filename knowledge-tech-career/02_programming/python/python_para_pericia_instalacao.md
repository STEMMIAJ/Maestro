---
titulo: Instalação e ambiente Python para perícia
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# Python para perícia — instalação e ambiente

Objetivo: ter Python funcional no Mac, isolar dependências por projeto, evitar quebrar scripts antigos.

## Por que não usar o Python do sistema
Mac vem com Python 2.x ou 3.x antigo reservado para uso interno da Apple. Instalar pacotes via `sudo pip` no Python do sistema corrompe o macOS. **Nunca fazer.**

## pyenv — gerenciar versões do Python
`pyenv` instala várias versões (3.10, 3.11, 3.12) lado a lado sem conflito.

```bash
brew install pyenv
pyenv install 3.12.3
pyenv global 3.12.3
```

Por que importa: um script pericial antigo pode depender de 3.10. Um novo, de 3.12. Com pyenv, cada pasta pode ter sua versão via `pyenv local 3.11.8` (cria arquivo `.python-version`).

## venv — ambiente virtual por projeto
Ambiente virtual = pasta com cópia isolada do Python + pacotes. O que instala num venv não vaza para outros.

```bash
cd ~/Desktop/STEMMIA\ Dexter/src/automacoes
python3 -m venv .venv
source .venv/bin/activate        # ativa
pip install requests selenium
deactivate                        # sai
```

Por que venv é obrigatório: script A precisa `requests==2.28`, script B precisa `requests==2.31`. Sem venv, um quebra o outro. Com venv, cada projeto tem seu conjunto.

Exemplo pericial: o scraper DataJud e o monitor DJEN devem ter venvs separados — cada um congela sua versão de `requests` via `pip freeze > requirements.txt`.

## pip — instalar pacotes
Dentro do venv ativo:
```bash
pip install requests            # última versão
pip install "requests==2.31.0"  # versão travada
pip freeze > requirements.txt   # congela tudo
pip install -r requirements.txt # reinstala igual em outra máquina
```

## uv — alternativa moderna (recomendado 2026)
`uv` é um gerenciador Python feito em Rust, 10–100× mais rápido que `pip`+`venv`. Substitui ambos.

```bash
brew install uv
uv venv                          # cria .venv
uv pip install requests          # instala rápido
uv add requests                  # em projeto uv: edita pyproject.toml
uv run python script.py          # roda dentro do venv automaticamente
```

Por que importa: instalar 50 pacotes Selenium+pandas leva 2 min com `pip`, 5 s com `uv`. Economia real em loop de teste.

## Fluxo recomendado para projeto novo
```bash
mkdir projeto_novo && cd projeto_novo
uv venv
source .venv/bin/activate
uv pip install requests pandas
echo ".venv/" >> .gitignore
```

## Armadilhas comuns
- `pip install` fora de venv → polui Python do sistema.
- Esquecer de ativar venv → instala no lugar errado. Verificar com `which python`: deve apontar para `.venv/bin/python`.
- Commitar `.venv/` no Git → repo fica gigante. Sempre no `.gitignore`.

## Referências
- [TODO/RESEARCH] confirmar versão estável atual do uv (abr/2026).
