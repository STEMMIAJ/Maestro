---
titulo: "Métricas para perícia médica — prática individual"
bloco: "07_health_data/analytics_for_medical_work"
tipo: "pratica"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "moderado"
tempo_leitura_min: 7
---

# Métricas para perícia médica

Gestão baseada em dado vale também para o perito solo. Permite detectar gargalos, prever carga de trabalho, defender honorários e identificar tendências.

## Métricas operacionais

### Volume

- **Nomeações recebidas/mês** — entrada.
- **Laudos entregues/mês** — saída.
- **Estoque ativo** = nomeações aceitas − laudos entregues − recusas.
- **Taxa de aceitação** = aceites / nomeações.

### Tempo

- **Tempo médio de elaboração** (horas/laudo) — da aceitação à entrega.
- **Tempo médio desde nomeação até aceite** (triagem).
- **Tempo médio desde entrega até pagamento** (ciclo financeiro).
- **Atraso (dias)** = data atual − prazo judicial, para processos não entregues.

### Financeiro

- **Receita bruta/mês** = soma honorários pagos.
- **Receita por hora trabalhada** = honorários / horas de elaboração.
- **Inadimplência** = % honorários arbitrados não pagos em 90 dias.

## Métricas de qualidade

- **% de impugnação pela parte contrária** após entrega do laudo.
- **% de complementação solicitada pelo juiz**.
- **% de discordância com parte contrária** (quando há assistente técnico).
- **% de laudos que dão origem a decisão alinhada** (quando rastreável).

`[TODO/RESEARCH: benchmarks nacionais — não há levantamento público consolidado]`.

## Métricas de composição

- **Distribuição por classe processual** (ex.: % acidente de trabalho, % erro médico, % DPVAT).
- **Distribuição por especialidade pericial**.
- **Distribuição por tribunal/vara**.
- **Distribuição por valor da causa** (faixas).

## Painel sugerido (5 cartões principais)

1. **Estoque ativo** + variação semana.
2. **Atrasos** (laudos além do prazo judicial).
3. **Laudos entregues no mês** vs. meta.
4. **Receita acumulada no ano**.
5. **Próximas audiências 7 dias**.

Ver `06_data_analytics/dashboards_bi/principios_de_dashboard.md`.

## Como medir — schema mínimo

```sql
-- Base: tabela `processos` + `laudos` (ver sqlite_local_para_pericia.md)

-- Nomeações/mês
SELECT strftime('%Y-%m', data_nomeacao) AS mes, COUNT(*) AS nomeacoes
FROM processos
GROUP BY mes ORDER BY mes;

-- Tempo médio de elaboração
SELECT AVG(tempo_elaboracao_horas) AS h_medio,
       CAST(AVG(tempo_elaboracao_horas) * 60 AS INTEGER) AS minutos
FROM laudos
WHERE data_entrega >= DATE('now', '-12 months');

-- Receita por hora
SELECT SUM(honorarios) / SUM(tempo_elaboracao_horas) AS reais_por_hora
FROM laudos
WHERE data_entrega >= DATE('now', '-12 months');

-- Taxa de aceitação
SELECT
  COUNT(*) AS nomeacoes,
  SUM(CASE WHEN status = 'aceito' OR status = 'entregue' THEN 1 ELSE 0 END) AS aceitas,
  SUM(CASE WHEN status = 'aceito' OR status = 'entregue' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS taxa
FROM processos;
```

## Indicadores de alerta

- Estoque subindo > 20% ao mês → saturação.
- Tempo médio de elaboração subindo → casos mais complexos ou ineficiência.
- Receita/hora caindo → honorários arbitrados desalinhados.
- % impugnação subindo → revisar metodologia/laudo-modelo.

## Uso em defesa de honorários

Em petição de majoração, apresentar:

- Tempo efetivo de elaboração (horas, com evidência — log de atividade).
- Complexidade do caso (n de quesitos, volumes de exame analisados).
- Comparação com honorários médios pagos em casos semelhantes.
- Média histórica pessoal de reais/hora.

## Frequência de leitura

- **Diário**: fila de atrasos, próximas audiências.
- **Semanal**: entradas vs saídas, estoque.
- **Mensal**: receita, distribuição por classe, qualidade.
- **Anual**: tendências, benchmark com anos anteriores.

## Pegadinhas

1. **Tempo de elaboração só confiável se cronometrado** — self-report sem método subestima.
2. **Impugnação nem sempre indica qualidade baixa** — pode ser estratégia da parte.
3. **Receita mensal oscila** (pagamento judicial é irregular) — usar médias móveis 3 ou 6 meses.
4. **Amostra pequena** em subgrupos — cuidado com % em n < 10.
