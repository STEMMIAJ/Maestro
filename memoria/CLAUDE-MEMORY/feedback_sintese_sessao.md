---
name: Síntese antes de compactar contexto
description: Sempre salvar resumo da sessão antes de perder contexto por compactação
type: feedback
---

Quando o contexto estiver no limite, ANTES de compactar:
1. Criar síntese em `~/Desktop/Projetos - Plan Mode/Registros Sessões/`
2. Nome: `SESSAO-[PROJETO]-[DATA].md`
3. Incluir: objetivo, o que fez, o que falta, decisões, arquivos, pendências
4. Avisar o usuário

**Why:** Sem isso, informações importantes se perdem na compactação e o usuário precisa repetir tudo.

**How to apply:** Monitorar tamanho do contexto. Quando estiver chegando no limite, salvar antes de qualquer compactação.
