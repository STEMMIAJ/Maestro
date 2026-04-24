---
name: FTP Deploy Stemmia
description: Credenciais FTP para deploy de sites — servidor nuvemIDC
type: reference
---

**Host FTP:** alvorada.nuvemidc.com (IP: 177.73.233.49)
**Usuário:** deploy@stemmia.com.br
**Senha:** @$xHQ[c*B&mqUj]R
**Caminho real (FTP root = webdev/):** /teste/ para sites de teste
**Caminho antigo (NÃO funciona):** /home/stemmiac/public_html/webdev/ — cria diretórios fantasma que o WordPress intercepta
**IMPORTANTE:** usar IPv4 obrigatoriamente (IPv6 passivo timeout). curl: usar `-4 --ftp-pasv`. Python ftplib: funciona direto.
**Script de deploy:** `~/Desktop/ANALISADOR FINAL/scripts/deploy_site.py` — upload FTP + notificação Telegram
**Atualizado em:** 06/abr/2026
**cPanel:** alvorada.nuvemidc.com
