# FLUXO 02 — Download de PDFs

## Objetivo

Baixar **todas** as peças de um processo, pastas prontas para análise. Este fluxo está **funcionando** hoje (desde 13/abr/2026).

## Pré-requisito manual (humano)

1. Abrir PJe TJMG (ou TRF6) no navegador.
2. Entrar na aba **PUSH** do processo.
3. Escrever **cidade + vara** no campo de observação.
4. Só então acionar o script de download.

Sem o passo 2-3 o script não encontra o processo na fila.

## Passos automáticos (quando roda)

1. Script abre Chrome com perfil isolado (`~/Desktop/chrome-pje-profile` ou `~/.pje-browser-data`).
2. Loga usando sessão já autenticada (ou pede login no 1º run).
3. Navega até PUSH, pega lista de processos marcados.
4. Baixa todos os PDFs de cada processo.
5. Salva em pasta estruturada `~/Desktop/pje-YYYYMMDD/<CNJ>/`.
6. Notifica Telegram (@stemmiapericia_bot) ao terminar.

## SCRIPTS EXISTENTES

### Mac → Windows (ponte Parallels)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/_MESA/20-SCRIPTS/command-mac/CLICAR_AQUI_BAIXAR_PJE.command` | Clicável no Mac. Dispara `.bat` dentro do Parallels (Windows) | FUNCIONA |

### Windows/Mac (Selenium direto)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/_MESA/20-SCRIPTS/python-avulsos/baixar_direto_selenium.py` | **Script principal.** Selenium + webdriver-manager. Roda no Windows (ARM64). Flags `--teste`, `--so-comarca`, `--listar` | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Processos Atualizados/baixar_direto_selenium.py` | Cópia (mesmo conteúdo) | DUPLICATA |

### Maestro (variantes Playwright/Selenium)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/download/baixar_push_pje.py` | Selenium v2, perfil isolado, flags `--limite --pagina --download-dir`. Notifica Telegram | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/download/baixar_e_organizar.py` | Orquestrador: baixa + organiza em pasta CNJ | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/download/pje_verificacao.py` | Helper: confirma integridade do PDF baixado | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/baixar_push_pje_playwright.py` | Variante Playwright | LEGADO |
| `/Users/jesus/stemmia-forense/src/pje/rodar_download_ate_4.py` | Loop retry (até 4 tentativas) | FUNCIONA |

### Emergência (Chrome já aberto)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/emergencia/baixar_documentos_processo_aberto.py` | Playwright async + CDP (remote-debug 9222/9223). Depende de sessão aberta | EMERGÊNCIA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/emergencia/baixar_prioritarios.py` | Baixa os marcados como prioritários | EMERGÊNCIA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pje/emergencia/baixar_avulsos_emergencia.py` | Baixa peças avulsas | EMERGÊNCIA |

### Priorização (decide o que baixar)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/automacoes/faltam_baixar.py` | Lê `~/Desktop/LISTA PERICIAS CERTA.pdf` + PDFs já baixados. Gera `FALTA-BAIXAR-YYYYMMDD.md` + `processos_hoje.txt` (60 CNJs) + `processos_amanha.txt`. Priorização por comarca (Taiobeiras > GV > Mantena) | FUNCIONA |

## Pontos ainda manuais

1. Logar no PJe (certificado A3 no Parallels Windows).
2. Marcar PUSH + escrever cidade+vara na observação.
3. Resolver popup/captcha esporádico do PJe TJMG.
4. Escolher comarca na flag `--so-comarca` se quiser filtrar.
5. Fechar o Chrome antes de rodar (senão conflita com perfil).

## Saída esperada

```
~/Desktop/pje-YYYYMMDD/
├── 0000000-00.0000.8.13.0000/
│   ├── inicial.pdf
│   ├── contestacao.pdf
│   ├── laudo-inss.pdf
│   └── ...
└── download-log.txt
```

## Perfil Chrome/Playwright

- Mac: `~/Desktop/chrome-pje-profile/`
- Alias: `~/.pje-browser-data/` → `~/Desktop/STEMMIA Dexter/PJE-INFRA/`
- Parallels (Windows): `C:\Users\Public\chrome-pje-profile\`
