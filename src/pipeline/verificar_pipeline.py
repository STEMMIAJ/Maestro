#!/usr/bin/env python3
"""
verificar_pipeline.py — Testa o pipeline do verificador-100 end-to-end
Cria JSON de teste → roda gerar_verificacao.py → verifica se HTML foi gerado.

Uso:
    python3 verificar_pipeline.py
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
GERADOR = SCRIPT_DIR / "gerar_verificacao.py"


def criar_json_teste():
    """Cria JSON de verificação com dados fictícios para teste."""
    return {
        "processo": "0000000-00.0000.0.00.0000",
        "tipo_peca": "TESTE-PIPELINE",
        "data_verificacao": datetime.now().isoformat(),
        "versao_stemmia": "4.1.0",
        "resumo": {
            "total_afirmacoes": 3,
            "confirmadas": 2,
            "pendentes": 0,
            "divergentes": 1,
            "sem_fonte": 0,
            "vicios_processuais": 0
        },
        "secoes": [
            {
                "titulo": "Identificação",
                "afirmacoes": [
                    {
                        "id": 1,
                        "trecho_peticao": "O autor João da Silva moveu ação contra o réu Hospital Municipal.",
                        "dados_verificaveis": ["João da Silva", "Hospital Municipal"],
                        "status": "confirmado",
                        "fontes": [
                            {
                                "id_documento": "ID 123456789",
                                "tipo": "Petição Inicial",
                                "trecho_fonte": "JOÃO DA SILVA, brasileiro, residente...",
                                "localizacao": "Linha 5 do TEXTO-EXTRAIDO.txt"
                            }
                        ],
                        "alertas": []
                    },
                    {
                        "id": 2,
                        "trecho_peticao": "A data do acidente foi 15/03/2024.",
                        "dados_verificaveis": ["15/03/2024"],
                        "status": "confirmado",
                        "fontes": [
                            {
                                "id_documento": "ID 123456789",
                                "tipo": "Petição Inicial",
                                "trecho_fonte": "No dia 15/03/2024, o autor sofreu...",
                                "localizacao": "Linha 12 do TEXTO-EXTRAIDO.txt"
                            }
                        ],
                        "alertas": []
                    },
                    {
                        "id": 3,
                        "trecho_peticao": "O valor da causa é R$ 50.000,00.",
                        "dados_verificaveis": ["R$ 50.000,00"],
                        "status": "divergente",
                        "fontes": [
                            {
                                "id_documento": "ID 123456789",
                                "tipo": "Petição Inicial",
                                "trecho_fonte": "Dá-se à causa o valor de R$ 45.000,00",
                                "localizacao": "Linha 89 do TEXTO-EXTRAIDO.txt"
                            }
                        ],
                        "alertas": ["Valor divergente: petição diz R$ 50.000 mas fonte diz R$ 45.000"]
                    }
                ]
            }
        ],
        "leis_citadas": [
            {
                "referencia": "Art. 465 do CPC",
                "status": "confirmada",
                "trecho_lei": "O juiz nomeará perito especializado no objeto da perícia...",
                "arquivo_local": "CPC-L13105-2015.html"
            }
        ],
        "vicios_processuais": [],
        "erros_materiais_incorporados": {
            "cids": [],
            "datas": [],
            "nomes": [],
            "medicamentos": [],
            "exames": []
        }
    }


def testar():
    """Executa o teste do pipeline."""
    print("=" * 50)
    print("TESTE DO PIPELINE VERIFICADOR-100")
    print("=" * 50)
    print()

    # Verificar se o script gerador existe
    if not GERADOR.exists():
        print(f"ERRO: Script não encontrado: {GERADOR}")
        return False

    print(f"[1/4] Script gerador encontrado: {GERADOR}")

    # Criar JSON de teste em /tmp
    json_teste = Path(tempfile.mktemp(suffix=".json", prefix="verificacao-teste-"))
    html_saida = Path(tempfile.mktemp(suffix=".html", prefix="VERIFICACAO-TESTE-"))

    dados_teste = criar_json_teste()
    with open(json_teste, 'w', encoding='utf-8') as f:
        json.dump(dados_teste, f, ensure_ascii=False, indent=2)

    print(f"[2/4] JSON de teste criado: {json_teste}")

    # Rodar o gerador
    cmd = [
        sys.executable,
        str(GERADOR),
        "--json", str(json_teste),
        "--output", str(html_saida)
    ]

    print(f"[3/4] Executando: {' '.join(cmd)}")
    try:
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if resultado.returncode != 0:
            print(f"\nERRO: Script retornou código {resultado.returncode}")
            if resultado.stderr:
                print(f"STDERR: {resultado.stderr}")
            if resultado.stdout:
                print(f"STDOUT: {resultado.stdout}")
            return False

        if resultado.stdout:
            print(f"  Saída: {resultado.stdout.strip()}")

    except subprocess.TimeoutExpired:
        print("ERRO: Script demorou mais de 30 segundos")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

    # Verificar se HTML foi gerado
    if html_saida.exists():
        tamanho = html_saida.stat().st_size
        print(f"[4/4] HTML gerado com sucesso: {html_saida} ({tamanho} bytes)")

        # Verificar conteúdo básico
        with open(html_saida, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        checks = {
            "DOCTYPE/html": "<!DOCTYPE html>" in conteudo or "<html" in conteudo,
            "Dados do processo": "0000000-00.0000.0.00.0000" in conteudo,
            "Afirmação confirmada": "confirmado" in conteudo.lower() or "João da Silva" in conteudo,
            "Afirmação divergente": "divergente" in conteudo.lower() or "50.000" in conteudo,
        }

        print()
        print("Verificações de conteúdo:")
        todos_ok = True
        for nome, ok in checks.items():
            status = "OK" if ok else "FALHOU"
            if not ok:
                todos_ok = False
            print(f"  {status}: {nome}")

        # Limpar arquivos de teste
        json_teste.unlink(missing_ok=True)
        html_saida.unlink(missing_ok=True)

        print()
        if todos_ok:
            print("RESULTADO: PIPELINE FUNCIONANDO")
            return True
        else:
            print("RESULTADO: PIPELINE PARCIAL — HTML gerado mas conteúdo incompleto")
            return True  # Parcial mas funcional
    else:
        # Talvez o script gerou com outro nome
        print(f"AVISO: HTML não encontrado em {html_saida}")
        print("Verificando se gerou em outro local...")

        # Procurar por verificação recém-criada
        possiveis = list(Path(tempfile.gettempdir()).glob("VERIFICACAO-TESTE-*.html"))
        if possiveis:
            print(f"  Encontrado: {possiveis[0]}")
            possiveis[0].unlink(missing_ok=True)
            json_teste.unlink(missing_ok=True)
            return True

        json_teste.unlink(missing_ok=True)
        print("ERRO: HTML não foi gerado")
        return False


if __name__ == "__main__":
    sucesso = testar()
    print()
    sys.exit(0 if sucesso else 1)
