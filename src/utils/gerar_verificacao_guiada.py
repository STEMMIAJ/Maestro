#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_verificacao_guiada.py — Gera HTML de verificação guiada (tour interativo)

Uso:
    python3 gerar_verificacao_guiada.py \
        --json processos/[CNJ]/verificacao-proposta-honorarios.json \
        --texto processos/[CNJ]/TEXTO-EXTRAIDO.txt \
        --output processos/[CNJ]/VERIFICACAO-GUIADA.html
"""

import argparse
import json
import html
import os
import re
import sys


def extrair_linhas_referenciadas(fonte_texto: str) -> list:
    """Extrai números de linha mencionados em fontes como 'Linha 358'."""
    return [int(m) for m in re.findall(r'[Ll]inha\s+(\d+)', fonte_texto)]


def preparar_afirmacoes(data: dict) -> list:
    """Converte o JSON de verificação em lista plana de afirmações."""
    afirmacoes = []
    idx = 0
    for secao in data.get('secoes', []):
        titulo_secao = secao.get('titulo', '')
        for af in secao.get('afirmacoes', []):
            idx += 1
            linhas_ref = []
            fontes_texto = []
            for f in af.get('fontes', []):
                loc = f.get('localizacao', '') + ' ' + f.get('trecho_fonte', '')
                linhas_ref.extend(extrair_linhas_referenciadas(loc))
                fontes_texto.append({
                    'tipo': f.get('tipo', ''),
                    'trecho': f.get('trecho_fonte', ''),
                    'localizacao': f.get('localizacao', '')
                })
            afirmacoes.append({
                'idx': idx,
                'secao': titulo_secao,
                'trecho': af.get('trecho_peticao', ''),
                'dados': af.get('dados_verificaveis', []),
                'status_original': af.get('status', ''),
                'linhas_ref': sorted(set(linhas_ref)),
                'fontes': fontes_texto,
                'alertas': af.get('alertas', [])
            })
    return afirmacoes


def escapar_js_string(s: str) -> str:
    """Escapa string para uso seguro dentro de JS."""
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('"', '\\"')
             .replace('\n', '\\n')
             .replace('\r', '\\r')
             .replace('</', '<\\/'))


def gerar_html(data: dict, linhas_texto: list, processo: str) -> str:
    """Gera o HTML completo do tour guiado."""

    afirmacoes = preparar_afirmacoes(data)
    resumo = data.get('resumo', {})
    total = resumo.get('total_afirmacoes', len(afirmacoes))

    # Preparar texto do processo como array JS (escapado)
    linhas_js = []
    for linha in linhas_texto:
        linhas_js.append("'" + escapar_js_string(linha) + "'")
    texto_js_array = ',\n'.join(linhas_js)

    # Preparar afirmações como JSON JS
    afirmacoes_js = json.dumps(afirmacoes, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verificacao Guiada — {html.escape(processo)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #e0e0e0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}

/* BARRA DE PROGRESSO */
.barra-topo {{ background: #16213e; padding: 12px 20px; display: flex; align-items: center; gap: 16px; border-bottom: 2px solid #0f3460; flex-shrink: 0; }}
.barra-topo .titulo {{ font-size: 13px; color: #8899aa; white-space: nowrap; }}
.barra-topo .passo {{ font-size: 15px; font-weight: 600; color: #e94560; min-width: 120px; }}
.progresso-container {{ flex: 1; background: #0f3460; border-radius: 8px; height: 8px; overflow: hidden; }}
.progresso-fill {{ height: 100%; background: linear-gradient(90deg, #e94560, #0f3460); border-radius: 8px; transition: width 0.4s ease; }}
.pct {{ font-size: 13px; color: #8899aa; min-width: 40px; text-align: right; }}

/* BOTOES */
.botoes {{ display: flex; gap: 8px; padding: 10px 20px; background: #16213e; border-bottom: 1px solid #0f3460; flex-shrink: 0; }}
.btn {{ padding: 8px 18px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; }}
.btn-anterior {{ background: #2a2a4a; color: #aaa; }}
.btn-anterior:hover {{ background: #3a3a5a; }}
.btn-conferido {{ background: #27ae60; color: #fff; }}
.btn-conferido:hover {{ background: #2ecc71; }}
.btn-problema {{ background: #e74c3c; color: #fff; }}
.btn-problema:hover {{ background: #c0392b; }}
.btn-pular {{ background: #f39c12; color: #fff; }}
.btn-pular:hover {{ background: #e67e22; }}
.btn-lista {{ background: #3498db; color: #fff; margin-left: auto; }}
.btn-lista:hover {{ background: #2980b9; }}
.atalho {{ font-size: 10px; opacity: 0.7; margin-left: 4px; }}

/* CONTEUDO PRINCIPAL */
.conteudo {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}

/* ZONA 1 — AFIRMACAO */
.zona-afirmacao {{ background: #16213e; padding: 16px 20px; border-bottom: 2px solid #e94560; flex-shrink: 0; }}
.secao-label {{ font-size: 11px; text-transform: uppercase; color: #e94560; letter-spacing: 1px; margin-bottom: 6px; }}
.trecho {{ font-size: 16px; line-height: 1.6; color: #fff; }}
.dado-destaque {{ background: #e94560; color: #fff; padding: 1px 6px; border-radius: 3px; font-weight: 600; }}
.fontes-info {{ margin-top: 10px; font-size: 12px; color: #8899aa; }}
.fonte-item {{ margin-top: 4px; padding: 4px 8px; background: #0f3460; border-radius: 4px; border-left: 3px solid #3498db; }}
.alerta-item {{ margin-top: 4px; padding: 4px 8px; background: #4a2020; border-radius: 4px; border-left: 3px solid #e74c3c; color: #ff9999; }}
.status-badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-left: 8px; }}
.status-confirmado {{ background: #27ae60; color: #fff; }}
.status-divergente {{ background: #e74c3c; color: #fff; }}
.status-pendente {{ background: #f39c12; color: #fff; }}

/* ZONA 2 — TEXTO DO PROCESSO */
.zona-texto {{ flex: 1; overflow-y: auto; background: #0d1117; padding: 0; font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace; font-size: 13px; line-height: 1.5; }}
.linha-texto {{ display: flex; padding: 1px 12px; }}
.linha-texto:hover {{ background: #161b22; }}
.linha-num {{ color: #484f58; min-width: 50px; text-align: right; padding-right: 12px; user-select: none; border-right: 1px solid #21262d; margin-right: 12px; }}
.linha-conteudo {{ color: #c9d1d9; white-space: pre-wrap; word-break: break-word; flex: 1; }}
.linha-destaque {{ background: #3b2e00 !important; }}
.linha-destaque .linha-num {{ color: #f0c000; font-weight: 700; }}
.linha-destaque .linha-conteudo {{ color: #fff; }}
.linha-marcador {{ border-left: 3px solid #f0c000; }}

/* ZONA 3 — NOTAS */
.zona-notas {{ background: #16213e; padding: 10px 20px; border-top: 1px solid #0f3460; flex-shrink: 0; }}
.zona-notas textarea {{ width: 100%; height: 50px; background: #0d1117; border: 1px solid #0f3460; color: #e0e0e0; border-radius: 6px; padding: 8px; font-size: 13px; resize: vertical; font-family: inherit; }}
.zona-notas label {{ font-size: 11px; color: #8899aa; margin-bottom: 4px; display: block; }}

/* SIDEBAR */
.sidebar-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: none; }}
.sidebar-overlay.aberto {{ display: block; }}
.sidebar {{ position: fixed; right: 0; top: 0; bottom: 0; width: 360px; background: #16213e; z-index: 101; transform: translateX(100%); transition: transform 0.3s ease; overflow-y: auto; padding: 16px; }}
.sidebar-overlay.aberto .sidebar {{ transform: translateX(0); }}
.sidebar-titulo {{ font-size: 16px; font-weight: 700; color: #e94560; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #0f3460; }}
.sidebar-item {{ padding: 8px 10px; margin-bottom: 4px; border-radius: 6px; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; transition: background 0.2s; }}
.sidebar-item:hover {{ background: #1a2a4a; }}
.sidebar-item.atual {{ background: #0f3460; border-left: 3px solid #e94560; }}
.sidebar-icone {{ font-size: 16px; min-width: 20px; text-align: center; }}

/* TELA FINAL */
.tela-final {{ display: none; flex: 1; justify-content: center; align-items: center; flex-direction: column; padding: 40px; text-align: center; }}
.tela-final.visivel {{ display: flex; }}
.tela-final h2 {{ font-size: 28px; color: #27ae60; margin-bottom: 20px; }}
.contadores {{ display: flex; gap: 24px; margin: 20px 0; }}
.contador {{ text-align: center; }}
.contador .num {{ font-size: 36px; font-weight: 700; }}
.contador .label {{ font-size: 12px; color: #8899aa; }}
.obs-lista {{ text-align: left; margin-top: 20px; max-width: 500px; width: 100%; }}
.obs-item {{ padding: 8px; margin-bottom: 4px; background: #0f3460; border-radius: 4px; font-size: 13px; }}
</style>
</head>
<body>

<!-- BARRA DE PROGRESSO -->
<div class="barra-topo">
  <span class="titulo">VERIFICACAO</span>
  <span class="passo" id="indicadorPasso">1 de {total}</span>
  <div class="progresso-container"><div class="progresso-fill" id="barraProgresso" style="width:0%"></div></div>
  <span class="pct" id="pctTexto">0%</span>
</div>

<!-- BOTOES -->
<div class="botoes" id="painelBotoes">
  <button class="btn btn-anterior" id="btnAnterior" onclick="navegarAnterior()">Anterior <span class="atalho">[&larr;]</span></button>
  <button class="btn btn-conferido" id="btnConferido" onclick="marcar('conferido')">Conferido <span class="atalho">[Enter]</span></button>
  <button class="btn btn-problema" id="btnProblema" onclick="marcar('problema')">Problema <span class="atalho">[P]</span></button>
  <button class="btn btn-pular" id="btnPular" onclick="marcar('pulado')">Pular <span class="atalho">[&rarr;]</span></button>
  <button class="btn btn-lista" id="btnLista" onclick="toggleSidebar()">Sumario <span class="atalho">[S]</span></button>
</div>

<!-- CONTEUDO -->
<div class="conteudo" id="conteudoPrincipal">
  <!-- ZONA 1 -->
  <div class="zona-afirmacao" id="zonaAfirmacao"></div>
  <!-- ZONA 2 -->
  <div class="zona-texto" id="zonaTexto"></div>
  <!-- ZONA 3 -->
  <div class="zona-notas">
    <label for="campoNotas">Anotacoes (salvas automaticamente):</label>
    <textarea id="campoNotas" placeholder="Observacoes sobre este item..." oninput="salvarNota()"></textarea>
  </div>
</div>

<!-- TELA FINAL -->
<div class="tela-final" id="telaFinal">
  <h2 id="tituloFinal">Verificacao Concluida</h2>
  <div class="contadores" id="contadores"></div>
  <div class="obs-lista" id="obsLista"></div>
  <div style="margin-top:20px">
    <button class="btn btn-lista" onclick="reiniciar()">Revisar novamente</button>
  </div>
</div>

<!-- SIDEBAR -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="fecharSidebar(event)">
  <div class="sidebar" id="sidebarConteudo">
    <div class="sidebar-titulo">Sumario de Verificacao</div>
    <div id="sidebarLista"></div>
  </div>
</div>

<script>
// ===== DADOS EMBUTIDOS =====
var TEXTO_PROCESSO = [
{texto_js_array}
];

var AFIRMACOES = {afirmacoes_js};

var PROCESSO = '{escapar_js_string(processo)}';
var TOTAL = AFIRMACOES.length;
var STORAGE_KEY = 'verificacao_guiada_' + PROCESSO;

// ===== ESTADO =====
var passoAtual = 0;
var estado = carregarEstado();

function carregarEstado() {{
  try {{
    var salvo = localStorage.getItem(STORAGE_KEY);
    if (salvo) return JSON.parse(salvo);
  }} catch(e) {{}}
  return {{ decisoes: {{}}, notas: {{}}, passoAtual: 0 }};
}}

function salvarEstado() {{
  estado.passoAtual = passoAtual;
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(estado)); }} catch(e) {{}}
}}

// ===== RENDERIZACAO COM DOM SEGURO =====

function criarElemento(tag, classes, texto) {{
  var el = document.createElement(tag);
  if (classes) el.className = classes;
  if (texto) el.textContent = texto;
  return el;
}}

function renderizarAfirmacao(af) {{
  var zona = document.getElementById('zonaAfirmacao');
  while (zona.firstChild) zona.removeChild(zona.firstChild);

  // Secao label
  var secLabel = criarElemento('div', 'secao-label', af.secao);
  // Badge de status original
  var badge = criarElemento('span', 'status-badge status-' + af.status_original, af.status_original);
  secLabel.appendChild(document.createTextNode(' '));
  secLabel.appendChild(badge);
  zona.appendChild(secLabel);

  // Trecho da peticao
  var trechoDiv = criarElemento('div', 'trecho');
  // Destacar dados verificaveis no trecho
  var textoTrecho = af.trecho;
  if (af.dados && af.dados.length > 0) {{
    var fragmento = document.createDocumentFragment();
    var textoRestante = textoTrecho;
    var partes = [];
    // Encontrar posicoes de dados no texto
    af.dados.forEach(function(dado) {{
      var pos = textoRestante.indexOf(dado);
      if (pos >= 0) {{
        if (pos > 0) partes.push({{ tipo: 'texto', valor: textoRestante.substring(0, pos) }});
        partes.push({{ tipo: 'destaque', valor: dado }});
        textoRestante = textoRestante.substring(pos + dado.length);
      }}
    }});
    if (textoRestante) partes.push({{ tipo: 'texto', valor: textoRestante }});

    if (partes.length > 0) {{
      partes.forEach(function(p) {{
        if (p.tipo === 'destaque') {{
          var span = criarElemento('span', 'dado-destaque', p.valor);
          fragmento.appendChild(span);
        }} else {{
          fragmento.appendChild(document.createTextNode(p.valor));
        }}
      }});
      trechoDiv.appendChild(fragmento);
    }} else {{
      trechoDiv.textContent = textoTrecho;
    }}
  }} else {{
    trechoDiv.textContent = textoTrecho;
  }}
  zona.appendChild(trechoDiv);

  // Fontes
  if (af.fontes && af.fontes.length > 0) {{
    var fontesDiv = criarElemento('div', 'fontes-info', 'Fontes encontradas:');
    af.fontes.forEach(function(f) {{
      var fItem = criarElemento('div', 'fonte-item');
      var locSpan = criarElemento('strong', null, f.localizacao);
      fItem.appendChild(locSpan);
      fItem.appendChild(document.createTextNode(' — ' + f.trecho));
      fontesDiv.appendChild(fItem);
    }});
    zona.appendChild(fontesDiv);
  }}

  // Alertas
  if (af.alertas && af.alertas.length > 0) {{
    af.alertas.forEach(function(a) {{
      var aDiv = criarElemento('div', 'alerta-item', 'ALERTA: ' + a);
      zona.appendChild(aDiv);
    }});
  }}
}}

function renderizarTexto(af) {{
  var zona = document.getElementById('zonaTexto');
  while (zona.firstChild) zona.removeChild(zona.firstChild);

  var linhasRef = af.linhas_ref || [];
  if (linhasRef.length === 0) {{
    var aviso = criarElemento('div', 'linha-texto');
    aviso.style.padding = '20px';
    aviso.style.color = '#8899aa';
    aviso.textContent = 'Nenhuma linha especifica referenciada. Confira o texto completo abaixo.';
    zona.appendChild(aviso);
    // Mostrar primeiras 50 linhas como contexto
    renderizarBlocoLinhas(zona, 0, Math.min(50, TEXTO_PROCESSO.length), []);
    return;
  }}

  // Para cada linha referenciada, mostrar contexto de +/- 10 linhas
  var blocos = [];
  linhasRef.forEach(function(numLinha) {{
    var inicio = Math.max(0, numLinha - 11); // -10 linhas (0-indexed = numLinha-1-10)
    var fim = Math.min(TEXTO_PROCESSO.length, numLinha + 10);
    blocos.push({{ inicio: inicio, fim: fim, ref: numLinha }});
  }});

  // Mesclar blocos sobrepostos
  blocos.sort(function(a, b) {{ return a.inicio - b.inicio; }});
  var mesclados = [blocos[0]];
  for (var i = 1; i < blocos.length; i++) {{
    var ult = mesclados[mesclados.length - 1];
    if (blocos[i].inicio <= ult.fim + 3) {{
      ult.fim = Math.max(ult.fim, blocos[i].fim);
    }} else {{
      mesclados.push(blocos[i]);
    }}
  }}

  mesclados.forEach(function(bloco, idx) {{
    if (idx > 0) {{
      var sep = criarElemento('div', 'linha-texto');
      sep.style.padding = '8px 12px';
      sep.style.color = '#484f58';
      sep.style.borderTop = '1px dashed #21262d';
      sep.style.borderBottom = '1px dashed #21262d';
      sep.textContent = '...';
      zona.appendChild(sep);
    }}
    renderizarBlocoLinhas(zona, bloco.inicio, bloco.fim, linhasRef);
  }});

  // Scroll para a primeira linha destacada
  setTimeout(function() {{
    var dest = zona.querySelector('.linha-destaque');
    if (dest) dest.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}, 100);
}}

function renderizarBlocoLinhas(container, inicio, fim, linhasRef) {{
  for (var i = inicio; i < fim; i++) {{
    var numLinha = i + 1; // linhas sao 1-indexed
    var div = document.createElement('div');
    div.className = 'linha-texto';
    if (linhasRef.indexOf(numLinha) >= 0) {{
      div.className += ' linha-destaque linha-marcador';
    }}

    var numSpan = criarElemento('span', 'linha-num', String(numLinha));
    var contSpan = criarElemento('span', 'linha-conteudo', TEXTO_PROCESSO[i] || '');
    div.appendChild(numSpan);
    div.appendChild(contSpan);
    container.appendChild(div);
  }}
}}

function renderizarSidebar() {{
  var lista = document.getElementById('sidebarLista');
  while (lista.firstChild) lista.removeChild(lista.firstChild);

  AFIRMACOES.forEach(function(af, idx) {{
    var item = document.createElement('div');
    item.className = 'sidebar-item';
    if (idx === passoAtual) item.className += ' atual';

    var icone = criarElemento('span', 'sidebar-icone');
    var decisao = estado.decisoes[idx];
    if (decisao === 'conferido') icone.textContent = 'V';
    else if (decisao === 'problema') icone.textContent = 'X';
    else if (decisao === 'pulado') icone.textContent = '>';
    else icone.textContent = 'O';

    if (decisao === 'conferido') icone.style.color = '#27ae60';
    else if (decisao === 'problema') icone.style.color = '#e74c3c';
    else if (decisao === 'pulado') icone.style.color = '#f39c12';
    else icone.style.color = '#484f58';

    var texto = criarElemento('span', null);
    texto.textContent = af.idx + '. ' + af.trecho.substring(0, 60);
    if (af.trecho.length > 60) texto.textContent += '...';

    item.appendChild(icone);
    item.appendChild(texto);
    item.setAttribute('data-idx', idx);
    item.addEventListener('click', function() {{
      passoAtual = idx;
      mostrarPasso();
      fecharSidebarDireto();
    }});

    lista.appendChild(item);
  }});
}}

// ===== NAVEGACAO =====

function mostrarPasso() {{
  if (passoAtual >= TOTAL) {{
    mostrarTelaFinal();
    return;
  }}

  document.getElementById('conteudoPrincipal').style.display = 'flex';
  document.getElementById('telaFinal').className = 'tela-final';
  document.getElementById('painelBotoes').style.display = 'flex';

  var af = AFIRMACOES[passoAtual];
  renderizarAfirmacao(af);
  renderizarTexto(af);

  // Atualizar indicadores
  var conferidos = contarDecisoes();
  var pct = Math.round((conferidos.total / TOTAL) * 100);
  document.getElementById('indicadorPasso').textContent = (passoAtual + 1) + ' de ' + TOTAL;
  document.getElementById('barraProgresso').style.width = pct + '%';
  document.getElementById('pctTexto').textContent = pct + '%';

  // Restaurar nota
  document.getElementById('campoNotas').value = estado.notas[passoAtual] || '';

  salvarEstado();
}}

function navegarAnterior() {{
  if (passoAtual > 0) {{
    passoAtual--;
    mostrarPasso();
  }}
}}

function marcar(decisao) {{
  estado.decisoes[passoAtual] = decisao;
  salvarEstado();
  passoAtual++;
  mostrarPasso();
}}

function salvarNota() {{
  estado.notas[passoAtual] = document.getElementById('campoNotas').value;
  salvarEstado();
}}

function contarDecisoes() {{
  var c = 0, p = 0, s = 0;
  for (var k in estado.decisoes) {{
    if (estado.decisoes[k] === 'conferido') c++;
    else if (estado.decisoes[k] === 'problema') p++;
    else if (estado.decisoes[k] === 'pulado') s++;
  }}
  return {{ conferidos: c, problemas: p, pulados: s, total: c + p + s }};
}}

function mostrarTelaFinal() {{
  document.getElementById('conteudoPrincipal').style.display = 'none';
  document.getElementById('painelBotoes').style.display = 'none';
  var tela = document.getElementById('telaFinal');
  tela.className = 'tela-final visivel';

  var contagem = contarDecisoes();

  // Titulo
  var titulo = document.getElementById('tituloFinal');
  if (contagem.problemas > 0) {{
    titulo.textContent = 'Verificacao Concluida — ' + contagem.problemas + ' problema(s) encontrado(s)';
    titulo.style.color = '#e74c3c';
  }} else {{
    titulo.textContent = 'Verificacao Concluida — Tudo conferido!';
    titulo.style.color = '#27ae60';
  }}

  // Contadores
  var divContadores = document.getElementById('contadores');
  while (divContadores.firstChild) divContadores.removeChild(divContadores.firstChild);

  var dados = [
    {{ num: contagem.conferidos, label: 'Conferidos', cor: '#27ae60' }},
    {{ num: contagem.problemas, label: 'Problemas', cor: '#e74c3c' }},
    {{ num: contagem.pulados, label: 'Pulados', cor: '#f39c12' }}
  ];
  dados.forEach(function(d) {{
    var cont = criarElemento('div', 'contador');
    var numEl = criarElemento('div', 'num', String(d.num));
    numEl.style.color = d.cor;
    var labEl = criarElemento('div', 'label', d.label);
    cont.appendChild(numEl);
    cont.appendChild(labEl);
    divContadores.appendChild(cont);
  }});

  // Observacoes de problemas
  var obsDiv = document.getElementById('obsLista');
  while (obsDiv.firstChild) obsDiv.removeChild(obsDiv.firstChild);

  for (var k in estado.decisoes) {{
    if (estado.decisoes[k] === 'problema') {{
      var idx = parseInt(k);
      var af = AFIRMACOES[idx];
      var item = criarElemento('div', 'obs-item');
      var strong = criarElemento('strong', null, '#' + af.idx + ': ');
      item.appendChild(strong);
      item.appendChild(document.createTextNode(af.trecho.substring(0, 80)));
      if (estado.notas[k]) {{
        var nota = criarElemento('div', null, 'Nota: ' + estado.notas[k]);
        nota.style.color = '#f39c12';
        nota.style.marginTop = '4px';
        nota.style.fontSize = '12px';
        item.appendChild(nota);
      }}
      obsDiv.appendChild(item);
    }}
  }}

  // Atualizar barra
  document.getElementById('barraProgresso').style.width = '100%';
  document.getElementById('pctTexto').textContent = '100%';
  document.getElementById('indicadorPasso').textContent = 'Concluido';
}}

function reiniciar() {{
  passoAtual = 0;
  mostrarPasso();
}}

// ===== SIDEBAR =====

function toggleSidebar() {{
  var overlay = document.getElementById('sidebarOverlay');
  if (overlay.classList.contains('aberto')) {{
    overlay.classList.remove('aberto');
  }} else {{
    renderizarSidebar();
    overlay.classList.add('aberto');
  }}
}}

function fecharSidebar(e) {{
  if (e.target === document.getElementById('sidebarOverlay')) {{
    document.getElementById('sidebarOverlay').classList.remove('aberto');
  }}
}}

function fecharSidebarDireto() {{
  document.getElementById('sidebarOverlay').classList.remove('aberto');
}}

// ===== ATALHOS DE TECLADO =====

document.addEventListener('keydown', function(e) {{
  // Ignorar se estiver digitando notas
  if (e.target.tagName === 'TEXTAREA') return;

  switch(e.key) {{
    case 'Enter':
      e.preventDefault();
      marcar('conferido');
      break;
    case 'p':
    case 'P':
      e.preventDefault();
      marcar('problema');
      break;
    case 'ArrowRight':
      e.preventDefault();
      marcar('pulado');
      break;
    case 'ArrowLeft':
      e.preventDefault();
      navegarAnterior();
      break;
    case 's':
    case 'S':
      e.preventDefault();
      toggleSidebar();
      break;
    case 'Escape':
      fecharSidebarDireto();
      break;
  }}
}});

// ===== INICIALIZACAO =====
passoAtual = estado.passoAtual || 0;
mostrarPasso();
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='Gera HTML de verificação guiada')
    parser.add_argument('--json', required=True, help='Caminho do JSON de verificação')
    parser.add_argument('--texto', required=True, help='Caminho do TEXTO-EXTRAIDO.txt')
    parser.add_argument('--output', required=True, help='Caminho de saída do HTML')
    args = parser.parse_args()

    # Ler JSON
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ler texto do processo
    with open(args.texto, 'r', encoding='utf-8') as f:
        linhas_texto = f.read().splitlines()

    processo = data.get('processo', os.path.basename(os.path.dirname(args.json)))

    # Gerar HTML
    html_content = gerar_html(data, linhas_texto, processo)

    # Salvar
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Verificação guiada gerada: {args.output}")
    total = len(preparar_afirmacoes(data))
    print(f"  {total} afirmações para verificar")
    print(f"  {len(linhas_texto)} linhas do processo embutidas")
    tamanho = os.path.getsize(args.output)
    print(f"  Tamanho: {tamanho / 1024:.0f} KB")


if __name__ == '__main__':
    main()
