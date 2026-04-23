---
titulo: "Ameaças e Vetores de Ataque"
bloco: "05_security_and_governance"
tipo: "conceito"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Ameaças e Vetores de Ataque

Vetor de ataque é o caminho usado para explorar vulnerabilidade. Ameaça é a possibilidade concreta de dano. O perito precisa identificar ameaças relevantes ao seu fluxo para priorizar defesa.

## Phishing

E-mail, SMS ou mensagem que simula entidade legítima para capturar credenciais ou instalar malware.

- Spear phishing: ataque direcionado ao alvo (nome, CRM, vara judicial).
- Clone phishing: cópia fiel de e-mail real anterior (intimação PJe falsa).
- BEC (Business Email Compromise): fraude com conta comprometida de contador, secretária.

Defesa: verificar remetente real (`Received:` header), nunca clicar em link de intimação — acessar PJe direto pelo navegador, MFA obrigatório.

## Engenharia social

Manipulação psicológica. Mais eficaz contra profissionais sobrecarregados.

- Pretexto: "sou do TRT, preciso confirmar seu CPF para liberar honorários".
- Urgência: "audiência em 1 hora, envie laudo para este e-mail".
- Autoridade: falso magistrado, falso CNJ.

Defesa: canal oficial sempre (PJe, e-proc, telefone da serventia do próprio site do tribunal). Nunca responder pressão por canal não verificado.

## Ransomware

Malware que criptografa arquivos e exige resgate. Para perito, perder base de processos ativos pode ser catastrófico.

- Vetor comum: anexo macro em .docx, executável disfarçado, RDP exposto, vulnerabilidade de VPN.
- Double extortion: exfiltra antes de criptografar, ameaça vazar.

Defesa: backup 3-2-1 offline, EDR, não abrir anexos executáveis, macros Office bloqueadas por padrão, patch em dia.

## Supply chain

Ataque via dependência confiável. Biblioteca Python maliciosa, plugin de navegador comprometido, update de software adulterado.

- Exemplos: SolarWinds (2020), XZ Utils (2024), pacotes npm tipo-squat.

Defesa: pin de versão (`requirements.txt` com hash), SBOM, revisar permissões de extensões Chrome, usar gestor de dependências reprodutível (`uv`, `poetry.lock`).

## Credential stuffing e reuso de senha

Atacante usa base vazada de um site para tentar em outro. Se Dr. Jesus reusar senha entre e-mail pericial e fórum antigo, um vazamento compromete tudo.

Defesa: senha única por serviço (gestor), MFA em tudo que aceita.

## Roubo físico

Notebook roubado em estacionamento do fórum contém laudos em andamento.

Defesa: FileVault obrigatório, senha forte de boot, Find My Mac ativo, não armazenar laudos em Desktop sem pasta criptografada.

## Insider threat

Estagiária, secretária, familiar com acesso ao computador. Pode ser malicioso ou negligente.

Defesa: conta separada por pessoa, princípio do menor privilégio, logs.

## Vetores específicos ao perito

- E-mail de intimação falsa com PDF malicioso.
- Pendrive trazido por parte em audiência com "cópia dos autos".
- Link de prontuário eletrônico de hospital em rede Wi-Fi pública.
- Ataque a assinador digital (PjeOffice) via update comprometido.

## Modelagem de ameaça mínima

Para cada ativo crítico (laudo, base de processos, chave privada ICP):

1. Quem ataca? (fraudador, parte insatisfeita, Estado hostil)
2. O que ganha? (dinheiro, chantagem, vazamento para réu)
3. Por onde entra? (e-mail, USB, rede, app)
4. Como detecto? (log, alerta, backup íntegro)

## Referência cruzada

- `../secrets_access/mfa_e_passkeys.md`
- `../incident_response/playbook_incidente_minimo.md`
