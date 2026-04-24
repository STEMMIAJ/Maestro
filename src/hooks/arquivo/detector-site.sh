#!/bin/bash
# Hook: UserPromptSubmit — Detecta quando o usuário está criando um site
# Injeta lembrete para consultar o Manual de Design e seguir o workflow

PROMPT="$CLAUDE_USER_PROMPT"

# Palavras-chave que indicam criação/edição de site
if echo "$PROMPT" | grep -qiE '(criar site|fazer site|montar site|novo site|site do|site da|site para|landing page|página web|frontend|html.*css|hero section|layout do site|design do site|paleta.*site|fontes.*site|faz.*site|monta.*site|cria.*site|site.*cliente|webdesign|web design)'; then

  cat <<'EOF'
🎨 MODO DESIGN ATIVADO — Consultar antes de começar:

OBRIGATÓRIO:
1. Invocar skill `frontend-design`
2. Rodar agente `designer-brief` para gerar BRIEF.md
3. Consultar Manual: ~/Desktop/Sites Novos/_WORKFLOW/MANUAL-DESIGN-STEMMIA.pdf
4. Buscar 3 referências do nicho (web search)
5. Salvar projeto em ~/Desktop/Sites Novos/[nome-cliente]/

REGRAS:
- NUNCA usar Inter, Roboto, gradientes roxos
- NUNCA fazer sem brief aprovado
- Stack: Vanilla CSS3 + Custom Properties + Google Fonts
- Seguir workflow: ~/Desktop/Sites Novos/_WORKFLOW/COMO-CRIAR-SITE.md

ANTI-AI-SLOP (25 regras — consultar ~/Desktop/Sites Novos/_WORKFLOW/ANTI-AI-SLOP.md):
- ZERO Inter/Roboto/Arial. Contraste peso 300 vs 800+. h1 = 3x+ body.
- ZERO gradiente roxo. Hierarquia 70-25-5. Background NUNCA #fff.
- Assimetria intencional. Padding ≥ 80px. Grid 8pt. NUNCA "3 cards com ícone".
- Stagger 80-120ms. Max 3-5 animações/viewport. Textura noise obrigatória.
- Wave SVG entre seções. Cada projeto = fonte ÚNICA. 3 referências ANTES.
- Vocabulário específico ("art deco", "editorial"), NUNCA "moderno e clean".
- Ler bloco <frontend_aesthetics> no CLAUDE.md antes de qualquer decisão.
EOF

fi
