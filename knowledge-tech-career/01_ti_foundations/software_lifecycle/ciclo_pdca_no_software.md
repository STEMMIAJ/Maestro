---
titulo: "Ciclo PDCA no software"
bloco: "01_ti_foundations/software_lifecycle"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "B"
tempo_leitura_min: 4
---

# Ciclo PDCA no software

## O modelo

PDCA — *Plan, Do, Check, Act*. Ciclo iterativo de melhoria contínua formalizado por Deming a partir do trabalho de Shewhart. Aplica-se a qualquer processo; aqui, a escrever código.

1. **Plan (planejar)** — definir o que fazer, qual hipótese testar, qual critério de sucesso.
2. **Do (executar)** — implementar o plano em escopo pequeno.
3. **Check (verificar)** — medir resultado contra critério. Funcionou? Por quê ou por que não?
4. **Act (agir)** — padronizar o que deu certo; voltar ao Plan para o que não deu.

Importante: o ciclo não termina; reinicia com aprendizado acumulado.

## PDCA aplicado a escrita de código

### Plan

Antes de abrir o editor:
- Qual problema resolver? (1 frase concreta, mensurável)
- Qual o critério de "pronto"? (teste automatizado passa; função retorna X para entrada Y)
- Qual o risco de quebra? (o que pode piorar com essa mudança?)
- Tempo estimado.

Produto: *issue* no GitHub, nota no plano, branch nomeada (`fix/prazo-calculo-errado`).

### Do

Codar e comitar em pequenos passos. Regra prática: **o commit deve ser revertível sem perda de contexto**. Se demorou mais que o estimado em 2×, parar e repensar.

### Check

- Rodar testes.
- Medir: tempo de execução, consumo de memória, acurácia, % de processos detectados.
- Comparar com estado anterior.

Se critério não foi atingido, **não siga adiante**. Diagnostique. Documente o que você descobriu (comentário no issue, arquivo de notas).

### Act

- Deu certo → merge, atualiza documentação, arquiva issue, **extrai a lição** (ex.: "sempre rodar `pytest -x` antes de deploy").
- Deu errado → reverter, registrar a hipótese falhada, abrir novo Plan com ajuste.

## Exemplo pericial

Problema real: monitor de processos não detecta intimações do DJEN no dia correto.

- **Plan**: hipótese — offset de timezone na query (UTC vs -03:00). Critério — 100% dos processos de teste com intimação hoje devem aparecer no relatório das 18h.
- **Do**: ajustar `datajud_client.py:84` para converter `datetime.now(tz=ZoneInfo("America/Sao_Paulo"))`.
- **Check**: rodar contra lote de 20 processos conhecidos. Resultado: 19/20 detectados. Processo faltante tinha tramitação em tribunal federal (índice diferente).
- **Act**: padroniza timezone no módulo; abre novo Plan para cobrir índice federal. Adiciona teste de regressão.

## Relação com outras estruturas

- **Agile / Scrum** — sprint é um PDCA de 1–2 semanas; retrospectiva é o Act/Plan combinados.
- **Kaizen** — filosofia japonesa de melhoria contínua; PDCA é sua ferramenta operacional.
- **Experimentos controlados** — método científico em forma administrativa: hipótese → teste → observação → conclusão.

## Armadilha comum

Pular Check. Programador ansioso que conclui "funcionou" só porque compilou, sem medir. Em contexto pericial, equivale a laudo emitido sem exame físico — inválido.

## Por que importa para o perito

- **Processo pericial** é PDCA disfarçado: Plan (quesitos), Do (exame), Check (comparação com literatura), Act (laudo, conclusões, recomendações).
- **Desenvolvimento de automação pericial** ganha robustez aplicando PDCA: cada script novo passa por plano, teste, verificação em amostra antes de virar rotina.
- **Quando algo falha em produção** (monitor não avisa intimação), o *postmortem* é um PDCA compacto: o que aconteceu, o que fizemos, funcionou, como prevenir.

## Referências

- Deming, W. E. — *Out of the Crisis*, 1986.
- [TODO/RESEARCH: confirmar origem atribuída a Shewhart vs Deming].
