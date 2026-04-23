---
titulo: "SSH e acesso remoto"
bloco: "01_ti_foundations/hardware_networks_os"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 6
---

# SSH e acesso remoto

## O que é SSH

*Secure Shell*. Protocolo e comando para operar uma máquina remota de forma criptografada. Substituiu telnet/rlogin (texto claro, inseguro) nos anos 2000.

Uso típico: `ssh jesus@srv19105.nvhm.cloud` abre shell remoto na VPS do N8N.

Porta padrão: 22 (TCP). Pode ser customizada (2222) para reduzir ataques automatizados.

Funcionalidades além de shell:
- Transferência de arquivos: `scp`, `sftp`, `rsync -e ssh`.
- Túnel (*port forwarding*) local ou reverso.
- Execução de comando único: `ssh host 'ls /var/log'`.
- Proxy SOCKS dinâmico: `ssh -D 1080`.

## Chaves pública e privada (criptografia assimétrica)

SSH moderno autentica por par de chaves, não senha:

- **Chave privada** — fica só na sua máquina, nunca sai. Arquivo típico: `~/.ssh/id_ed25519`. Dono a lê; deve ter permissão `600`.
- **Chave pública** — derivada matematicamente da privada, pode ser distribuída livremente. Arquivo: `~/.ssh/id_ed25519.pub`.

Princípio: o que a privada assina, só a pública verifica (e vice-versa). Recuperar privada a partir da pública é computacionalmente inviável.

## ssh-keygen

Comando que gera par de chaves:

```
ssh-keygen -t ed25519 -C "perito@drjesus.com.br"
```

- `-t ed25519` — tipo do algoritmo. Ed25519 é o padrão atual (rápido, chave curta, seguro). RSA 4096 ainda aceito; DSA obsoleto.
- `-C` — comentário (apenas rótulo).
- Pergunta onde salvar (`~/.ssh/id_ed25519` padrão) e opcionalmente uma *passphrase* para criptografar a própria chave privada em repouso.

## authorized_keys

Arquivo no servidor remoto (`~/.ssh/authorized_keys`) que lista chaves públicas autorizadas a entrar naquele usuário. Uma linha por chave.

Fluxo:
1. Gera par no cliente.
2. Copia conteúdo de `~/.ssh/id_ed25519.pub` para `~/.ssh/authorized_keys` no servidor.
3. Atalho: `ssh-copy-id jesus@srv19105.nvhm.cloud`.

Permissões obrigatórias no servidor:
- `~/.ssh` → `700`
- `~/.ssh/authorized_keys` → `600`

Se estiverem abertas demais, o sshd ignora por segurança.

## Por que não usar senha

1. **Senha é adivinhável**. Bots varrem porta 22 tentando `root:123456`, `admin:password` etc.
2. **Senha trafega por dígitos limitados**. Mesmo criptografada na sessão, o espaço de busca é pequeno (senhas humanas têm ~30 bits de entropia).
3. **Chave Ed25519 tem 256 bits de entropia real**. Inquebrável na prática.
4. **Senha pode vazar** em phishing, keylogger, reuso entre serviços. Chave privada mora num único arquivo que você protege.
5. **Auditoria** — no servidor, dá para ver qual chave (pelo fingerprint) logou em cada momento; senha única compartilhada perde rastreabilidade.

Boa prática: no `/etc/ssh/sshd_config` do servidor, setar `PasswordAuthentication no` e `PermitRootLogin no`.

## Config do cliente (~/.ssh/config)

Evita digitar tudo toda vez:

```
Host n8n
  HostName srv19105.nvhm.cloud
  User jesus
  Port 22
  IdentityFile ~/.ssh/id_ed25519
```

Depois: `ssh n8n` basta.

## Por que importa para o perito

- **VPS N8N pericial** só acessa por SSH com chave — se a chave privada vazar, atacante entra na infraestrutura.
- **Transferência de PDFs de laudo** para o servidor deve ser via `scp`/`sftp`, nunca FTP puro (texto claro, expõe credenciais).
- **Perícia forense em servidor invadido** costuma examinar `~/.ssh/authorized_keys` — chave desconhecida adicionada = indício de persistência do invasor.
- **Git sobre SSH** (`git@github.com:...`) usa o mesmo mecanismo; por isso configurar chave no GitHub é requisito para versionar código pericial.

## Referências

- RFC 4251–4256 (SSH protocol).
- [TODO/RESEARCH: NIST SP 800-185 sobre SHA-3; não diretamente SSH mas contexto crypto].
