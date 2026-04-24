# Rotina Diária — Perícia Judicial

## Sequência de Início

1. Abrir [[../AGORA]] — ver tarefa imediata
2. Verificar pendências processuais (prazos, intimações)
3. Checar ~/Desktop/processos-pje-windows/ por PDFs novos baixados do PJe

## Processamento de PDFs Novos

1. Localizar PDFs em ~/Desktop/processos-pje-windows/
2. Identificar número CNJ de cada PDF (nome do arquivo ou conteúdo)
3. Organizar por CNJ em ~/Desktop/STEMMIA Dexter/processos/{CNJ}/
4. Extrair texto:
   - pdftotext primeiro
   - Se retornar vazio (< 50 caracteres): tesseract --oem 1 --psm 6
5. Gerar FICHA.json com metadados (partes, vara, tipo, data)
6. Gerar URGENCIA.json com prazo e nível de urgência

## Classificação por Tipo de Documento

Cada PDF se encaixa em uma dessas categorias:

| Tipo | Ação imediata |
|------|--------------|
| Intimação para laudo | Verificar prazo, iniciar análise |
| Petição (parte/advogado) | Ler, extrair alegações relevantes |
| Laudo (outro perito/assistente) | Analisar, comparar com dados médicos |
| Quesitos | Rascunhar respostas ponto a ponto |
| Agendamento de perícia | Confirmar data, preparar roteiro |
| Proposta de honorários | Calcular via fórmula base |
| Ciência/despacho | Registrar, sem ação além de ciência |

## Final do Dia

1. Atualizar [[../AGORA]] com status
2. Registrar sessão em [[conversas/TEMPLATE-CONVERSA]] se houve trabalho com IA
3. Atualizar diário do sistema se houve marco relevante
