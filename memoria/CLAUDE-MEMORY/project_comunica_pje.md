---
name: Cadastro Intimações Eletrônicas (PJe + DJE + DJEN)
description: 3 cadastros pendentes para receber intimações: PJe TJMG (perito), Domicílio Judicial Eletrônico, e monitoramento DJEN
type: project
originSessionId: 84649f96-0bbb-4ebc-a11e-25b3dd508789
---
Perito NÃO recebe intimação como advogado. Precisa de 3 cadastros separados:

## 1. PJe TJMG (perfil Perito) — VERIFICAR
- Peritos do Sistema AJ são cadastrados pela COAPE automaticamente
- Se não tiver → abrir chamado Portal de Serviços TI TJMG
- **Requer certificado digital A3 ICP-Brasil**
- Aviso CGJ 37/2019 + Aviso CGJ 73/2021
- Suporte: 0800-3535-600
- URL: https://pje.tjmg.jus.br

## 2. Domicílio Judicial Eletrônico — CADASTRADO (16/abr/2026)
- Centraliza citações e intimações pessoais de TODOS os tribunais
- Resolução CNJ 455/2022 + 569/2024
- URL: https://domicilio-eletronico.pdpj.jus.br (autenticação gov.br)
- Prazo ciência: 3 dias úteis (PJ) / 10 dias corridos (intimação)
- Ciência tácita se não abrir no prazo
- Email cadastrado: perito@drjesus.com.br
- Notificação: resumo diário das comunicações processuais
- Termo de Adesão: 16/04/2026

## 3. DJEN (consulta) — JÁ FUNCIONA
- URL: https://comunica.pje.jus.br
- Acesso livre para consulta
- Script `descobrir_processos.py` já monitora

## API para automação
- MNI Client: headers X-MNI-CPF + X-MNI-SENHA (CPF e senha PJe)
- Swagger: https://mni-client.prd.cnj.cloud/swagger-ui/index.html
- Comunica API: https://comunicaapi.pje.jus.br/api/v1 (acesso institucional)

**Why:** Sem esses cadastros, nomeações passam despercebidas. Com os 3 ativos + scripts de monitoramento, cobertura fica quase total.

**How to apply:** Guia completo em ~/Desktop/STEMMIA Dexter/docs/comunica-pje/GUIA-COMPLETO-CADASTRO-INTIMACOES.md

**Arquivos:**
- Guia: ~/Desktop/STEMMIA Dexter/docs/comunica-pje/GUIA-COMPLETO-CADASTRO-INTIMACOES.md
- URLs: ~/Desktop/STEMMIA Dexter/docs/comunica-pje/URLS-E-ACESSOS.md
- Script: ~/Desktop/ANALISADOR FINAL/scripts/monitor-publicacoes/comunica_pje.py
- Chamador: ~/Desktop/ANALISADOR FINAL/scripts/descobrir_processos.py
