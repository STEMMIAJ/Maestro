---
titulo: "Chaves SSH e Hardening"
bloco: "05_security_and_governance"
tipo: "pratica"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Chaves SSH e Hardening

SSH autentica acesso a servidores, GitHub, hosts remotos. Chave comprometida = acesso direto a infra. Para o perito, relevante ao manter servidores N8N, VPS, deploy FTP via SFTP.

## Algoritmo: use ed25519

RSA 2048 ainda funciona, mas ed25519 é menor, mais rápido, matematicamente mais robusto. Gerar:

```bash
ssh-keygen -t ed25519 -C "jesus@perito-2026-04" -f ~/.ssh/id_ed25519_perito
```

Passphrase obrigatória. Chave sem passphrase = senha em claro no disco.

## Estrutura `~/.ssh`

```
~/.ssh/
├── config              # apelidos, opções por host
├── id_ed25519_perito   # chave privada (chmod 600)
├── id_ed25519_perito.pub
├── known_hosts         # impressões digitais de hosts conhecidos
└── authorized_keys     # chaves autorizadas a entrar NESTA máquina
```

Permissões:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519_perito ~/.ssh/config
chmod 644 ~/.ssh/*.pub ~/.ssh/known_hosts
```

SSH recusa chave com permissão frouxa.

## `~/.ssh/config` — base

```
Host n8n-srv
    HostName srv19105.nvhm.cloud
    User deploy
    IdentityFile ~/.ssh/id_ed25519_perito
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes

Host github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes
```

`IdentitiesOnly yes` impede envio de todas as chaves do agente (vazamento de inventário).

## ssh-agent e Keychain

Carregar chave uma vez por sessão:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_perito
```

No macOS a passphrase vai pro Keychain, solicitada apenas no login.

## Agent forwarding — cuidado

`ssh -A host` encaminha o agente. Se `host` estiver comprometido, atacante usa suas chaves. **Regra:** só com forward para hosts que você controla integralmente. Para saltar entre hosts, prefira `ProxyJump`:

```
Host bastion
    HostName bastion.example.com

Host interno
    HostName 10.0.0.5
    ProxyJump bastion
```

## known_hosts e TOFU

Na primeira conexão, SSH mostra fingerprint e pergunta se confia. Isso é Trust On First Use — janela de ataque MITM. Mitigações:

- Verificar fingerprint fora de banda (painel do provedor, telefone).
- `StrictHostKeyChecking accept-new` aceita novo, alerta em mudança.
- Nunca executar `ssh-keygen -R host` e reconectar sem investigar — mudança de host key pode ser ataque.

## Hardening do servidor (sshd_config)

Quando Dr. Jesus mantiver VPS:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
KbdInteractiveAuthentication no
AllowUsers deploy jesus
Protocol 2
LoginGraceTime 30
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

Adicional: fail2ban bloqueia IP após tentativas falhas. UFW/iptables restringe porta 22 a IPs conhecidos ou VPN.

## Chaves por contexto

Não reutilizar. Uma chave para GitHub, outra para VPS produção, outra para VPS desenvolvimento. Revogação localizada.

## YubiKey / chave resident

Chave SSH pode residir em YubiKey (`ssh-keygen -t ed25519-sk`). Requer toque físico para autenticar. Máximo hardening para acesso a servidor crítico.

## Rotação e inventário

Tabela em `~/.ssh/INVENTARIO.md` (fora do Git):

| Chave | Criada | Onde está cadastrada | Expira |
|-------|--------|----------------------|--------|
| id_ed25519_github | 2026-01-10 | GitHub Jesus | revisar 2027-01 |
| id_ed25519_n8n | 2026-03-15 | srv19105 | rotacionar 2026-09 |

## Anti-padrões

- Chave sem passphrase.
- `id_rsa` de 2014 ainda ativa.
- Mesma chave no celular, notebook pessoal e notebook pericial.
- `authorized_keys` nunca auditado.

## Referência cruzada

- `gerenciamento_de_segredos.md`
- `mfa_e_passkeys.md`
