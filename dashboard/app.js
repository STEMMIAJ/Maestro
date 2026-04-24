// Maestro dashboard - app.js
// Vanilla JS. Consome ./data.json gerado pelo T-DB (exportar_dashboard.py).
// Monta DOM via createElement/textContent (sem innerHTML) para evitar XSS.

(function () {
  "use strict";

  var estado = {
    recentes: [],
    recentesFiltrado: []
  };

  function $(id) {
    return document.getElementById(id);
  }

  function mostrarBanner(msg) {
    var b = $("banner-erro");
    b.textContent = msg;
    b.hidden = false;
  }

  function formatarTimestamp(ts) {
    if (!ts) return "-";
    try {
      var d = new Date(ts);
      if (isNaN(d.getTime())) return String(ts);
      var pad = function (n) { return n < 10 ? "0" + n : String(n); };
      return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
        " " + pad(d.getHours()) + ":" + pad(d.getMinutes());
    } catch (e) {
      return String(ts);
    }
  }

  function classeUrgencia(u) {
    if (u === null || u === undefined) return "badge badge-neutro";
    var s = String(u).toLowerCase();
    if (s === "urgente" || s === "alta" || s === "high" || s === "critica" || s === "critico") {
      return "badge badge-urgente";
    }
    if (s === "media" || s === "medio" || s === "alerta" || s === "medium") {
      return "badge badge-alerta";
    }
    if (s === "baixa" || s === "ok" || s === "normal" || s === "low") {
      return "badge badge-ok";
    }
    return "badge badge-neutro";
  }

  function preencherCards(resumo) {
    resumo = resumo || {};
    $("card-total").textContent = resumo.total_processos != null ? resumo.total_processos : "0";
    $("card-urgentes").textContent = resumo.urgentes != null ? resumo.urgentes : "0";
    $("card-tarefas").textContent = resumo.tarefas_prazo_7d != null ? resumo.tarefas_prazo_7d : "0";
    $("card-heartbeat").textContent = formatarTimestamp(resumo.ultimo_heartbeat_ts);
  }

  function criarCel(tag, texto, classe, estilo) {
    var el = document.createElement(tag);
    if (classe) el.className = classe;
    if (estilo) el.setAttribute("style", estilo);
    if (texto !== undefined && texto !== null) el.textContent = texto;
    return el;
  }

  function limparFilhos(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function renderizarTabela(lista) {
    var tbody = $("tabela-body");
    limparFilhos(tbody);

    if (!lista || lista.length === 0) {
      var trVazio = document.createElement("tr");
      var tdVazio = criarCel("td", "Nenhum processo no banco ainda.", "vazio");
      tdVazio.setAttribute("colspan", "5");
      trVazio.appendChild(tdVazio);
      tbody.appendChild(trVazio);
      return;
    }

    for (var i = 0; i < lista.length; i++) {
      var p = lista[i];
      var tr = document.createElement("tr");

      tr.appendChild(criarCel("td", p.cnj || "", null, "font-family:ui-monospace,monospace;font-size:0.85rem;"));
      tr.appendChild(criarCel("td", p.comarca || "-"));

      var tdUrg = document.createElement("td");
      var span = criarCel("span", p.urgencia || "-", classeUrgencia(p.urgencia));
      tdUrg.appendChild(span);
      tr.appendChild(tdUrg);

      tr.appendChild(criarCel("td", formatarTimestamp(p.updated_at)));

      var tdFicha = document.createElement("td");
      if (p.ficha_path) {
        var a = document.createElement("a");
        a.className = "link-ficha";
        a.href = p.ficha_path;
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = "abrir";
        tdFicha.appendChild(a);
      } else {
        var dash = criarCel("span", "-", null, "color:#bbb;");
        tdFicha.appendChild(dash);
      }
      tr.appendChild(tdFicha);

      tbody.appendChild(tr);
    }
  }

  function aplicarFiltro(termo) {
    var t = (termo || "").trim().toLowerCase();
    if (!t) {
      estado.recentesFiltrado = estado.recentes;
    } else {
      estado.recentesFiltrado = estado.recentes.filter(function (p) {
        var cnj = String(p.cnj || "").toLowerCase();
        return cnj.indexOf(t) !== -1;
      });
    }
    renderizarTabela(estado.recentesFiltrado);
  }

  function bindBusca() {
    var input = $("busca");
    if (!input) return;
    input.addEventListener("input", function (ev) {
      aplicarFiltro(ev.target.value);
    });
  }

  function bootstrap(data) {
    if (data && data.placeholder) {
      mostrarBanner("Indexador ainda nao rodou. Execute indexer_ficha.py + exportar_dashboard.py.");
    }

    preencherCards(data && data.resumo ? data.resumo : {});

    estado.recentes = (data && Array.isArray(data.recentes)) ? data.recentes : [];
    estado.recentesFiltrado = estado.recentes;
    renderizarTabela(estado.recentesFiltrado);

    $("gerado-em").textContent = (data && data.gerado_em) ? formatarTimestamp(data.gerado_em) : "-";
  }

  function carregar() {
    bindBusca();
    fetch("./data.json", { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) {
          throw new Error("HTTP " + r.status);
        }
        return r.json();
      })
      .then(function (data) {
        bootstrap(data);
      })
      .catch(function (err) {
        mostrarBanner("Indexador ainda nao rodou. Execute indexer_ficha.py + exportar_dashboard.py. (" + err.message + ")");
        preencherCards({});
        renderizarTabela([]);
        $("gerado-em").textContent = "-";
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", carregar);
  } else {
    carregar();
  }
})();
