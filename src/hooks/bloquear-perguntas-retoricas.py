#!/usr/bin/env python3
"""
Hook Stop: bloqueia perguntas retóricas de confirmação no output do Claude.
Se detectar padrão proibido na última mensagem do assistente, retorna
feedback forçando reescrita com execução direta.

Anti-loop: máximo 2 intervenções por sessão para evitar loop infinito.
"""
import json
import re
import sys
import os
import tempfile

PATTERNS = [
    r'(?i)\bquer que eu\b.*\?',
    r'(?i)\bposso prosseguir\b.*\?',
    r'(?i)\bdevo continuar\b.*\?',
    r'(?i)\bgostaria que eu\b.*\?',
    r'(?i)\bdeseja que eu\b.*\?',
    r'(?i)\bposso (?:começar|fazer|ir|seguir|abrir|criar|executar|rodar|instalar|configurar|gerar|analisar)\b.*\?',
    r'(?i)\bdevo (?:começar|fazer|ir|seguir|abrir|criar|executar|rodar|instalar|configurar|gerar|analisar)\b.*\?',
    r'(?i)\bquer que (?:eu )?(?:abra|crie|faça|execute|rode|instale|configure|gere|analise)\b.*\?',
    r'(?i)\bvocê (?:quer|gostaria|deseja|prefere) que eu\b.*\?',
    r'(?i)\bdevo (?:ir em frente|avançar|prosseguir)\b.*\?',
]

MAX_INTERVENTIONS = 2
COUNTER_FILE = os.path.join(tempfile.gettempdir(), "claude-retorica-counter")


def get_counter(session_id: str) -> int:
    try:
        with open(COUNTER_FILE) as f:
            data = json.load(f)
            if data.get("session") != session_id:
                return 0
            return data.get("count", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def set_counter(session_id: str, count: int):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"session": session_id, "count": count}, f)


def extract_assistant_text(message) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return ""


def find_violations(text: str) -> list[str]:
    found = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(">") or stripped.startswith("```"):
            continue
        for pattern in PATTERNS:
            match = re.search(pattern, stripped)
            if match:
                found.append(match.group(0))
                break
    return found


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    transcript = data.get("transcript", [])

    if get_counter(session_id) >= MAX_INTERVENTIONS:
        sys.exit(0)

    last_assistant = None
    for msg in reversed(transcript):
        if msg.get("role") == "assistant":
            last_assistant = msg
            break

    if not last_assistant:
        sys.exit(0)

    text = extract_assistant_text(last_assistant)
    violations = find_violations(text)

    if not violations:
        sys.exit(0)

    count = get_counter(session_id) + 1
    set_counter(session_id, count)

    feedback = (
        f"<user-prompt-submit-hook>\n"
        f"HOOK BLOQUEIO: Detectei {len(violations)} pergunta(s) retórica(s) "
        f"no seu output: {violations}. "
        f"REGRA: NUNCA perguntar 'posso?', 'quer que eu?', 'devo?'. "
        f"REESCREVA a resposta EXECUTANDO a ação diretamente, sem pedir confirmação. "
        f"Intervenção {count}/{MAX_INTERVENTIONS}.\n"
        f"</user-prompt-submit-hook>"
    )
    print(feedback)


if __name__ == "__main__":
    main()
