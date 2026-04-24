#!/usr/bin/env python3
"""
gerar_verificacao.py — Gerador determinístico de HTML de verificação
Stemmia Forense v4.1.0

Recebe JSON de verificação e gera HTML interativo.
DETERMINÍSTICO: mesmo JSON = mesmo HTML, sempre.

Uso:
    python3 gerar_verificacao.py --json verificacao.json --output VERIFICACAO-TIPO.html
    python3 gerar_verificacao.py --json verificacao.json  # saída padrão: VERIFICACAO-[tipo].html
"""

import json
import sys
import os
import argparse
from datetime import datetime
from html import escape


def gerar_html(dados: dict) -> str:
    """Gera HTML completo a partir do JSON de verificação."""

    processo = escape(dados.get("processo", "SEM NÚMERO"))
    tipo_peca = escape(dados.get("tipo_peca", "PEÇA"))
    data_verif = dados.get("data_verificacao", datetime.now().isoformat())
    versao = escape(dados.get("versao_stemmia", "4.1.0"))
    resumo = dados.get("resumo", {})

    total = resumo.get("total_afirmacoes", 0)
    confirmadas = resumo.get("confirmadas", 0)
    pendentes = resumo.get("pendentes", 0)
    divergentes = resumo.get("divergentes", 0)
    sem_fonte = resumo.get("sem_fonte", 0)
    vicios = resumo.get("vicios_processuais", 0)

    secoes = dados.get("secoes", [])
    leis = dados.get("leis_citadas", [])
    vicios_lista = dados.get("vicios_processuais", [])
    erros_mat = dados.get("erros_materiais_incorporados", {})

    # Gerar cards de verificação
    cards_html = ""
    card_id = 0
    for secao in secoes:
        titulo_secao = escape(secao.get("titulo", "Seção"))
        cards_html += f'<h3 class="secao-titulo">{titulo_secao}</h3>\n'

        for afirmacao in secao.get("afirmacoes", []):
            card_id += 1
            aid = afirmacao.get("id", card_id)
            trecho = escape(afirmacao.get("trecho_peticao", ""))
            status = afirmacao.get("status", "pendente").lower()
            fontes = afirmacao.get("fontes", [])
            alertas = afirmacao.get("alertas", [])
            dados_verif = afirmacao.get("dados_verificaveis", [])

            # Classe CSS por status
            status_map = {
                "confirmado": "status-ok",
                "pendente": "status-pendente",
                "divergente": "status-erro",
                "sem_fonte": "status-sem-fonte",
                "vicio": "status-vicio"
            }
            status_class = status_map.get(status, "status-pendente")

            # Ícone por status
            icone_map = {
                "confirmado": "✅",
                "pendente": "⚠️",
                "divergente": "❌",
                "sem_fonte": "🟢",
                "vicio": "🔴"
            }
            icone = icone_map.get(status, "⚠️")

            # Label por status
            label_map = {
                "confirmado": "CONFIRMADO",
                "pendente": "PENDENTE",
                "divergente": "DIVERGENTE",
                "sem_fonte": "SEM FONTE",
                "vicio": "VÍCIO PROCESSUAL"
            }
            label = label_map.get(status, "PENDENTE")

            # Highlight de dados verificáveis no trecho
            trecho_marcado = trecho
            for dado in dados_verif:
                dado_esc = escape(dado)
                trecho_marcado = trecho_marcado.replace(
                    dado_esc,
                    f'<mark class="dado-verificavel">{dado_esc}</mark>'
                )

            # Fontes HTML
            fontes_html = ""
            if fontes:
                for fonte in fontes:
                    f_id = escape(str(fonte.get("id_documento", "—")))
                    f_tipo = escape(fonte.get("tipo", "—"))
                    f_trecho = escape(fonte.get("trecho_fonte", "—"))
                    f_loc = escape(fonte.get("localizacao", "—"))
                    fontes_html += f'''
                    <div class="fonte-item">
                        <div class="fonte-header">
                            <span class="fonte-id">ID {f_id}</span>
                            <span class="fonte-tipo">{f_tipo}</span>
                        </div>
                        <blockquote class="fonte-trecho">"{f_trecho}"</blockquote>
                        <div class="fonte-loc">{f_loc}</div>
                    </div>'''
            elif status == "sem_fonte":
                fontes_html = '''
                    <div class="sem-fonte-alerta">
                        <span class="sem-fonte-icone">🟢</span>
                        <strong>INFORMAÇÃO SEM FONTE IDENTIFICADA</strong>
                        <p>Verificar manualmente no processo original.</p>
                    </div>'''
            elif status == "vicio":
                for alerta in alertas:
                    alerta_esc = escape(alerta)
                    fontes_html += f'''
                    <div class="vicio-alerta">
                        <span class="vicio-icone">🔴</span>
                        <strong>VÍCIO PROCESSUAL DETECTADO</strong>
                        <p>{alerta_esc}</p>
                    </div>'''
            elif status == "divergente":
                for alerta in alertas:
                    alerta_esc = escape(alerta)
                    fontes_html += f'''
                    <div class="divergente-alerta">
                        <span class="divergente-icone">❌</span>
                        <strong>DIVERGÊNCIA DETECTADA</strong>
                        <p>{alerta_esc}</p>
                    </div>'''
                # Mostrar também a fonte divergente
                for fonte in fontes:
                    f_id = escape(str(fonte.get("id_documento", "—")))
                    f_trecho = escape(fonte.get("trecho_fonte", "—"))
                    fontes_html += f'''
                    <div class="fonte-item fonte-divergente">
                        <div class="fonte-header">
                            <span class="fonte-id">ID {f_id}</span>
                            <span class="fonte-tipo">Fonte divergente</span>
                        </div>
                        <blockquote class="fonte-trecho">"{f_trecho}"</blockquote>
                    </div>'''

            # Data attributes para filtros
            cards_html += f'''
            <div class="card-verif {status_class}" data-status="{status}" data-id="{aid}">
                <div class="card-header" onclick="toggleCard({aid})">
                    <span class="card-numero">#{aid}</span>
                    <span class="card-resumo">{trecho[:80]}{'...' if len(trecho) > 80 else ''}</span>
                    <span class="status-badge badge-{status}">{icone} {label}</span>
                    <div class="status-btns">
                        <button class="status-btn btn-ok" onclick="event.stopPropagation(); setStatus({aid}, 'ok')" title="Confirmado">✓</button>
                        <button class="status-btn btn-pendente" onclick="event.stopPropagation(); setStatus({aid}, 'pendente')" title="Pendente">⏳</button>
                        <button class="status-btn btn-erro" onclick="event.stopPropagation(); setStatus({aid}, 'erro')" title="Erro">✗</button>
                    </div>
                </div>
                <div class="card-body" id="body-{aid}">
                    <div class="card-conteudo">
                        <div class="coluna-peticao">
                            <div class="coluna-label">Trecho da petição</div>
                            <div class="trecho-texto">{trecho_marcado}</div>
                        </div>
                        <div class="coluna-fonte">
                            <div class="coluna-label">Fonte no processo</div>
                            {fontes_html}
                        </div>
                    </div>
                    <div class="card-notas">
                        <textarea class="notas-input" id="notas-{aid}" placeholder="Anotações..." onchange="salvarNotas({aid})"></textarea>
                    </div>
                </div>
            </div>'''

    # Seção de leis citadas
    leis_html = ""
    if leis:
        leis_html = '<h3 class="secao-titulo">Referências Legais Citadas</h3>\n'
        for lei in leis:
            ref = escape(lei.get("referencia", "—"))
            lei_status = lei.get("status", "pendente").lower()
            trecho_lei = escape(lei.get("trecho_lei", ""))
            arquivo = escape(lei.get("arquivo_local", ""))

            lei_icone = {"confirmada": "✅", "pendente": "⚠️", "nao_encontrada": "❌"}.get(lei_status, "⚠️")
            lei_label = {"confirmada": "CONFIRMADA", "pendente": "PENDENTE", "nao_encontrada": "NÃO ENCONTRADA"}.get(lei_status, "PENDENTE")
            lei_class = {"confirmada": "status-ok", "pendente": "status-pendente", "nao_encontrada": "status-erro"}.get(lei_status, "status-pendente")

            leis_html += f'''
            <div class="card-lei {lei_class}">
                <div class="lei-header">
                    <span class="lei-ref">{ref}</span>
                    <span class="status-badge badge-{lei_status}">{lei_icone} {lei_label}</span>
                </div>'''
            if trecho_lei:
                leis_html += f'<blockquote class="lei-trecho">"{trecho_lei}"</blockquote>'
            if arquivo:
                leis_html += f'<div class="lei-arquivo">Arquivo local: {arquivo}</div>'
            leis_html += '</div>\n'

    # Seção de vícios processuais
    vicios_html = ""
    if vicios_lista:
        vicios_html = '<h3 class="secao-titulo secao-vicios">Vícios Processuais Detectados</h3>\n'
        for vicio in vicios_lista:
            desc = escape(vicio.get("descricao", ""))
            cnj_estranho = escape(vicio.get("cnj_detectado", ""))
            vicios_html += f'''
            <div class="card-vicio">
                <span class="vicio-icone-grande">🔴</span>
                <div class="vicio-conteudo">
                    <strong>{desc}</strong>
                    {f'<div class="cnj-estranho">CNJ detectado: {cnj_estranho}</div>' if cnj_estranho else ''}
                </div>
            </div>'''

    # Seção de erros materiais incorporados
    erros_html = ""
    tem_erros = any(erros_mat.get(k) for k in ["cids", "datas", "nomes", "medicamentos", "exames"])
    if tem_erros:
        erros_html = '<h3 class="secao-titulo">Erros Materiais (verificadores anteriores)</h3>\n'
        categorias = {
            "cids": "CIDs",
            "datas": "Datas",
            "nomes": "Nomes/Números",
            "medicamentos": "Medicamentos",
            "exames": "Exames"
        }
        for chave, nome in categorias.items():
            itens = erros_mat.get(chave, [])
            if itens:
                erros_html += f'<div class="erros-cat"><strong>{nome}:</strong><ul>'
                for item in itens:
                    erros_html += f'<li>{escape(str(item))}</li>'
                erros_html += '</ul></div>'

    # Montar HTML completo
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verificação 100% — {tipo_peca} — {processo}</title>
<style>
  :root {{
    --azul: #1a365d;
    --azul-claro: #2c5282;
    --fundo: #f0f2f5;
    --card: #ffffff;
    --texto: #1a1a1a;
    --texto-leve: #4a5568;
    --borda: #e2e8f0;
    --verde: #38a169;
    --verde-bg: #f0fff4;
    --amarelo: #d69e2e;
    --amarelo-bg: #fffff0;
    --vermelho: #e53e3e;
    --vermelho-bg: #fff5f5;
    --vicio-bg: #fce4ec;
    --sem-fonte-bg: #e8f5e9;
    --sombra: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --sombra-hover: 0 4px 12px rgba(0,0,0,0.1);
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--fundo);
    color: var(--texto);
    line-height: 1.6;
  }}

  /* HEADER */
  .header {{
    background: linear-gradient(135deg, var(--azul), var(--azul-claro));
    color: white;
    padding: 30px 40px;
  }}
  .header h1 {{ font-size: 1.4em; font-weight: 600; margin-bottom: 4px; }}
  .header .subtitulo {{ opacity: 0.85; font-size: 0.95em; }}
  .header .processo {{ font-family: 'SF Mono', Monaco, monospace; font-size: 0.9em; opacity: 0.7; margin-top: 8px; }}
  .header .meta {{ display: flex; gap: 20px; margin-top: 8px; font-size: 0.8em; opacity: 0.6; }}

  /* PROGRESSO STICKY */
  .progresso-container {{
    background: var(--card);
    padding: 16px 40px;
    border-bottom: 1px solid var(--borda);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--sombra);
  }}
  .progresso-bar-outer {{
    background: #e2e8f0;
    border-radius: 10px;
    height: 12px;
    margin: 10px 0;
    overflow: hidden;
  }}
  .progresso-bar-inner {{
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
    background: linear-gradient(90deg, var(--verde), #48bb78);
  }}
  .progresso-stats {{
    display: flex;
    gap: 20px;
    font-size: 0.85em;
    color: var(--texto-leve);
    flex-wrap: wrap;
  }}
  .stat {{ display: flex; align-items: center; gap: 4px; }}
  .stat-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
  .stat-dot.ok {{ background: var(--verde); }}
  .stat-dot.pendente {{ background: var(--amarelo); }}
  .stat-dot.erro {{ background: var(--vermelho); }}
  .stat-dot.sem-fonte {{ background: #66bb6a; border: 2px dashed #388e3c; }}
  .stat-dot.vicio {{ background: var(--vermelho); animation: pulse 1s infinite; }}

  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
  }}

  /* FILTROS */
  .filtros {{
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 12px;
    flex-wrap: wrap;
  }}
  .filtro-btn {{
    padding: 5px 14px;
    border-radius: 20px;
    border: 1px solid var(--borda);
    background: white;
    cursor: pointer;
    font-size: 0.82em;
    transition: all 0.2s;
  }}
  .filtro-btn:hover {{ border-color: var(--azul); color: var(--azul); }}
  .filtro-btn.ativo {{ background: var(--azul); color: white; border-color: var(--azul); }}
  .busca-input {{
    padding: 6px 14px;
    border: 1px solid var(--borda);
    border-radius: 20px;
    font-size: 0.85em;
    width: 220px;
    outline: none;
  }}
  .busca-input:focus {{ border-color: var(--azul); }}

  /* CONTEUDO */
  .conteudo {{ max-width: 1200px; margin: 0 auto; padding: 24px 20px; }}
  .secao-titulo {{
    font-size: 1.1em;
    font-weight: 700;
    color: var(--azul);
    margin: 28px 0 14px;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--azul);
  }}
  .secao-vicios {{ color: var(--vermelho); border-bottom-color: var(--vermelho); }}

  /* CARD DE VERIFICAÇÃO */
  .card-verif {{
    background: var(--card);
    border-radius: 10px;
    box-shadow: var(--sombra);
    margin-bottom: 16px;
    overflow: hidden;
    transition: box-shadow 0.2s;
    border-left: 4px solid var(--amarelo);
  }}
  .card-verif:hover {{ box-shadow: var(--sombra-hover); }}
  .card-verif.status-ok {{ border-left-color: var(--verde); }}
  .card-verif.status-pendente {{ border-left-color: var(--amarelo); }}
  .card-verif.status-erro {{ border-left-color: var(--vermelho); }}
  .card-verif.status-sem-fonte {{ border-left-color: #66bb6a; border-left-style: dashed; }}
  .card-verif.status-vicio {{ border-left-color: var(--vermelho); border-left-width: 6px; animation: pulse 2s infinite; }}

  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px;
    background: #fafbfc;
    border-bottom: 1px solid var(--borda);
    cursor: pointer;
    gap: 12px;
  }}
  .card-header:hover {{ background: #f0f2f5; }}
  .card-numero {{ font-weight: 700; color: var(--azul); font-size: 0.85em; white-space: nowrap; }}
  .card-resumo {{ font-size: 0.9em; flex: 1; color: var(--texto); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

  .status-badge {{
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: 600;
    white-space: nowrap;
  }}
  .badge-confirmado {{ background: var(--verde-bg); color: var(--verde); }}
  .badge-pendente {{ background: var(--amarelo-bg); color: var(--amarelo); }}
  .badge-divergente {{ background: var(--vermelho-bg); color: var(--vermelho); }}
  .badge-sem_fonte {{ background: var(--sem-fonte-bg); color: #2e7d32; }}
  .badge-vicio {{ background: var(--vicio-bg); color: var(--vermelho); }}

  .status-btns {{ display: flex; gap: 4px; }}
  .status-btn {{
    width: 32px; height: 32px;
    border-radius: 50%;
    border: 1px solid var(--borda);
    background: white;
    cursor: pointer;
    font-size: 0.9em;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }}
  .btn-ok:hover {{ background: var(--verde-bg); border-color: var(--verde); }}
  .btn-pendente:hover {{ background: var(--amarelo-bg); border-color: var(--amarelo); }}
  .btn-erro:hover {{ background: var(--vermelho-bg); border-color: var(--vermelho); }}
  .status-btn.ativo-ok {{ background: var(--verde); color: white; border-color: var(--verde); }}
  .status-btn.ativo-pendente {{ background: var(--amarelo); color: white; border-color: var(--amarelo); }}
  .status-btn.ativo-erro {{ background: var(--vermelho); color: white; border-color: var(--vermelho); }}

  /* CARD BODY */
  .card-body {{
    display: none;
    padding: 20px;
  }}
  .card-body.aberto {{ display: block; }}
  .card-conteudo {{
    display: grid;
    grid-template-columns: 55% 45%;
    gap: 20px;
  }}
  @media (max-width: 768px) {{
    .card-conteudo {{ grid-template-columns: 1fr; }}
  }}
  .coluna-label {{
    font-size: 0.75em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--texto-leve);
    margin-bottom: 8px;
  }}
  .trecho-texto {{
    font-size: 0.95em;
    line-height: 1.7;
    padding: 12px;
    background: #f8fafc;
    border-radius: 6px;
    border: 1px solid var(--borda);
  }}
  mark.dado-verificavel {{
    background: #fef3c7;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 600;
  }}

  /* FONTES */
  .fonte-item {{
    margin-bottom: 12px;
    padding: 10px;
    background: var(--verde-bg);
    border-radius: 6px;
    border: 1px solid #c6f6d5;
  }}
  .fonte-item.fonte-divergente {{
    background: var(--vermelho-bg);
    border-color: #fed7d7;
  }}
  .fonte-header {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
  }}
  .fonte-id {{ font-weight: 700; font-size: 0.85em; color: var(--azul); }}
  .fonte-tipo {{ font-size: 0.8em; color: var(--texto-leve); }}
  .fonte-trecho {{
    font-size: 0.88em;
    font-style: italic;
    color: #2d3748;
    border-left: 3px solid var(--verde);
    padding-left: 10px;
    margin: 6px 0;
  }}
  .fonte-loc {{ font-size: 0.75em; color: var(--texto-leve); }}

  /* ALERTAS */
  .sem-fonte-alerta {{
    background: var(--sem-fonte-bg);
    border: 2px dashed #66bb6a;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
  }}
  .sem-fonte-alerta strong {{ color: #2e7d32; display: block; margin: 8px 0 4px; }}
  .sem-fonte-alerta p {{ font-size: 0.85em; color: var(--texto-leve); }}
  .sem-fonte-icone {{ font-size: 1.5em; }}

  .vicio-alerta {{
    background: var(--vicio-bg);
    border: 2px solid var(--vermelho);
    border-radius: 8px;
    padding: 16px;
  }}
  .vicio-alerta strong {{ color: var(--vermelho); display: block; margin: 4px 0; }}
  .vicio-icone {{ font-size: 1.3em; }}

  .divergente-alerta {{
    background: var(--vermelho-bg);
    border: 1px solid #fed7d7;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
  }}
  .divergente-alerta strong {{ color: var(--vermelho); }}

  /* NOTAS */
  .card-notas {{ margin-top: 12px; }}
  .notas-input {{
    width: 100%;
    min-height: 40px;
    padding: 8px 12px;
    border: 1px solid var(--borda);
    border-radius: 6px;
    font-family: inherit;
    font-size: 0.85em;
    resize: vertical;
  }}
  .notas-input:focus {{ border-color: var(--azul); outline: none; }}

  /* LEIS */
  .card-lei {{
    background: var(--card);
    border-radius: 8px;
    box-shadow: var(--sombra);
    padding: 14px 20px;
    margin-bottom: 10px;
    border-left: 4px solid var(--amarelo);
  }}
  .card-lei.status-ok {{ border-left-color: var(--verde); }}
  .card-lei.status-erro {{ border-left-color: var(--vermelho); }}
  .lei-header {{ display: flex; justify-content: space-between; align-items: center; }}
  .lei-ref {{ font-weight: 700; color: var(--azul); }}
  .lei-trecho {{
    font-size: 0.88em;
    font-style: italic;
    border-left: 3px solid var(--azul);
    padding-left: 10px;
    margin: 8px 0;
    color: #2d3748;
  }}
  .lei-arquivo {{ font-size: 0.75em; color: var(--texto-leve); }}

  /* VÍCIOS */
  .card-vicio {{
    background: var(--vicio-bg);
    border: 2px solid var(--vermelho);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }}
  .vicio-icone-grande {{ font-size: 1.5em; }}
  .cnj-estranho {{ font-family: 'SF Mono', Monaco, monospace; font-size: 0.85em; color: var(--vermelho); margin-top: 4px; }}

  /* ERROS MATERIAIS */
  .erros-cat {{ margin-bottom: 10px; }}
  .erros-cat ul {{ padding-left: 20px; }}
  .erros-cat li {{ font-size: 0.9em; margin-bottom: 4px; }}

  /* HIDDEN */
  .hidden {{ display: none !important; }}

  /* RODAPÉ */
  .rodape {{
    text-align: center;
    padding: 30px;
    font-size: 0.8em;
    color: var(--texto-leve);
    border-top: 1px solid var(--borda);
    margin-top: 40px;
  }}

  /* PRINT */
  @media print {{
    .progresso-container {{ position: static; }}
    .status-btns, .filtros, .busca-input, .notas-input {{ display: none; }}
    .card-body {{ display: block !important; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <h1>Verificação 100% — {tipo_peca}</h1>
    <div class="subtitulo">Rastreabilidade de cada afirmação até a fonte no processo</div>
    <div class="processo">{processo}</div>
    <div class="meta">
        <span>Gerado em: {data_verif[:19].replace('T', ' ')}</span>
        <span>Stemmia Forense v{versao}</span>
    </div>
</div>

<!-- PROGRESSO STICKY -->
<div class="progresso-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="font-size: 0.9em;">Progresso da conferência manual</strong>
        <span id="progresso-pct" style="font-size: 0.85em; color: var(--texto-leve);">0/{total} conferidos</span>
    </div>
    <div class="progresso-bar-outer">
        <div class="progresso-bar-inner" id="progresso-bar" style="width: 0%;"></div>
    </div>
    <div class="progresso-stats">
        <div class="stat"><span class="stat-dot ok"></span> {confirmadas} confirmados</div>
        <div class="stat"><span class="stat-dot pendente"></span> {pendentes} pendentes</div>
        <div class="stat"><span class="stat-dot erro"></span> {divergentes} divergentes</div>
        <div class="stat"><span class="stat-dot sem-fonte"></span> {sem_fonte} sem fonte</div>
        {'<div class="stat"><span class="stat-dot vicio"></span> ' + str(vicios) + ' vícios</div>' if vicios > 0 else ''}
    </div>
    <div class="filtros">
        <button class="filtro-btn ativo" onclick="filtrar('todos')">Todos ({total})</button>
        <button class="filtro-btn" onclick="filtrar('confirmado')">✅ Confirmados ({confirmadas})</button>
        <button class="filtro-btn" onclick="filtrar('pendente')">⚠️ Pendentes ({pendentes})</button>
        <button class="filtro-btn" onclick="filtrar('divergente')">❌ Divergentes ({divergentes})</button>
        <button class="filtro-btn" onclick="filtrar('sem_fonte')">🟢 Sem fonte ({sem_fonte})</button>
        {'<button class="filtro-btn" onclick="filtrar(\'vicio\')">🔴 Vícios (' + str(vicios) + ')</button>' if vicios > 0 else ''}
        <input type="text" class="busca-input" placeholder="Buscar no texto..." oninput="buscar(this.value)">
    </div>
</div>

<!-- CONTEÚDO -->
<div class="conteudo">
    {cards_html}
    {leis_html}
    {vicios_html}
    {erros_html}
</div>

<!-- RODAPÉ -->
<div class="rodape">
    <p>Verificação 100% — Stemmia Forense v{versao}</p>
    <p>Processo: {processo} | Tipo: {tipo_peca} | {data_verif[:10]}</p>
    <p><strong>Este relatório é ferramenta de apoio. A verificação manual pelo perito é obrigatória.</strong></p>
</div>

<script>
// Chave de persistência
const STORAGE_KEY = 'verif-{processo}-{tipo_peca}';
const TOTAL = {total};

// Estado
let estado = carregarEstado();

function carregarEstado() {{
    try {{
        const salvo = localStorage.getItem(STORAGE_KEY);
        return salvo ? JSON.parse(salvo) : {{}};
    }} catch(e) {{
        return {{}};
    }}
}}

function salvarEstado() {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(estado));
    atualizarProgresso();
}}

// Toggle card
function toggleCard(id) {{
    const body = document.getElementById('body-' + id);
    body.classList.toggle('aberto');
}}

// Set status manual
function setStatus(id, status) {{
    estado[id] = estado[id] || {{}};
    estado[id].status = status;
    salvarEstado();

    // Visual
    const card = document.querySelector('[data-id="' + id + '"]');
    card.querySelectorAll('.status-btn').forEach(b => {{
        b.classList.remove('ativo-ok', 'ativo-pendente', 'ativo-erro');
    }});
    const btn = card.querySelector('.btn-' + status);
    if (btn) btn.classList.add('ativo-' + status);
}}

// Salvar notas
function salvarNotas(id) {{
    const textarea = document.getElementById('notas-' + id);
    estado[id] = estado[id] || {{}};
    estado[id].notas = textarea.value;
    salvarEstado();
}}

// Atualizar progresso
function atualizarProgresso() {{
    let conferidos = 0;
    for (const k in estado) {{
        if (estado[k].status) conferidos++;
    }}
    const pct = TOTAL > 0 ? Math.round((conferidos / TOTAL) * 100) : 0;
    document.getElementById('progresso-bar').style.width = pct + '%';
    document.getElementById('progresso-pct').textContent = conferidos + '/' + TOTAL + ' conferidos (' + pct + '%)';
}}

// Filtrar
function filtrar(tipo) {{
    document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('ativo'));
    event.target.classList.add('ativo');

    document.querySelectorAll('.card-verif').forEach(card => {{
        if (tipo === 'todos') {{
            card.classList.remove('hidden');
        }} else {{
            card.classList.toggle('hidden', card.dataset.status !== tipo);
        }}
    }});
}}

// Buscar
function buscar(termo) {{
    const lower = termo.toLowerCase();
    document.querySelectorAll('.card-verif').forEach(card => {{
        const texto = card.textContent.toLowerCase();
        card.classList.toggle('hidden', lower.length > 0 && !texto.includes(lower));
    }});
}}

// Restaurar estado ao carregar
document.addEventListener('DOMContentLoaded', function() {{
    for (const id in estado) {{
        if (estado[id].status) {{
            const card = document.querySelector('[data-id="' + id + '"]');
            if (card) {{
                const btn = card.querySelector('.btn-' + estado[id].status);
                if (btn) btn.classList.add('ativo-' + estado[id].status);
            }}
        }}
        if (estado[id].notas) {{
            const textarea = document.getElementById('notas-' + id);
            if (textarea) textarea.value = estado[id].notas;
        }}
    }}
    atualizarProgresso();
}});
</script>

</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(
        description="Gera HTML de verificação 100% a partir de JSON"
    )
    parser.add_argument("--json", required=True, help="Caminho do JSON de verificação")
    parser.add_argument("--output", help="Caminho de saída do HTML")
    args = parser.parse_args()

    # Ler JSON
    with open(args.json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Definir saída
    if args.output:
        output_path = args.output
    else:
        tipo = dados.get("tipo_peca", "PECA").replace(" ", "-")
        output_path = f"VERIFICACAO-{tipo}.html"

    # Gerar HTML
    html = gerar_html(dados)

    # Escrever arquivo
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML gerado: {output_path}")
    print(f"Total de afirmações: {dados.get('resumo', {}).get('total_afirmacoes', 0)}")
    print(f"Confirmadas: {dados.get('resumo', {}).get('confirmadas', 0)}")
    print(f"Pendentes: {dados.get('resumo', {}).get('pendentes', 0)}")
    print(f"Divergentes: {dados.get('resumo', {}).get('divergentes', 0)}")
    print(f"Sem fonte: {dados.get('resumo', {}).get('sem_fonte', 0)}")
    print(f"Vícios: {dados.get('resumo', {}).get('vicios_processuais', 0)}")

    return output_path


if __name__ == "__main__":
    main()
