@echo off
chcp 65001 > nul
cls
echo ================================
echo    Lanzando generador de blogs
echo ================================

echo Creando entorno virtual si no existe...
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
    pip install -r requirements.txt
)

echo Iniciando la aplicacion web...
start http://127.0.0.1:5000/
python entradas.py

echo.
echo ================================
echo   Script finalizado con estilo 😎
echo ================================
pause
