---
titulo: "Segurança por Camadas — Defense in Depth e Zero Trust"
bloco: "05_security_and_governance"
tipo: "conceito"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Segurança por Camadas

Nenhum controle é suficiente sozinho. A arquitetura assume que qualquer camada pode falhar, e outras camadas contêm o dano.

## Defense in Depth

Modelo clássico: camadas concêntricas, cada uma com controles independentes.

1. **Perímetro**: firewall, VPN, filtro DNS.
2. **Rede interna**: segmentação, IDS/IPS.
3. **Host**: EDR, antivírus, hardening de SO.
4. **Aplicação**: WAF, validação de input, atualização.
5. **Dado**: criptografia em repouso e trânsito, DLP.
6. **Identidade**: MFA, SSO, RBAC.
7. **Pessoas**: treinamento, política, cultura.

O atacante que fura o firewall ainda encontra EDR. Que fura EDR encontra criptografia. Que captura o disco ainda precisa da chave.

## Princípios operacionais

- **Menor privilégio**: conta de trabalho não é admin. Sudo exige senha a cada vez.
- **Separação de deveres**: quem assina laudo não administra servidor.
- **Fail secure**: na dúvida, bloqueia.
- **Segurança por padrão**: configuração inicial já é a mais restritiva.

## Zero Trust

Evolução do modelo. Parte do princípio: "nenhuma rede é confiável, incluindo a interna". Cada requisição é autenticada e autorizada, independente de origem.

Pilares (NIST SP 800-207):

1. Verificar explicitamente (identidade + contexto: dispositivo, localização, hora, comportamento).
2. Menor privilégio com acesso just-in-time.
3. Assumir violação (projetar como se atacante já estivesse dentro).

Na prática para profissional liberal:

- Usar passkey ou YubiKey em vez de só senha.
- Dispositivo gerenciado (MDM) ou ao menos compliant (FileVault, patch, EDR).
- Acesso a PJe e sistemas sensíveis exige MFA a cada sessão.
- Nada de "rede interna confiável" — Wi-Fi do consultório não libera acessos extras.

## Aplicação ao fluxo pericial

| Camada | Controle concreto |
|--------|-------------------|
| Identidade | MFA no e-mail perito, certificado ICP-Brasil |
| Dispositivo | FileVault, patch macOS em dia |
| Rede | DNS filtrado (NextDNS), sem Wi-Fi público |
| App | Chrome/Safari atualizados, extensões auditadas |
| Dado | Laudos em pasta criptografada, backup cifrado |
| Detecção | Log de acesso ao Keychain, alerta de login novo |

## Anti-padrão comum

- Senha única compartilhada no consultório.
- VPN "aberta" que dá acesso a tudo após conectar.
- Senha salva em `.txt` no Desktop.
- Pendrive sem criptografia rodando entre fórum e casa.

## Referência cruzada

- `triade_cia.md`
- `../secrets_access/gerenciamento_de_segredos.md`
- `../secrets_access/mfa_e_passkeys.md`
