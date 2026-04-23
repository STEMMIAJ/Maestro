---
titulo: "Redes — básico"
bloco: "01_ti_foundations/hardware_networks_os"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 7
---

# Redes — básico

## Pilha em camadas (simplificada)

```
[ Aplicação ]   HTTP, SMTP, SSH, DNS       ← o que você fala
[ Transporte ]  TCP, UDP                   ← como entrega
[ Rede ]        IP                         ← como endereça
[ Enlace ]      Ethernet, Wi-Fi            ← como transmite
```

Modelo didático é OSI (7 camadas); modelo real é TCP/IP (4 camadas). Para prática, as 4 acima bastam.

## IP (Internet Protocol)

Endereço numérico único de cada dispositivo em rede. Duas versões:

- **IPv4** — 4 octetos, ex.: `192.168.1.10`. 2³² endereços (~4 bilhões). Esgotado globalmente desde 2011.
- **IPv6** — 128 bits, ex.: `2001:db8::1`. Praticamente infinito. Em adoção gradual.

Tipos:
- **Público** — roteável na internet. Dado pelo provedor (Claro, Vivo, Oi).
- **Privado** — só na rede local. Faixas `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. Seu roteador atribui por DHCP.

## DNS (Domain Name System)

Sistema que traduz nome legível em IP. Você digita `stemmia.com.br`; DNS resolve para `203.0.113.42`.

Hierarquia: root → TLD (`.br`) → `stemmia.com.br` → servidor autoritativo.

Cache DNS local (no Mac: `sudo dscacheutil -flushcache`) evita consulta repetida. TTL define tempo de validade.

Exemplo: mudar IP do servidor de `stemmia.com.br` no provedor — usuários no mundo só enxergam a mudança após TTL expirar (horas).

## TCP (Transmission Control Protocol)

Protocolo de transporte confiável. Garante ordem, entrega e integridade via acknowledgments e retransmissão.

Uso: HTTP, HTTPS, SSH, SMTP — tudo em que perder byte é inaceitável. Laudo em PDF baixado do PJe vem por TCP.

Abertura: *three-way handshake* (`SYN` → `SYN-ACK` → `ACK`). Caro em latência, por isso HTTP/2 e HTTP/3 reduzem custo reutilizando conexão.

## UDP (User Datagram Protocol)

Protocolo sem conexão, sem garantia. "Atira e esquece". Mais rápido, mais leve.

Uso: DNS, streaming de vídeo (perder frame é ok), VoIP, jogos online, QUIC/HTTP3 (TCP-like sobre UDP).

## Porta

Número de 0 a 65.535 que identifica aplicação dentro de um host. IP endereça a máquina; porta endereça o serviço na máquina.

Bem-conhecidas (0–1023):
- 22 — SSH
- 25 — SMTP (email envio)
- 53 — DNS
- 80 — HTTP
- 443 — HTTPS
- 3306 — MySQL
- 5432 — PostgreSQL

Efêmeras (32768–60999 no macOS) — atribuídas ao cliente dinamicamente.

## HTTP e HTTPS

HTTP = protocolo de aplicação usado pela web. Texto claro (legível na rede).
HTTPS = HTTP sobre TLS. Criptografado, autenticado, íntegro.

Se você acessa `stemmia.com.br` sem HTTPS, qualquer intermediário (Wi-Fi de café, provedor) lê e modifica o tráfego. Com HTTPS, só cliente e servidor leem.

## Certificado TLS

Documento digital assinado por **Autoridade Certificadora (CA)** confiável (Let's Encrypt, DigiCert, ICP-Brasil) que prova: "a chave pública abaixo pertence ao domínio `stemmia.com.br`".

Ao acessar HTTPS, o navegador:
1. Recebe o certificado do servidor.
2. Valida a cadeia até uma CA raiz confiável (pré-instalada no SO).
3. Confere validade, domínio, revogação.
4. Usa a chave pública para negociar chave simétrica de sessão.

Cadeado na barra = passou. Aviso vermelho = falhou (expirado, domínio errado, auto-assinado).

## Por que importa para o perito

- **Juntar URL como prova**: perícia em conteúdo online deve capturar IP resolvido, hash da página e certificado TLS — fixar identidade do servidor no momento.
- **Email pericial** (`perito@drjesus.com.br`): registros MX (DNS) apontam servidor; SPF/DKIM/DMARC autenticam remetente. Perícia em email forjado analisa cabeçalhos.
- **Porta 9223 do Chrome debug**: automação PJe usa CDP nessa porta local; abrir ao público compromete segurança.
- **Assinatura digital de laudo** (PAdES) usa mesma infraestrutura PKI do TLS — certificados ICP-Brasil são emitidos por CAs.

## Referências

- RFC 791 (IP), RFC 793 (TCP), RFC 768 (UDP), RFC 1035 (DNS), RFC 9110 (HTTP Semantics), RFC 8446 (TLS 1.3).
