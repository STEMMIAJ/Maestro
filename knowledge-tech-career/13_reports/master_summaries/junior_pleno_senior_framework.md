---
titulo: Framework Júnior/Pleno/Sênior
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Framework Júnior / Pleno / Sênior

## Premissa

Nível não é função de tempo de casa. Dev com 8 anos fazendo a mesma CRUD mecânica é pleno eterno. Dev com 2 anos que lidera decisão de arquitetura em produto crítico opera como sênior. O mercado mede nível por **autonomia, escopo, qualidade de decisão e comportamento em ambiguidade** — não por crachá.

Aplicar isso ao perfil médico: o título "Dr." não traduz para TI. O que traduz é a capacidade demonstrada de decidir sob incerteza, documentar e sustentar decisão com evidência — coisas que perito faz diariamente.

## Quatro eixos fundamentais

1. **Autonomia** — quanto precisa de direção para executar.
2. **Escopo** — tamanho do problema que consegue abraçar sozinho.
3. **Qualidade de decisão** — quantas decisões depois são revertidas, retrabalhadas, viram dívida técnica.
4. **Lidar com ambiguidade** — o que faz quando o requisito não está claro.

## Tabela — 8 dimensões × 3 níveis

| Dimensão | Júnior | Pleno | Sênior |
|---|---|---|---|
| Autonomia | Precisa de tarefa bem definida | Recebe problema, decide solução | Recebe objetivo, define problema e solução |
| Escopo típico | Função, tela, bug pequeno | Feature, módulo, sistema médio | Produto, arquitetura, múltiplos times |
| Ambiguidade | Congela ou chuta | Faz perguntas certas, propõe opções | Reduz ambiguidade, negocia escopo |
| Decisão técnica | Segue padrão do time | Propõe padrão com justificativa | Define padrão e ensina por que |
| Qualidade | Código funciona | Código funciona, testado, legível | Código funciona, mede efeito, evolui |
| Erro | Precisa ser descoberto por outro | Detecta sozinho | Antecipa e previne |
| Comunicação | Reporta status | Explica trade-off | Traduz entre técnico/negócio |
| Impacto | Na tarefa | No time | No produto/negócio |

## Sinais concretos de cada nível

### Júnior
- Abre o editor, espera instrução.
- Pergunta "como faz X?" antes de tentar.
- Pull request pequena, escopo de uma tela.
- Bug em produção: reporta, não investiga causa-raiz.
- Lê documentação quando mandam.

### Pleno
- Recebe ticket com requisito ruim, volta com 3 perguntas objetivas.
- Conhece o sistema inteiro, não só o pedaço que mexe.
- Bug em produção: investiga, identifica causa, propõe correção e prevenção.
- Faz code review de júnior com comentário construtivo.
- Estima prazo e cumpre (ou avisa cedo quando vai furar).

### Sênior
- Antecipa problema antes de virar incidente.
- Decisão técnica vira documento que sobrevive a ele.
- Reduz escopo quando o problema está mal formulado.
- Mentoria não é opcional, é parte do trabalho.
- Diz "não" a demanda ruim com argumento técnico + de negócio.
- Escolhe o que **não** construir.

## Anti-padrões

- **Sênior por tempo** — 10 anos na mesma stack fazendo a mesma coisa = pleno com velocidade.
- **Júnior eterno** — recusa responsabilidade, espera alguém resolver, não propõe.
- **Pleno-imitando-sênior** — palpita em arquitetura sem ter implementado; tom didático sem base.
- **Sênior técnico que não comunica** — impacto trava no próprio teclado.
- **Inflação de título** — startup promete "sênior" para atrair candidato júnior; escopo real não bate.

## Aplicação ao perfil médico-perito

Mapeamento direto de competências transferíveis:

| Competência pericial | Equivalente TI |
|---|---|
| Quesito mal formulado → esclarecimento | Requisito ruim → perguntas ao PM |
| Laudo sustentado em evidência | Decisão técnica sustentada em dado |
| Gestão de prazo judicial | Gestão de sprint |
| Produção sob ambiguidade diagnóstica | Produção sob ambiguidade de escopo |
| Documentar cada passo (cadeia de custódia) | Documentar decisão (ADR) |

Nível de entrada provável em interseção saúde/TI: **pleno direto**, desde que a habilidade técnica específica (SQL, Python, estatística) cubra o papel. Começar como júnior em dev genérico seria subutilização do ativo médico.

## Ver também

- `it_roles_taxonomy.md` — papéis onde aplicar esta régua.
- `certifications_framework.md` — certificações como sinal para cada nível.
