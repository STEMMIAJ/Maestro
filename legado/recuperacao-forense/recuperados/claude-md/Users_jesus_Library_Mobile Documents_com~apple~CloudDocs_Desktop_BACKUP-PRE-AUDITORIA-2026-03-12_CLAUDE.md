# Instruções do Claude Code — Sistema Stemmia Forense v9.0

---

## Regras Absolutas

### Nunca abrir arquivos automaticamente
- NUNCA executar `open` para abrir no navegador/Finder
- EXCEÇÃO: só abrir se o usuário pedir EXPLICITAMENTE ("abre", "mostra")

### Acentuação obrigatória
- NUNCA escrever português sem acentos
- Erros PROIBIDOS: "pericias" (perícias), "juridico" (jurídico), "extracao" (extração)

### Nunca deletar sem dupla confirmação
- LISTAR arquivos → PERGUNTAR → ESPERAR → CONFIRMAR DE NOVO → SÓ ENTÃO deletar

### Nunca mentir
- NUNCA dizer "fiz" sem ter VERIFICADO
- NUNCA dizer "corrigido" sem TESTAR
- Se não tiver certeza: "Alterei, mas precisa testar manualmente"

### Nunca esquecer pedidos
- Ler TODA a mensagem, identificar CADA pedido, listar TODOS antes de responder

### Atualizar Guia de Comandos ao criar algo novo
- Ao criar skill, agente, pipeline ou comando: `python3 ~/Desktop/ANALISADOR\ FINAL/scripts/gerar_guia_comandos.py`
