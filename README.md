# 📝 Generador de Entradas de Blog con IA y Voz Neural

Este proyecto es una herramienta completa que genera entradas de blog divertidas y narrativas a partir de un breve resumen. Combina la potencia de la **Inteligencia Artificial local (Ollama)** con las **voces de alta calidad de Microsoft Edge** para narrar tus historias.

## ✨ Características Principales

*   **🎙️ Voces Neurales de Alta Calidad**: Utiliza las voces oficiales de **Microsoft Edge** (Edge TTS). Son voces gratuitas que suenan increíblemente naturales, humanas y profesionales (nada de voces robóticas).
*   **⚡ Ejecución en un Clic**: Incluye un archivo **`iniciar.bat`** que hace todo el trabajo sucio por ti. Solo dale doble clic y listo.
*   **🧠 IA Generativa Local**: Usa modelos de Ollama para redactar historias creativas sin depender de la nube.
*   **🛡️ Sistema Robusto**: Limpia automáticamente el texto de símbolos raros y gestiona errores de conexión para que el audio siempre salga perfecto.
*   **🎨 Interfaz Web**: Todo se maneja desde una web limpia y moderna en tu navegador.

## 🚀 Cómo Usarlo (La forma fácil)

No necesitas saber programación ni usar la terminal.

1.  **Descarga** este proyecto.
2.  Busca el archivo llamado **`iniciar.bat`** en la carpeta.
3.  **Haz doble clic sobre él**.
    *   🪄 El script instalará todo lo necesario automáticamente.
    *   Abrirá la aplicación en tu navegador web.
4.  Escribe tu resumen, elige una voz (¡prueba las de Edge!) y disfruta.

## 📋 Requisitos Previos

*   **Python 3.10** o superior instalado.
*   **Ollama** instalado y funcionando con el modelo `gemma3:12b-it-qat` (o el que prefieras configurar).

## 🔧 Instalación Manual (Solo para expertos)

Si prefieres no usar el archivo `.bat` y hacerlo tú mismo por terminal:

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activarlo
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python entradas.py
```

## ⚠️ Nota sobre las Voces

Este proyecto usa `edge-tts` para acceder a las voces online de Microsoft.
*   **Calidad**: Son las mismas voces que usa el navegador Edge para "Leer en voz alta".
*   **Gratis**: No requiere claves de API ni pagos.
*   **Conexión**: Necesitas tener internet activo para que se genere el audio.

## 📄 Licencia

Proyecto de código abierto para uso personal y educativo.
