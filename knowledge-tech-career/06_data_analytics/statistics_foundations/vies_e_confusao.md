---
titulo: "Viés e confusão — erros sistemáticos em estudos e laudos"
bloco: "06_data_analytics/statistics_foundations"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Viés e confusão

Erro sistemático ≠ erro aleatório. Amostra maior **não corrige viés** — só reduz erro aleatório. Em perícia, saber identificar viés em literatura citada pelas partes é arma crítica.

## Viés de seleção

Amostra não representa a população-alvo porque o processo de inclusão favorece certos perfis.

- **Viés de Berkson**: estudo hospitalar superestima associação entre duas doenças (quem tem as duas procura mais hospital).
- **Viés do voluntário saudável**: quem aceita participar é mais saudável que a média.
- **Perda de seguimento diferencial**: dropout correlacionado com desfecho.
- **Viés de sobrevivência**: só analisa os que "sobreviveram" até a medida.

**Controle**: amostragem probabilística, protocolos de inclusão/exclusão claros, rastrear perdas.

## Viés de informação (aferição)

Erro na medida da exposição ou do desfecho.

- **Viés de memória (recall)**: caso-controle sobre malformação congênita — mãe de criança afetada lembra mais exposições que mãe-controle.
- **Viés do entrevistador**: pergunta de forma diferente a casos e controles.
- **Viés de classificação**: critério diagnóstico aplicado de modo diferente entre grupos.
- **Viés de publicação**: estudos positivos publicam mais. Metanálise precisa funnel plot.

**Controle**: cegamento, instrumentos padronizados, definições operacionais fixas.

## Confundidor (confounding)

Variável que está associada **tanto à exposição quanto ao desfecho**, **sem** estar no caminho causal.

- Exemplo clássico: **café × infarto**, confundido por tabagismo (fumantes bebem mais café E infartam mais).
- Exemplo pericial: **idade × mortalidade cirúrgica**, confundida por comorbidades.

**Critérios para ser confundidor**:
1. Associado à exposição.
2. Fator de risco para o desfecho (independentemente da exposição).
3. Não é efeito da exposição (não está no caminho causal).

**Controle** no desenho: randomização (gold standard), restrição, emparelhamento.
**Controle** na análise: estratificação, regressão multivariada, escore de propensão.

## Modificador de efeito (interação)

Variável cuja presença **muda a magnitude** do efeito da exposição.

- Exemplo: aspirina reduz infarto em homens, mas não em mulheres → sexo é modificador.
- Não é artefato a ser removido — é achado **real e reportável**.
- Diferente de confundidor: confundidor distorce estimativa global; modificador aparece quando estratifica.

## Checklist pericial rápido

Ao ler estudo citado:

1. Como foi a seleção? Hospitalar? Voluntários?
2. Exposição medida antes ou depois do desfecho?
3. Quem mediu sabia do grupo (cegamento)?
4. Perdas de seguimento > 20%? São diferentes entre grupos?
5. O ajuste multivariado inclui idade, sexo, comorbidades relevantes?
6. Há teste de interação reportado?

## Quantificação

- **Viés máximo** pode ser estimado por análise de sensibilidade (E-value).
- **Fator de inflação de variância (VIF)** detecta colinearidade entre preditores, não confusão em si.

## Diferença entre os três

| Conceito | Distorce? | Controla com? |
|---|---|---|
| Viés | Sim, sistemático | Desenho |
| Confundidor | Sim, relação espúria | Desenho ou análise |
| Modificador | Não distorce — revela heterogeneidade | Reportar por estrato |
