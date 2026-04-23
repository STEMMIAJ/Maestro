---
titulo: "Localhost e LAN"
bloco: "01_ti_foundations/hardware_networks_os"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 5
---

# Localhost e LAN

## Localhost (127.0.0.1)

Endereço IP especial que significa "esta mesma máquina". O tráfego não sai da placa de rede; fica dentro do SO (interface `lo` / *loopback*). Também vale o nome `localhost` — resolve sempre para `127.0.0.1` (IPv4) ou `::1` (IPv6).

Uso típico:
- Rodar servidor local durante desenvolvimento: `python -m http.server 8000` → abrir `http://localhost:8000`.
- Banco de dados local: PostgreSQL em `127.0.0.1:5432`.
- Chrome debug para automação PJe: `http://127.0.0.1:9223`.

Segurança: serviço em `127.0.0.1` não é acessível de fora. Se precisar expor, o binding tem que ser `0.0.0.0` (todas as interfaces) — decisão consciente, porque abre porta na LAN.

## LAN (Local Area Network)

Rede local — casa, escritório, vara judicial. Dispositivos conectados ao mesmo roteador/switch enxergam uns aos outros por IP privado.

Faixa típica residencial: `192.168.0.0/24` ou `192.168.1.0/24`. Seu Mac pode ser `192.168.1.23`, impressora `192.168.1.44`, roteador (gateway) `192.168.1.1`.

Descobrir IP local no Mac: `ipconfig getifaddr en0` (Wi-Fi) ou `ifconfig`.

## NAT (Network Address Translation)

Técnica que permite vários dispositivos da LAN compartilharem um único IP público. O roteador reescreve endereços na saída e remonta na volta, mantendo tabela de tradução.

Consequência: dispositivos atrás de NAT **não recebem conexão de fora** por padrão. Só saem para fora e recebem resposta. Para hospedar serviço visível na internet, precisa:
1. IP público + abrir porta no roteador (*port forwarding*), ou
2. Túnel reverso (ngrok, Cloudflare Tunnel, Tailscale), ou
3. VPS na nuvem com IP público próprio.

Por isso N8N pericial fica num VPS (`srv19105`) e não no seu Mac — o Mac está atrás de NAT do provedor.

## CGNAT

*Carrier-Grade NAT*. Provedor (Vivo fibra, Claro 4G) faz NAT duplo — vários clientes compartilham o mesmo IP público. Pior cenário para hospedar serviço em casa.

Teste: IP mostrado no roteador vs IP real em `https://api.ipify.org`. Se forem diferentes, há CGNAT.

## Portas relevantes em LAN/localhost

- **22 (SSH)** — acesso remoto seguro. Em LAN: `ssh jesus@192.168.1.23`. Da internet: exige port forward ou VPN.
- **80 (HTTP)** — servidor web sem TLS. Uso local apenas; jamais exposto à internet em produção.
- **443 (HTTPS)** — servidor web com TLS. Padrão público.
- **3000, 5173, 8000, 8080** — portas *ad hoc* comuns para dev local (React, Vite, Python, Node).

## Por que importa para o perito

- **Claude MCP servers** rodam em localhost (ex.: `http://127.0.0.1:3001`). Se a porta for exposta por engano (`0.0.0.0`), outro dispositivo da rede acessa suas ferramentas periciais.
- **Parallels** vê o Mac via rede bridge ou host-only; entender LAN evita frustração com "Windows não acessa localhost do Mac" (usar `host.docker.internal`-like em Parallels: `10.211.55.2` tipicamente).
- **Análise forense de log de rede** depende de distinguir IP público vs privado: `192.168.x.x` na evidência = atacante estava na LAN, não na internet aberta.

## Referências

- RFC 1918 (endereços privados).
- RFC 6598 (CGNAT).
