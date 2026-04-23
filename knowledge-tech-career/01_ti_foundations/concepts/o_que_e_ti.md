---
titulo: "O que é TI"
bloco: "01_ti_foundations/concepts"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "B"
tempo_leitura_min: 6
---

# O que é TI

## Definição técnica

Tecnologia da Informação (TI) é o conjunto de recursos computacionais — hardware, software, redes, dados e processos — aplicados à captação, armazenamento, processamento, transmissão e recuperação de informação dentro de uma organização ou sistema.

TI não é sinônimo de "mexer com computador". É disciplina aplicada: o foco é operar infraestrutura e sistemas para que a informação flua com integridade, disponibilidade e confidencialidade (tríade CIA — *Confidentiality, Integrity, Availability*).

## Distinção entre áreas próximas

TI é frequentemente confundida com outras disciplinas. Cada uma resolve um problema diferente:

- **TI (Information Technology)** — operação e suporte de infraestrutura e sistemas já existentes. Exemplo concreto: o técnico que configura o servidor que hospeda o PJe numa vara.
- **CS (Computer Science / Ciência da Computação)** — estudo teórico da computação: algoritmos, complexidade, teoria de linguagens, criptografia matemática. Exemplo: provar que um algoritmo de ordenação é O(n log n).
- **SI (Sistemas de Informação)** — intersecção entre TI e gestão; foco em como a tecnologia apoia decisões de negócio. Exemplo: modelar o fluxo de dados de um laudo pericial entre captação, N8N e banco SQLite.
- **ES (Engenharia de Software)** — disciplina de construção de software com qualidade mensurável: requisitos, arquitetura, testes, CI/CD, manutenção. Exemplo: projetar o pipeline de geração de laudo usando versionamento semântico e testes automatizados.

Resumo operacional:
- CS pensa o problema. ES constrói a solução. TI opera a solução. SI alinha a solução com o negócio.

## Por que importa para o perito

O perito judicial depende de TI para três coisas críticas:
1. **Integridade da prova digital** — hash SHA-256 de PDF de laudo, cadeia de custódia eletrônica.
2. **Disponibilidade** — servidor de email pericial fora do ar no dia da intimação = preclusão.
3. **Confidencialidade** — dados de saúde são sensíveis (LGPD, art. 5º, II).

Entender TI não é virar técnico; é saber fazer pergunta certa ao técnico e não ser enganado por jargão.

## O que TI NÃO é

- Não é "consertar impressora" (isso é suporte técnico, subconjunto da operação).
- Não é programação (isso é ES).
- Não é ciência (isso é CS).
- Não é marketing digital, design gráfico, edição de vídeo.

## Subáreas clássicas de TI

- Infraestrutura (servidores, rede, storage).
- Segurança da informação (SecOps, governança).
- Suporte e help desk.
- Governança e compliance (ITIL, COBIT).
- Administração de banco de dados (DBA).
- DevOps/SRE — híbrido TI + ES.

## Referências

- [TODO/RESEARCH: citar ABNT NBR ISO/IEC 20000 e ITIL v4 Foundation].
- [TODO/RESEARCH: confirmar definição de CS vs ES segundo ACM Computing Curricula].
