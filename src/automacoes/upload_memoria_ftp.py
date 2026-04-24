#!/usr/bin/env python3
"""
upload_memoria_ftp.py
Empacota CLAUDE-MEMORY/ em ZIP, sobe via FTP (IPv4 forcado),
mantem ultimos 7 backups, gera LATEST.md e sobe MEMORY.md legivel.
"""

from __future__ import annotations
import ftplib
import socket
import sys
import zipfile
from datetime import datetime
from pathlib import Path

VAULT = Path("/Users/jesus/Desktop/STEMMIA Dexter/memoria/CLAUDE-MEMORY")
LOCAL_BACKUP_DIR = Path("/Users/jesus/Desktop/STEMMIA Dexter/memoria/_backups-zip")
MEMORY_SRC = Path("/Users/jesus/.claude/projects/-Users-jesus/memory/MEMORY.md")

FTP_HOST = "alvorada.nuvemidc.com"
FTP_USER = "deploy@stemmia.com.br"
FTP_PASS = "@$xHQ[c*B&mqUj]R"
FTP_DIR = "/teste/backup-claude/memorias"

URL_PUBLICA = "https://stemmia.com.br/teste/backup-claude/memorias"


# Forca IPv4
_orig_getaddrinfo = socket.getaddrinfo


def _ipv4_only(*args, **kwargs):
    res = _orig_getaddrinfo(*args, **kwargs)
    return [r for r in res if r[0] == socket.AF_INET]


socket.getaddrinfo = _ipv4_only


def gerar_zip() -> Path:
    LOCAL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    data = datetime.now().strftime("%Y-%m-%d_%H%M")
    zip_path = LOCAL_BACKUP_DIR / f"CLAUDE-MEMORY-{data}.zip"

    if not VAULT.exists():
        raise FileNotFoundError(f"Vault nao existe: {VAULT}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in VAULT.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(VAULT.parent))
    return zip_path


def limpar_locais(manter: int = 7) -> list[Path]:
    zips = sorted(LOCAL_BACKUP_DIR.glob("CLAUDE-MEMORY-*.zip"), reverse=True)
    removidos = []
    for old in zips[manter:]:
        try:
            old.unlink()
            removidos.append(old)
        except Exception:
            pass
    return removidos


def conectar_ftp() -> ftplib.FTP:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, 21, timeout=30)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    return ftp


def garantir_dir(ftp: ftplib.FTP, caminho: str) -> None:
    partes = [p for p in caminho.split("/") if p]
    ftp.cwd("/")
    for p in partes:
        try:
            ftp.cwd(p)
        except ftplib.error_perm:
            ftp.mkd(p)
            ftp.cwd(p)


def upload_arquivo(ftp: ftplib.FTP, local: Path, remoto_nome: str) -> int:
    with local.open("rb") as f:
        ftp.storbinary(f"STOR {remoto_nome}", f)
    return local.stat().st_size


def limpar_remotos(ftp: ftplib.FTP, manter: int = 7) -> list[str]:
    arquivos = []
    try:
        ftp.retrlines("NLST", arquivos.append)
    except ftplib.error_perm:
        return []
    zips = sorted(
        [a for a in arquivos if a.startswith("CLAUDE-MEMORY-") and a.endswith(".zip")],
        reverse=True,
    )
    removidos = []
    for old in zips[manter:]:
        try:
            ftp.delete(old)
            removidos.append(old)
        except Exception:
            pass
    return removidos


def gerar_latest_md(zip_nome: str, tamanho_bytes: int) -> Path:
    p = LOCAL_BACKUP_DIR / "LATEST.md"
    p.write_text(
        f"""# Ultimo backup de memorias do Claude

- **Arquivo:** `{zip_nome}`
- **Tamanho:** {tamanho_bytes/1024:.1f} KB
- **Gerado em:** {datetime.now().isoformat(timespec='seconds')}
- **URL:** {URL_PUBLICA}/{zip_nome}

Atualizado por `upload_memoria_ftp.py`.
""",
        encoding="utf-8",
    )
    return p


def gerar_htaccess() -> Path:
    p = LOCAL_BACKUP_DIR / ".htaccess"
    p.write_text(
        """Options -Indexes
Header set X-Robots-Tag "noindex, nofollow"
AuthType Basic
AuthName "Claude Memory Backup"
AuthUserFile /home/stemmiac/.htpasswd-backup
Require valid-user
""",
        encoding="utf-8",
    )
    return p


def main() -> int:
    print(f"[upload] empacotando {VAULT}")
    zip_path = gerar_zip()
    tamanho = zip_path.stat().st_size
    print(f"[upload] zip gerado: {zip_path} ({tamanho/1024:.1f} KB)")

    removidos_local = limpar_locais(7)
    if removidos_local:
        print(f"[upload] removidos locais: {[p.name for p in removidos_local]}")

    latest = gerar_latest_md(zip_path.name, tamanho)
    htaccess = gerar_htaccess()

    erros = []

    try:
        print(f"[upload] conectando {FTP_HOST}")
        ftp = conectar_ftp()
        garantir_dir(ftp, FTP_DIR)

        print(f"[upload] enviando {zip_path.name}")
        upload_arquivo(ftp, zip_path, zip_path.name)

        print(f"[upload] enviando LATEST.md")
        upload_arquivo(ftp, latest, "LATEST.md")

        if MEMORY_SRC.exists():
            print(f"[upload] enviando MEMORY.md")
            upload_arquivo(ftp, MEMORY_SRC, "MEMORY.md")

        try:
            print(f"[upload] enviando .htaccess")
            upload_arquivo(ftp, htaccess, ".htaccess")
        except Exception as e:
            erros.append(f"htaccess: {e}")
            print(f"[upload] AVISO htaccess falhou: {e}")

        removidos_ftp = limpar_remotos(ftp, 7)
        if removidos_ftp:
            print(f"[upload] removidos FTP: {removidos_ftp}")

        ftp.quit()
        print(f"[upload] OK -- {URL_PUBLICA}/{zip_path.name}")
        if erros:
            print(f"[upload] avisos: {erros}")
        return 0
    except Exception as e:
        print(f"[upload] ERRO FTP: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"[upload] zip salvo localmente em: {zip_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
