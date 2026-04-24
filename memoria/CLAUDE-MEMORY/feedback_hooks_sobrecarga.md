---
name: Hooks excessivos podem causar sobrecarga
description: Diagnóstico original 04/abr/2026 — hooks em excesso podem degradar performance. Estado restaurado 17/abr/2026: 51 hooks ativos em ~/stemmia-forense/hooks/ após reversão de destruição de 16/abr 21:05.
type: feedback
originSessionId: 24bc858a-e792-43b2-90e5-30cddcbda3e0
---
Hooks em excesso podem causar lentidão no MacBook quando disparam em todos os eventos. Diagnóstico original de 04/abr/2026 identificou isso como causa de perda de fluência após migração Mac Mini → MacBook.

**Why:** Cada Write/Edit disparando múltiplos PostToolUse hooks, cada prompt disparando UserPromptSubmit hooks, tudo somado degrada performance percebida.

**How to apply:** Observar impacto real de cada hook adicionado. Se houver lentidão, investigar qual hook é o gargalo antes de remover em massa. Não usar "redução de hooks" como solução genérica — o usuário pode querer adicionar hooks novos conforme a necessidade, e isso é legítimo. NUNCA arquivar hooks em massa sem autorização explícita.

**Estado restaurado 17/abr/2026:** 51 hooks ativos em ~/stemmia-forense/hooks/ (44 restaurados de arquivo/ após reversão do estrago do "guia de otimização de tokens" de 16/abr 21:05 que tentou reduzir para 7). Os 7 hooks registrados no settings.json apontam para scripts específicos; os demais são disparados por outros mecanismos do plugin stemmia-forense.
