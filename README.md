# 📝 Generador de Entradas de Blog con IA y Voz Neural

Este proyecto es una herramienta completa que genera entradas de blog divertidas y narrativas a partir de un breve resumen, utilizando Inteligencia Artificial local (Ollama) y convirtiendo el texto resultante a audio de alta calidad usando las voces neurales de Microsoft Edge (Edge TTS).

## ✨ Características

*   **Generación de Texto con IA**: Utiliza modelos locales (vía Ollama) para expandir tus resúmenes en historias completas y entretenidas.
*   **Voces Neurales Gratuitas**: Integración con **Edge TTS** para generar audio ultra-realista sin costes de API.
*   **Limpieza Inteligente**: Elimina automáticamente símbolos de Markdown (*, #, enlaces) para que la lectura en voz alta sea fluida.
*   **Sistema Anti-Fallos**: 
    *   División automática de textos largos para evitar errores de servidor.
    *   Reintento automático y cambio de voz si la seleccionada falla.
*   **Interfaz Web Simple**: Todo funciona desde el navegador con una interfaz limpia y modo oscuro automático.
*   **Portátil**: Script de inicio automático (`iniciar.bat`) que configura todo por ti.

## 🚀 Requisitos Previos

1.  **Python 3.10+** instalado en tu sistema.
2.  **Ollama** instalado y ejecutándose.
    *   El script utiliza el modelo `gemma3:12b-it-qat`. Asegúrate de tenerlo descargado:
        ```bash
        ollama pull gemma3:12b-it-qat
        ```
    *   *Nota: Puedes cambiar el modelo en el archivo `entradas.py` si prefieres usar otro (ej: llama3, mistral).*

## 🛠️ Instalación y Uso Rápido (Windows)

1.  **Descarga o Clona** este repositorio.
2.  Haz doble clic en el archivo **`iniciar.bat`**.
    *   Este script creará automáticamente el entorno virtual.
    *   Instalará las dependencias necesarias.
    *   Abrirá la aplicación en tu navegador predeterminado.
3.  ¡Listo! Escribe tu resumen y genera tu post.

## 🔧 Instalación Manual

Si prefieres usar la terminal:

1.  Crear entorno virtual:
    ```bash
    python -m venv venv
    ```
2.  Activar entorno:
    ```bash
    .\venv\Scripts\activate
    ```
3.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecutar la aplicación:
    ```bash
    python entradas.py
    ```

## 📂 Estructura del Proyecto

*   `entradas.py`: El corazón de la aplicación. Contiene el servidor web Flask y la lógica de IA/TTS.
*   `templates/`: Archivos HTML para la interfaz (`index.html`, `resultado.html`).
*   `iniciar.bat`: Script de automatización para Windows.
*   `requirements.txt`: Lista de librerías necesarias.

## ⚠️ Solución de Problemas Comunes

*   **Error de Audio (403)**: La aplicación gestiona esto automáticamente reintentando. Si persiste, verifica tu conexión a internet.
*   **"No se pudo sintetizar con voces disponibles"**: Asegúrate de tener conexión a internet, ya que Edge TTS requiere acceso a los servidores de Microsoft.
*   **Ollama no responde**: Asegúrate de que la aplicación de escritorio de Ollama esté abierta y el icono visible en la barra de tareas.

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y personales.
