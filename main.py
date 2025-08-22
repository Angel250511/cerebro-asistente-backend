# ==============================================================================
# --- CEREBRO DEL ASISTENTE (BACKEND) - VERSIÓN ESTABLE ---
# ==============================================================================

from flask import Flask, request, jsonify
import os
from openai import OpenAI
import json
import tempfile

app = Flask(__name__)
api_key_openrouter = os.environ.get("OPENROUTER_API_KEY")

if not api_key_openrouter:
    print("¡ALERTA CRÍTICA! OPENROUTER_API_KEY no encontrada.")

client = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://cerebro-asistente-backend.onrender.com",
        "X-Title": "Dolphin Assistant",
    },
)

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    # ... (Esta función no necesita cambios)
    if 'audio' not in request.files:
        return jsonify({"error": "Petición inválida: No se envió ningún archivo de audio."}), 400
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        audio_file.save(temp_audio.name)
        try:
            with open(temp_audio.name, "rb") as file_to_transcribe:
                transcription = client.audio.transcriptions.create(model="openai/whisper-1", file=file_to_transcribe, language="es")
            return jsonify({"text": transcription.text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/process-command', methods=['POST'])
def process_command():
    data = request.get_json()
    if not data or 'history' not in data or 'tools' not in data:
        return jsonify({"error": "Petición inválida."}), 400
        
    try:
        MODELO_COMPATIBLE = "mistralai/mistral-small-3.1-24b-instruct:free" 
        print(f"[Backend] Procesando comando con el modelo: {MODELO_COMPATIBLE}")

        response = client.chat.completions.create(
            model=MODELO_COMPATIBLE,
            messages=data['history'],
            tools=data['tools']
        )
        return jsonify(json.loads(response.to_json()))
        
    except Exception as e:
        print(f"***** ERROR INTERNO DEL SERVIDOR: {type(e).__name__}: {e} *****")
        return jsonify({"error": "Ocurrió un problema interno en el cerebro."}), 500

@app.route('/')
def index():
    return "El cerebro del asistente está activo y en línea. ¡Listo para recibir comandos!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
