#!/usr/bin/env python3
"""
Gera visão unificada dos processos cruzando dados do scanner,
DataJud e DJe em um único arquivo Markdown.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# === Caminhos ===
BASE = Path.home() / "Desktop" / "ANALISADOR FINAL"
STATUS_JSON = BASE / "STATUS-PROCESSOS.json"
RESULTADOS = BASE / "scripts" / "monitor-publicacoes" / "resultados"
SAIDA = Path.home() / "Desktop" / "AUTOMAÇÃO PROCESSUAL" / "MEUS-PROCESSOS.md"

# Prioridade dos estados (menor = mais urgente)
PRIORIDADE = {
    "EM-CONTESTAÇÃO": 0,
    "PENDENTE-LAUDO": 1,
    "PENDENTE-AGENDAMENTO": 2,
    "PENDENTE-ACEITE": 3,
    "PENDENTE-PROPOSTA": 4,
    "PENDENTE-PDF": 5,
}

ACAO_POR_ESTADO = {
    "EM-CONTESTAÇÃO": "Responder contestação (/contestar)",
    "PENDENTE-LAUDO": "Elaborar laudo pericial",
    "PENDENTE-AGENDAMENTO": "Agendar perícia (/agendar)",
    "PENDENTE-ACEITE": "Gerar petição de aceite (/aceite)",
    "PENDENTE-PROPOSTA": "Gerar proposta de honorários (/proposta)",
    "PENDENTE-PDF": "Colocar PDF do processo na pasta",
}


def carregar_json(caminho: Path) -> Optional[dict]:
    """Carrega JSON tratando FileNotFoundError."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"  Aviso: JSON inválido em {caminho}")
        return None


def ultimo_arquivo(pasta: Path, prefixo: str) -> Optional[Path]:
    """Retorna o arquivo mais recente com dado prefixo."""
    if not pasta.exists():
        return None
    arquivos = sorted(pasta.glob(f"{prefixo}*.json"), reverse=True)
    return arquivos[0] if arquivos else None


def extrair_comarca(proc: dict) -> str:
    """Extrai comarca/cidade do processo."""
    ficha = proc.get("ficha", {})
    if ficha and ficha.get("cidade"):
        return ficha["cidade"]
    return "—"


def extrair_vara(proc: dict) -> str:
    """Extrai vara do processo."""
    ficha = proc.get("ficha", {})
    if ficha and ficha.get("vara"):
        return ficha["vara"]
    return "—"


def extrair_tipo(proc: dict) -> str:
    """Extrai tipo de ação/perícia."""
    ficha = proc.get("ficha", {})
    if ficha and ficha.get("tipo_pericia"):
        return ficha["tipo_pericia"]
    if ficha and ficha.get("area"):
        return ficha["area"]
    return "—"


def main():
    agora = datetime.now()
    data_str = agora.strftime("%d/%m/%Y às %H:%M")

    # 1. Carregar dados do scanner
    status = carregar_json(STATUS_JSON)
    if not status:
        print("ERRO: STATUS-PROCESSOS.json não encontrado.")
        print("       Rode primeiro: python3 scripts/scanner_processos.py --resumo")
        return

    processos = status.get("processos", [])
    estatisticas = status.get("estatisticas", {})

    # 2. Carregar DataJud (último resultado)
    datajud_path = ultimo_arquivo(RESULTADOS, "datajud-")
    datajud = {}
    datajud_data = "—"
    if datajud_path:
        dj = carregar_json(datajud_path)
        if dj:
            datajud_data = dj.get("data_consulta", "—")[:10]
            for r in dj.get("resultados", []):
                datajud[r["cnj"]] = r
            print(f"  DataJud carregado: {datajud_path.name} ({len(datajud)} processos)")

    # 3. Carregar DJe (último resultado)
    dje_path = ultimo_arquivo(RESULTADOS, "dje-")
    dje = {}
    dje_data = "—"
    if dje_path:
        dj = carregar_json(dje_path)
        if dj:
            dje_data = dj.get("data_consulta", "—")[:10]
            for r in dj.get("resultados", []):
                dje[r.get("cnj", "")] = r
            print(f"  DJe carregado: {dje_path.name} ({len(dje)} processos)")

    # 4. Deduplicar por CNJ (manter entrada com mais dados / estado mais avançado)
    por_cnj = {}
    for p in processos:
        cnj = p.get("cnj")
        if not cnj:
            continue
        if cnj not in por_cnj:
            por_cnj[cnj] = p
        else:
            existente = por_cnj[cnj]
            # Preferir entrada com ficha preenchida
            tem_ficha_novo = bool(p.get("ficha", {}).get("cidade"))
            tem_ficha_exist = bool(existente.get("ficha", {}).get("cidade"))
            if tem_ficha_novo and not tem_ficha_exist:
                por_cnj[cnj] = p
            # Se ambos têm ficha, preferir o estado mais avançado (menor prioridade)
            elif tem_ficha_novo and tem_ficha_exist:
                pri_novo = PRIORIDADE.get(p.get("estado", ""), 99)
                pri_exist = PRIORIDADE.get(existente.get("estado", ""), 99)
                if pri_novo < pri_exist:
                    por_cnj[cnj] = p
            # Se nenhum tem ficha, preferir estado mais avançado
            elif not tem_ficha_novo and not tem_ficha_exist:
                pri_novo = PRIORIDADE.get(p.get("estado", ""), 99)
                pri_exist = PRIORIDADE.get(existente.get("estado", ""), 99)
                if pri_novo < pri_exist:
                    por_cnj[cnj] = p

    validos = list(por_cnj.values())
    validos.sort(key=lambda p: (
        PRIORIDADE.get(p.get("estado", ""), 99),
        p.get("cnj", "")
    ))

    # 5. Identificar ações imediatas (movimentação recente ou estado urgente)
    limite_dias = 5
    limite_data = agora - timedelta(days=limite_dias)
    acoes_imediatas = []

    for p in validos:
        cnj = p["cnj"]
        estado = p.get("estado", "")
        dj_info = datajud.get(cnj, {})
        movs = dj_info.get("movimentacoes", [])

        # Verificar movimentação recente
        mov_recente = None
        for m in movs:
            try:
                dt = datetime.fromisoformat(m["data_iso"].replace("Z", "+00:00"))
                if dt.replace(tzinfo=None) >= limite_data:
                    mov_recente = m
                    break
            except (KeyError, ValueError):
                continue

        # Processos com contestação ou movimentação recente
        if mov_recente or estado in ("EM-CONTESTAÇÃO", "PENDENTE-LAUDO"):
            ult_mov = mov_recente["data"] if mov_recente else "—"
            acao = ACAO_POR_ESTADO.get(estado, p.get("proxima_acao", "—"))
            acoes_imediatas.append({
                "cnj": cnj,
                "comarca": extrair_comarca(p),
                "vara": extrair_vara(p),
                "estado": estado,
                "ultima_mov": ult_mov,
                "acao": acao,
            })

    # 6. Montar estatísticas (baseado nos processos deduplicados)
    total_ativos = len(validos)
    from collections import Counter
    contagem = Counter(p.get("estado", "DESCONHECIDO") for p in validos)
    n_aceite = contagem.get("PENDENTE-ACEITE", 0)
    n_proposta = contagem.get("PENDENTE-PROPOSTA", 0)
    n_agendamento = contagem.get("PENDENTE-AGENDAMENTO", 0)
    n_contestacao = contagem.get("EM-CONTESTAÇÃO", 0)
    n_laudo = contagem.get("PENDENTE-LAUDO", 0)
    n_pdf = contagem.get("PENDENTE-PDF", 0)
    n_outros = total_ativos - (n_aceite + n_proposta + n_agendamento + n_contestacao + n_laudo + n_pdf)

    # 7. Gerar Markdown
    linhas = []
    linhas.append(f"# Meus Processos — Atualizado em {data_str}")
    linhas.append("")
    linhas.append("## Resumo")
    linhas.append(f"- **Total**: {total_ativos} processos ativos ({status.get('total_pastas', '?')} pastas)")
    linhas.append(f"- Pendente aceite: {n_aceite}")
    linhas.append(f"- Pendente proposta: {n_proposta}")
    linhas.append(f"- Pendente agendamento: {n_agendamento}")
    linhas.append(f"- Em contestação: {n_contestacao}")
    linhas.append(f"- Pendente laudo: {n_laudo}")
    linhas.append(f"- Pendente PDF: {n_pdf}")
    if n_outros > 0:
        linhas.append(f"- Outros: {n_outros}")
    linhas.append("")
    linhas.append(f"> Fontes: Scanner ({status.get('data_scan', '—')[:10]})")
    if datajud_path:
        linhas.append(f"> DataJud ({datajud_data})")
    if dje_path:
        linhas.append(f"> DJe ({dje_data})")
    linhas.append("")

    # Seção Ação Imediata
    linhas.append("## Ação Imediata")
    if acoes_imediatas:
        linhas.append("")
        linhas.append("| CNJ | Comarca | Vara | Estado | Última Movimentação | Ação Necessária |")
        linhas.append("|-----|---------|------|--------|---------------------|-----------------|")
        for a in acoes_imediatas:
            linhas.append(
                f"| {a['cnj']} | {a['comarca']} | {a['vara']} "
                f"| {a['estado']} | {a['ultima_mov']} | {a['acao']} |"
            )
    else:
        linhas.append("Nenhuma ação imediata identificada.")
    linhas.append("")

    # Seção Todos os Processos
    linhas.append("## Todos os Processos")
    linhas.append("")
    linhas.append("| # | CNJ | Comarca | Vara | Estado | Tipo Ação | Última Mov. (DataJud) | Publicação (DJe) |")
    linhas.append("|---|-----|---------|------|--------|-----------|----------------------|------------------|")

    for i, p in enumerate(validos, 1):
        cnj = p["cnj"]
        comarca = extrair_comarca(p)
        vara = extrair_vara(p)
        estado = p.get("estado", "—")
        tipo = extrair_tipo(p)

        # DataJud — última movimentação
        dj_info = datajud.get(cnj, {})
        movs = dj_info.get("movimentacoes", [])
        if movs:
            ult_dj = movs[0].get("data", "—")
        elif dj_info.get("total_movimentacoes", 0) > 0:
            ult_dj = f"{dj_info['total_movimentacoes']} movs"
        else:
            ult_dj = "—"

        # DJe
        dje_info = dje.get(cnj, {})
        ult_dje = dje_info.get("data_publicacao", "—") if dje_info else "—"

        linhas.append(
            f"| {i} | {cnj} | {comarca} | {vara} "
            f"| {estado} | {tipo} | {ult_dj} | {ult_dje} |"
        )

    linhas.append("")
    linhas.append("---")
    linhas.append(f"*Gerado automaticamente por gerar_visao_unificada.py em {data_str}*")

    # 8. Salvar
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nVisão unificada salva em: {SAIDA}")
    print(f"  Total de processos: {total_ativos}")
    print(f"  Ações imediatas: {len(acoes_imediatas)}")


if __name__ == "__main__":
    main()
