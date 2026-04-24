---
name: Documentação obrigatória de fluxos
description: SEMPRE mapear fluxos passo a passo antes de executar, com pontos de falha e dependências
type: feedback
---

Ao criar QUALQUER automação, script, pipeline ou fluxo novo, ANTES de executar:

1. Documentar no MAPA-AUTOMACAO.html (~/Desktop/AUTOMAÇÃO PROCESSUAL/)
2. Listar CADA passo com comando exato e caminho exato
3. Listar CADA ponto de falha possível e como resolver
4. Listar CADA dependência e verificar se está satisfeita ANTES de começar
5. Marcar status real: FUNCIONA (testado), PARCIAL (o que falta), QUEBRADO (por quê)
6. Destacar ações manuais do usuário
7. NUNCA dizer "funciona" sem ter testado
8. Quando algo falhar, dizer EXATAMENTE onde e por quê

**Why:** O usuário tem TDAH e precisa VER o sistema inteiro antes de confiar nele. Executar sem documentar causa frustração, perda de tempo e sensação de que nada funciona. O padrão anterior (sair fazendo sem mapear) resultou em horas perdidas com detalhes escondidos.

**How to apply:** Antes de qualquer execução, adicionar entrada no MAPA-AUTOMACAO.html com o formato padronizado. Verificar dependências. Testar. Só depois marcar como FUNCIONA.
