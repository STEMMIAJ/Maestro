---
name: Sempre sincronizar e subir pro site
description: Quando gerar PDF ou HTML para a Mesa, SEMPRE subir via FTP para stemmia.com.br e atualizar o Planner
type: feedback
---

Quando gerar qualquer artefato (PDF, HTML, dashboard) que o usuário possa querer acessar remotamente, SEMPRE fazer upload FTP para stemmia.com.br/webdev/ e atualizar o planner.html.

**Why:** O usuário ficou irritado porque gerou o GUIA-COMPLETO-STEMMIA.pdf mas não foi sincronizado com o site. Ele espera que a entrega inclua o upload. Omitir isso prejudica ele — ele esquece e depois não encontra.

**How to apply:** Após qualquer geração de PDF/HTML para a Mesa:
1. Subir via FTP (ver reference_ftp_deploy.md para credenciais)
2. Atualizar planner.html se relevante
3. Confirmar: "Subido para stemmia.com.br/webdev/[arquivo]"
