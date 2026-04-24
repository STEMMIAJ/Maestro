# REPLICABILIDADE — Guia de Clonagem da Estrutura cowork/

Guia seco para replicar a arquitetura `cowork/` em outros domínios (Clínica Minas, Stemmia Forense, projetos pessoais).

---

## 1. Princípio central

Template + dados = entregável. UMA fonte de verdade por ativo (nunca duplicar). Zero trabalho manual que seja repetível — se repete, vira pipeline ou script.

---

## 2. Os 5 universais (toda replicação tem)

Pastas obrigatórias. Cada uma responde UMA pergunta.

| Pasta | Pergunta que responde |
|---|---|
| `01-ATIVO/` | O que estou trabalhando AGORA? |
| `02-BIBLIOTECA/` | Qual template/referência eu reuso? |
| `03-IDENTIDADE/` | Como eu me apresento (timbrado, assinatura, dados fixos)? |
| `04-PIPELINES/` | Qual a receita passo-a-passo para cada tipo de tarefa? |
| `05-AUTOMACOES/` | O que a máquina faz sozinha (skills, hooks, scripts, slash-commands)? |

Sem uma destas, a estrutura não é replicável — é bagunça organizada.

---

## 3. Os 3 adaptáveis (podem fundir ou sumir)

| Pasta | Quando usar | Quando cortar |
|---|---|---|
| `00-INDICE/` | Domínio com +5 fluxos ou múltiplos colaboradores | Projeto pessoal solo com 1 fluxo |
| `06-APRENDIZADO/` | Erros recorrentes que merecem destilação | Domínio estável, sem feedback loop |
| `07-ARQUIVO/` | Casos encerrados precisam ser consultáveis | Projeto descartável |
| `INBOX/` | Chegam itens não-classificados com frequência | Tudo entra já categorizado |

Regra: na dúvida, NÃO crie. Criar pasta vazia = dívida organizacional.

---

## 4. Receita de replicação — 7 passos

1. **Criar as 5 pastas universais** na raiz do novo domínio. Nada além disso no dia 1.
2. **Definir o que é um "caso"** no domínio. Substantivo concreto, pluralizável, com início e fim. Escrever a definição em `00-INDICE/README.md` (ou raiz, se não houver índice).
3. **Criar `01-ATIVO/_TEMPLATE-CASO/`** com as subpastas mínimas que todo caso terá (ex: `entrada/`, `trabalho/`, `saida/`, `FICHA.md`). Template é pasta, não arquivo.
4. **Identificar fontes já existentes** (templates, bases, identidade visual) e criar SYMLINKS em `02-BIBLIOTECA/` e `03-IDENTIDADE/`. Nunca copiar — copiar divide a verdade.
5. **Escrever `PLANO-ACAO.md`** com 3-4 fases curtas (Fundação → Primeiro caso → Automação mínima → Feedback). Cada fase tem critério de saída objetivo.
6. **Criar 2-3 pipelines em Markdown** em `04-PIPELINES/` — receitas numeradas, executáveis por outra pessoa sem perguntar. Um pipeline = um fluxo recorrente.
7. **Criar 1 slash-command** em `05-AUTOMACOES/` que crie um caso novo a partir do template. Se abrir um caso exige +3 passos manuais, a estrutura falhou.

Fim do dia 1: a estrutura está pronta para receber o primeiro caso real.

---

## 5. Três exemplos concretos

### (a) Clínica Minas — gestão médica

- **Caso** = paciente em acompanhamento (NÃO atendimento isolado). Paciente tem início (primeira consulta) e encerramento (alta ou abandono).
- **01-ATIVO/** = prontuários ativos.
- **02-BIBLIOTECA/** = modelos de atestado, receituário, termos de consentimento, protocolos clínicos.
- **03-IDENTIDADE/** = timbrado da clínica, CRM, CNPJ, assinatura digital.
- **04-PIPELINES/** = "primeira consulta", "retorno", "alta", "encaminhamento".
- **07-ARQUIVO/** = pacientes com alta ou sem retorno há 12 meses.

### (b) Stemmia Forense — consultoria pericial

- **Caso** = demanda de cliente (NÃO cliente). Um cliente pode ter N demandas; cada demanda tem escopo, prazo, entregável.
- **01-ATIVO/** = demandas em andamento.
- **02-BIBLIOTECA/** = modelos de parecer, roteiros de análise, jurisprudência-base, cláusulas contratuais padrão.
- **03-IDENTIDADE/** = timbrado Stemmia, CNPJ, dados bancários, proposta comercial padrão.
- **04-PIPELINES/** = "onboarding cliente", "entrega de parecer", "fechamento de demanda".
- **06-APRENDIZADO/** = padrões de quesitos recorrentes, erros de escopo.

### (c) Projeto pessoal — "Apartamento novo"

- **Caso** = ambiente da casa (sala, cozinha, quarto). Cada ambiente tem orçamento, decisões, fornecedores.
- **01-ATIVO/** = ambientes em obra/compra.
- **02-BIBLIOTECA/** = referências visuais, medidas padrão, contatos de marceneiros/eletricistas.
- **03-IDENTIDADE/** = endereço, dados do condomínio, plantas.
- **04-PIPELINES/** = "cotar móvel planejado", "contratar serviço", "fechar ambiente".
- Sem `06-APRENDIZADO/` — projeto finito. Sem `INBOX/` — escopo fechado.

---

## 6. Armadilhas comuns

- **Duplicar template em vez de symlink** — cria N versões "quase iguais" da mesma coisa. Verdade se fragmenta.
- **Criar pasta "organizando" / "misc" / "temp"** sem finalidade definida. Vira buraco negro. Se não responde a uma pergunta, não existe.
- **Pipeline sem dono único** — duas pessoas (ou dois scripts) editando a mesma receita = conflito garantido. Cada pipeline tem 1 responsável por atualização.
- **Automação prematura** — automatizar antes do 3º caso real. Você está automatizando algo que ainda não existe.
- **Não definir o que é "encerrado"** — sem critério de fechamento, `01-ATIVO/` vira cemitério. Definir no dia 1: "caso encerrado quando X".

---

## 7. Checklist de saúde

Rode mensalmente. Qualquer "não" = intervir.

- [ ] Posso criar um caso novo em 1 comando (slash-command ou script)?
- [ ] A biblioteca tem 1 fonte de verdade por template (sem duplicatas)?
- [ ] O timbrado/identidade é global — alterado em 1 lugar, reflete em todos os casos?
- [ ] Os pipelines são executáveis por um iniciante sem me perguntar?
- [ ] Cada caso encerrado migra automaticamente (ou por 1 comando) para `07-ARQUIVO/`?
- [ ] Há 1 dashboard/índice que mostra o estado de todos os casos ativos?
- [ ] A pasta `INBOX/` (se existe) é triada ao menos 1x por semana — não acumula?

---

## 8. Ordem de replicação sugerida

1. Clínica Minas (domínio mais próximo do cowork/ atual — reusa 80% da lógica).
2. Stemmia Forense (reusa identidade + biblioteca jurídica já existente via symlink).
3. Projeto pessoal (teste de aderência da estrutura a domínio não-profissional).

Se a estrutura não sobrevive ao teste (3), ela tem acoplamento oculto ao domínio pericial. Refatorar.
