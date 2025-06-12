# main.py - El código completo para El Cerebro

# 1. Importar las herramientas necesarias
from flask import Flask, request, jsonify
import os
from openai import OpenAI
import json

# 2. Crear la aplicación web
app = Flask(__name__)

# 3. Cargar la API Key de forma segura desde los "Secrets"
api_key_openrouter = os.environ.get("OPENROUTER_API_KEY")

# Verificar si la clave se cargó correctamente
if not api_key_openrouter:
    print("¡ALERTA! La OPENROUTER_API_KEY no se encontró en los Secrets.")
    
# 4. Preparar el cliente para hablar con la IA de OpenRouter
client = OpenAI(
    api_key=api_key_openrouter,
    base_url="https://openrouter.ai/api/v1",
)

# 5. Definir la ruta principal que escuchará las peticiones del asistente
@app.route('/process-command', methods=['POST'])
def process_command():
    # Obtener los datos que envía el asistente (historial y herramientas)
    data = request.get_json()
    
    # Validar los datos
    if not data or 'history' not in data or 'tools' not in data:
        return jsonify({"error": "Petición inválida"}), 400
        
    try:
        # Elegir el modelo de IA gratuito que usaremos
        MODELO_GRATUITO = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        
        # Enviar la conversación a la IA para que la procese
        response = client.chat.completions.create(
            model=MODELO_GRATUITO,
            messages=data['history'],
            tools=data['tools'],
            tool_choice="auto"
        )
        
        # Devolver la respuesta de la IA al asistente
        return jsonify(json.loads(response.to_json()))
        
    except Exception as e:
        # Si algo sale mal, informar del error
        print(f"Error al contactar la IA: {e}")
        return jsonify({"error": str(e)}), 500

# 6. Una ruta de bienvenida para saber que el servidor está vivo
@app.route('/')
def index():
    return "El cerebro del asistente está activo y en línea."
    
# 7. Iniciar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
