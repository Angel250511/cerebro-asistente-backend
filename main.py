# ==============================================================================
# --- CEREBRO DEL ASISTENTE (BACKEND) - VERSIÓN FINAL Y DEFINITIVA ---
# ==============================================================================

# 1. Importar las herramientas necesarias del servidor y de la IA
from flask import Flask, request, jsonify
import os
from openai import OpenAI
import json
import tempfile

# 2. Crear la aplicación web con Flask
# La variable 'app' es la que Gunicorn buscará y ejecutará en Render.
app = Flask(__name__)

# 3. Cargar la clave de API de forma segura desde las variables de entorno de Render
api_key_openrouter = os.environ.get("OPENROUTER_API_KEY")

# Verificación inicial para asegurarnos de que la clave se cargó al iniciar el servidor
if not api_key_openrouter:
    print("¡ALERTA CRÍTICA! La variable de entorno OPENROUTER_API_KEY no se encontró.")

# 4. Preparar el cliente para hablar con la IA de OpenRouter
# Se añaden headers personalizados para asegurar la compatibilidad con OpenRouter.
client = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://cerebro-asistente-backend.onrender.com",
        "X-Title": "Dolphin Assistant",
    },
)

# ==============================================================================
# --- RUTAS DE LA API (LOS "PODERES" DE NUESTRO CEREBRO) ---
# ==============================================================================

# --- RUTA 1: TRANSCRIPCIÓN DE AUDIO (ESCUCHA MEJORADA) ---
@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "Petición inválida: No se envió ningún archivo de audio."}), 400
    
    audio_file = request.files['audio']
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        audio_file.save(temp_audio.name)
        
        try:
            with open(temp_audio.name, "rb") as file_to_transcribe:
                print("[Backend] Recibido audio. Enviando a Whisper para transcripción...")
                
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=file_to_transcribe,
                    language="es"
                )
                
            print(f"[Backend] Texto transcrito: '{transcription.text}'")
            return jsonify({"text": transcription.text})

        except Exception as e:
            print(f"[Backend ERROR] Error durante la transcripción: {e}")
            return jsonify({"error": str(e)}), 500

# --- RUTA 2: PROCESAMIENTO DE COMANDOS (PENSAMIENTO DE LA IA) ---
@app.route('/process-command', methods=['POST'])
def process_command():
    data = request.get_json()
    
    if not data or 'history' not in data or 'tools' not in data:
        return jsonify({"error": "Petición inválida: Faltan datos de historial o herramientas."}), 400
    
    # Verificamos si se pidió una respuesta en streaming
    stream = data.get("stream", False)
        
    try:
        MODELO_COMPATIBLE = "anthropic/claude-3-haiku" 
        print(f"[Backend] Procesando comando con el modelo: {MODELO_COMPATIBLE} (Stream: {stream})")

        response = client.chat.completions.create(
            model=MODELO_COMPATIBLE,
            messages=data['history'],
            tools=data['tools'],
            stream=stream # Pasamos el parámetro stream a la API
        )
        
        if stream:
            # Si es un stream, devolvemos una respuesta en streaming
            def generate():
                for chunk in response:
                    yield f"data: {chunk.json()}\n\n"
            return Response(generate(), mimetype='text/event-stream')
        else:
            # Si no es un stream, devolvemos la respuesta completa
            return jsonify(json.loads(response.to_json()))
        
    except Exception as e:
        print(f"***** ERROR INTERNO DEL SERVIDOR EN /process-command *****")
# --- RUTA 3: PÁGINA DE INICIO (PARA VERIFICAR QUE ESTÁ VIVO) ---
@app.route('/')
def index():
    return "El cerebro del asistente está activo y en línea. ¡Listo para recibir comandos!"
    
# --- BLOQUE DE EJECUCIÓN ---
# Esta sección solo se ejecuta si corres el archivo directamente en un PC (python main.py)
# Cuando Render usa Gunicorn, este bloque se ignora, y Gunicorn usa directamente la variable 'app'.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
