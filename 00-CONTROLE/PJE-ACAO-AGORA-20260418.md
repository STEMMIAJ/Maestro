# PJe - ação agora

Data: 2026-04-18 21:05 -03

## Verdade curta

Sim, dá para automatizar a parte operacional.

O que fica manual: login VidaaS/gov.br/certificado no Chrome do Windows.

O que já está automatizado: lista, prova DataJud, inclusão no PUSH, download, validação do CNJ da primeira página e relatório.

## Estado verificado

- Pasta real acessível no Mac: `/Users/jesus/Desktop/processos-pje`.
- PDFs na raiz: 102.
- CNJs por nome de arquivo: 82.
- Link `processos-pje-windows` existe, mas o alvo Parallels não está montado no Mac neste momento.
- Scripts principais compilaram sem erro: `contar_push_pje.py`, `incluir_push.py`, `baixar_push_pje_playwright.py`, `consultar_aj.py`, `consultar_ajg.py`.
- Novos online validados no DataJud: 18/18.

## Prova dos novos

Arquivos gerados:

- `/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/PROVA-NOVOS-ONLINE-DATAJUD-20260418.md`
- `/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/PROVA-NOVOS-ONLINE-DATAJUD-20260418.json`

Dois dos 18 já estavam marcados como baixados nos arquivos locais antigos: `5005267-30.2025.8.13.0105` e `5007830-31.2024.8.13.0105`.

Fila operacional criada para os 16 ainda não baixados:

- `/Users/jesus/stemmia-forense/src/pje/novos-online-nao-baixados.txt`

## Próxima ação única

No Windows/Parallels, abrir:

```bat
\\Mac\Home\stemmia-forense\INCLUIR_E_BAIXAR_NOVOS_ONLINE.bat
```

Atalho visível na Mesa do Mac:

```text
/Users/jesus/Desktop/INCLUIR_E_BAIXAR_NOVOS_ONLINE.bat
```

O BAT faz:

1. abre/conecta o Chrome do Windows na porta 9223;
2. espera login manual se o PJe pedir;
3. inclui os 16 CNJs novos no PUSH;
4. baixa somente esses 16;
5. manda PDF divergente para `_mismatch`;
6. grava relatório em `Desktop\processos-pje\relatorio-*.json`.

## Depois do download

Rodar:

```bat
\\Mac\Home\stemmia-forense\CONTAR_PJE_PUSH.bat
```

O número decisivo fica em:

```text
Desktop\processos-pje\_relatorios_push\RESUMO-PJE-PUSH-*.md
```

## Não fazer agora

- Não reorganizar PDFs antigos.
- Não apagar duplicados.
- Não usar `sincronizar_aj_pje.py` como executor principal.
- Não mexer em Claude, plugins, MCPs ou hooks antes de baixar os processos.
