#!/usr/bin/env python3
"""
Baixa documentos avulsos do processo PJe ja aberto no Chrome.

Uso urgente:
  python baixar_documentos_processo_aberto.py --cnj 5030880-86.2024.8.13.0105

Premissa:
  O Chrome do Windows/Parallels precisa estar aberto com remote debugging.
  O usuario deve deixar a pagina de autos/documentos do processo visivel.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from contextlib import suppress
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import Error as PlaywrightError, async_playwright
except ImportError:
    print("Playwright nao instalado. Rode: python -m pip install playwright")
    sys.exit(1)


DEFAULT_HOSTS = "127.0.0.1,10.211.55.3"
DEFAULT_PORTS = "9223,9222"
CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
DOC_ID_RE = re.compile(r"\b\d{6,12}\b")
MIN_BYTES = 900

HOME = Path(os.environ.get("USERPROFILE", str(Path.home())))
DEFAULT_DOWNLOAD_DIR = HOME / "Desktop" / "processos-pje" / "documentos-processo-aberto"

_logs = []


CANDIDATE_JS = r"""
({ includeAll }) => {
  const norm = (s) => (s || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();

  const visible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style && style.visibility !== "hidden" && style.display !== "none" &&
      rect.width > 0 && rect.height > 0;
  };

  const attrs = (el) => {
    if (!el) return "";
    const names = ["id", "class", "title", "aria-label", "href", "onclick", "name", "value", "src"];
    const values = names.map((name) => {
      try {
        const v = name === "class" ? el.className : el.getAttribute(name);
        if (typeof v === "string") return v;
      } catch (_) {}
      return "";
    });
    values.push(el.innerText || el.textContent || "");
    return values.join(" ");
  };

  const clickTarget = (node) => {
    if (!node) return null;
    return node.closest("a,button,input,[onclick],[role='button']") || node;
  };

  const contextText = (el) => {
    let node = el;
    let fallback = clean((el.innerText || el.textContent || attrs(el) || "").slice(0, 500));
    for (let depth = 0; depth < 7 && node; depth += 1) {
      const text = clean(node.innerText || node.textContent || "");
      if (/\b\d{6,12}\b/.test(text) && text.length <= 900) return text;
      node = node.parentElement;
    }
    return fallback;
  };

  const hash = (s) => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16);
  };

  const titleFromContext = (ctx, docId) => {
    let title = clean(ctx);
    const m = title.match(new RegExp(docId + "\\s*[-–:]?\\s*([^\\n\\r]{0,160})"));
    if (m && m[1]) title = clean(`${docId} - ${m[1]}`);
    title = title.replace(/\b(documento|tipo|movimento|data da assinatura)\b/ig, " ");
    return clean(title).slice(0, 180) || docId;
  };

  const nodes = Array.from(document.querySelectorAll(
    "a,button,input[type='button'],input[type='submit'],[onclick],[role='button'],i,img,span"
  ));
  const seen = new Set();
  const out = [];

  for (const node of nodes) {
    const el = clickTarget(node);
    if (!el || seen.has(el) || !visible(el)) continue;
    seen.add(el);

    const ctx = contextText(el);
    const blobRaw = `${attrs(el)} ${attrs(node)} ${ctx}`;
    const blob = norm(blobRaw);

    let docId = "";
    const idMatch = blobRaw.match(/\b\d{6,12}\b/);
    if (idMatch) docId = idMatch[0];
    if (!docId) continue;

    const negative = /(fixar|pin|pino|favorit|bookmark|clipboard|copiar|copiado|selecionar|checkbox|marcar|expandir|recolher)/.test(blob);
    if (negative) continue;

    const positive = /(download|baixar|visualizar|abrir|documento|pje-bin|processodocumento|idprocessodocumento|iddocumento|pdf|file-pdf|fa-file|glyphicon-file|icone-doc|documentos)/.test(blob);
    const tag = (el.tagName || "").toLowerCase();
    const isTextLink = tag === "a" && ctx.length < 900;
    if (!includeAll && !positive && !isTextLink) continue;

    const href = el.href || el.getAttribute("href") || "";
    const onclick = el.getAttribute("onclick") || "";
    const title = titleFromContext(ctx, docId);
    const keyBase = [docId, title, href, onclick, el.id || "", el.className || ""].join("|");
    const key = `${docId}-${hash(keyBase)}`;

    out.push({
      key,
      doc_id: docId,
      title,
      tag,
      href,
      score: (positive ? 2 : 0) + (isTextLink ? 1 : 0),
      text: clean(ctx).slice(0, 260),
    });
  }

  const byKey = new Map();
  for (const item of out) {
    const dedupe = `${item.doc_id}|${norm(item.title)}`;
    const old = byKey.get(dedupe);
    if (!old || item.score > old.score) byKey.set(dedupe, item);
  }
  return Array.from(byKey.values());
}
"""


CLICK_CANDIDATE_JS = r"""
({ key, includeAll }) => {
  const norm = (s) => (s || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
  const visible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style && style.visibility !== "hidden" && style.display !== "none" &&
      rect.width > 0 && rect.height > 0;
  };
  const attrs = (el) => {
    if (!el) return "";
    const names = ["id", "class", "title", "aria-label", "href", "onclick", "name", "value", "src"];
    const values = names.map((name) => {
      try {
        const v = name === "class" ? el.className : el.getAttribute(name);
        if (typeof v === "string") return v;
      } catch (_) {}
      return "";
    });
    values.push(el.innerText || el.textContent || "");
    return values.join(" ");
  };
  const clickTarget = (node) => node ? (node.closest("a,button,input,[onclick],[role='button']") || node) : null;
  const contextText = (el) => {
    let node = el;
    let fallback = clean((el.innerText || el.textContent || attrs(el) || "").slice(0, 500));
    for (let depth = 0; depth < 7 && node; depth += 1) {
      const text = clean(node.innerText || node.textContent || "");
      if (/\b\d{6,12}\b/.test(text) && text.length <= 900) return text;
      node = node.parentElement;
    }
    return fallback;
  };
  const hash = (s) => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16);
  };
  const titleFromContext = (ctx, docId) => {
    let title = clean(ctx);
    const m = title.match(new RegExp(docId + "\\s*[-–:]?\\s*([^\\n\\r]{0,160})"));
    if (m && m[1]) title = clean(`${docId} - ${m[1]}`);
    title = title.replace(/\b(documento|tipo|movimento|data da assinatura)\b/ig, " ");
    return clean(title).slice(0, 180) || docId;
  };

  const nodes = Array.from(document.querySelectorAll(
    "a,button,input[type='button'],input[type='submit'],[onclick],[role='button'],i,img,span"
  ));
  const seen = new Set();
  for (const node of nodes) {
    const el = clickTarget(node);
    if (!el || seen.has(el) || !visible(el)) continue;
    seen.add(el);
    const ctx = contextText(el);
    const blobRaw = `${attrs(el)} ${attrs(node)} ${ctx}`;
    const blob = norm(blobRaw);
    const idMatch = blobRaw.match(/\b\d{6,12}\b/);
    if (!idMatch) continue;
    const docId = idMatch[0];
    if (/(fixar|pin|pino|favorit|bookmark|clipboard|copiar|copiado|selecionar|checkbox|marcar|expandir|recolher)/.test(blob)) continue;
    const positive = /(download|baixar|visualizar|abrir|documento|pje-bin|processodocumento|idprocessodocumento|iddocumento|pdf|file-pdf|fa-file|glyphicon-file|icone-doc|documentos)/.test(blob);
    const tag = (el.tagName || "").toLowerCase();
    const isTextLink = tag === "a" && ctx.length < 900;
    if (!includeAll && !positive && !isTextLink) continue;
    const title = titleFromContext(ctx, docId);
    const keyBase = [docId, title, el.href || el.getAttribute("href") || "", el.getAttribute("onclick") || "", el.id || "", el.className || ""].join("|");
    const itemKey = `${docId}-${hash(keyBase)}`;
    if (itemKey !== key) continue;
    el.scrollIntoView({ block: "center", inline: "center" });
    el.click();
    return { ok: true, doc_id: docId, title, tag };
  }
  return { ok: false, erro: "candidato nao encontrado na pagina atual" };
}
"""


PDF_URLS_JS = r"""
() => {
  const urls = [];
  const add = (raw) => {
    if (!raw) return;
    try {
      const url = new URL(raw, document.baseURI).href;
      const lower = url.toLowerCase();
      if (lower.includes(".pdf") || lower.includes("download") || lower.includes("documento")) urls.push(url);
    } catch (_) {}
  };
  for (const el of Array.from(document.querySelectorAll("embed[src],iframe[src],a[href]"))) {
    add(el.getAttribute("src") || el.getAttribute("href"));
  }
  return Array.from(new Set(urls));
}
"""


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower().strip()


def slug(texto, limite=90):
    texto = normalizar(texto)
    texto = re.sub(r"[^a-z0-9._-]+", "-", texto).strip("-")
    return (texto or "documento")[:limite].strip("-") or "documento"


def ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def log(msg, level="INFO", **fields):
    entry = {"timestamp": datetime.now().isoformat(), "level": level, "msg": msg}
    entry.update({k: v for k, v in fields.items() if v is not None})
    _logs.append(entry)
    prefix = {"OK": "[OK]", "ERR": "[ERRO]", "WARN": "[AVISO]", "DL": "[DL]", "WAIT": "[...]"} .get(level, "   ")
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {prefix} {msg}"
    if fields.get("arquivo"):
        line += f" -> {fields['arquivo']}"
    print(line, flush=True)


def parse_ports(raw):
    ports = []
    for part in str(raw).split(","):
        part = part.strip()
        if part:
            ports.append(int(part))
    if not ports:
        raise argparse.ArgumentTypeError("Informe ao menos uma porta")
    return ports


def parse_hosts(raw):
    hosts = [p.strip() for p in str(raw).split(",") if p.strip()]
    if not hosts:
        raise argparse.ArgumentTypeError("Informe ao menos um host")
    return hosts


def cdp_ativo(host, port):
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/json/version", timeout=2) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
        return "Browser" in body
    except Exception:
        return False


def cnj_digits(cnj):
    return re.sub(r"\D", "", cnj or "")


def arquivo_valido(path):
    try:
        return path.exists() and path.stat().st_size >= MIN_BYTES
    except OSError:
        return False


def pdf_valido(path):
    try:
        if not arquivo_valido(path):
            return False
        with path.open("rb") as f:
            return f.read(4) == b"%PDF"
    except OSError:
        return False


def destino_documento(download_dir, indice, item, ext=".pdf"):
    doc_id = item.get("doc_id") or "sem-id"
    title = item.get("title") or item.get("text") or doc_id
    name = f"{indice:04d}-{doc_id}-{slug(title)}{ext}"
    path = download_dir / name
    if not path.exists():
        return path
    return download_dir / f"{indice:04d}-{doc_id}-{slug(title)}-{ts()}{ext}"


def ja_existe(download_dir, doc_id):
    if not doc_id:
        return None
    for path in sorted(download_dir.glob(f"*-{doc_id}-*.pdf")):
        if pdf_valido(path):
            return path
    return None


async def conectar_cdp(pw, hosts, portas):
    for host in hosts:
        for port in portas:
            if not cdp_ativo(host, port):
                continue
            browser = await pw.chromium.connect_over_cdp(f"http://{host}:{port}")
            try:
                from pje_cdp import pick_context_by_url, PJE_URL_HINTS
                context = pick_context_by_url(browser, PJE_URL_HINTS) or (
                    browser.contexts[0] if browser.contexts else await browser.new_context(accept_downloads=True)
                )
            except ImportError:
                context = browser.contexts[0] if browser.contexts else await browser.new_context(accept_downloads=True)
            context.set_default_timeout(10_000)
            log(f"Conectado ao Chrome via CDP {host}:{port}", "OK")
            return browser, context
    raise RuntimeError("Chrome CDP nao encontrado. Abra o Chrome do Windows com --remote-debugging-port=9223.")


async def pagina_texto(page, limite=5000):
    try:
        text = await page.locator("body").inner_text(timeout=2500)
        return text[:limite]
    except Exception:
        return ""


async def escolher_pagina(context, cnj):
    pages = [p for p in context.pages if not p.is_closed()]
    alvo = cnj_digits(cnj)
    melhor = None
    for page in pages:
        url = page.url or ""
        text = await pagina_texto(page)
        blob = f"{url} {text}"
        if cnj and (cnj in blob or alvo in re.sub(r"\D", "", blob)):
            await page.bring_to_front()
            return page
        if "pje.tjmg.jus.br" in url and ("documento" in normalizar(blob) or "processo" in normalizar(blob)):
            melhor = page
    if melhor:
        await melhor.bring_to_front()
        return melhor
    if pages:
        await pages[-1].bring_to_front()
        return pages[-1]
    raise RuntimeError("Nenhuma aba aberta no Chrome CDP")


async def rolar_frame(frame):
    try:
        return await frame.evaluate(
            """async () => {
              const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
              let last = -1;
              for (let i = 0; i < 18; i += 1) {
                const height = Math.max(
                  document.body ? document.body.scrollHeight : 0,
                  document.documentElement ? document.documentElement.scrollHeight : 0
                );
                window.scrollTo(0, height);
                await sleep(180);
                if (height === last) break;
                last = height;
              }
              window.scrollTo(0, 0);
              return last;
            }"""
        )
    except Exception:
        return 0


async def coletar_candidatos(page, include_all=False, rolar=True):
    if rolar:
        for frame in page.frames:
            await rolar_frame(frame)

    candidatos = []
    seen = set()
    for frame_index, frame in enumerate(page.frames):
        with suppress(Exception):
            items = await frame.evaluate(CANDIDATE_JS, {"includeAll": include_all})
            for item in items or []:
                key = item.get("key")
                if not key or key in seen:
                    continue
                seen.add(key)
                item["frame_index"] = frame_index
                candidatos.append(item)
    candidatos.sort(key=lambda x: (x.get("doc_id") or "", x.get("title") or ""))
    return candidatos


async def salvar_debug(page, logs_dir, label):
    logs_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{ts()}-{slug(label)}"
    out = {}
    with suppress(Exception):
        png = logs_dir / f"{stem}.png"
        await page.screenshot(path=str(png), full_page=True)
        out["screenshot"] = str(png)
    with suppress(Exception):
        html = logs_dir / f"{stem}.html"
        html.write_text(await page.content(), encoding="utf-8")
        out["html"] = str(html)
    return out


async def response_para_arquivo(context, url, destino, timeout_s):
    if not url or not url.lower().startswith(("http://", "https://")):
        return False
    try:
        resp = await context.request.get(url, timeout=int(timeout_s * 1000))
        if not resp.ok:
            return False
        body = await resp.body()
        if len(body) < MIN_BYTES:
            return False
        destino.write_bytes(body)
        return pdf_valido(destino)
    except Exception:
        return False


async def tentar_salvar_de_pagina(context, page, destino, timeout_s):
    with suppress(Exception):
        await page.wait_for_load_state("domcontentloaded", timeout=min(8000, int(timeout_s * 1000)))

    if await response_para_arquivo(context, page.url, destino, timeout_s):
        return {"tipo": "url", "url": page.url}

    for frame in page.frames:
        with suppress(Exception):
            urls = await frame.evaluate(PDF_URLS_JS)
            for url in urls:
                if await response_para_arquivo(context, url, destino, timeout_s):
                    return {"tipo": "embed", "url": url}
    return None


async def clicar_e_capturar(context, page, item, destino, timeout_s, include_all):
    frame_index = item["frame_index"]
    frame = page.frames[frame_index]
    download_tasks = []
    pages_seen = {p for p in context.pages if not p.is_closed()}
    url_before = page.url

    async def watch_download(p):
        return await p.wait_for_event("download", timeout=int(timeout_s * 1000))

    download_tasks.append(asyncio.create_task(watch_download(page)))
    click_result = await frame.evaluate(
        CLICK_CANDIDATE_JS,
        {"key": item["key"], "includeAll": include_all},
    )
    if not click_result.get("ok"):
        raise RuntimeError(click_result.get("erro") or "falha ao clicar candidato")

    deadline = time.monotonic() + timeout_s
    new_pages_done = set()

    while time.monotonic() < deadline:
        for task in list(download_tasks):
            if not task.done():
                continue
            download_tasks.remove(task)
            download = task.result()
            await download.save_as(str(destino))
            if pdf_valido(destino):
                return {"tipo": "download", "suggested_filename": download.suggested_filename}
            raise RuntimeError("arquivo baixado nao e PDF valido")

        current_pages = {p for p in context.pages if not p.is_closed()}
        for new_page in current_pages - pages_seen:
            pages_seen.add(new_page)
            download_tasks.append(asyncio.create_task(watch_download(new_page)))

        for candidate_page in list(current_pages):
            if candidate_page in new_pages_done:
                continue
            if candidate_page == page:
                continue
            info = await tentar_salvar_de_pagina(context, candidate_page, destino, timeout_s)
            new_pages_done.add(candidate_page)
            with suppress(Exception):
                await candidate_page.close()
            if info and pdf_valido(destino):
                return info

        if page.url != url_before and await tentar_salvar_de_pagina(context, page, destino, 3):
            if pdf_valido(destino):
                return {"tipo": "pagina-atual", "url": page.url}

        await page.wait_for_timeout(500)

    for task in download_tasks:
        task.cancel()
    raise TimeoutError(f"download nao concluiu em {timeout_s}s")


def salvar_relatorio(path, report):
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def montar_parser():
    parser = argparse.ArgumentParser(
        description="Baixa documentos avulsos do processo aberto no PJe/Chrome CDP"
    )
    parser.add_argument("--cnj", default="5030880-86.2024.8.13.0105")
    parser.add_argument("--download-dir", default=str(DEFAULT_DOWNLOAD_DIR))
    parser.add_argument("--hosts", type=parse_hosts, default=parse_hosts(DEFAULT_HOSTS))
    parser.add_argument("--portas", type=parse_ports, default=parse_ports(DEFAULT_PORTS))
    parser.add_argument("--limite", type=int, default=0, help="0 = todos")
    parser.add_argument("--timeout-documento", type=int, default=35)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--incluir-todos", action="store_true", help="Inclui candidatos menos obvios")
    parser.add_argument("--sem-scroll", action="store_true")
    parser.add_argument("--nao-pular-existentes", action="store_true")
    return parser


async def executar(args):
    download_dir = Path(args.download_dir).expanduser()
    download_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = download_dir / "_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    relatorio = download_dir / f"relatorio-documentos-{ts()}.json"

    report = {
        "inicio": datetime.now().isoformat(),
        "cnj": args.cnj,
        "download_dir": str(download_dir),
        "dry_run": args.dry_run,
        "documentos": [],
    }

    print("=" * 72)
    print("  PJe - Baixar documentos avulsos do processo aberto")
    print("=" * 72)
    print(f"  CNJ:      {args.cnj}")
    print(f"  Destino:  {download_dir}")
    print(f"  Modo:     {'DRY-RUN' if args.dry_run else 'DOWNLOAD'}")
    print("=" * 72)

    pw = await async_playwright().start()
    browser = None
    exit_code = 0
    try:
        browser, context = await conectar_cdp(pw, args.hosts, args.portas)
        page = await escolher_pagina(context, args.cnj)
        log(f"Aba selecionada: {page.url}", "OK")

        candidatos = await coletar_candidatos(
            page,
            include_all=args.incluir_todos,
            rolar=not args.sem_scroll,
        )
        if args.limite:
            candidatos = candidatos[: args.limite]

        report["candidatos_encontrados"] = len(candidatos)
        log(f"{len(candidatos)} candidato(s) de documento encontrado(s)", "OK")

        if not candidatos:
            report["debug"] = await salvar_debug(page, logs_dir, "sem-candidatos")
            exit_code = 1
            return exit_code

        if args.dry_run:
            for i, item in enumerate(candidatos, 1):
                log(f"[DRY-RUN] {i:04d} {item['doc_id']} - {item['title']}", "OK")
                report["documentos"].append({"indice": i, "status": "dry-run", **item})
            return 0

        ok = 0
        pulados = 0
        erros = 0
        for i, item in enumerate(candidatos, 1):
            doc_id = item.get("doc_id")
            if not args.nao_pular_existentes:
                existente = ja_existe(download_dir, doc_id)
                if existente:
                    pulados += 1
                    log(f"Ja existe: {doc_id}", "OK", arquivo=str(existente))
                    report["documentos"].append({
                        "indice": i,
                        "status": "ja-existe",
                        "arquivo": str(existente),
                        **item,
                    })
                    salvar_relatorio(relatorio, report)
                    continue

            destino = destino_documento(download_dir, i, item)
            log(f"Baixando {i:04d}/{len(candidatos)}: {doc_id} - {item.get('title')}", "DL")
            t0 = time.monotonic()
            try:
                info = await clicar_e_capturar(
                    context=context,
                    page=page,
                    item=item,
                    destino=destino,
                    timeout_s=args.timeout_documento,
                    include_all=args.incluir_todos,
                )
                kb = destino.stat().st_size // 1024
                ok += 1
                log(f"Salvo: {destino.name} ({kb} KB)", "OK", arquivo=str(destino))
                report["documentos"].append({
                    "indice": i,
                    "status": "ok",
                    "arquivo": str(destino),
                    "kb": kb,
                    "tempo_s": round(time.monotonic() - t0, 1),
                    "captura": info,
                    **item,
                })
            except Exception as exc:
                erros += 1
                with suppress(Exception):
                    if destino.exists() and not pdf_valido(destino):
                        destino.unlink()
                debug = await salvar_debug(page, logs_dir, f"erro-{doc_id or i}")
                log(f"Erro no documento {doc_id}: {exc}", "ERR")
                report["documentos"].append({
                    "indice": i,
                    "status": "erro",
                    "erro": str(exc),
                    "debug": debug,
                    "tempo_s": round(time.monotonic() - t0, 1),
                    **item,
                })
            finally:
                salvar_relatorio(relatorio, report)
                with suppress(Exception):
                    await page.bring_to_front()
                await page.wait_for_timeout(300)

        report["contadores"] = {"ok": ok, "ja_existe": pulados, "erros": erros}
        exit_code = 2 if erros else 0
        return exit_code

    except Exception as exc:
        report["fatal"] = str(exc)
        log(f"Erro fatal: {exc}", "ERR")
        exit_code = 1
        return exit_code
    finally:
        report["fim"] = datetime.now().isoformat()
        report["log"] = _logs
        salvar_relatorio(relatorio, report)
        print("=" * 72)
        print("  CONCLUIDO")
        print(f"  Relatorio: {relatorio}")
        print("=" * 72)
        with suppress(Exception):
            if browser:
                await browser.close()
        await pw.stop()


def main():
    parser = montar_parser()
    args = parser.parse_args()
    return asyncio.run(executar(args))


if __name__ == "__main__":
    raise SystemExit(main())
