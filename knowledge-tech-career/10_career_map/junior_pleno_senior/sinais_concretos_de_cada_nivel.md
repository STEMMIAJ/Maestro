---
titulo: "Sinais Concretos de Cada Nível — Júnior, Pleno, Sênior"
bloco: "10_career_map"
tipo: "referencia"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# Sinais Concretos de Cada Nível

Evita medir por tempo de casa ou tamanho de salário. Mede por comportamento observável. Cada nível tem 20 sinais distribuídos — 7 júnior, 7 pleno, 6 sênior. Inclui contra-exemplos.

## JÚNIOR

### Sinais

1. **Executa tarefa bem definida com supervisão**: recebe issue, entende escopo, entrega.
2. **Pede ajuda cedo**: travou 30 min, escalou. Não fica 2 dias preso em silêncio.
3. **Pergunta "como" frequentemente, "por que" eventualmente**: ainda absorvendo mecânica.
4. **Lê documentação antes de perguntar**: mostra esforço, não exige mastigação.
5. **Usa ferramentas padrão do time sem contestar**: aprende o stack antes de sugerir trocar.
6. **PR pequeno e focado**: 1 mudança por PR, fácil de revisar.
7. **Aceita feedback sem ressentimento visível**: sabe que está aprendendo.

### Contra-exemplos de júnior imaturo

- Silêncio prolongado sem perguntar.
- Reclamar de revisão em canal público.
- Querer reescrever toda a arquitetura na primeira semana.
- Entregar PR gigante misturando refactor + feature + bugfix.

## PLENO

### Sinais

1. **Entrega feature completa com autonomia**: recebe objetivo, divide, executa, valida.
2. **Identifica ambiguidade em requisito e levanta**: não começa a codar pedido vago.
3. **Escreve testes antes de considerar feature pronta**: automação como default.
4. **Revisa PR de colega com comentários construtivos**: sabe julgar código alheio sem atacar pessoa.
5. **Decide trade-offs simples sozinho**: "usar lib X ou Y" sem consultar sênior.
6. **Documenta decisões técnicas relevantes (ADR)**: deixa trilha.
7. **Mentora júnior em aspectos pontuais**: pareamento, revisão.

### Contra-exemplos de pleno sênior-wannabe / pleno travado

- Dar opinião arquitetural forte sem ter rodado a solução antes.
- Delegar tudo o que é chato e ficar só com a parte "interessante".
- Ainda exigir briefing linha a linha para tarefas rotineiras.
- Ficar defensivo em revisão de código (pleno forte aceita).

## SÊNIOR

### Sinais

1. **Define problema antes de resolver**: reformula pedido do PM quando o pedido é solução pronta.
2. **Desenha arquitetura com trade-offs explícitos**: lista alternativas descartadas e por quê.
3. **Antecipa modo de falha**: "isso quebra quando Y acontece; vou adicionar retry + alerta".
4. **Eleva colegas tecnicamente**: PR bate 70% do feedback técnico dele.
5. **Conecta trabalho técnico a impacto de negócio**: justifica tempo em dívida técnica com custo operacional concreto.
6. **Sabe quando não resolver**: fecha projeto, mata feature, diz "não" com dado.

### Contra-exemplos de "falso sênior"

- Anos de casa, mas ainda entrega feature como pleno sem conectar a negócio.
- Arquiteta tudo e não implementa nada (síndrome do arquiteto de slide).
- Derruba projeto de subordinado para impor o próprio sem fundamento.
- Refém de uma única stack ("só sei Java, tudo é Java").
- Comunicação destrutiva em revisão (mata a cultura do time).

## Sinais transversais a qualquer nível

- Honestidade sobre o que sabe e não sabe.
- Capacidade de reconstruir o próprio raciocínio por escrito.
- Curiosidade ativa: lê código além do que precisa mexer.
- Entrega previsível: compromissos cumpridos ou renegociados cedo.

## Tabela-resumo

| Dimensão | Júnior | Pleno | Sênior |
|----------|--------|-------|--------|
| Escopo | Tarefa | Feature | Projeto/Sistema |
| Supervisão | Ativa | Pontual | Mínima (e dá supervisão) |
| Decisão técnica | Segue padrão | Trade-off local | Trade-off sistêmico + negócio |
| Ambiguidade | Evita | Levanta | Resolve e documenta |
| Mentoria | Recebe | Dá pontual | Dá estratégica |
| Comunicação | Pergunta bem | Explica bem | Negocia bem |
| Erro | Aprende | Previne | Antecipa e mitiga |

## Como Dr. Jesus lê isso

Em tech, Dr. Jesus está em **júnior forte / pleno inicial** em Python/automação — já entrega features complexas (Dexter, monitor de processos), levanta ambiguidade, lê fontes antes de perguntar.

Em perícia médica, é **sênior consolidado** — nomeação judicial, casos complexos, mentoria implícita.

O objetivo da trilha é mover tech para pleno consolidado nos próximos 18 meses sem perder o sênior pericial.

## Referência cruzada

- `../professions_taxonomy/familias_profissionais_detalhadas.md`
- `../role_expectations/expectativas_por_papel.md`
- `../learning_paths/trilha_medico_para_tech.md`
