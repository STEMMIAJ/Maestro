---
titulo: Fundamentos de Tecnologia da Informacao
bloco: 01_ti_foundations
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 01 — Fundamentos de TI

## Definição do domínio

Este bloco reúne o vocabulário e os modelos mentais mínimos para operar qualquer discussão técnica em TI: o que é hardware, como funcionam redes e sistemas operacionais, como software nasce e é mantido, e qual o vocabulário canônico do campo.

É o bloco pré-requisito dos demais. Sem ele, qualquer discussão de programação, arquitetura, segurança ou dados vira repetição de jargão sem lastro. Aqui não se discute escolha de stack; discute-se o que essas coisas são e como se relacionam.

Público-alvo do material: profissional não-TI (médico, perito) que precisa de base sólida para dialogar com engenheiros, revisar escopos e tomar decisões técnicas informadas.

## Subdomínios

- `concepts/` — conceitos fundantes: bit, byte, arquivo, processo, protocolo, API, cliente/servidor.
- `hardware_networks_os/` — CPU, memória, disco, rede (TCP/IP, DNS, HTTP), sistemas operacionais (Linux, macOS, Windows).
- `internet_web_basics/` — como a web funciona: URL, DNS, HTTP/HTTPS, navegador, servidor, CDN.
- `software_lifecycle/` — ciclo de vida: requisito, design, codificação, teste, deploy, operação, descontinuação.
- `glossario/` — termos canônicos com definição curta, sinônimos e referência cruzada.

## Perguntas que este bloco responde

1. O que é uma API e por que ela existe?
2. Qual a diferença entre memória RAM e disco, e por que isso importa para custo e performance?
3. O que acontece entre digitar uma URL e ver a página renderizada?
4. O que é um sistema operacional e por que Linux domina servidores?
5. O que é DNS e o que falha quando "a internet não funciona"?
6. Qual a diferença entre compilado e interpretado?
7. O que é um processo e o que é uma thread?
8. O que é HTTPS e o que ele garante (e não garante)?

## Como coletar conteúdo para este bloco

- Livros-texto introdutórios (Tanenbaum, Silberschatz) para SO e redes.
- RFCs relevantes (HTTP, DNS, TCP) como fonte primária.
- Documentação oficial de Linux (man pages) e Mozilla MDN para web basics.
- Cursos estruturados (CS50, MIT OCW 6.004) para ciclo de vida e conceitos.
- Artefatos próprios: diagramas, resumos de 1 página, fichas de glossário.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Preferir fonte primária (RFC, documentação oficial, livro acadêmico) sobre blog secundário. Registrar autor, data, versão e link. Evitar conteúdo gerado por LLM sem verificação.

## Exemplos de artefatos que podem entrar

- Ficha "O que é TCP/IP em 1 página" com diagrama de camadas.
- Tabela comparativa hardware de servidor vs. desktop vs. mobile.
- Resumo dos 7 estados de um processo em Linux.
- Mapa mental do ciclo de vida de software (cascata, ágil, devops).
- Glossário com 200 termos canônicos em PT-BR e EN.
- Timeline da internet (ARPANET → HTTP/3).

## Interseções com outros blocos

- `02_programming` — conceitos de processo/memória alimentam entendimento de linguagens.
- `03_web_development` — internet_web_basics é pré-requisito direto.
- `04_systems_architecture` — redes e SO sustentam qualquer arquitetura.
- `05_security_and_governance` — protocolos e SO definem superfície de ataque.
- `11_personal_skill_mapping` — glossário serve de base para autoavaliação de nivelamento.
