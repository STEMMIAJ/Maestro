# Rotina Manual — PJe TJMG Painel

**Frequência:** 2× por semana (segunda e quinta), 2 min cada.

**Por que manual:** PJe TJMG exige certificado A3 VidaaS que só funciona no
Windows. Não dá para automatizar sem presença humana.

## Passo a passo

1. Abrir Parallels Desktop → Windows 11
2. No Windows, duplo-click no atalho:
   ```
   \\Mac\Home\Desktop\Projetos - Plan Mode\processos-pje\abrir_pje_debug.bat
   ```
3. Login VidaaS com certificado A3
4. No Painel do Advogado/Perito, verificar aba **"Pendentes de análise"**
5. Se houver novos processos:
   - No CMD (Windows):
     ```
     pushd "\\Mac\Home\stemmia-forense\src\pje"
     py baixar_push_pje.py --download-dir "%USERPROFILE%\Desktop\processos-pje"
     ```
6. Fechar Chrome ao terminar

## Lembrete automático

O sistema envia lembrete no Telegram toda **segunda e quinta às 8h** (se o cron
do MONITOR-FONTES rodou e detectou dia da semana).

## Troubleshooting

- Certificado expirado → renovar no VidaaS (até 3 anos)
- Chrome trava → fechar Parallels, reabrir
- PDF não baixa → aumentar `TIMEOUT_PROCESSO` em `baixar_push_pje.py`
