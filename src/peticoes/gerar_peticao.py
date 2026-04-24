#!/usr/bin/env python3
"""
gerar_peticao.py — Gerador rápido de petições em PDF na folha timbrada
=======================================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 25/02/2026

USO:
    python3 gerar_peticao.py --output NOME.pdf --corpo-arquivo corpo.xml
    python3 gerar_peticao.py --output NOME.pdf --corpo "<w:p>...</w:p>"

COMO FUNCIONA:
    1. Copia template-timbrado/ (sem document.xml) para pasta temporária
    2. Injeta o corpo recebido dentro de um document.xml completo
    3. Empacota como .docx (zipfile direto, sem validação)
    4. Converte para PDF via Microsoft Word (ou LibreOffice como fallback)
    5. Copia PDF para "petições automáticas claude/" e "PETIÇÕES COWORK/"
    6. Limpa temporários

TEMPO ESPERADO: ~8-12 segundos (Word) ou ~12-14 segundos (LibreOffice)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

# === CAMINHOS FIXOS ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "template-timbrado")
# Fallback: template no diretório de sessão
if not os.path.exists(TEMPLATE_DIR):
    TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "template-timbrado")
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PASTA_CLAUDE = os.path.join(BASE_DIR, "saida", "peticoes-claude")
PASTA_COWORK = os.path.join(BASE_DIR, "saida", "peticoes-cowork")

# === XML ENVELOPE ===
# Tudo que vem antes do corpo (namespaces, background, <w:body>)
XML_HEADER = '''<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">
  <w:background w:color="F7F7F7"/>
  <w:body>
'''

# sectPr mantém headers, footers, margens, tamanho da página
XML_FOOTER = '''
    <w:sectPr w:rsidR="00453A2B" w:rsidRPr="00453A2B" w:rsidSect="001A4F83">
      <w:headerReference w:type="even" r:id="rId8"/>
      <w:headerReference w:type="default" r:id="rId9"/>
      <w:footerReference w:type="even" r:id="rId10"/>
      <w:footerReference w:type="default" r:id="rId11"/>
      <w:headerReference w:type="first" r:id="rId12"/>
      <w:footerReference w:type="first" r:id="rId13"/>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="567" w:right="720" w:bottom="720" w:left="720" w:header="0" w:footer="283" w:gutter="0"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:body>
</w:document>'''


def gerar_document_xml(corpo_xml: str) -> str:
    """Monta o document.xml completo envolvendo o corpo recebido."""
    return XML_HEADER + corpo_xml + XML_FOOTER


def empacotar_docx(template_dir: str, document_xml: str, output_docx: str):
    """Cria o .docx a partir do template + document.xml gerado."""
    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Adicionar todos os arquivos do template
        for root, dirs, files in os.walk(template_dir):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, template_dir)
                # Pular document.xml do template (será gerado dinamicamente)
                if arcname == os.path.join('word', 'document.xml'):
                    continue
                zf.write(filepath, arcname)
        # Adicionar o document.xml gerado
        zf.writestr('word/document.xml', document_xml)


def converter_pdf_word(docx_abs: str, pdf_abs: str) -> bool:
    """Converte DOCX para PDF via Microsoft Word (AppleScript).
    Licença via App Store — ativa pelo Apple ID."""
    if not os.path.exists('/Applications/Microsoft Word.app'):
        return False
    script = f'''
    tell application "Microsoft Word"
        activate
        delay 2
        close every document saving no
        delay 1
        open POSIX file "{docx_abs}"
        delay 3
        save as active document file name POSIX file "{pdf_abs}" file format (format PDF)
        delay 1
        close active document saving no
    end tell
    '''
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True, timeout=120
        )
        if os.path.exists(pdf_abs):
            return True
        print(f"AVISO: Word falhou ({result.stderr.strip()})", file=sys.stderr)
    except Exception as e:
        print(f"AVISO: Word exceção ({e})", file=sys.stderr)
    return False


def converter_pdf_appkit(docx_abs: str, pdf_abs: str) -> bool:
    """Converte DOCX para PDF via AppKit/Quartz nativo do macOS.
    Funciona sem Word licenciado. Renderiza texto e formatação básica,
    mas NÃO renderiza headers/footers/imagens embutidas do template Word."""
    try:
        import AppKit
        import Quartz

        url = AppKit.NSURL.fileURLWithPath_(docx_abs)
        attrString, docAttrs, error = (
            AppKit.NSAttributedString.alloc()
            .initWithURL_options_documentAttributes_error_(url, {}, None, None)
        )
        if error or attrString is None:
            print(f"AVISO: AppKit não carregou o DOCX ({error})", file=sys.stderr)
            return False

        # Configurar layout — página A4 (595 x 842 pt)
        pageWidth, pageHeight = 595.0, 842.0
        margin = 50.0
        textWidth = pageWidth - 2 * margin
        textHeight = pageHeight - 2 * margin

        textStorage = AppKit.NSTextStorage.alloc().initWithAttributedString_(attrString)
        layoutManager = AppKit.NSLayoutManager.alloc().init()
        textStorage.addLayoutManager_(layoutManager)

        textContainer = AppKit.NSTextContainer.alloc().initWithSize_(
            AppKit.NSMakeSize(textWidth, 1e7)
        )
        textContainer.setWidthTracksTextView_(False)
        layoutManager.addTextContainer_(textContainer)

        # Forçar layout completo
        layoutManager.glyphRangeForTextContainer_(textContainer)
        usedRect = layoutManager.usedRectForTextContainer_(textContainer)
        totalHeight = usedRect.size.height
        numPages = max(1, int(totalHeight / textHeight) + 1)

        # Criar PDF via CGContext
        mediaBox = Quartz.CGRectMake(0, 0, pageWidth, pageHeight)
        pdfURL = Quartz.CFURLCreateWithFileSystemPath(
            None, pdf_abs, Quartz.kCFURLPOSIXPathStyle, False
        )
        pdfContext = Quartz.CGPDFContextCreateWithURL(pdfURL, mediaBox, None)
        if pdfContext is None:
            return False

        for page in range(numPages):
            Quartz.CGPDFContextBeginPage(pdfContext, None)
            nsContext = AppKit.NSGraphicsContext.graphicsContextWithCGContext_flipped_(
                pdfContext, False
            )
            AppKit.NSGraphicsContext.setCurrentContext_(nsContext)

            yOffset = page * textHeight
            Quartz.CGContextSaveGState(pdfContext)
            Quartz.CGContextTranslateCTM(pdfContext, margin, pageHeight - margin)
            Quartz.CGContextScaleCTM(pdfContext, 1.0, -1.0)

            glyphRange = layoutManager.glyphRangeForBoundingRect_inTextContainer_(
                AppKit.NSMakeRect(0, yOffset, textWidth, textHeight), textContainer
            )
            if glyphRange.length > 0:
                layoutManager.drawBackgroundForGlyphRange_atPoint_(
                    glyphRange, AppKit.NSMakePoint(0, -yOffset)
                )
                layoutManager.drawGlyphsForGlyphRange_atPoint_(
                    glyphRange, AppKit.NSMakePoint(0, -yOffset)
                )

            Quartz.CGContextRestoreGState(pdfContext)
            Quartz.CGPDFContextEndPage(pdfContext)

        Quartz.CGPDFContextClose(pdfContext)

        if os.path.exists(pdf_abs) and os.path.getsize(pdf_abs) > 500:
            print("  [AppKit] PDF gerado via macOS nativo (sem headers/footers do template)", file=sys.stderr)
            return True
        return False
    except Exception as e:
        print(f"AVISO: AppKit exceção ({e})", file=sys.stderr)
        return False


def converter_pdf_libreoffice(docx_abs: str, output_dir: str, pdf_abs: str) -> bool:
    """Converte DOCX para PDF via LibreOffice headless."""
    try:
        subprocess.run(
            ['soffice', '--headless', '--convert-to', 'pdf',
             '--outdir', output_dir, docx_abs],
            capture_output=True, timeout=60
        )
        return os.path.exists(pdf_abs)
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"AVISO: LibreOffice exceção ({e})", file=sys.stderr)
        return False


def converter_pdf(docx_path: str, output_dir: str) -> str:
    """Converte DOCX para PDF tentando 3 métodos em ordem:
    1. Microsoft Word (AppleScript) — melhor qualidade, requer licença
    2. AppKit/Quartz (macOS nativo) — sempre disponível, sem headers/footers
    3. LibreOffice (headless) — boa qualidade, requer instalação
    """
    pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_name)
    docx_abs = os.path.abspath(docx_path)
    pdf_abs = os.path.abspath(pdf_path)

    # Método 1: Word (melhor qualidade, requer licença)
    if converter_pdf_word(docx_abs, pdf_abs):
        print("  [Word] Conversão via Microsoft Word", file=sys.stderr)
        return pdf_path

    # Método 2: LibreOffice (boa qualidade COM timbrado)
    if converter_pdf_libreoffice(docx_abs, output_dir, pdf_abs):
        print("  [LibreOffice] Conversão via soffice", file=sys.stderr)
        return pdf_path

    # Método 3: AppKit/Quartz (fallback, SEM headers/footers)
    if converter_pdf_appkit(docx_abs, pdf_abs):
        return pdf_path

    print(f"ERRO: nenhum método conseguiu gerar PDF em {pdf_path}", file=sys.stderr)
    print("  Soluções possíveis:", file=sys.stderr)
    print("  1. Ativar licença do Microsoft Word", file=sys.stderr)
    print("  2. Instalar LibreOffice: brew install --cask libreoffice", file=sys.stderr)
    sys.exit(1)


def copiar_saidas(pdf_path: str, nome_final: str):
    """Copia o PDF para as duas pastas de saída."""
    for pasta in [PASTA_CLAUDE, PASTA_COWORK]:
        if os.path.exists(pasta):
            destino = os.path.join(pasta, nome_final)
            shutil.copy2(pdf_path, destino)
            print(f"  → {destino}")


def main():
    parser = argparse.ArgumentParser(description='Gerar petição em PDF na folha timbrada')
    parser.add_argument('--output', required=True, help='Nome do arquivo PDF de saída')
    parser.add_argument('--corpo', help='XML do corpo da petição (inline)')
    parser.add_argument('--corpo-arquivo', help='Caminho para arquivo com XML do corpo')
    args = parser.parse_args()

    start = time.time()

    # 1. Ler corpo
    if args.corpo_arquivo:
        with open(args.corpo_arquivo, 'r', encoding='utf-8') as f:
            corpo_xml = f.read()
    elif args.corpo:
        corpo_xml = args.corpo
    else:
        print("ERRO: forneça --corpo ou --corpo-arquivo", file=sys.stderr)
        sys.exit(1)

    # 2. Verificar template
    if not os.path.exists(TEMPLATE_DIR):
        print(f"ERRO: template não encontrado em {TEMPLATE_DIR}", file=sys.stderr)
        sys.exit(1)

    # 3. Gerar document.xml
    document_xml = gerar_document_xml(corpo_xml)

    # 4. Criar DOCX em pasta temporária
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, 'peticao.docx')
        empacotar_docx(TEMPLATE_DIR, document_xml, docx_path)

        # 5. Converter para PDF
        pdf_path = converter_pdf(docx_path, tmpdir)

        # 6. Copiar para saídas
        nome_pdf = args.output if args.output.endswith('.pdf') else args.output + '.pdf'

        # Copiar para pasta principal também
        destino_principal = os.path.join(SCRIPT_DIR, nome_pdf)
        shutil.copy2(pdf_path, destino_principal)
        print(f"  → {destino_principal}")

        copiar_saidas(pdf_path, nome_pdf)

    elapsed = time.time() - start
    print(f"\nPDF gerado em {elapsed:.1f}s: {nome_pdf}")


if __name__ == '__main__':
    main()
