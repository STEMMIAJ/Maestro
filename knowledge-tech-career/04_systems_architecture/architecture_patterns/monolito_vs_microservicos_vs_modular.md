---
titulo: Monólito vs Microsserviços vs Modular
bloco: 04_systems_architecture
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 8
---

# Monólito vs Microsserviços vs Modular

Três estilos de organização. A escolha errada custa anos. Regra prática de 2026: **começar monólito modular; extrair microsserviços sob dor real**.

## Monólito (clássico)

Um único processo, um único deploy, um único banco. Todo código junto.

Prós:
- Deploy simples (um container, um binário).
- Transação ACID grátis (mesmo DB).
- Refactor fácil (grep no projeto inteiro).
- Debug simples (um processo para inspecionar).
- Latência zero entre módulos (chamada de função).

Contras:
- Scale só vertical (ou escalar tudo junto).
- Stack única — difícil misturar Python e Go.
- Deploy de qualquer coisa = deploy de tudo.
- Time grande pisando no pé um do outro.
- Código degrada se não houver disciplina (módulos viram espaguete).

## Microsserviços

Serviços pequenos, independentes, comunicando via rede (REST, gRPC, filas). Cada um tem seu DB.

Prós:
- Escala independente (scale só o serviço de busca).
- Stack por serviço (Python para ML, Go para gateway).
- Deploy isolado (time A deploya sem esperar time B).
- Isolamento de falha (crash em um não derruba outros, se bem feito).
- Organização por time (Conway's Law aplicada).

Contras:
- **Complexidade operacional gigante** — service mesh, distributed tracing, service discovery, circuit breakers.
- Consistência eventual — sem transações ACID entre serviços. Saga pattern.
- Latência de rede entre chamadas.
- Debug distribuído — precisa de correlation IDs, OpenTelemetry, logs centralizados.
- Custo infra (k8s, registry, múltiplos bancos, observability stack).
- Versionamento de API cross-service.

Cobrança de entrada: só vale a pena com 20+ engenheiros E tráfego/criticidade que exige.

## Monólito modular (modular monolith)

Monólito por fora, bem separado por dentro. Módulos com fronteiras claras, comunicação via interfaces internas (não funções internas de outros módulos).

Estrutura típica:

```
app/
  modules/
    processos/
      domain/       # entidades, regras
      application/  # casos de uso
      infra/        # DB, HTTP clients
      api/          # endpoints públicos DO MÓDULO
    laudos/
      domain/
      application/
      infra/
      api/
    shared/         # só tipos neutros
  composition/      # app "monta" os módulos
```

Regra de ouro: módulo A **nunca importa** código interno de módulo B. Só consome `laudos.api` (interface pública).

Prós:
- Simplicidade do monólito.
- Fronteiras claras permitem extrair serviço depois SEM reescrever.
- Deploy único, sem ops distribuída.
- Time pequeno e médio produz muito.

Contras:
- Disciplina exige ferramenta (linters de dependência, ArchUnit, boundaries.py).
- Pode virar monólito clássico se ninguém reforçar regras.

## Matriz de decisão

| Contexto | Escolha |
|----------|---------|
| 1–10 devs, produto novo | **Monólito modular** |
| 10–30 devs, produto maduro | **Monólito modular** + extração pontual |
| 30+ devs, domínios claros | **Microsserviços** (por domínio) |
| Equipe 1 pessoa (Dr. Jesus) | **Monólito** simples |
| Pico de tráfego previsível | Monólito vertical + réplicas |
| Workload heterogêneo (ML pesado + CRUD leve) | Monólito principal + 1 serviço isolado |
| Regulatório exige isolamento | Serviços separados |
| Multi-tenant com SLA diferente por cliente | Serviços ou Monólito multi-região |

## Armadilhas dos microsserviços

1. **Distributed monolith** — microsserviços tão acoplados que mudança em um quebra outros. Pior dos mundos.
2. **Nano-services** — serviço com 1 endpoint e 50 linhas. Overhead enorme, benefício zero.
3. **Shared database** — serviços "diferentes" escrevendo na mesma tabela. Volta ao monólito pela porta dos fundos.
4. **Sem observabilidade** — produção vira caixa preta. Sem traces, debug impossível.
5. **Migrar tudo em big bang** — reescrever monólito em microsserviços simultaneamente. Strangler Fig pattern é o certo: extrair aos poucos.

## Sinais para extrair microsserviço

- Um módulo escala muito diferente do resto (picos irregulares).
- Stack incompatível (ML em Python, resto em Go).
- Time dedicado que sofre com deploy compartilhado.
- Dependência externa que compromete estabilidade do resto.
- Regulatório/isolamento de dados.

## Modular monolith na prática

- Python: `boundaries` linter, package structure disciplinada.
- JS/TS: Nx workspace com `enforce-module-boundaries`.
- Java: ArchUnit, jMolecules.
- Banco: esquemas separados por módulo, ou schema único com prefixo.

## Para o sistema pericial

Dr. Jesus = 1 pessoa. Sistema pericial = monólito simples (Python/FastAPI + banco Postgres ou SQLite). Módulos: `processos`, `laudos`, `integracoes/datajud`, `integracoes/pje`, `notificacoes`. Começar sem overengineering; extrair serviço só se uma integração instável (PJe) começar a derrubar o resto.

O monitor de processos já é um "serviço" separado (script Python com launchd) — padrão ok. Dashboard pode ser outro serviço em Streamlit. Isso já é mini-arquitetura distribuída sem complexidade operacional.
