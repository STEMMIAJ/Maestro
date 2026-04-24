#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atualizar_modelos_n8n.py — Atualiza modelos Gemini nos workflows N8N com fallback automático.

Substitui nós HTTP simples por nós Code com lógica de fallback:
  1º gemini-2.5-flash (10 RPM, 250 RPD)
  2º gemini-2.5-flash-lite (15 RPM, 1000 RPD)
  3º gemini-2.5-pro (5 RPM, 100 RPD)

Quando um modelo retorna 429 (quota excedida), tenta o próximo automaticamente.
Notifica no Telegram qual modelo foi usado.

Uso:
    python3 atualizar_modelos_n8n.py                    # atualiza JSONs locais
    python3 atualizar_modelos_n8n.py --deploy            # atualiza + reimporta no N8N
    python3 atualizar_modelos_n8n.py --deploy --ativar   # atualiza + reimporta + ativa

Autor: Sistema Stemmia
"""

import json
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

GEMINI_KEY = "AIzaSyA9Gh9JYW4VEiKVlmCR0ziUD3umK9pJYWQ"

# Hierarquia de modelos gratuitos (melhor custo-benefício primeiro)
MODELO_HIERARQUIA = [
    "gemini-2.5-flash",       # 10 RPM, 250 RPD — melhor equilíbrio
    "gemini-2.5-flash-lite",  # 15 RPM, 1000 RPD — mais rápido, maior quota
    "gemini-2.5-pro",         # 5 RPM, 100 RPD — melhor qualidade, menor quota
]

N8N_URL = "https://n8n.srv19105.nvhm.cloud"
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxZjliN2ZiNC0zNDVlLTRjODktODExZi0wZjI0ODMwZjRhNDQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNTA3OTQxfQ.N4zwLEuubVJXuvfIT7zgqJ80ejs5tPTmg28EyxCJnHI"
TELEGRAM_TOKEN = "8603024374:AAH81RHxIBwOsTaDI87nM7ap2DHcuE3xnxA"
TELEGRAM_CHAT = "8397602236"

WF_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "n8n-workflows"
WF_COPY = Path.home() / "Desktop" / "N8N Workflows Stemmia"

# ═══════════════════════════════════════════════════════════════════════════════
# CÓDIGO JS DO NÓ COM FALLBACK (injetado nos workflows)
# ═══════════════════════════════════════════════════════════════════════════════

FALLBACK_JS_TEMPLATE = """
// === GEMINI FALLBACK AUTOMÁTICO ===
// Tenta modelos em ordem até um funcionar
// Se todos falharem, lança erro com detalhes

const GEMINI_KEY = '{gemini_key}';
const MODELOS = {modelos_json};
const TELEGRAM_TOKEN = '{telegram_token}';
const TELEGRAM_CHAT = '{telegram_chat}';

const promptCompleto = {prompt_source};
const temperature = {temperature};
const maxTokens = {max_tokens};

async function chamarGemini(modelo, prompt, temp, tokens) {{
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${{modelo}}:generateContent?key=${{GEMINI_KEY}}`;
  const body = JSON.stringify({{
    contents: [{{parts: [{{text: prompt}}]}}],
    generationConfig: {{temperature: temp, maxOutputTokens: tokens}}
  }});

  const resp = await fetch(url, {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: body,
    signal: AbortSignal.timeout(120000)
  }});

  const data = await resp.json();

  if (data.error) {{
    const code = data.error.code || resp.status;
    throw new Error(`${{code}}: ${{data.error.message}}`);
  }}

  if (!data.candidates || data.candidates.length === 0) {{
    throw new Error('Resposta vazia');
  }}

  if (data.candidates[0].finishReason === 'SAFETY') {{
    throw new Error('Bloqueado por filtro de segurança');
  }}

  return data;
}}

async function notificarTelegram(msg) {{
  try {{
    await fetch(`https://api.telegram.org/bot${{TELEGRAM_TOKEN}}/sendMessage`, {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{chat_id: TELEGRAM_CHAT, text: msg}})
    }});
  }} catch(e) {{}}
}}

let resultado = null;
let modeloUsado = '';
const erros = [];

for (const modelo of MODELOS) {{
  try {{
    resultado = await chamarGemini(modelo, promptCompleto, temperature, maxTokens);
    modeloUsado = modelo;
    break;
  }} catch (e) {{
    erros.push(`${{modelo}}: ${{e.message}}`);
    if (e.message.includes('429') || e.message.includes('RESOURCE_EXHAUSTED') || e.message.includes('quota')) {{
      await notificarTelegram(`⚠️ Gemini ${{modelo}} sem quota. Tentando próximo...`);
      continue;
    }}
    // Erro não relacionado a quota — tentar próximo mesmo assim
    continue;
  }}
}}

if (!resultado) {{
  await notificarTelegram(`❌ TODOS os modelos Gemini falharam:\\n${{erros.join('\\n')}}`);
  throw new Error('Todos os modelos falharam: ' + erros.join(' | '));
}}

// Se usou modelo diferente do primeiro, notificar
if (modeloUsado !== MODELOS[0]) {{
  await notificarTelegram(`🔄 Modelo trocado: ${{modeloUsado}} (primário indisponível)`);
}}

const texto = resultado.candidates[0].content.parts[0].text;

return [{{
  json: {{
    ...($input.all()[0].json),
    gemini_response: resultado,
    gemini_text: texto,
    modelo_usado: modeloUsado,
    fallback: modeloUsado !== MODELOS[0]
  }}
}}];
""".strip()


def gerar_js_fallback(prompt_source="$json.prompt_completo", temperature=0.2, max_tokens=8192):
    """Gera o código JS com fallback para injetar no nó Code."""
    return FALLBACK_JS_TEMPLATE.format(
        gemini_key=GEMINI_KEY,
        modelos_json=json.dumps(MODELO_HIERARQUIA),
        telegram_token=TELEGRAM_TOKEN,
        telegram_chat=TELEGRAM_CHAT,
        prompt_source=prompt_source,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def substituir_no_gemini(wf_data, nome_no_http, prompt_source="$json.prompt_completo", temp=0.2, max_tokens=8192):
    """Substitui um nó HTTP Request do Gemini por nó Code com fallback."""
    nodes = wf_data["nodes"]
    no_idx = None
    no_antigo = None

    for i, node in enumerate(nodes):
        if node["name"] == nome_no_http:
            no_idx = i
            no_antigo = node
            break

    if no_idx is None:
        print(f"  ⚠️  Nó '{nome_no_http}' não encontrado")
        return False

    # Criar novo nó Code no lugar do HTTP
    novo_no = {
        "parameters": {
            "jsCode": gerar_js_fallback(prompt_source, temp, max_tokens),
            "nodeVersion": 2
        },
        "id": no_antigo["id"],
        "name": nome_no_http,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": no_antigo["position"]
    }

    nodes[no_idx] = novo_no
    print(f"  ✅ '{nome_no_http}' → Code com fallback ({len(MODELO_HIERARQUIA)} modelos)")
    return True


def precisa_adaptar_extrator(wf_data, nome_extrator):
    """Adapta nó extrator para usar $json.gemini_text em vez de response.candidates."""
    nodes = wf_data["nodes"]
    for node in nodes:
        if node["name"] == nome_extrator and node["type"] == "n8n-nodes-base.code":
            code = node["parameters"].get("jsCode", "")
            # Substituir acesso direto ao response por $json.gemini_text
            if "response.candidates" in code or "$input.all()[0].json" in code:
                # Adicionar no início: pegar texto do gemini_text
                novo_prefixo = (
                    "// Texto já extraído pelo nó de fallback\n"
                    "const sintese = $input.all()[0].json.gemini_text;\n"
                    "const modeloUsado = $input.all()[0].json.modelo_usado || 'desconhecido';\n\n"
                )
                # Remover a extração antiga de candidates
                code_limpo = re.sub(
                    r'const response = \$input\.all\(\)\[0\]\.json;.*?'
                    r'const sintese = response\.candidates\[0\]\.content\.parts\[0\]\.text;',
                    '',
                    code,
                    flags=re.DOTALL
                )
                # Remover checagem de erro do candidates (já feita no fallback)
                code_limpo = re.sub(
                    r'// Verificar erro.*?finishReason.*?}',
                    '',
                    code_limpo,
                    flags=re.DOTALL
                )
                node["parameters"]["jsCode"] = novo_prefixo + code_limpo.strip()
                print(f"  ✅ '{nome_extrator}' adaptado para usar gemini_text")
                return True
    return False


def processar_workflow(filepath):
    """Processa um workflow JSON."""
    print(f"\n📄 {filepath.name}")

    with open(filepath, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    # Encontrar nós HTTP que chamam Gemini
    gemini_nodes = []
    for node in wf["nodes"]:
        if node["type"] == "n8n-nodes-base.httpRequest":
            url = node["parameters"].get("url", "")
            if "generativelanguage.googleapis.com" in url:
                gemini_nodes.append(node["name"])

    if not gemini_nodes:
        print("  ℹ️  Nenhum nó Gemini encontrado")
        return wf

    print(f"  Encontrados {len(gemini_nodes)} nós Gemini: {', '.join(gemini_nodes)}")

    for nome in gemini_nodes:
        # Determinar fonte do prompt baseado no workflow
        if "aceite" in filepath.name.lower():
            prompt_src = "$json.prompt_completo"
        elif "analise" in filepath.name.lower():
            prompt_src = "$json.prompt_completo"
        elif "verificar" in filepath.name.lower() or "verificador" in filepath.name.lower():
            prompt_src = "$json.prompt_completo"
        else:
            prompt_src = "$json.prompt_completo"

        substituir_no_gemini(wf, nome, prompt_src)

    # Adaptar nós que leem resposta do Gemini
    for node in wf["nodes"]:
        if node["type"] == "n8n-nodes-base.code":
            code = node["parameters"].get("jsCode", "")
            if "response.candidates" in code and node["name"] not in gemini_nodes:
                precisa_adaptar_extrator(wf, node["name"])

    return wf


def deploy_n8n(wf_data, wf_id):
    """Atualiza workflow no N8N via API."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Filtrar campos aceitos pela API
    payload = {
        "name": wf_data.get("name"),
        "nodes": wf_data.get("nodes"),
        "connections": wf_data.get("connections"),
        "settings": wf_data.get("settings"),
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{N8N_URL}/api/v1/workflows/{wf_id}",
        data=data,
        headers={
            'Content-Type': 'application/json',
            'X-N8N-API-KEY': N8N_KEY,
        },
        method='PUT'
    )

    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        result = json.loads(resp.read())
        print(f"  🚀 Deploy OK: {result.get('name', '?')}")
        return True
    except Exception as e:
        print(f"  ❌ Deploy falhou: {e}")
        return False


def ativar_n8n(wf_id):
    """Ativa workflow no N8N."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        f"{N8N_URL}/api/v1/workflows/{wf_id}/activate",
        headers={'X-N8N-API-KEY': N8N_KEY},
        method='POST'
    )

    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        result = json.loads(resp.read())
        active = result.get('active', False)
        print(f"  {'✅' if active else '⚠️'} Ativo: {active}")
        return active
    except Exception as e:
        print(f"  ❌ Ativação falhou: {e}")
        return False


def notificar_telegram(msg):
    """Envia notificação no Telegram."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg}).encode('utf-8')
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        urllib.request.urlopen(req, context=ctx, timeout=10)
    except:
        pass


def main():
    deploy = "--deploy" in sys.argv
    ativar = "--ativar" in sys.argv

    print("=" * 60)
    print("🔄 ATUALIZADOR DE MODELOS GEMINI — STEMMIA")
    print("=" * 60)
    print(f"\nHierarquia de fallback:")
    for i, m in enumerate(MODELO_HIERARQUIA, 1):
        print(f"  {i}. {m}")
    print()

    # IDs dos workflows no N8N (da última importação)
    wf_ids = {
        "workflow-01-aceite-simples.json": "1puXca03wQSqjTt3",
        "workflow-02-analise-proposta.json": "KHKFkL7dFI9GAz9b",
        "workflow-03-verificador.json": "tDnoxMoWVShC6USh",
    }

    resultados = []

    for filename, wf_id in wf_ids.items():
        filepath = WF_DIR / filename
        if not filepath.exists():
            print(f"\n⚠️  {filename} não encontrado")
            continue

        wf = processar_workflow(filepath)

        # Salvar JSON atualizado
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)
        print(f"  💾 Salvo: {filepath}")

        # Copiar para Mesa
        copy_path = WF_COPY / filename
        if copy_path.parent.exists():
            with open(copy_path, 'w', encoding='utf-8') as f:
                json.dump(wf, f, ensure_ascii=False, indent=2)
            print(f"  📋 Copiado: {copy_path}")

        if deploy:
            ok = deploy_n8n(wf, wf_id)
            if ok and ativar:
                ativar_n8n(wf_id)
            resultados.append((filename, ok))

    # Resumo
    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO")
    print(f"   Modelos: {' → '.join(MODELO_HIERARQUIA)}")
    print(f"   Workflows atualizados: {len(wf_ids)}")
    if deploy:
        ok_count = sum(1 for _, ok in resultados if ok)
        print(f"   Deploy: {ok_count}/{len(resultados)}")

    # Notificar Telegram
    msg = (
        f"🔄 MODELOS GEMINI ATUALIZADOS\n"
        f"Hierarquia: {' → '.join(MODELO_HIERARQUIA)}\n"
        f"Fallback automático ativado nos 3 workflows\n"
        f"Quando um modelo zerar quota, troca pro próximo e avisa"
    )
    notificar_telegram(msg)
    print("\n📱 Telegram notificado")


if __name__ == "__main__":
    main()
