"""Buscador no JusBrasil Diários — focado em comarcas próximas de Gov. Valadares."""

import re
import asyncio
import random
import logging
from urllib.parse import quote_plus
from playwright.async_api import async_playwright, Page
from config import (
    USER_AGENTS, TIMEOUT_PAGINA, COMARCAS_200KM,
    TERMOS_COMARCA, TERMOS_DJMG,
)
from models import Oportunidade

logger = logging.getLogger(__name__)

JS_EXTRACT = """() => {
    const results = [];
    const links = document.querySelectorAll('a[href*="/diarios/"]');
    const seen = new Set();
    for (const link of links) {
        const href = link.href;
        if (seen.has(href)) continue;
        if (!href.includes('/diarios/') || href.includes('/diarios/busca')) continue;
        seen.add(href);
        const container = link.closest('div, article, li') || link.parentElement;
        const text = container ? container.innerText.substring(0, 1000) : link.innerText;
        const title = link.innerText.trim().substring(0, 300);
        if (title.length > 5) {
            results.push({url: href, titulo: title, trecho: text.substring(0, 500)});
        }
    }
    return results;
}"""


class BuscadorJusBrasil:
    nome = "jusbrasil"

    async def buscar_todos(self) -> list[Oportunidade]:
        """Busca em duas fases: termos genéricos com DJMG + termos por comarca."""
        resultados = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 720},
            )
            page = await context.new_page()
            page.set_default_timeout(TIMEOUT_PAGINA * 1000)

            # Fase 1: Termos genéricos com DJMG
            logger.info("=== Fase 1: Termos genéricos DJMG ===")
            for cat, termo in TERMOS_DJMG:
                encontrados = await self._buscar_termo(page, cat, termo)
                resultados.extend(encontrados)
                await asyncio.sleep(random.uniform(2, 4))

            # Fase 2: Termos por comarca (2 termos mais eficazes x 32 comarcas)
            logger.info("=== Fase 2: Busca por comarca ===")
            termos_top = TERMOS_COMARCA[:2]  # Só os 2 mais produtivos
            cloudflare_hits = 0

            for comarca in COMARCAS_200KM:
                for cat, termo in termos_top:
                    busca = f'{termo} "{comarca}"'
                    encontrados = await self._buscar_termo(
                        page, cat, busca, comarca_hint=comarca
                    )
                    resultados.extend(encontrados)

                    # Delay maior entre buscas para evitar Cloudflare
                    await asyncio.sleep(random.uniform(4, 8))

                    # Detectar Cloudflare
                    try:
                        title = await page.title()
                        if "moment" in title.lower():
                            cloudflare_hits += 1
                            logger.warning(f"Cloudflare #{cloudflare_hits}. Pausando 30s...")
                            await asyncio.sleep(30)

                            # Recriar contexto do browser para resetar cookies
                            await browser.close()
                            browser = await p.chromium.launch(headless=True)
                            context = await browser.new_context(
                                user_agent=random.choice(USER_AGENTS),
                                viewport={"width": 1280, "height": 720},
                            )
                            page = await context.new_page()
                            page.set_default_timeout(TIMEOUT_PAGINA * 1000)

                            if cloudflare_hits >= 3:
                                logger.error("Cloudflare persistente (3x). Encerrando busca.")
                                await browser.close()
                                return resultados
                    except Exception:
                        pass

            await browser.close()

        return resultados

    async def _buscar_termo(self, page: Page, categoria: str, termo: str,
                            comarca_hint: str = "") -> list[Oportunidade]:
        resultados = []
        termo_encoded = quote_plus(termo)
        url = f"https://www.jusbrasil.com.br/diarios/busca?q={termo_encoded}"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.error(f"[jusbrasil] Erro ao carregar: {e}")
            return resultados

        # Verificar Cloudflare
        try:
            title = await page.title()
            if "moment" in title.lower():
                logger.info(f"[jusbrasil] Cloudflare em '{termo[:50]}', esperando...")
                await asyncio.sleep(8)
                title = await page.title()
                if "moment" in title.lower():
                    return resultados
        except Exception:
            pass

        # Esperar resultados
        try:
            await page.wait_for_selector('a[href*="/diarios/"]', timeout=8000)
        except Exception:
            logger.info(f"[jusbrasil] Sem resultados para '{termo[:50]}'")
            return resultados

        # Extrair
        try:
            items = await page.evaluate(JS_EXTRACT)
        except Exception as e:
            logger.error(f"[jusbrasil] Erro JS: {e}")
            return resultados

        for item in items:
            titulo = item.get("titulo", "")
            trecho = item.get("trecho", "")
            texto_completo = titulo + " " + trecho

            op = Oportunidade(
                url=item["url"],
                fonte="jusbrasil",
                termo_busca=termo[:200],
                categoria=categoria,
                titulo=titulo,
                trecho=trecho,
                comarca=comarca_hint or self._extrair_comarca(texto_completo),
                tribunal=self._extrair_tribunal(texto_completo),
                estado=self._extrair_estado(texto_completo),
                data_publicacao=self._extrair_data(texto_completo),
                data_titulo=self._extrair_data_iso(titulo),
            )
            resultados.append(op)

        if resultados:
            logger.info(f"[jusbrasil] '{termo[:50]}' -> {len(resultados)} resultado(s)")

        return resultados

    def _extrair_comarca(self, texto: str) -> str:
        # Formato DJMG: "DJMG DD/MM/YYYY - Pág. X - ComarcaOuSeção - ..."
        m = re.search(r'DJ\w+\s+\d{2}/\d{2}/\d{4}\s+-\s+Pág\.\s*\d+\s+-\s+(.+?)\s+-\s+', texto)
        if m:
            candidato = m.group(1).strip()
            # Filtrar seções que não são comarcas
            if candidato not in ("Administrativo", "Judiciário", "Belo Horizonte"):
                return candidato
            if candidato == "Belo Horizonte":
                return candidato

        m = re.search(r'[Cc]omarca\s+de\s+([\w\s]+?)(?:\s*[-/\n]|\s{2,})', texto)
        if m:
            return m.group(1).strip()
        return ""

    def _extrair_tribunal(self, texto: str) -> str:
        m = re.search(r'(TJ[A-Z]{2}|TRT-?\d*|TRF-?\d*|STJ|STF|CNJ)', texto)
        return m.group(1) if m else ""

    def _extrair_estado(self, texto: str) -> str:
        # Primeiro tentar pela sigla do diário
        mapa = {
            "DJMG": "MG", "DJSP": "SP", "DJRJ": "RJ", "DJBA": "BA", "DJGO": "GO",
            "DJPR": "PR", "DJSC": "SC", "DJRS": "RS", "DJCE": "CE", "DJMT": "MT",
            "DJMS": "MS", "DJES": "ES", "DJPE": "PE", "DJPA": "PA",
            "DOECE": "CE", "DOETO": "TO",
        }
        for sigla, uf in mapa.items():
            if sigla in texto:
                return uf
        m = re.search(r'TJ([A-Z]{2})', texto)
        if m:
            return m.group(1)
        if "Minas Gerais" in texto:
            return "MG"
        return ""

    def _extrair_data(self, texto: str) -> str:
        m = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        return m.group(1) if m else ""

    def _extrair_data_iso(self, titulo: str) -> str:
        """Extrai data do título e converte para YYYY-MM-DD."""
        m = re.search(r'(\d{2})/(\d{2})/(\d{4})', titulo)
        if m:
            return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        return ""
