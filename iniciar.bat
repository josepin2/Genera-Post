@echo off
REM Copyright 2025 Josepin2
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM
REM     http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM limitations under the License.

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
