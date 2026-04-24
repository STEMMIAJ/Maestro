# CENTRAL-DE-FLUXOS-MAESTRO

## O que é

Mapa único dos fluxos do sistema pericial do Dr. Jesus. **Não roda código.** Só descreve, numera passos e aponta onde está cada script que já existe.

Objetivo: parar de perder tempo procurando "onde estava aquele script". Tudo indexado aqui.

## Como usar

1. Começar por `MAPA-GERAL-DE-FLUXOS.md` — tabela de todos os fluxos.
2. Abrir o `.md` do fluxo que interessa dentro de `FLUXOS/`.
3. Se quiser só lista seca de scripts, ver `SCRIPTS-MAPEADOS/`.
4. Ao final do dia, ler `PROXIMO-PASSO-HOJE.md` — máximo 3 passos, sem sobrecarga.

## Os 7 fluxos

1. **Captura de processos** — AJ/AJG/PJe/DataJud/DJEN
2. **Download de PDFs** — script Mac+Selenium (funciona)
3. **Análise de processos** — FICHA.json + OCR + partes + quesitos
4. **Modelos e laudos** — templates reaproveitáveis + laudos elogiados
5. **Honorários** — proposta vs tabela AJG (NUNCA misturar)
6. **Jurisprudência e sentenças** — TJMG captcha, DataJud, MCP brlaw
7. **Memória e GitHub** — o que está indo pro repo sem controle

## Relação com o resto

- **Dexter** (`~/Desktop/STEMMIA Dexter/`) = raiz de tudo (scripts, banco, memória).
- **Maestro** (`~/Desktop/STEMMIA Dexter/Maestro/`) = repo Git subordinado.
- **Cowork** (`~/Desktop/STEMMIA Dexter/cowork/`) = biblioteca de templates + motor `aplicar_template.py`.
- **OpenClaw** = **NÃO PARTICIPA HOJE**. Futuro possível (cron noturno). Congelado.
- **GitHub** = uso atual sem controle (hook "salva no github" empurra para `main`). **A revisar em outra tarefa.**

## Regra ferro

Não inventar fluxo. Só documentar o que está na máquina. Se faltar script, marcar **FALTANDO**.
