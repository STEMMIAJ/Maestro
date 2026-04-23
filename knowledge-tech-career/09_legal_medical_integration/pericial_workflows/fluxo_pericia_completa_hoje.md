---
titulo: Fluxo de perícia completa — estado atual
bloco: 09_legal_medical_integration
tipo: fluxo
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: inventario-local
tempo_leitura_min: 7
---

# Fluxo de perícia completa — estado atual

Fluxo real do Dr. Jesus, nomeação → entrega. Cada etapa tem ferramenta atual, gargalo conhecido e próxima ação. Útil como mapa para otimização.

## 1. Nomeação

- **O que acontece**: juiz nomeia perito; intimação via DJEN ou email do tribunal.
- **Ferramenta atual**: Monitor de movimentações (DJEN + Comunica PJe + hub.py) roda 3x/dia via launchd. Alerta por Telegram (@stemmiapericia_bot).
- **Gargalo atual**: cadastro no Comunica PJe ainda **pendente** (ver `project_comunica_pje.md` da memória). Email `perito@drjesus.com.br` NÃO recebe intimações.
- **Próxima ação**: concluir cadastro Comunica PJe para centralizar.

## 2. Triagem (aceitar / recusar)

- **O que acontece**: avaliar competência técnica, honorários, prazo, interesse; impugnar se necessário.
- **Ferramenta atual**: agente `triador-peticao` + template de prompt #3 (`prompt_para_pericia.md`).
- **Gargalo**: triagem ainda feita manualmente em muitos casos; dados do Datajud nem sempre completos.
- **Próxima ação**: auto-triagem com Opus + agente `orq-analise-rapida` em minutos.

## 3. Download das peças

- **O que acontece**: baixar autos digitais do PJe (PDF ou peças individuais).
- **Ferramenta atual**: script Selenium + Chrome debug porta 9223 + perfil isolado em `~/Desktop/STEMMIA Dexter/PJE-INFRA/`. Funciona desde 13/abr/2026. Detalhes em `project_download_pje_139.md`.
- **Gargalo**: PJe só roda no **Windows/Parallels** (ver `feedback_pje_windows.md`). Mac Chrome não funciona. Certificado ICP-Brasil exige Windows.
- **Próxima ação**: manter o que funciona; ocasionalmente falha por atualização do PJe → verificar logs em `project_pje_erros_log.md`.

## 4. Pré-processamento (OCR, estruturação, indexação)

- **O que acontece**: PDFs → texto com OCR (se imagem); quebra em peças; atribui `doc_id`; extrai metadata processual.
- **Ferramenta atual**: scripts Python em `~/Desktop/STEMMIA Dexter/src/automacoes/`. Usa Tesseract + pdfplumber. Estrutura em `dados/processos/{cnj}/`.
- **Gargalo**: OCR lento em processos de 1000+ páginas. Qualidade varia com scan do cartório.
- **Próxima ação**: avaliar Google Document AI ou Apple Vision (nativo macOS) para OCR rápido + custo zero.

## 5. Análise documental automatizada

- **O que acontece**: extrai quesitos, partes, cronologia, CIDs, exames citados, contradições.
- **Ferramenta atual**: orquestradores `orq-analise-completa`, `orq-analise-documento`. Agentes especializados em paralelo: `extrator-partes`, `extrator-informacoes-doc`, `analisador-quesitos-auto`, `resumidor-fatos`, `detetive-inconsistencias`, `mapeador-provas`.
- **Saída**: `ficha.json` preenchida (ver `pericia_judicial_and_data/dados_de_pericia_judicial.md`).
- **Gargalo**: CID detectado nem sempre validado contra tabela oficial; contradições às vezes falso-positivas.
- **Próxima ação**: ligar `verificador-cids` ao fim do pipeline; calibrar `detetive-inconsistencias`.

## 6. Exame presencial

- **O que acontece**: agendamento, entrevista, exame físico, fotos/medidas.
- **Ferramenta atual**: roteiro gerado por `gerador-roteiro-pericial` a partir da ficha.json + quesitos. Dr. Jesus conduz exame, preenche formulário em iPad/Mac.
- **Gargalo**: transcrição do áudio do exame. Uso atual: Whisper ou ditado macOS.
- **Próxima ação**: padronizar captura via app; transcrição automática direta em campo da ficha.json.

## 7. Pesquisa de suporte

- **O que acontece**: busca literatura médica, normas CFM, jurisprudência, tabelas AACD/CNSP.
- **Ferramenta atual**: MCP PubMed + `buscador-academico` + `orq-jurisprudencia` + MCP-Brasil (326 tools jurídicas). Sempre paralelo.
- **Gargalo**: acesso a texto completo de papers pagos; jurisprudência em PT com jargão exige bom rerank.
- **Próxima ação**: cadastrar Oasis Brasil; testar `voyage-law-2` para rerank jurídico.

## 8. Redação do laudo

- **O que acontece**: monta laudo a partir de template + ficha.json + achados + discussão.
- **Ferramenta atual**: `redator-laudo` + `revisor-laudo`. Templates em `~/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/` + script `usar_template_pericia.py` que substitui placeholders (ver `project_pericias_reaproveitaveis.md`).
- **Gargalo**: discussão técnica (o "miolo") ainda exige muita intervenção manual. Redator bom em estrutura, fraco em nuance clínica.
- **Próxima ação**: few-shot com laudos anteriores do próprio Dr. Jesus como exemplo de estilo.

## 9. Verificação anti-mentira

- **O que acontece**: checa cada claim do laudo contra fonte; detecta data, CID, medicamento, nome, número errados.
- **Ferramenta atual**: `verificador-100`, `verificador-cids`, `verificador-datas`, `verificador-de-fontes`, `verificador-exames`, `verificador-medicamentos`, `verificador-nomes-numeros`, `verificador-cruzado`. Hooks anti-mentira interceptam claims de "feito/pronto" sem verificação.
- **Gargalo**: custos cumulativos (vários verificadores em Opus). Alguns falsos positivos.
- **Próxima ação**: sequenciar verificadores só até um falhar (short-circuit).

## 10. Geração do PDF assinado

- **O que acontece**: markdown → PDF com layout oficial; assinatura digital ICP-Brasil.
- **Ferramenta atual**: Pandoc ou WeasyPrint para render; assinador CNJ em `~/.pjeoffice-pro/` (NÃO MOVER — path hardcoded). Ver `document_automation/geracao_de_laudo_com_template.md`.
- **Gargalo**: assinador só roda confiável no Windows; Mac tem instabilidade.
- **Próxima ação**: manter Windows/Parallels; documentar passo em `.command` disparável do Mac.

## 11. Entrega

- **O que acontece**: protocolar no PJe; guardar cópia em pasta do processo; atualizar Planner; subir para site.
- **Ferramenta atual**: upload manual no PJe (Windows). FTP deploy automatiza site (ver `reference_ftp_deploy.md`).
- **Gargalo**: upload PJe não tem automação confiável (CAPTCHA, certificado).
- **Próxima ação**: manter manual; automatizar só os passos periféricos (cópia, planner, FTP).

## 12. Pós-entrega

- **O que acontece**: atualizar diário, registrar aprendizado, arquivar, aguardar possíveis impugnações.
- **Ferramenta atual**: `resumo-sessao`, `handoff-sessao`, `~/Desktop/DIARIO-PROJETOS.md`, `MAPEAMENTO-HABILIDADES.md`.
- **Gargalo**: registro de aprendizado é manual e irregular.
- **Próxima ação**: auto-destilação via `detectar_habilidade_nova.py` já roda no Stop hook (19/abr/2026).

## Resumo dos gargalos prioritários

1. Cadastro Comunica PJe (fonte única de intimação).
2. Transcrição pós-exame presencial.
3. Discussão técnica do laudo ainda muito manual.
4. Upload final no PJe sem automação.

## Referências

- `~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md`
- `~/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html`
- `~/Desktop/DIARIO-PROJETOS.md`
