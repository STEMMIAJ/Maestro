---
titulo: "Cliente-servidor e nuvem"
bloco: "01_ti_foundations/concepts"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "B"
tempo_leitura_min: 6
---

# Cliente-servidor e nuvem

## Modelo cliente-servidor

Arquitetura em que duas peças de software conversam por rede:

- **Cliente** — quem inicia a requisição. Exemplo: o navegador no seu Mac.
- **Servidor** — quem responde. Exemplo: a máquina que hospeda `stemmia.com.br` e devolve o HTML.

Protocolo típico: cliente faz `HTTP GET /laudo/123` → servidor processa → devolve resposta (HTML, JSON, PDF). Um servidor atende vários clientes simultâneos; um cliente pode falar com vários servidores.

Alternativa: **peer-to-peer (P2P)**, onde não há hierarquia — cada nó é cliente e servidor ao mesmo tempo (BitTorrent).

## Nuvem (cloud)

Nuvem é modelo de consumo em que recursos computacionais (CPU, RAM, disco, rede) são contratados sob demanda de um provedor, em vez de comprados e instalados fisicamente. Você paga pelo uso, não pelo ativo.

### Modelos de implantação

- **Nuvem pública** — infraestrutura compartilhada operada por terceiro (AWS, Google Cloud, Azure, Oracle Cloud). Multi-tenant.
- **Nuvem privada** — infraestrutura dedicada a uma única organização, on-premises ou em data center terceirizado. Exemplo: PJe do CNJ roda em nuvem privada do Judiciário.
- **Nuvem híbrida** — mistura das duas. Dados sensíveis on-premises, processamento pesado na pública.

### Modelos de serviço (pilha de responsabilidade)

Do mais "você gerencia tudo" para "o provedor gerencia tudo":

- **IaaS (Infrastructure as a Service)** — provedor entrega máquina virtual crua. Você instala SO, banco, aplicação. Exemplo: EC2 da AWS.
- **PaaS (Platform as a Service)** — provedor entrega plataforma pronta (banco, runtime, deploy). Você só sobe o código. Exemplo: Heroku, Google App Engine.
- **SaaS (Software as a Service)** — provedor entrega aplicação pronta. Você só usa. Exemplo: Gmail, Notion, Planner.

## Exemplo aplicado ao seu ambiente

- **stemmia.com.br** — servidor web (hospedagem Hostinger — [TODO/RESEARCH: confirmar provedor atual]). Modelo: SaaS para o visitante, IaaS/PaaS para você como administrador.
- **Claude (claude.ai)** — SaaS hospedado em nuvem pública. Você é cliente via navegador ou CLI; o modelo roda em GPUs da Anthropic/AWS.
- **Seu Mac** — cliente na maior parte do tempo (navega, consome). Vira servidor quando roda `python -m http.server` local ou quando abre a porta 9223 do Chrome debug.
- **PJe** — sistema em nuvem privada do Judiciário. Cliente: seu navegador (ou o Selenium automatizando-o).
- **N8N self-hosted** — roda em nuvem pública (VPS srv19105). Modelo IaaS: você instalou tudo numa máquina alugada.

## Por que importa para o perito

- Perícia sobre prova digital hospedada em nuvem exige entender **jurisdição** dos dados (servidor no exterior = Marco Civil art. 11).
- SLA (*Service Level Agreement*) do provedor define disponibilidade contratada — crítico se sistema pericial cair no prazo.
- LGPD responsabiliza controlador (você) mesmo quando operador (provedor) é quem falha.

## Referências

- NIST SP 800-145 (definição de cloud computing).
- [TODO/RESEARCH: citar Res. CNJ 396/2021 sobre computação em nuvem no Judiciário].
