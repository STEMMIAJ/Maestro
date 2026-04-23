---
titulo: Quando refatorar
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: medio
tempo_leitura_min: 4
---

# Quando refatorar

Refatoração = mudar **forma** do código sem mudar **comportamento**. Não é reescrever; é melhorar estrutura mantendo o que faz.

Pré-requisito: testes cobrindo a parte refatorada. Sem teste, refatoração vira reescrita com bugs.

## Sinais de código ruim ("code smells")

### Função longa
Mais de 40–50 linhas sem razão clara. Provavelmente faz muitas coisas (viola SRP).

Ação: quebrar em funções menores com nomes que expliquem o quê.

### Nomes vagos
`dados`, `tmp`, `valor`, `processar()`, `util()`. Não indicam nada.

Ação: renomear para algo que diga propósito. `dados` → `movimentacoes_djen_hoje`. Editor faz busca-e-substitui em segundos.

### Duplicação
Dois blocos de 10+ linhas quase idênticos. Bug corrigido num, esquecido no outro.

Ação: extrair função comum.

### Aninhamento profundo
4+ níveis de `if`/`for` aninhados. Ilegível.

```python
# ruim
for p in processos:
    if p.ativo:
        if p.tem_audiencia:
            if p.data > hoje:
                if p.tipo == "pericia":
                    ...
```

Ação: usar early return ou guard clauses:
```python
for p in processos:
    if not p.ativo: continue
    if not p.tem_audiencia: continue
    if p.data <= hoje: continue
    if p.tipo != "pericia": continue
    ...   # resto plano, legível
```

### Muitos parâmetros
Função com 6+ parâmetros é difícil de lembrar e usar. Provável sinal de que devia receber um objeto.

### Comentário explicando o óbvio
`# incrementa i em 1 | i += 1` é ruído. Comentário deve explicar **por quê**, não **o quê**.

### "Mexi aqui, quebrou lá"
Acoplamento alto. Módulos interdependentes sem precisar.

### Ninguém entende — nem você depois de 2 semanas
Sinal de que precisa refatoração ou documentação.

## Refatoração mínima vs ampla

### Mínima (sempre faça)
Enquanto mexe no arquivo para outra coisa, corrige pequenos vícios:
- Renomear uma variável confusa.
- Extrair uma função de 6 linhas duplicadas.
- Inverter condicional para reduzir aninhamento.

Custo: minutos. Benefício: compound interest ao longo do tempo. **Regra do escoteiro**: deixa o código mais limpo do que encontrou.

### Ampla (com planejamento)
Mudança estrutural — quebrar classe em várias, mover responsabilidades, trocar arquitetura.

Exige:
1. Testes cobrindo o que vai mudar.
2. Tempo alocado (não "enquanto termina a feature urgente").
3. Branch dedicada.
4. Commits pequenos durante.

Quando: acumulou pressão demais, progresso virou lento, bug recorrente. Ou antes de adicionar feature grande em área confusa.

## Quando NÃO refatorar

- **Código que vai ser descartado**: script one-off, prova de conceito.
- **Sem testes e sem tempo de escrever**: risco alto, baixa recompensa.
- **Pressão de prazo em produção**: não é hora. Agenda depois.
- **Refatorar por gosto estético**: sem problema concreto, gasta tempo de todos.

## Regra pericial
Perguntas antes de começar:
1. Tem teste? Se não → escrever primeiro.
2. Vai levar mais de 1 hora? → virou feature. Avisa.
3. Muda comportamento externo? → não é refatoração, é mudança.
4. Consigo fazer em commits pequenos e reversíveis? → se não, quebra o plano antes.

Commit típico de refatoração: `"refactor: extrai extrair_cnj de processar_laudo"`. Mensagem começa com `refactor:` para diferenciar de feature/bug.
