# ==============================================================================
# --- CEREBRO DEL ASISTENTE (BACKEND) - VERSIÓN FINAL CORREGIDA ---
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

# = sí! Aquí tienes el código completo y corregido para tu archivo `main.py` del backend.

He aplicado la solución que discutimos para el `BadRequestError`. El único cambio está en la **sección 4**, donde se inicializa el cliente de `OpenAI`. He añadido el parámetro `default_headers` con la información que OpenRouter requiere para validar tus peticiones a modelos como Gemini Pro.

Tu URL de Render, `https://cerebro-asistente-backend.onrender.com`, se ha incluido directamente.

---

### **`main.py` (Backend Corregido)**

```python
# ==============================================================================
# --- CEREBRO DEL ASISTENTE (BACKEND) - VERSIÓN FINAL CORREGIDA ---
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
# --- INICIO DE LA CORRECCIÓN ---
# Añadimos headers personalizados para cumplir con los requisitos de OpenRouter
# y evitar el error 'BadRequestError' (400).
client = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://cerebro-asistente-backend.onrender.com", # Tu URL de Render
        "X-Title": "Dolphin Assistant", # El nombre de tu proyecto
    },
)
# --- FIN DE LA CORRECCIÓN ---

# ==============================================================================
# --- RUTAS DE LA API (LOS "PODERES" DE NUESTRO CEREBRO) ---
# ==============================================================================

# --- RUTA 1: TRANSCRIPCIÓN DE AUDIO (ESCUCHA MEJORADA) ---
@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    # Verifica que el frontend envió un archivo de audio
    if 'audio' not in request.files:
        return jsonify({"error": "Petición inválida: No se envió ningún archivo de audio."}), 400
    
    audio_file = request.files['audio']
    
    # Guarda el archivo de audio recibido en un archivo temporal para procesarlo
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        audio_file.save(temp_audio.name)
        
        try:
            # Abre el archivo temporal y lo envía a la API de Whisper a través de OpenRouter
            with open(temp_audio.name, "rb") as file_to_transcribe:
                print("[Backend] Recibido audio. Enviando a Whisper para transcripción...")
                
                transcription = client.audio.transcriptions.create(
                    model="openai/whisper-1",  # El modelo de transcripción de OpenAI
                    file=file_to_transcribe,
                    language="es"  # Especificamos español para mejorar la precisión
                )
                
            print(f"[Backend] Texto transcrito: '{transcription.text}'")
            # Devuelve el texto transcrito al frontend
            return jsonify({"text": transcription.text})

        except Exception as e:
            print(f"[Backend ERROR] Error durante la transcripción: {e}")
            return jsonify({"error": str(e)}), 500

# --- RUTA 2: PROCESAMIENTO DE COMANDOS (PENSAMIENTO DE LA IA) ---
@app.route('/process-command', methods=['POST'])
def process_command():
    # Obtiene los datos (historial de chat y lista de herramientas) del frontend
    data = request.get_json()
    
    # Valida que los datos necesarios fueron enviados
    # (El token de acceso se verificará en el futuro, por ahora lo dejamos así)
    if not data or 'history' not in data or 'tools' not in data:
        return jsonify({"error": "Petición inválida: Faltan datos de historial o herramientas."}), 400
        
    try:
        # ¡LA ELECCIÓN MÁS IMPORTANTE! Usamos un modelo potente y con buen plan gratuito.
        MODELO_COMPATIBLE = "google/gemini-pro"

        print(f"[Backend] Procesando comando con el modelo: {MODELO_COMPATIBLE}")

        # Hacemos la llamada a la IA con el historial y las herramientas
        response = client.chat.completions.create(
            model=MODELO_COMPATIBLE,
            messages=data['history'],
            tools=data['tools']
        )
        
        # Devuelve la respuesta completa de la IA al frontend
        return jsonify(json.loads(response.to_json()))
        
    except Exception as e:
        # Si algo sale mal, lo imprimimos en los logs de Render para poder verlo
        print(f"***** ERROR INTERNO DEL SERVIDOR EN /process-command *****")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        print(f"*****************************************************")
        # Y devolvemos un mensaje de error genérico al frontend
        return jsonify({"error": "Ocurrió un problema interno en el cerebro del asistente."}), 500

# --- RUTA 3: PÁGINA DE INICIO (PARA VERIFICAR QUE ESTÁ VIVO) ---
@app.route('/')
def index():
    return "El cerebro del asistente está activo y en línea. ¡Listo para recibir comandos!"
    
# --- BLOQUE DE EJECUCIÓN ---
# Esta sección solo se ejecuta si corres el archivo directamente en un PC (python main.py)
# Cuando Render usa Gunicorn, este bloque se ignora, y Gunicorn usa directamente la variable 'app'.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
