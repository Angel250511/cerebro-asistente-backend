# main.py en GitHub - VERSIÓN CORREGIDA PARA RENDER

# 1. Importar las herramientas necesarias
from flask import Flask, request, jsonify
import os
from openai import OpenAI
import json
import tempfile

# 2. Crear la aplicación web
app = Flask(__name__) # La variable 'app' es la que Gunicorn busca

# 3. Cargar la API Key de forma segura desde los "Secrets"
api_key_openrouter = os.environ.get("OPENROUTER_API_KEY")

# Verificar si la clave se cargó correctamente
if not api_key_openrouter:
    print("¡ALERTA! La OPENROUTER_API_KEY no se encontró en las variables de entorno.")

# 4. Preparar los clientes para hablar con la IA de OpenRouter
# Cliente para los modelos de LENGUAJE
client_language = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
)
# Cliente para la transcripción de AUDIO (Whisper)
client_audio = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
)

# --- RUTA PARA LA TRANSCRIPCIÓN DE AUDIO ---
@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No se encontró el archivo de audio"}), 400
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        audio_file.save(temp_audio.name)
        try:
            with open(temp_audio.name, "rb") as file_to_transcribe:
                transcription = client_audio.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=file_to_transcribe,
                    language="es"
                )
            return jsonify({"text": transcription.text})
        except Exception as e:
            print(f"Error durante la transcripción: {e}")
            return jsonify({"error": str(e)}), 500

# --- RUTA PARA PROCESAR COMANDOS ---
@app.route('/process-command', methods=['POST'])
def process_command():
    data = request.get_json()
    if not data or 'history' not in data or 'tools' not in data:
        return jsonify({"error": "Petición inválida"}), 400
    try:
        MODELO_GRATUITO = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        response = client_language.chat.completions.create(
            model=MODELO_GRATUITO,
            messages=data['history'],
            tools=data['tools'],
            tool_choice="auto"
        )
        return jsonify(json.loads(response.to_json()))
    except Exception as e:
        print(f"Error al contactar la IA: {e}")
        return jsonify({"error": str(e)}), 500

# --- RUTA DE BIENVENIDA ---
@app.route('/')
def index():
    return "El cerebro del asistente (v2 con Whisper) está activo y en línea."

# --- BLOQUE PARA EJECUCIÓN ---
# Esta sección solo se ejecuta si corres el archivo directamente (ej: python main.py)
# Gunicorn ignora este bloque y usa directamente la variable 'app' de arriba.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
