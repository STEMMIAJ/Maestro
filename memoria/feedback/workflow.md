# Feedback de Workflow

## Execução

1. **Paralelo sempre, nunca sequencial** — se pode fazer ao mesmo tempo, fazer
2. **Gastar tokens > gastar tempo** — velocidade máxima, mesmo que use mais recurso
3. **Ler TODA a mensagem, identificar CADA pedido antes de agir** — não começar pelo primeiro item e esquecer o resto
4. **Extrair do contexto e executar** — não perguntar o que já está implícito

## Segurança

5. **NUNCA rm -rf** — usar `mv /tmp/` como padrão seguro para remoção
6. **NUNCA deletar sem dupla confirmação** do usuário
7. **NUNCA executar `open`** — exceção: pedido explícito
8. **NUNCA criar arquivos na raiz do Desktop** — usar estrutura de pastas

## Verificação

9. **NUNCA dizer "feito" sem verificar** — mostrar output de verificação comprovada
10. **NUNCA dizer "corrigido" sem testar** — rodar teste ou verificação
11. **Falhou 2x = mudar estratégia** — diagnosticar causa raiz, não repetir

## Continuidade

12. **Ler diário antes de qualquer ação** — ~/Desktop/DIARIO-PROJETOS.md ou diário do sistema
13. **Ler fluxo existente antes de criar novo** — não duplicar
14. **Salvar síntese antes de compactar contexto** — informação não pode se perder
15. **Cada sessão deve ter 1 resultado concreto** — priorizar casos reais > infraestrutura

## Modelos

16. **Tudo Opus** — NUNCA sugerir trocar modelo por agente
17. **Subagentes:** `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6`
18. **NUNCA rebaixar para Sonnet/Haiku** sem autorização explícita
