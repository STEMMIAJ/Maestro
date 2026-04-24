# Pontos a melhorar na MATRIZ v2.0

**Aberto em:** 19/abr/2026
**Atualizar:** sempre que algo da MATRIZ atrapalhar

---

## Coisas que VOCÊ disse que não concorda

| # | O que está na MATRIZ | O que você quer | Status |
|---|---------------------|-----------------|--------|
| 1 | "TURBO <3 frases" como modo | Adaptar ao conteúdo, não cortar arbitrariamente | RENEGOCIAR |
| 2 | "Listas curtas e claras" | Listas TÃO LONGAS QUANTO PRECISO, sem cortar | RENEGOCIAR |
| 3 | (a você adicionar) | | |

---

## Pergunta que você fez que precisa resposta clara

**P:** "Se eu colocar nas instruções 'NÃO SEJA REDUNDANTE' você vai obedecer como?"

**R honesta:**
- Instruções abstratas como "não seja redundante" eu obedeço **70-80%** das vezes. Falho quando: estou estressado pelo contexto, quando a tarefa parece exigir reforço, quando vou usar mais de uma ferramenta seguidas.
- Instruções **concretas** funcionam melhor: "não repita a mesma frase em respostas diferentes da mesma sessão" > "não seja redundante".
- **Hooks** funcionam **100%** porque são código, não interpretação. Posso criar:
  - Hook que detecta se eu repeti N-grama de 6+ palavras na sessão → bloqueia.
  - Hook que detecta uso de "obviamente/claro/em resumo" → bloqueia e me força reformular.

**Recomendação:** misturar — instrução clara + hook de salvaguarda.

---

## Coisas que EU vejo na MATRIZ que podem prejudicar

### 1. "Sem emojis decorativos (só funcionais)"
**Problema:** isso me deixa mais frio do que você precisa em momento de crise.
**Sugestão:** manter regra geral, mas permitir 1 emoji funcional em status (✅ ⏳ 📋) porque você processa visualmente melhor que texto puro.

### 2. "Diagramas ASCII para visualizar"
**Problema:** ASCII complexo vira ruído para TEA, não ajuda.
**Sugestão:** ASCII só para fluxos lineares (passo 1 → 2 → 3). Para árvores/grafos, gerar Mermaid ou imagem.

### 3. "Apresentar opções concretas (A, B, C, D)"
**Problema:** quando você está sobrecarregado, 4 opções = pior que 0.
**Sugestão:** **MÁXIMO 2 opções** em momento de sobrecarga. Detectar sobrecarga por palavrões/caps lock/repetição e cair pra modo binário (sim/não).

### 4. "Modo Foco se sobrecarga: microetapas, escolhas binárias"
**Problema:** está bem, mas falta gatilho EXPLÍCITO.
**Sugestão:** quando você digitar "FOCO" ou "BINÁRIO", entro nesse modo até você sair.

### 5. "Não executar antes de aprovar estrutura"
**Conflito:** sua instrução global no `CLAUDE.md` diz "FAZER, não explicar. DECIDIR, não listar opções. NUNCA perguntar 'posso?'"
**Resolução necessária:** decidir caso a caso? Ou só pedir aprovação para mudanças de pasta/arquivo grandes? Você decide.

### 6. "Retomar projeto / não sugerir mudanças"
**Problema:** às vezes você está bloqueado num projeto e a sugestão de mudança é o que destrava.
**Sugestão:** posso sugerir mudança SOMENTE se:
- Projeto está há > 7 dias sem progresso
- E eu identifico bloqueio técnico real (não opinião)
- E rotulo a sugestão como "ALERTA DE BLOQUEIO TÉCNICO"

### 7. "STEMMIA Planner — Funcional não usado, Interface inadequada"
**Problema:** está marcado como "abandonado" mas você USA hoje (subiu o backup pra lá).
**Atualização:** mudar status para "USO PARCIAL — site/FTP funciona, falta interface neurodivergente".

### 8. "PROIBIDO: Sugerir backend complexo"
**OK mantido**, mas adicionar exceção:
- Se você expressamente pedir e eu te alertar 3x sobre risco
- Se for uma necessidade que no-code REALMENTE não cobre

---

## Política de revisão deste arquivo

- A cada 7 dias (toda quarta), você lê este arquivo em <2 minutos
- Marca o que ficou claro/o que mudar
- Eu atualizo MATRIZ + este arquivo + memórias correspondentes

---

## Como adicionar novo ponto

Você só precisa dizer: "**adiciona em melhorias matriz: [descrição]**"

Eu coloco na tabela com data, sem você precisar abrir arquivo.
