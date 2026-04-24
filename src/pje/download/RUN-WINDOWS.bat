@echo off
REM ============================================================
REM  RUN-WINDOWS.bat — Launcher unico do baixar_e_organizar.py
REM  Roda na VM Parallels (Windows ARM64)
REM  Script-fonte vive na Mac, este .bat copia pra C:\ e executa
REM
REM  Por que copiar? UNC (\\psf\Home\) eh compartilhamento
REM  Parallels — python.exe ora trava ora corrompe bytes
REM  quando o script roda direto la. (ref PJE-015, PJE-021)
REM ============================================================

chcp 65001 >nul
setlocal EnableDelayedExpansion

set "SRC_DIR=\\psf\Home\Desktop\STEMMIA Dexter\src\pje\download"
set "DST_DIR=C:\pje"
set "SCRIPT_NAME=baixar_e_organizar.py"

echo.
echo ============================================================
echo   STEMMIA — Baixar e organizar PJe
echo ============================================================
echo.
echo   Fonte:  %SRC_DIR%
echo   Local:  %DST_DIR%
echo.

REM --- 1) Garante pasta local C:\pje
if not exist "%DST_DIR%" (
    echo [1/4] Criando pasta local %DST_DIR%
    mkdir "%DST_DIR%" || goto :fail_mkdir
) else (
    echo [1/4] Pasta local OK
)

REM --- 2) Copia script da Mac pra C:\pje (sempre — pra pegar updates)
echo [2/4] Copiando script da Mac...
xcopy "%SRC_DIR%\%SCRIPT_NAME%" "%DST_DIR%\" /Y /Q >nul
if errorlevel 1 goto :fail_xcopy
echo        OK

REM --- 3) Checa pypdf (usado pra extrair vara do PDF)
echo [3/4] Verificando pypdf...
python -c "import pypdf" 2>nul
if errorlevel 1 (
    echo        pypdf nao encontrado — instalando...
    python -m pip install --quiet pypdf || goto :fail_pip
    echo        OK
) else (
    echo        OK
)

REM --- 4) Executa o script
echo [4/4] Iniciando download...
echo ============================================================
echo.
cd /d "%DST_DIR%"
python "%SCRIPT_NAME%" %*
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if %RC% EQU 0 (
    echo   CONCLUIDO OK
) else (
    echo   TERMINADO COM ERRO — codigo %RC%
)
echo ============================================================
echo.
pause
exit /b %RC%

:fail_mkdir
echo [ERRO] Nao consegui criar %DST_DIR%
pause
exit /b 10

:fail_xcopy
echo [ERRO] xcopy falhou. VM com Shared Folders habilitado?
echo        Checa: Parallels ^> Configure ^> Options ^> Sharing
pause
exit /b 11

:fail_pip
echo [ERRO] pip install pypdf falhou. Checa internet.
pause
exit /b 12
