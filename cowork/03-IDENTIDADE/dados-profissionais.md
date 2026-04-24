# Dados Profissionais — Fonte Única de Verdade

> ATENÇÃO: este arquivo é a ÚNICA fonte dos dados pessoais/profissionais que aparecem em petições, laudos, atestados, ofícios e e-mails. Os templates leem os placeholders `{{CAMPO}}` daqui e substituem automaticamente no momento de gerar cada peça. NÃO copie valores para outro lugar. Editar aqui = propagar em tudo.

> Preenchimento: substitua cada `{{CAMPO}}` pelo valor real. Se um campo não se aplica, deixar `N/A` (não apagar a linha, para o template saber que o campo foi considerado).

> Revisão recomendada: a cada 6 meses ou ao mudar endereço, conta bancária, CRM ou telefone.

---

## 1. Identificação civil

- Nome completo: Dr. Jésus Eduardo Nolêto da Penha
- Nome profissional (como assina): Dr. Jésus Eduardo Nolêto da Penha
- Nome curto no timbrado (header): Dr. Jésus E. Nolêto da Penha
- CPF: {{CPF}}  <!-- PENDENTE -->
- RG: {{RG_ORGAO_UF}}  <!-- PENDENTE -->
- Data de nascimento: {{DATA_NASCIMENTO}}  <!-- PENDENTE -->
- Nacionalidade: brasileiro
- Estado civil: {{ESTADO_CIVIL}}  <!-- PENDENTE -->

## 2. Registros profissionais

- CRM principal: CRM/MG 92.148
- CRM secundário (se houver): {{CRM_SECUNDARIO}}  <!-- N/A ou PENDENTE -->
- RQE (Registro de Qualificação de Especialista): {{RQE_NUMERO}}  <!-- PENDENTE — buscar no CRM-MG -->
- Especialidade registrada: {{ESPECIALIDADE}}  <!-- PENDENTE -->
- Área de atuação pericial: Medicina Legal e Perícia Médica
- OAB (se também advogado): N/A
- Outros registros: Membro da ABMLPM — Associação Brasileira de Medicina Legal e Perícia Médica

## 3. Qualificação para petições

Linha completa pronta para cabeçalho de petição (gerada a partir dos campos acima):

> {{NOME_PROFISSIONAL}}, médico, {{ESPECIALIDADE}}, inscrito no CRM/{{CRM_UF_NUMERO}}, RQE {{RQE_NUMERO}}, CPF {{CPF}}, com endereço profissional em {{ENDERECO_PERICIAL_COMPLETO}}, e-mail {{EMAIL_PERICIAL}}, telefone {{TELEFONE_PROFISSIONAL}}.

## 4. Endereço pericial (onde realiza perícias e recebe correspondência)

- Logradouro: Rua João Pinheiro
- Número: 531
- Complemento: Edifício Empresarial Maria Costa, Sala 207, 2º andar (última sala do corredor à esquerda)
- Bairro: Centro
- Cidade: Governador Valadares
- UF: MG
- CEP: {{CEP}}  <!-- PENDENTE -->
- Ponto de referência: prédio de esquina entre Rua Artur Bernardes (onde se encontra o ponto de ônibus) e Rua João Pinheiro; em frente ao muro lateral do Colégio Imaculada
- Endereço completo (linha única): Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 — Centro — Governador Valadares/MG

## 5. Endereço residencial (uso interno — NÃO sai em petição)

- Linha única: {{ENDERECO_RESIDENCIAL_COMPLETO}}  <!-- PENDENTE -->

## 6. Contatos

- E-mail pericial (oficial, sai em petição): perito@drjesus.com.br
- E-mail alternativo (intimações, se cadastrado): {{EMAIL_ALTERNATIVO}}  <!-- PENDENTE (ver reference_email_pericial.md: perito@drjesus.com.br NÃO recebe intimações) -->
- Telefone profissional (fixo/WhatsApp que entra em petição): (33) 99900-1122
- Telefone secretaria: {{TELEFONE_SECRETARIA}}  <!-- PENDENTE -->
- Site: {{SITE}}  <!-- PENDENTE -->
- LinkedIn: {{LINKEDIN}}  <!-- PENDENTE -->

> Confirmar: telefone (33) 99900-1122 é do footer do DOCX. Verificar se ainda ativo.

## 7. Dados bancários (honorários periciais)

- Banco (nome e número): {{BANCO_NOME_NUMERO}}
- Agência: {{AGENCIA}}
- Conta (tipo e número): {{CONTA_TIPO_NUMERO}}
- Titular: {{TITULAR_CONTA}}
- CPF/CNPJ do titular: {{CPF_CNPJ_TITULAR}}
- Chave PIX principal: {{PIX_PRINCIPAL}}
- Tipo da chave PIX: {{PIX_TIPO}}
- Chave PIX reserva: {{PIX_RESERVA}}

## 8. Dados fiscais (para RPV/precatório/NF)

- Pessoa física ou jurídica: {{PF_OU_PJ}}
- CNPJ (se PJ): {{CNPJ}}
- Razão social (se PJ): {{RAZAO_SOCIAL}}
- Inscrição municipal: {{INSCRICAO_MUNICIPAL}}
- Regime tributário: {{REGIME_TRIBUTARIO}}
- Emite NF de serviço: {{EMITE_NF_SIM_NAO}}

## 9. Nomeação pericial (jurisdições ativas)

- Justiça Estadual MG — comarcas: {{COMARCAS_ESTADUAIS}}
- Justiça Federal — seção/subseção: {{SECAO_FEDERAL}}
- JEF (Juizado Especial Federal): {{JEF}}
- Justiça do Trabalho (se houver): {{TRT}}
- Cadastro AJG/JF (assistência judiciária gratuita): {{AJG_STATUS}}
- Cadastro PJe Perito (estadual): {{PJE_ESTADUAL_STATUS}}
- Cadastro PJe Perito (federal): {{PJE_FEDERAL_STATUS}}

## 10. Assinatura e timbre

- Arquivo de assinatura digitalizada: `assinatura/{{ARQUIVO_ASSINATURA}}` <!-- PENDENTE -->
- **Timbrado oficial do topo da página (confirmado pelo usuário 2026-04-20):** `timbrado/timbrado-topo-pagina.png` (500×500, 8-bit gray+alpha) — vai no cabeçalho de toda petição/laudo no Word
- Timbrado variante/alternativa: `timbrado/timbrado-variante-alternativa.png` (500×500, RGBA) — origem desconhecida, preservar até validação
- Papel timbrado (DOCX): `_fonte-originais-perito/Agendamento de Perícia - MODELO - cópia.docx` (contém timbrado gráfico com logo)
- Papel timbrado (DOCX texto puro, header+footer): `_fonte-originais-perito/Petição de Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx` (timbrado só texto — nome, CRM, endereço, contato)
- Header textual (imediatamente acima): `Dr. Jésus E. Nolêto da Penha | Médico - Perito Judicial | CRM-MG 92.148 | Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica`
- Footer textual: `Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br`
- Certificado digital (ICP-Brasil) — titular/validade: {{CERTIFICADO_DIGITAL}} <!-- PENDENTE -->

### Fonte dos 3 originais preservados
- `cowork/02-BIBLIOTECA/peticoes/_fonte-originais-perito/Petição de Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx` (aceite condicionado com placeholder R$)
- `cowork/02-BIBLIOTECA/peticoes/_fonte-originais-perito/Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx` (aceite simples)
- `cowork/02-BIBLIOTECA/peticoes/_fonte-originais-perito/Agendamento de Perícia - MODELO - cópia.docx` (tem imagens de timbrado)

## 11. Fecho padrão de petição (padrão REAL extraído dos DOCX originais)

Formato exato atualmente usado (extraído de `Aceite - 0038122-07...Mantena.docx`):

> Termos em que,
> Pede deferimento.
>
> Dr. Jésus Eduardo Nolêto da Penha
> Médico - Perito Judicial – CRM-MG 92.148
> Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica
>
> {{DATA_POR_EXTENSO}}, Governador Valadares - MG.

Exemplo real: `17 de março de 2026, Governador Valadares - MG.`

---

## Checklist de integridade

- [ ] Todos os `{{CAMPO}}` substituídos ou marcados N/A.
- [ ] CRM confere com consulta ao site do CFM.
- [ ] PIX testado com transferência de R$ 0,01 nos últimos 6 meses.
- [ ] E-mail pericial recebe intimações de teste.
- [ ] Assinatura digitalizada em PNG com fundo transparente.
- [ ] Papel timbrado localizado e copiado para `timbrado/`.
