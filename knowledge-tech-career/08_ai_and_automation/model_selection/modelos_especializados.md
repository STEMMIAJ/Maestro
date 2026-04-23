---
titulo: Claude vs GPT vs Gemini vs open-source
bloco: 08_ai_and_automation
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 5
---

# Claude vs GPT vs Gemini vs open-source

## Provedores principais (abr/2026) [TODO/RESEARCH: confirmar lineup]

### Anthropic — Claude (Opus 4, Sonnet 4, Haiku 4)

**Fortes em**:
- Raciocínio longo, análise de documento extenso.
- Instruções complexas e multi-passo.
- Redação em PT de qualidade.
- Constitutional AI → menos alucinação confiante.
- Prompt caching barato.
- Claude Code (CLI oficial).

**Fracos em**:
- Multimodal: imagem OK, áudio/vídeo limitado.
- Janela 200k — menor que Gemini/GPT.
- Disponibilidade em enterprise com filtros rígidos pode bloquear temas médicos.

**Uso no Dexter**: padrão absoluto. Opus para tudo que vale ao cartório.

### OpenAI — GPT-4.1, o3, GPT-4o

**Fortes em**:
- Ecosistema (Assistants API, function calling maduro, Realtime API para voz).
- Multimodal (imagem, áudio bidirecional).
- Mais integrações nativas em SaaS.
- o3: raciocínio "thinking" dedicado.
- Janela 1M em GPT-4.1.

**Fracos em**:
- Alucinação confiante histórica.
- Preço o3 muito alto.
- Políticas de conteúdo mais restritivas em contexto médico sensível.

**Quando usar em perícia**: dictado de voz em tempo real (Whisper + GPT-4o realtime), análise de raio-X/RM (embora imagem médica exija cuidado).

### Google — Gemini 2.5 Pro, Flash

**Fortes em**:
- Janela de contexto enorme (1M–2M tokens) — processo inteiro com anexos cabe.
- Integração Google Workspace.
- Preço competitivo.
- Multimodal incluindo vídeo.

**Fracos em**:
- Qualidade de raciocínio abaixo do Opus/o3 em benchmarks exigentes.
- PT às vezes mais engessado.
- Comportamento de tool use menos previsível.

**Quando usar em perícia**: primeira leitura de processo gigante (1M+ tokens) para sumário bruto; depois Opus refina.

### Open-source — Llama, Qwen, Mistral, DeepSeek

**Fortes em**:
- **Zero custo por token** (apenas custo de hardware).
- **Privacidade total**: roda no próprio Mac, dado nunca sai.
- Fine-tuning viável.
- Sem política de conteúdo arbitrária.

**Fracos em**:
- Qualidade abaixo dos top comerciais em raciocínio complexo.
- Hardware: 70B exige 48GB+ VRAM (ou quantização Q4/Q5 num Mac com 64GB unified memory).
- Operação: você é o SRE — atualizações, monitoramento, patch.

**Modelos relevantes**:

- **Llama 3.1 70B / 405B** (Meta): generalista forte.
- **Qwen 2.5 72B** (Alibaba): excelente em PT, código, raciocínio estruturado.
- **Mistral Large 2** / **Mixtral 8x22B**: bom custo-benefício.
- **DeepSeek-R1**: raciocínio tipo o3, open-weight. [TODO/RESEARCH: disponibilidade abr/2026]
- **Qwen-2.5-Coder** / **CodeLlama**: específicos para código.

**Runtime local**:
- **Ollama** (mais simples, Mac M-series rápido).
- **vLLM** (servidor de produção, exige GPU).
- **LM Studio** (GUI).

## Quando vale rodar local

- Volume alto e previsível (> USD 200/mês em API). ROI de hardware em 6–12 meses.
- Dado que não pode sair do controle (prontuário, laudo em andamento, dado de menor, segredo de justiça).
- Experimentação intensiva (fine-tuning, LoRA).
- Latência crítica sem depender de rede.

## Quando NÃO vale rodar local

- Uso esporádico.
- Tarefas que exigem raciocínio de ponta (Opus 4 vence Llama 405B em tarefas médico-legais complexas).
- Equipe sem tempo para operar.

## Recomendação para Dr. Jesus

- **Padrão**: Claude Opus 4 via Claude Code (já é o setup).
- **Escala/batch noturno**: Claude Sonnet 4 com `opus-auditor` na saída crítica.
- **Privacidade total** (ex.: OCR de documento de paciente identificado antes de anonimizar): Qwen 2.5 72B local via Ollama.
- **Processo gigante (> 500k tokens)**: Gemini 2.5 Pro para sumário bruto; Opus refina.

## Referências

- Artificial Analysis leaderboard. [TODO/RESEARCH: URL]
- LMSys Chatbot Arena. [TODO/RESEARCH]
- Anthropic docs, OpenAI docs, Google AI docs.
