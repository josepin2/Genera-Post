import subprocess
import threading
from datetime import datetime
import os
import sys
import asyncio
import re
import time
import tempfile
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import edge_tts

app = Flask(__name__)
VOICES_CACHE = {
    'timestamp': 0,
    'voices': []
}
VOICE_OK_CACHE = {}

def limpiar_ansi(texto: str) -> str:
    import re
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', texto)

def limpiar_spinner(texto: str) -> str:
    # Caracteres de spinner unicode comunes
    spinner_chars = '⠙⠸⠴⠧⠏⠹⠼⠦⠇⠋'
    return ''.join(c for c in texto if c not in spinner_chars)

def generar_post(resumen_usuario: str, callback=None) -> str:
    prompt = (
        f"Por favor, escribe un post divertido, cercano y extenso para un blog dirigido a gente joven. "
        f"Desarrolla bien la historia basada en este resumen: {resumen_usuario}\n"
        f"Usa humor ligero y anécdotas para hacerlo entretenido, sin inventar detalles, solo expandiendo lo que se cuenta.\n"
        f"Que el texto tenga al menos 200 palabras, no te refieras a mi con un género ni masculino ni femenino, no te dirijas a mi ni conm el, ni con la."
    )
    proceso = subprocess.Popen(
        ["ollama", "run", "gemma3:12b-it-qat"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        bufsize=1
    )
    salida = []
    def leer_salida():
        for linea in proceso.stdout:
            limpia = limpiar_ansi(linea)
            limpia = limpiar_spinner(limpia)
            if callback:
                callback(limpia)
            salida.append(limpia)
    hilo_lectura = threading.Thread(target=leer_salida, daemon=True)
    hilo_lectura.start()
    try:
        proceso.stdin.write(prompt)
        proceso.stdin.close()
    except Exception as e:
        print(f"⚠️ Error enviando prompt: {e}")
        proceso.kill()
        return ""
    proceso.wait()
    hilo_lectura.join()
    return ''.join(salida)

def guardar_post(contenido: str) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"entrada_blog_{fecha}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido + "\n")
    print(f"\n✅ Entrada de blog guardada como: {nombre_archivo}")
    return nombre_archivo

def abrir_archivo(nombre_archivo: str):
    try:
        if sys.platform == "win32":
            os.startfile(nombre_archivo)
        elif sys.platform == "darwin":
            subprocess.call(["open", nombre_archivo])
        else:
            subprocess.call(["xdg-open", nombre_archivo])
    except Exception as e:
        print(f"⚠️ No se pudo abrir el archivo automáticamente: {e}")

def configurar_utf8_windows():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resumen = request.form.get('resumen', '')
        if resumen:
            resultado = generar_post(resumen)
            return render_template('resultado.html', post=resultado)
    return render_template('index.html')

@app.route('/stream_post', methods=['POST'])
def stream_post():
    resumen = request.form.get('resumen', '')
    return Response(generar_post_stream(resumen), mimetype='text/plain')

def generar_post_stream(resumen_usuario: str):
    prompt = (
        f"Por favor, escribe un post divertido, cercano y extenso para un blog dirigido a gente joven. "
        f"Desarrolla bien la historia basada en este resumen: {resumen_usuario}\n"
        f"Usa humor ligero y anécdotas para hacerlo entretenido, sin inventar detalles, solo expandiendo lo que se cuenta.\n"
        f"Que el texto tenga al menos 300 palabras."
    )
    proceso = subprocess.Popen(
        ["ollama", "run", "gemma3:12b-it-qat"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        bufsize=1
    )
    try:
        proceso.stdin.write(prompt)
        proceso.stdin.close()
    except Exception as e:
        proceso.kill()
        yield f"Error: {e}\n"
        return
    for linea in proceso.stdout:
        limpia = limpiar_ansi(linea)
        limpia = limpiar_spinner(limpia)
        yield limpia
    proceso.wait()

@app.route('/resultado')
def resultado():
    resumen = request.args.get('resumen', '')
    return render_template('resultado.html', resumen=resumen)

async def sintetizar_audio(texto: str, voz: str) -> bytes:
    comunicador = edge_tts.Communicate(texto, voice=voz)
    audio = bytearray()
    async for frag in comunicador.stream():
        if frag["type"] == "audio":
            audio.extend(frag["data"])
    return bytes(audio)

async def sintetizar_audio_save(texto: str, voz: str) -> bytes:
    # Dividir texto en fragmentos más pequeños para evitar 403
    fragmentos = dividir_texto(texto, max_len=500)
    audio_final = bytearray()
    
    for i, frag in enumerate(fragmentos):
        if not frag.strip():
            continue
            
        print(f"  Processing chunk {i+1}/{len(fragmentos)} ({len(frag)} chars)...")
        
        # Reintentos por fragmento
        max_retries_chunk = 3
        chunk_success = False
        last_chunk_err = None
        
        for attempt in range(max_retries_chunk):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tmp_path = tmp.name
            tmp.close()
            
            try:
                comunicador = edge_tts.Communicate(frag, voice=voz)
                await comunicador.save(tmp_path)
                
                # Verificar si el archivo tiene contenido válido
                if os.path.getsize(tmp_path) < 100: # Menos de 100 bytes es sospechoso
                    raise Exception("Audio generado demasiado pequeño o vacío")
                    
                with open(tmp_path, 'rb') as f:
                    audio_final.extend(f.read())
                
                chunk_success = True
                # Pausa entre chunks para evitar rate limiting
                await asyncio.sleep(0.5)
                
                try:
                    os.remove(tmp_path)
                except:
                    pass
                break # Éxito, salir del bucle de reintentos
                
            except Exception as e:
                last_chunk_err = e
                print(f"    Chunk error (attempt {attempt+1}): {e}")
                try:
                    os.remove(tmp_path)
                except:
                    pass
                
                # Si es 403, esperar más
                if "403" in str(e):
                    wait_time = 2 + (attempt * 2)
                    print(f"    Rate limited (403). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    await asyncio.sleep(1)
        
        if not chunk_success:
            raise Exception(f"Fallo al generar fragmento {i+1}: {last_chunk_err}")
                
    return bytes(audio_final)

def dividir_texto(texto: str, max_len: int = 400) -> list:
    # Primero dividir por puntuación
    s = re.split(r'(\.|\!|\?|\n)', texto)
    out = []
    buf = ''
    
    def push_buf(buffer):
        if not buffer:
            return []
        # Si el buffer es demasiado largo, dividirlo por espacios
        if len(buffer) > max_len:
            palabras = buffer.split(' ')
            sub_buf = ''
            res = []
            for pal in palabras:
                if len(sub_buf) + len(pal) + 1 <= max_len:
                    sub_buf += ((' ' if sub_buf else '') + pal)
                else:
                    if sub_buf:
                        res.append(sub_buf)
                    sub_buf = pal
            if sub_buf:
                res.append(sub_buf)
            return res
        return [buffer]

    for i in range(0, len(s), 2):
        frag = s[i]
        sep = s[i+1] if i+1 < len(s) else ''
        piece = (frag + sep).strip()
        if not piece:
            continue
            
        if len(buf) + len(piece) + 1 <= max_len:
            buf += ((' ' if buf else '') + piece)
        else:
            if buf:
                out.extend(push_buf(buf))
            buf = piece
            
    if buf:
        out.extend(push_buf(buf))
        
    if not out:
        # Si falló todo, dividir a la fuerza
        return [texto[i:i+max_len] for i in range(0, len(texto), max_len)]
        
    return out

def obtener_voces_es() -> list:
    now = time.time()
    if now - VOICES_CACHE['timestamp'] > 60 or not VOICES_CACHE['voices']:
        voces = asyncio.run(edge_tts.list_voices())
        VOICES_CACHE['voices'] = [v for v in voces if str(v.get('Locale','')).startswith('es')]
        VOICES_CACHE['timestamp'] = now
    return VOICES_CACHE['voices']

def probar_voz(voz: str) -> bool:
    cache = VOICE_OK_CACHE.get(voz)
    now = time.time()
    if cache and (now - cache['ts'] < 300):
        return cache['ok']
    try:
        _ = asyncio.run(sintetizar_audio("Hola", voz))
        VOICE_OK_CACHE[voz] = {'ok': True, 'ts': now}
        return True
    except Exception:
        VOICE_OK_CACHE[voz] = {'ok': False, 'ts': now}
        return False

def sintetizar_audio_fallback(texto: str, voz: str) -> tuple:
    es = obtener_voces_es()
    # Lista de voces preferidas de alta calidad
    preferidas = [voz, 'es-ES-AlvaroNeural', 'es-ES-ElviraNeural', 'es-MX-LibertoNeural', 'es-MX-DaliaNeural', 'es-CO-GonzaloNeural', 'es-US-PalomaNeural', 'es-US-AlonsoNeural']
    disponibles = [v.get('ShortName') for v in es]
    
    # Filtrar candidatos válidos
    candidatos = []
    seen = set()
    for p in preferidas:
        if p in disponibles and p not in seen:
            candidatos.append(p)
            seen.add(p)
            
    # Si fallan las preferidas, añadir el resto de voces en español como último recurso
    for v in disponibles:
        if v not in seen:
            candidatos.append(v)
            
    last_err = ''
    
    for candidato in candidatos:
        # Intentar generar con este candidato
        # No usamos probar_voz estricto aquí para no descartar falsos negativos, 
        # confiamos en el reintento del bucle.
        
        print(f"Intentando sintetizar con voz: {candidato}")
        for intento in range(3):
            try:
                # Usar asyncio.run para llamar a la función async desde síncrono
                # Nota: Crear un nuevo loop cada vez es costoso pero seguro en Flask threaded
                data = asyncio.run(sintetizar_audio_save(texto, candidato))
                if len(data) > 0:
                    return data, candidato
            except Exception as e:
                print(f"Error con {candidato} (intento {intento+1}): {e}")
                last_err = str(e)
                # Backoff exponencial: 1s, 2s, 4s
                time.sleep(1 + (intento * 1))
        
        # Si fallaron los 3 intentos, pasamos al siguiente candidato
        continue

    if last_err:
        raise RuntimeError(f'No se pudo sintetizar con ninguna voz disponible. Último error: {last_err}')
    raise RuntimeError('No se pudo sintetizar con voces disponibles')

def limpiar_markdown(texto: str) -> str:
    # Eliminar encabezados Markdown (## Titulo)
    texto = re.sub(r'#+\s*', '', texto)
    # Eliminar negritas y cursivas (**texto**, *texto*)
    texto = re.sub(r'\*\*|__|\*|_', '', texto)
    # Eliminar enlaces [texto](url) -> texto
    texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
    # Eliminar código `codigo`
    texto = re.sub(r'`', '', texto)
    # Eliminar viñetas (- elemento)
    texto = re.sub(r'^\s*[\-\*]\s+', '', texto, flags=re.MULTILINE)
    return texto

@app.route('/tts', methods=['POST'])
def tts():
    texto = request.form.get('text', '')
    voz = request.form.get('voice', 'es-ES-ElviraNeural')
    
    # Limpiar texto y símbolos de Markdown antes de sintetizar
    texto = limpiar_markdown(texto)
    texto = texto.strip()
    
    if not texto:
        return Response("Texto vacío", status=400)
    try:
        voces = obtener_voces_es()
        if not any(v.get('ShortName') == voz for v in voces):
            return Response("Voz no soportada. Prueba otra voz.", status=400)
        data, usada = sintetizar_audio_fallback(texto[:1500], voz)
        nombre = datetime.now().strftime("post_%Y%m%d_%H%M%S.mp3")
        headers = {"Content-Disposition": f"attachment; filename={nombre}", "X-Edge-Voice-Used": usada}
        return Response(data, mimetype='audio/mpeg', headers=headers)
    except Exception as e:
        return Response(f"Error al generar audio: {e}", status=500)

@app.route('/voices', methods=['GET'])
def voices():
    try:
        voces = asyncio.run(edge_tts.list_voices())
        es = [
            {
                'shortName': v.get('ShortName'),
                'displayName': v.get('DisplayName', v.get('ShortName')),
                'locale': v.get('Locale'),
                'gender': v.get('Gender')
            }
            for v in voces if str(v.get('Locale','')).startswith('es')
        ]
        return jsonify({'voices': es})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Motor offline eliminado

def main():
    configurar_utf8_windows()
    print("✍️  Bienvenido al generador de entradas de blog divertidas.\n")
    resumen_usuario = input("Escribe un breve resumen de lo que hiciste o tu viaje: ").strip()
    if not resumen_usuario:
        print("⚠️ No has introducido ningún texto. Saliendo.")
        return

    print("\n✍️  Generando tu post... dame unos segundos... 🤖💭\n")
    contenido_generado = generar_post(resumen_usuario)

    if contenido_generado:
        archivo = guardar_post(contenido_generado)
        abrir_archivo(archivo)
    else:
        print("⚠️ No se pudo generar el post.")

    print("\n================================")
    print("  Script finalizado.")
    print("================================")

if __name__ == "__main__":
    app.run(debug=True)
