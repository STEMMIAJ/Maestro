---
titulo: "Princípios de dashboard — foco, hierarquia, 5 métricas"
bloco: "06_data_analytics/dashboards_bi"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 5
---

# Princípios de dashboard

Dashboard não é "tela com muitos gráficos". É instrumento de decisão. Falha mais comum: excesso de informação → ninguém olha.

## Regra das 5 métricas

Se não cabe em **5 números/gráficos principais**, não é dashboard — é relatório. Dashboard de perícia ativo (exemplo):

1. Processos ativos — total + variação (semana).
2. Laudos em atraso (> prazo judicial).
3. Tempo médio de elaboração (dias).
4. Receita do mês.
5. Próximas audiências (7 dias).

Tudo mais vira **drill-down** sob demanda.

## Hierarquia visual

Olho humano faz leitura em **Z** (ou F em telas longas). Itens mais importantes no **topo-esquerda**. Tamanho comunica importância mais que cor.

- **Grande + negrito**: KPI principal (ex.: 12 laudos em atraso).
- **Médio**: contexto (variação vs. semana anterior).
- **Pequeno**: detalhes (link para lista).

## Menos é mais (princípio de Tufte)

- **Alta razão dado/tinta**: cada pixel deve carregar informação.
- Eliminar: bordas 3D, sombras, gradientes, ícones decorativos.
- **Eixos**: começam em zero para barras; podem ser truncados para linhas se justificado.
- **Cores**: 1 cor de destaque + tons neutros. Paleta categórica só com ≤ 6 categorias.

## Contexto é obrigatório

Número sozinho mente. Sempre comparar com:

- Período anterior (semana passada, mesmo mês ano anterior).
- Meta / limite (prazo judicial = 30 dias).
- Benchmark (média histórica pessoal).

Exemplo ruim: "Laudos entregues: 14".
Exemplo bom: "Laudos entregues: 14 ↑3 vs. mês anterior (média 12 últimos 6 meses)".

## Tipos de gráfico — escolher certo

| Pergunta | Gráfico |
|---|---|
| Evolução temporal | Linha |
| Comparação entre categorias | Barras horizontais (se nomes longos) |
| Composição de um total | Barras empilhadas ou 100% stacked (evitar pizza > 3 fatias) |
| Distribuição | Histograma, boxplot |
| Correlação | Dispersão |
| Densidade geográfica | Mapa coroplético |

## Atualização e latência

- Dashboard operacional (perito vendo agora): atualização ≤ 1 h ou tempo real.
- Dashboard estratégico (mensal): diário é suficiente.
- Sempre mostrar **timestamp da última atualização** no rodapé.

## Acessibilidade

- Contraste mínimo 4,5:1 (WCAG AA).
- Não depender só de cor — adicionar rótulo / ícone.
- Paleta amigável a daltonismo (evitar verde × vermelho puros; preferir azul × laranja).

## Anti-padrões

1. **Semáforo colorido sem escala** ("vermelho = ruim" sem limite definido).
2. **Gauges** ocupam muito espaço para pouco dado.
3. **Tabelas gigantes sem ordenação/filtro**.
4. **Gráfico de pizza com > 5 fatias** — vira mosaico ilegível.
5. **Eixos duplos** — quase sempre induzem erro de interpretação.

## Checklist final

- [ ] Fica claro **em 5 segundos** qual o estado atual?
- [ ] Cada métrica tem contexto (vs. período / meta)?
- [ ] Timestamp visível?
- [ ] Cabe em 1 tela (sem scroll) para o caso principal?
- [ ] Alguém consegue tomar decisão só olhando?
