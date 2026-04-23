---
titulo: "MFA e Passkeys"
bloco: "05_security_and_governance"
tipo: "pratica"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# MFA e Passkeys

Autenticação multifator exige dois ou mais fatores independentes: algo que você sabe (senha), tem (token, celular), é (biometria). Senha sozinha é insuficiente em 2026.

## Tipos de segundo fator

### SMS OTP

Código via torpedo. **Evitar.** Vulnerável a SIM swap — operadora porta número para chip do atacante. Já houve casos de roubo de conta bancária e Gov.br por esse vetor.

### TOTP (app autenticador)

Time-based One-Time Password, RFC 6238. Código de 6 dígitos que muda a cada 30s, gerado localmente a partir de segredo compartilhado.

Apps: Google Authenticator, Authy, Aegis (Android, open), Raivo (iOS), 1Password (integrado).

Boa escolha padrão. Limite: se atacante intercepta a tela de login via phishing em tempo real, TOTP é reenviado (adversary-in-the-middle).

### Push notification

App do provedor manda alerta "é você?". Usuário aprova ou nega. Vulnerável a MFA fatigue — atacante spammeia até vítima clicar sim por cansaço.

### FIDO2 / WebAuthn / Chave física

Chave criptográfica ligada ao domínio. YubiKey, Titan, Nitrokey. Padrão aberto FIDO Alliance.

- Imune a phishing: a chave só assina para o domínio correto.
- Requer toque físico.
- Biblioteca estável, suporte nativo em Chrome/Safari/Firefox.

**Recomendação pericial:** YubiKey 5C (USB-C, NFC) + backup YubiKey em cofre. Cadastrar ambas em cada serviço crítico.

### Passkey

Sucessor do FIDO2 orientado a usuário final. Chave privada fica no dispositivo (Secure Enclave no Mac/iPhone, TPM no Windows). Sincronização via iCloud Keychain, Google Password Manager, 1Password.

- Substitui senha + MFA num único gesto (Touch ID).
- Imune a phishing.
- Recuperação via outro dispositivo da mesma conta.

Adotado por Apple ID, Google, Microsoft, GitHub, 1Password, Amazon, eBay.

## Recomendação pericial

| Serviço | 1º fator | 2º fator |
|---------|----------|----------|
| Apple ID | passkey | confiança em device |
| Google (e-mail pericial) | passkey | YubiKey de backup |
| GitHub | passkey | YubiKey |
| 1Password / Bitwarden | senha mestra longa | YubiKey |
| Gov.br | senha | app Gov.br (push) |
| PJe | certificado ICP-Brasil | token físico ou A3 |
| Banco | senha + biometria | token do banco |
| N8N self-host | senha | TOTP |
| Telegram | senha 2FA | — |

## Backup e recuperação

Perder o segundo fator sem backup = perder a conta. Regras:

- Códigos de recuperação impressos, guardados em local físico seguro (cofre, gaveta com chave).
- Segunda YubiKey cadastrada em todo serviço crítico.
- Passkey sincronizado em Apple ID + 1Password (dois caminhos independentes).
- Nunca guardar códigos em pasta do Desktop em claro.

## Segredo médico e MFA

Proteger e-mail pericial com MFA é obrigação técnica derivada do art. 46 do CEM (sigilo) e LGPD (art. 46-49, segurança). Sem MFA = negligência documentada em caso de vazamento.

## Anti-padrões

- SMS como único MFA no e-mail profissional.
- TOTP armazenado no mesmo gestor de senha sem segundo fator no próprio gestor.
- Única YubiKey sem backup (perdeu = perdeu tudo).

## Referência cruzada

- `gerenciamento_de_segredos.md`
- `../compliance_privacy/lgpd_para_medico_perito.md`
