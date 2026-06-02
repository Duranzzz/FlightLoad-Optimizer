@echo off
chcp 65001 >nul
title FlightLoad Optimizer — Instalación y Servidor
color 0B

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   ✈  FlightLoad Optimizer — Setup Automático    ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ──────────────────────────────────────────────────────
:: 1. Verificar que Python esté instalado
:: ──────────────────────────────────────────────────────
echo  [1/3] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ❌ Python no está instalado o no está en el PATH.
    echo     Descárgalo de https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo        ✔ Python encontrado.
echo.

:: ──────────────────────────────────────────────────────
:: 2. Instalar dependencias
:: ──────────────────────────────────────────────────────
echo  [2/3] Instalando dependencias (requirements.txt)...
echo.
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo  ⚠ Algunas dependencias no se instalaron correctamente.
    echo    Revisa los mensajes de error arriba.
    echo    Nota: CPLEX requiere licencia de IBM Academic Initiative.
    echo.
    pause
)
echo.
echo        ✔ Dependencias instaladas.
echo.

:: ──────────────────────────────────────────────────────
:: 3. Levantar servidor HTTP en /interface
:: ──────────────────────────────────────────────────────
echo  [3/3] Iniciando servidor HTTP en puerto 8080...
echo.
echo  ┌──────────────────────────────────────────────────┐
echo  │  Abre tu navegador en:                           │
echo  │                                                  │
echo  │     👉  http://localhost:8080                     │
echo  │                                                  │
echo  │  Presiona Ctrl+C para detener el servidor.       │
echo  └──────────────────────────────────────────────────┘
echo.

cd /d "%~dp0interface"
python -m http.server 8080

pause
