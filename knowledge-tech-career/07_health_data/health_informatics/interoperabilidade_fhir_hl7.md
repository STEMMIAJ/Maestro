---
titulo: "Interoperabilidade em saúde — HL7 v2, FHIR, RNDS"
bloco: "07_health_data/health_informatics"
tipo: "fundamento"
nivel: "intermediario"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# Interoperabilidade — HL7 v2, FHIR, RNDS

Interoperar = sistemas trocam dado **com significado preservado**. Três níveis: sintático (mesmo formato), semântico (mesmo vocabulário), organizacional (mesmos fluxos).

## HL7 v2.x (legado, ainda onipresente)

- Mensageria textual, delimitada por pipe `|` e `^`.
- Mensagens: ADT (admissão/alta/transferência), ORM (pedido de exame), ORU (resultado), SIU (agendamento).
- Transporte: MLLP (TCP com frames delimitados) ou arquivo.

Exemplo ADT^A01 (admissão):

```
MSH|^~\&|HIS|HOSP|LAB|LAB|20260423123000||ADT^A01|MSG00001|P|2.5
PID|1||1234567^^^HOSP^MR||SILVA^JOSE||19800115|M|||RUA X^^BH^MG^30130-000
PV1|1|I|UTI^101^1|...
```

- Pontos fortes: simples, leve, suporte universal em HIS.
- Pontos fracos: sem modelo semântico formal, ambíguo, customizações locais "quebram" integrações.

## HL7 CDA (R2)

- Documento clínico em XML com estrutura narrativa + dados estruturados.
- Base do Continuity of Care Document (CCD).
- Usado como portador de sumário clínico antes do FHIR.

## FHIR (HL7 Fast Healthcare Interoperability Resources)

- Padrão moderno (desde ~2012), versão estável **R4** (2019); **R5** publicada em 2023.
- Baseado em **recursos** (Resources) serializados em JSON ou XML.
- API REST: `GET /Patient/123`, `POST /Observation`, `PUT /MedicationRequest/456`.
- Profiles: restrições locais em cima do recurso genérico (ex.: perfil BR-Paciente da RNDS).
- Extensions: campos adicionais sem quebrar modelo-base.

### Recursos-chave

| Recurso | Uso |
|---|---|
| **Patient** | Demografia do paciente |
| **Practitioner / PractitionerRole** | Profissional e vínculo |
| **Organization** | Estabelecimento |
| **Encounter** | Atendimento (consulta, internação) |
| **Condition** | Diagnóstico, problema |
| **Observation** | Sinal vital, laboratório, medida |
| **MedicationRequest / MedicationStatement** | Prescrição, uso |
| **Procedure** | Procedimento realizado |
| **DiagnosticReport** | Laudo (laboratório, imagem) |
| **Immunization** | Vacina |
| **AllergyIntolerance** | Alergia |
| **Composition / Bundle** | Agrupar recursos em documento/mensagem |

Exemplo Observation (glicemia):

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{"system":"http://loinc.org", "code":"2339-0", "display":"Glucose"}]
  },
  "subject": {"reference":"Patient/123"},
  "effectiveDateTime": "2026-04-23T08:30:00-03:00",
  "valueQuantity": {"value": 98, "unit":"mg/dL", "system":"http://unitsofmeasure.org", "code":"mg/dL"}
}
```

### Operações e buscas

- `GET /Patient?name=silva&birthdate=1980-01-15`
- `GET /Observation?patient=123&code=loinc|2339-0&date=ge2026-01-01`
- `$everything`, `$validate`, `$expand` (ValueSet).
- Paginação via `_count` + `link`.

### Terminologias embutidas

- **CodeSystem**: define códigos (LOINC, SNOMED, CID).
- **ValueSet**: subconjuntos reutilizáveis.
- **ConceptMap**: mapeamentos entre sistemas.

## HL7 v2 vs FHIR — resumo

| | HL7 v2 | FHIR |
|---|---|---|
| Formato | Delimitado pipe | JSON/XML |
| Transporte | MLLP/TCP, arquivo | REST/HTTPS |
| Modelo | Mensagem | Recurso + documento + mensagem |
| Busca | Limitada | Search nativo, expressivo |
| Curva | Alta (ambígua) | Menor para devs web |
| Adoção BR | Alta em HIS legados | RNDS, novos sistemas |

## RNDS no Brasil

- Plataforma nacional baseada em **FHIR R4** com perfis brasileiros.
- Portaria GM/MS 1.434/2020 institui.
- Conectividade: APIs autenticadas por certificado digital ICP-Brasil + OAuth2.
- Perfis (IG — Implementation Guide): Paciente BR, Profissional BR, Estabelecimento BR, Imunização BR, Laboratório BR, Prescrição BR, Encaminhamento BR.
- Fluxo: sistema local → encaminha recurso → RNDS recebe, valida perfil, armazena.
- Utilidade pericial: possível obter histórico longitudinal do paciente quando integrado.

## Como começar a trabalhar com FHIR

- **Servidor de teste público**: https://hapi.fhir.org/baseR4.
- **SDK Python**: `fhir.resources`, `fhirpy`.
- **SDK JS**: `fhir.js`, `fhirclient`.
- **R**: `fhircrackr`.
- **Simplifier / Firely Terminal**: validar perfis.

## Armadilhas

1. Mapear código local para LOINC/SNOMED manualmente é trabalhoso — existem serviços de terminologia (tx.fhir.org).
2. Timezones: FHIR exige ISO 8601 com offset; data sem hora perde informação.
3. FHIR permite extensões livres, então "compatível FHIR" nem sempre é plug-and-play — exigir perfil declarado.
4. RNDS tem rate limit e janela de retenção — documentar no fluxo.
